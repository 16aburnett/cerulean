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

TEST_CASE (test_load8_sign_extend) {
    std::vector<uint8_t> bytecode = {
        // Use stack pointer (r15=sp) with negative offsets to write into stack
        
        // Store positive byte (0x7F) - should sign-extend to 0x000000000000007F
        Opcode::LLI,     0x20, 0x7F, 0x00, // r2 <- 0x7F
        Opcode::STORE8,  0xf2, 0xF8, 0xFF, // [r15-8] <- r2 (store 0x7F)
        
        // Store negative byte (0xFF) - should sign-extend to 0xFFFFFFFFFFFFFFFF
        Opcode::LLI,     0x30, 0xFF, 0x00, // r3 <- 0xFF
        Opcode::STORE8,  0xf3, 0xF7, 0xFF, // [r15-9] <- r3 (store 0xFF)
        
        // Test LOAD8 (signed) - positive value
        Opcode::LOAD8,   0x4f, 0xF8, 0xFF, // r4 <- [r15-8] (load 0x7F with sign-extend)
        
        // Test LOAD8 (signed) - negative value
        Opcode::LOAD8,   0x5f, 0xF7, 0xFF, // r5 <- [r15-9] (load 0xFF with sign-extend)
        
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    // Positive byte should sign-extend to positive 64-bit value
    REQUIRE (vm.getRegister (4) == 0x000000000000007Ful);
    // Negative byte (0xFF) should sign-extend to all 1s
    REQUIRE (vm.getRegister (5) == 0xFFFFFFFFFFFFFFFFul);
}

TEST_CASE (test_loadu8_zero_extend) {
    std::vector<uint8_t> bytecode = {
        // Use stack pointer (r15=sp) with negative offsets
        
        // Store byte 0x7F
        Opcode::LLI,     0x20, 0x7F, 0x00, // r2 <- 0x7F
        Opcode::STORE8,  0xf2, 0xF8, 0xFF, // [r15-8] <- r2
        
        // Store byte 0xFF
        Opcode::LLI,     0x30, 0xFF, 0x00, // r3 <- 0xFF
        Opcode::STORE8,  0xf3, 0xF7, 0xFF, // [r15-9] <- r3
        
        // Test LOADU8 (unsigned) - should zero-extend
        Opcode::LOADU8,  0x4f, 0xF8, 0xFF, // r4 <- [r15-8] (load 0x7F with zero-extend)
        Opcode::LOADU8,  0x5f, 0xF7, 0xFF, // r5 <- [r15-9] (load 0xFF with zero-extend)
        
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    // Both should zero-extend (no sign bit propagation)
    REQUIRE (vm.getRegister (4) == 0x000000000000007Ful);
    REQUIRE (vm.getRegister (5) == 0x00000000000000FFul);
}

TEST_CASE (test_load16_sign_extend) {
    std::vector<uint8_t> bytecode = {
        // Use stack pointer (r15=sp) with negative offsets
        
        // Store positive 16-bit value (0x7FFF)
        Opcode::LLI,     0x20, 0xFF, 0x7F, // r2 <- 0x7FFF
        Opcode::STORE16, 0xf2, 0xF8, 0xFF, // [r15-8] <- r2
        
        // Store negative 16-bit value (0xFFFF)
        Opcode::LLI,     0x30, 0xFF, 0xFF, // r3 <- 0xFFFF
        Opcode::STORE16, 0xf3, 0xF0, 0xFF, // [r15-16] <- r3
        
        // Test LOAD16 (signed)
        Opcode::LOAD16,  0x4f, 0xF8, 0xFF, // r4 <- [r15-8]
        Opcode::LOAD16,  0x5f, 0xF0, 0xFF, // r5 <- [r15-16]
        
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (4) == 0x0000000000007FFFul);
    REQUIRE (vm.getRegister (5) == 0xFFFFFFFFFFFFFFFFul);
}

TEST_CASE (test_loadu16_zero_extend) {
    std::vector<uint8_t> bytecode = {
        // Use stack pointer (r15=sp) with negative offsets
        
        // Store 16-bit values
        Opcode::LLI,     0x20, 0xFF, 0x7F, // r2 <- 0x7FFF
        Opcode::STORE16, 0xf2, 0xF8, 0xFF, // [r15-8] <- r2
        
        Opcode::LLI,     0x30, 0xFF, 0xFF, // r3 <- 0xFFFF
        Opcode::STORE16, 0xf3, 0xF0, 0xFF, // [r15-16] <- r3
        
        // Test LOADU16 (unsigned)
        Opcode::LOADU16, 0x4f, 0xF8, 0xFF, // r4 <- [r15-8]
        Opcode::LOADU16, 0x5f, 0xF0, 0xFF, // r5 <- [r15-16]
        
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (4) == 0x0000000000007FFFul);
    REQUIRE (vm.getRegister (5) == 0x000000000000FFFFul);
}

TEST_CASE (test_load32_sign_extend) {
    std::vector<uint8_t> bytecode = {
        // Use stack pointer (r15=sp) with negative offsets
        
        // Store positive 32-bit value (0x7FFFFFFF)
        Opcode::LLI,     0x20, 0xFF, 0xFF, // r2 <- 0xFFFF
        Opcode::LUI,     0x20, 0xFF, 0x7F, // r2 <- 0x7FFFFFFF
        Opcode::STORE32, 0xf2, 0xF8, 0xFF, // [r15-8] <- r2
        
        // Store negative 32-bit value (0xFFFFFFFF)
        Opcode::LLI,     0x30, 0xFF, 0xFF, // r3 <- 0xFFFF
        Opcode::LUI,     0x30, 0xFF, 0xFF, // r3 <- 0xFFFFFFFF
        Opcode::STORE32, 0xf3, 0xF0, 0xFF, // [r15-16] <- r3
        
        // Test LOAD32 (signed)
        Opcode::LOAD32,  0x4f, 0xF8, 0xFF, // r4 <- [r15-8]
        Opcode::LOAD32,  0x5f, 0xF0, 0xFF, // r5 <- [r15-16]
        
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (4) == 0x000000007FFFFFFFul);
    REQUIRE (vm.getRegister (5) == 0xFFFFFFFFFFFFFFFFul);
}

TEST_CASE (test_loadu32_zero_extend) {
    std::vector<uint8_t> bytecode = {
        // Use stack pointer (r15=sp) with negative offsets
        
        // Store 32-bit values
        Opcode::LLI,     0x20, 0xFF, 0xFF, // r2 <- 0xFFFF
        Opcode::LUI,     0x20, 0xFF, 0x7F, // r2 <- 0x7FFFFFFF
        Opcode::STORE32, 0xf2, 0xF8, 0xFF, // [r15-8] <- r2
        
        Opcode::LLI,     0x30, 0xFF, 0xFF, // r3 <- 0xFFFF
        Opcode::LUI,     0x30, 0xFF, 0xFF, // r3 <- 0xFFFFFFFF
        Opcode::STORE32, 0xf3, 0xF0, 0xFF, // [r15-16] <- r3
        
        // Test LOADU32 (unsigned)
        Opcode::LOADU32, 0x4f, 0xF8, 0xFF, // r4 <- [r15-8]
        Opcode::LOADU32, 0x5f, 0xF0, 0xFF, // r5 <- [r15-16]
        
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (4) == 0x000000007FFFFFFFul);
    REQUIRE (vm.getRegister (5) == 0x00000000FFFFFFFFul);
}

TEST_CASE (test_load64) {
    std::vector<uint8_t> bytecode = {
        // Use stack pointer (r15=sp) with negative offsets
        
        // Store 64-bit value (0x123456789ABCDEF0)
        // Build lower 32 bits first
        Opcode::LLI,     0x20, 0x78, 0x56, // r2 <- 0x5678
        Opcode::LUI,     0x20, 0x34, 0x12, // r2 <- 0x12345678
        // Shift to upper 32 bits
        Opcode::SLL64I,  0x22, 0x20, 0x00, // r2 <- r2 << 32 = 0x1234567800000000
        // Build lower 32 bits
        Opcode::LLI,     0x20, 0xF0, 0xDE, // r2 lower <- 0xDEF0
        Opcode::LUI,     0x20, 0xBC, 0x9A, // r2 lower <- 0x9ABCDEF0
        // Now r2 = 0x123456789ABCDEF0
        Opcode::STORE64, 0xf2, 0xF8, 0xFF, // [r15-8] <- r2
        
        // Test LOAD64
        Opcode::LOAD64,  0x3f, 0xF8, 0xFF, // r3 <- [r15-8]
        
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (3) == 0x123456789ABCDEF0ul);
}
