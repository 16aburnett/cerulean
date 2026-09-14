#include "test_framework.hpp"
#include "criscvm.hpp"
#include "encoders.hpp"
#include "tee_buf.hpp"
#include <fstream>
#include <vector>
#include <cstdint>
#include <sstream>
#include <iostream>

extern bool g_debug;

// Helloworld4 - Encasulates string printing to a function
TEST_CASE(test_helloworld4) {
    std::vector<uint8_t> bytecode;
    const std::string msg = "Hello, World!\n";

    uint16_t print_str_addr = 0x20;
    uint16_t loop_cond = print_str_addr + 15 * 4; // 0x5C
    uint16_t loop_end  = loop_cond + 5 * 4;       // 0x70
    uint16_t str_addr  = loop_end + 9 * 4;        // 0x94

    // main:
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, str_addr));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeR(Opcode::PUSH, 1));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 9, print_str_addr));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 9, 0));
    pushInstr(bytecode, encodeR(Opcode::CALL, 9));
    pushInstr(bytecode, encodeR(Opcode::POP, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT)); // 0x20

    // print_string:
    pushInstr(bytecode, encodeR(Opcode::PUSH, 30)); // bp
    pushInstr(bytecode, encodeRRI(Opcode::ADD64I, 30, 31, 0)); // bp = sp
    pushInstr(bytecode, encodeR(Opcode::PUSH, 1));
    pushInstr(bytecode, encodeR(Opcode::PUSH, 2));
    pushInstr(bytecode, encodeR(Opcode::PUSH, 3));
    pushInstr(bytecode, encodeR(Opcode::PUSH, 4));
    pushInstr(bytecode, encodeR(Opcode::PUSH, 5));
    pushInstr(bytecode, encodeR(Opcode::PUSH, 9));

    // get param string_addr from [bp + 16]
    pushInstr(bytecode, encodeRRI(Opcode::LOAD32, 1, 30, 16));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 3, loop_cond));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 3, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 4, loop_end));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 4, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));

    // loop_cond: lb r2, 0(r1)
    pushInstr(bytecode, encodeRRI(Opcode::LOAD8, 2, 1, 0));
    // beq r2, r5, r4
    pushInstr(bytecode, encodeRRR(Opcode::BEQ, 2, 5, 4));
    // putchar(r2)
    pushInstr(bytecode, encodeR(Opcode::PUTCHAR, 2));
    // addi r1, r1, 1
    pushInstr(bytecode, encodeRRI(Opcode::ADD32I, 1, 1, 1));
    // jmp r3
    pushInstr(bytecode, encodeR(Opcode::JMP, 3));

    // loop_end:
    pushInstr(bytecode, encodeR(Opcode::POP, 9));
    pushInstr(bytecode, encodeR(Opcode::POP, 5));
    pushInstr(bytecode, encodeR(Opcode::POP, 4));
    pushInstr(bytecode, encodeR(Opcode::POP, 3));
    pushInstr(bytecode, encodeR(Opcode::POP, 2));
    pushInstr(bytecode, encodeR(Opcode::POP, 1));
    pushInstr(bytecode, encodeRRI(Opcode::ADD64I, 31, 30, 0)); // sp = bp
    pushInstr(bytecode, encodeR(Opcode::POP, 30)); // bp
    pushInstr(bytecode, encodeNONE(Opcode::RET));

    while (bytecode.size() < str_addr) {
        bytecode.push_back(0x00);
    }
    for (char c : msg) {
        bytecode.push_back(c);
    }
    bytecode.push_back(0x00);
    bytecode.push_back(0x00);

    // Temporarily redirect std::cout to dualOut
    std::ostringstream captured;
    TeeBuf tee(std::cout.rdbuf(), captured);
    std::ostream dualOut(&tee);
    auto* originalBuf = std::cout.rdbuf();
    std::cout.rdbuf(dualOut.rdbuf());

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    // Restore std::cout
    std::cout.rdbuf(originalBuf);

    // Ensure stdout matches expected output
    REQUIRE(captured.str() == "Hello, World!\n");
}
