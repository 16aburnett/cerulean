#include "test_framework.hpp"
#include "ceruleanvm.hpp"
#include "tee_buf.hpp"
#include <fstream>
#include <vector>
#include <cstdint>
#include <sstream>
#include <iostream>

extern bool g_debug;

// Helloworld2 - Hello world string is stored in code memory
TEST_CASE(test_helloworld2) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0xc8, 0x00, // [0x00] r0.0 <- string_addr
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x04] r0.1 <- string_addr
        Opcode::LOAD8,   0x10, 0x00, 0x00, // [0x08] lb r1, r0, 0x00 ; load char from mem
        Opcode::PUTCHAR, 0x10, 0x00, 0x00, // [0x0c] putchar(r1)
        Opcode::ADD32I,  0x00, 0x01, 0x00, // [0x10] addi r0, r0, 1 ; move to next char
        Opcode::LOAD8,   0x10, 0x00, 0x00, // [0x14] lb r1, r0, 0x00 ; load char from mem
        Opcode::PUTCHAR, 0x10, 0x00, 0x00, // [0x18] putchar(r1)
        Opcode::ADD32I,  0x00, 0x01, 0x00, // [0x1c] addi r0, r0, 1 ; move to next char
        Opcode::LOAD8,   0x10, 0x00, 0x00, // [0x20] lb r1, r0, 0x00 ; load char from mem
        Opcode::PUTCHAR, 0x10, 0x00, 0x00, // [0x24] putchar(r1)
        Opcode::ADD32I,  0x00, 0x01, 0x00, // [0x28] addi r0, r0, 1 ; move to next char
        Opcode::LOAD8,   0x10, 0x00, 0x00, // [0x2c] lb r1, r0, 0x00 ; load char from mem
        Opcode::PUTCHAR, 0x10, 0x00, 0x00, // [0x30] putchar(r1)
        Opcode::ADD32I,  0x00, 0x01, 0x00, // [0x34] addi r0, r0, 1 ; move to next char
        Opcode::LOAD8,   0x10, 0x00, 0x00, // [0x38] lb r1, r0, 0x00 ; load char from mem
        Opcode::PUTCHAR, 0x10, 0x00, 0x00, // [0x3c] putchar(r1)
        Opcode::ADD32I,  0x00, 0x01, 0x00, // [0x40] addi r0, r0, 1 ; move to next char
        Opcode::LOAD8,   0x10, 0x00, 0x00, // [0x44] lb r1, r0, 0x00 ; load char from mem
        Opcode::PUTCHAR, 0x10, 0x00, 0x00, // [0x48] putchar(r1)
        Opcode::ADD32I,  0x00, 0x01, 0x00, // [0x4c] addi r0, r0, 1 ; move to next char
        Opcode::LOAD8,   0x10, 0x00, 0x00, // [0x50] lb r1, r0, 0x00 ; load char from mem
        Opcode::PUTCHAR, 0x10, 0x00, 0x00, // [0x54] putchar(r1)
        Opcode::ADD32I,  0x00, 0x01, 0x00, // [0x58] addi r0, r0, 1 ; move to next char
        Opcode::LOAD8,   0x10, 0x00, 0x00, // [0x5c] lb r1, r0, 0x00 ; load char from mem
        Opcode::PUTCHAR, 0x10, 0x00, 0x00, // [0x60] putchar(r1)
        Opcode::ADD32I,  0x00, 0x01, 0x00, // [0x64] addi r0, r0, 1 ; move to next char
        Opcode::LOAD8,   0x10, 0x00, 0x00, // [0x68] lb r1, r0, 0x00 ; load char from mem
        Opcode::PUTCHAR, 0x10, 0x00, 0x00, // [0x6c] putchar(r1)
        Opcode::ADD32I,  0x00, 0x01, 0x00, // [0x70] addi r0, r0, 1 ; move to next char
        Opcode::LOAD8,   0x10, 0x00, 0x00, // [0x74] lb r1, r0, 0x00 ; load char from mem
        Opcode::PUTCHAR, 0x10, 0x00, 0x00, // [0x78] putchar(r1)
        Opcode::ADD32I,  0x00, 0x01, 0x00, // [0x7c] addi r0, r0, 1 ; move to next char
        Opcode::LOAD8,   0x10, 0x00, 0x00, // [0x80] lb r1, r0, 0x00 ; load char from mem
        Opcode::PUTCHAR, 0x10, 0x00, 0x00, // [0x84] putchar(r1)
        Opcode::ADD32I,  0x00, 0x01, 0x00, // [0x88] addi r0, r0, 1 ; move to next char
        Opcode::LOAD8,   0x10, 0x00, 0x00, // [0x8c] lb r1, r0, 0x00 ; load char from mem
        Opcode::PUTCHAR, 0x10, 0x00, 0x00, // [0x90] putchar(r1)
        Opcode::ADD32I,  0x00, 0x01, 0x00, // [0x94] addi r0, r0, 1 ; move to next char
        Opcode::LOAD8,   0x10, 0x00, 0x00, // [0x98] lb r1, r0, 0x00 ; load char from mem
        Opcode::PUTCHAR, 0x10, 0x00, 0x00, // [0x9c] putchar(r1)
        Opcode::ADD32I,  0x00, 0x01, 0x00, // [0xa0] addi r0, r0, 1 ; move to next char
        Opcode::LOAD8,   0x10, 0x00, 0x00, // [0xa4] lb r1, r0, 0x00 ; load char from mem
        Opcode::PUTCHAR, 0x10, 0x00, 0x00, // [0xa8] putchar(r1)
        Opcode::HALT,    0x00, 0x00, 0x00, // [0xac]
        0x00,            0x00, 0x00, 0x00, // [0xb0] buffer
        0x00,            0x00, 0x00, 0x00, // [0xb4] buffer
        0x00,            0x00, 0x00, 0x00, // [0xb8] buffer
        0x00,            0x00, 0x00, 0x00, // [0xbc] buffer
        0x00,            0x00, 0x00, 0x00, // [0xc0] buffer
        0x00,            0x00, 0x00, 0x00, // [0xc4] buffer
        'H',              'e',  'l',  'l', // [0xc8] string_addr
        'o',              ',',  ' ',  'W', // [0xcc]
        'o',              'r',  'l',  'd', // [0xd0]
        '!',             '\n', 0x00, 0x00, // [0xd4]
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
