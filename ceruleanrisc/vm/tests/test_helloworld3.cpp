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

// Helloworld3 - Uses a loop to print the Hello World string
TEST_CASE(test_helloworld3) {
    std::vector<uint8_t> bytecode;
    const std::string msg = "Hello, World!\n";
    uint16_t str_addr = 0x38;
    uint16_t str_end  = str_addr + msg.size();
    uint16_t loop_cond = 0x20;
    uint16_t loop_end  = 0x34;

    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, str_addr));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, str_end));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 3, loop_cond));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 3, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 4, loop_end));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 4, 0));

    // [0x20] loop_cond: bge r5, r1, r4
    pushInstr(bytecode, encodeRRR(Opcode::BGE, 5, 1, 4));
    // [0x24] lb r2, 0(r5)
    pushInstr(bytecode, encodeRRI(Opcode::LOAD8, 2, 5, 0));
    // [0x28] putchar(r2)
    pushInstr(bytecode, encodeR(Opcode::PUTCHAR, 2));
    // [0x2C] addi r5, r5, 1
    pushInstr(bytecode, encodeRRI(Opcode::ADD32I, 5, 5, 1));
    // [0x30] jmp r3
    pushInstr(bytecode, encodeR(Opcode::JMP, 3));
    // [0x34] loop_end: halt
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    while (bytecode.size() < str_addr) {
        bytecode.push_back(0x00);
    }
    for (char c : msg) {
        bytecode.push_back(c);
    }

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
