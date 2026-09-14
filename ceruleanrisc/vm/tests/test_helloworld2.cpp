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

// Helloworld2 - Hello world string is stored in code memory
TEST_CASE(test_helloworld2) {
    std::vector<uint8_t> bytecode;
    // Load string_addr (0xC8) into r1
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0xC8));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    const std::string msg = "Hello, World!\n";
    for (size_t i = 0; i < msg.size(); ++i) {
        pushInstr(bytecode, encodeRRI(Opcode::LOAD8, 2, 1, 0));
        pushInstr(bytecode, encodeR(Opcode::PUTCHAR, 2));
        pushInstr(bytecode, encodeRRI(Opcode::ADD32I, 1, 1, 1));
    }
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    while (bytecode.size() < 0xC8) {
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
