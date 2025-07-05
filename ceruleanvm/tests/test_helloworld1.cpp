#include "test_framework.hpp"
#include "ceruleanvm.hpp"
#include "tee_buf.hpp"
#include <fstream>
#include <vector>
#include <cstdint>
#include <sstream>
#include <iostream>

extern bool g_debug;

// Helloworld - Super simple Hello World program
TEST_CASE(test_helloworld1) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x90,  'H', 0x00, // [0x00] r9 <- 'H'
        Opcode::LUI,     0x90, 0x00, 0x00, // [0x04] r9 <- 'H'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x08] putchar(r9)
        Opcode::LLI,     0x90,  'e', 0x00, // [0x0c] r9 <- 'e'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x14] putchar(r9)
        Opcode::LLI,     0x90,  'l', 0x00, // [0x18] r9 <- 'l'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x20] putchar(r9)
        Opcode::LLI,     0x90,  'l', 0x00, // [0x24] r9 <- 'l'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x2c] putchar(r9)
        Opcode::LLI,     0x90,  'o', 0x00, // [0x30] r9 <- 'o'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x38] putchar(r9)
        Opcode::LLI,     0x90,  ',', 0x00, // [0x30] r9 <- ','
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x38] putchar(r9)
        Opcode::LLI,     0x90,  ' ', 0x00, // [0x30] r9 <- ' '
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x38] putchar(r9)
        Opcode::LLI,     0x90,  'W', 0x00, // [0x30] r9 <- 'W'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x38] putchar(r9)
        Opcode::LLI,     0x90,  'o', 0x00, // [0x30] r9 <- 'o'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x38] putchar(r9)
        Opcode::LLI,     0x90,  'r', 0x00, // [0x30] r9 <- 'r'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x38] putchar(r9)
        Opcode::LLI,     0x90,  'l', 0x00, // [0x30] r9 <- 'l'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x38] putchar(r9)
        Opcode::LLI,     0x90,  'd', 0x00, // [0x30] r9 <- 'd'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x38] putchar(r9)
        Opcode::LLI,     0x90,  '!', 0x00, // [0x30] r9 <- '!'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x38] putchar(r9)
        Opcode::LLI,     0x90, '\n', 0x00, // [0x3c] r9 <- '\n'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x44] putchar(r9)
        Opcode::HALT
    };

    // Temporarily redirect std::cout to dualOut
    std::ostringstream captured;
    TeeBuf tee(std::cout.rdbuf(), captured);
    std::ostream dualOut(&tee);
    auto* originalBuf = std::cout.rdbuf();
    std::cout.rdbuf(dualOut.rdbuf());

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    // Restore std::cout
    std::cout.rdbuf(originalBuf);

    // Ensure stdout matches expected output
    REQUIRE(captured.str() == "Hello, World!\n");
}
