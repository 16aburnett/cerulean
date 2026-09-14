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

// Helloworld - Super simple Hello World program
TEST_CASE(test_helloworld1) {
    std::vector<uint8_t> bytecode;
    const std::string msg = "Hello, World!\n";
    for (char c : msg) {
        pushInstr(bytecode, encodeRI(Opcode::LLI, 9, c));
        pushInstr(bytecode, encodeRI(Opcode::LUI, 9, 0));
        pushInstr(bytecode, encodeR(Opcode::PUTCHAR, 9));
    }
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

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
