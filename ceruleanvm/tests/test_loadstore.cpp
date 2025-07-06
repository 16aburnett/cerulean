#include "test_framework.hpp"
#include "ceruleanvm.hpp"
#include "tee_buf.hpp"
#include <fstream>
#include <vector>
#include <cstdint>
#include <sstream>
#include <iostream>

extern bool g_debug;

TEST_CASE (test_loadstore_imm) {
    std::vector<uint8_t> bytecode = {
        // Load  8bit imm value 0x12
        Opcode::LLI,     0x00, 0x12, 0x00, // [0x] r0.0 <- 0x12
        // Load 16bit imm value 0x1234
        Opcode::LLI,     0x10, 0x34, 0x12, // [0x] r1.0 <- 0x1234
        // Load 32bit imm value 0x12345678
        Opcode::LLI,     0x20, 0x78, 0x56, // [0x] r2.1 <- 0x5678
        Opcode::LUI,     0x20, 0x34, 0x12, // [0x] r2.0 <- 0x1234
        // Load 64bit imm value 0x12345678_90abcdef
        Opcode::LLI,     0x30, 0x78, 0x56, // [0x] r3.0 <- 0x5678
        Opcode::LUI,     0x30, 0x34, 0x12, // [0x] r3.1 <- 0x1234
        Opcode::SLL64I,  0x33, 0x20, 0x00, // [0x] r3 <- r3 << 32 // shift to top half of 64bit
        Opcode::LLI,     0x30, 0xef, 0xcd, // [0x] r3.0 <- 0xcdef
        Opcode::LUI,     0x30, 0xab, 0x90, // [0x] r3.1 <- 0x90ab
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (0) == 0x12ul);
    REQUIRE (vm.getRegister (1) == 0x1234ul);
    REQUIRE (vm.getRegister (2) == 0x12345678ul);
    REQUIRE (vm.getRegister (3) == 0x1234567890abcdeful);
}
