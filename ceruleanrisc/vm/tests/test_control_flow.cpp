#include "test_framework.hpp"
#include "criscvm.hpp"
#include "tee_buf.hpp"
#include <fstream>
#include <vector>
#include <cstdint>
#include <sstream>
#include <iostream>

extern bool g_debug;

TEST_CASE (test_control_flow_conditional) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x0a, 0x00, // [0x00] r0.0 <- 10
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x04] r0.1 <- 0
        Opcode::LLI,     0x10, 0x0f, 0x00, // [0x08] r1.0 <- 15
        Opcode::LUI,     0x10, 0x00, 0x00, // [0x0c] r1.1 <- 0
        Opcode::LLI,     0x20, 0x20, 0x00, // [0x10] r2.0 <- cond_end
        Opcode::LUI,     0x20, 0x00, 0x00, // [0x14] r2.1 <- 0
        Opcode::BGE,     0x10, 0x20, 0x00, // [0x18] BGE r1, r0, r2(cond_end) // if r1 >= r0, jump to cond_end
        // cond_true: if r0 > 15
        Opcode::LLI,     0x00, 0x01, 0x00, // [0x1c] r0.0 <- 1
        // cond_end:
        Opcode::HALT,    0x00, 0x00, 0x00, // [0x20]
    };

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (0) == 10);
}

TEST_CASE (test_control_flow_loop) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x00, 0x00, // [0x00] r0.0 <- 0 ; i = 0
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x04] r0.1 <- 0
        Opcode::LLI,     0x10, 0x0a, 0x00, // [0x08] r1.0 <- 10 ; N = 10
        Opcode::LUI,     0x10, 0x00, 0x00, // [0x0c] r1.1 <- 0
        Opcode::LLI,     0x20, 0x40, 0x00, // [0x10] r2.0 <- loop_end
        Opcode::LUI,     0x20, 0x00, 0x00, // [0x14] r2.1 <- 0
        Opcode::LLI,     0x30, 0x30, 0x00, // [0x18] r3.0 <- loop_cond
        Opcode::LUI,     0x30, 0x00, 0x00, // [0x1c] r3.1 <- 0
        Opcode::LLI,     0x40,  '*', 0x00, // [0x20] r4.0 <- '*'
        Opcode::LUI,     0x40, 0x00, 0x00, // [0x24] r4.1 <- 0
        Opcode::LLI,     0x50, '\n', 0x00, // [0x28] r5.0 <- '\n'
        Opcode::LUI,     0x50, 0x00, 0x00, // [0x2c] r5.1 <- 0
        // loop_cond:
        Opcode::BGE,     0x01, 0x20, 0x00, // [0x30] beq r0, r1, r2(loop_end) ; i >= N
        // loop_body:
        Opcode::PUTCHAR, 0x40, 0x00, 0x00, // [0x34] putchar(r4) ; print '*'
        // loop_update:
        Opcode::ADD32I,  0x00, 0x01, 0x00, // [0x38] addi r0, r0, 1 ; i = i + 1
        Opcode::JMP,     0x30, 0x00, 0x00, // [0x3c] jmp r3 ; jmp loop_cond
        // loop_end:
        Opcode::PUTCHAR, 0x50, 0x00, 0x00, // [0x40] putchar(r5) ; print '\n'
        Opcode::HALT,    0x00, 0x00, 0x00, // [0x44]
    };

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
    REQUIRE(captured.str() == "**********\n");
    REQUIRE (vm.getRegister (0) == 10); // Ensure i == N
}

TEST_CASE (test_beq_taken) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x05, 0x00, // r0 <- 5
        Opcode::LUI,     0x00, 0x00, 0x00,
        Opcode::LLI,     0x10, 0x05, 0x00, // r1 <- 5
        Opcode::LUI,     0x10, 0x00, 0x00,
        Opcode::LLI,     0x20, 0x20, 0x00, // r2 <- jump_target (0x20)
        Opcode::LUI,     0x20, 0x00, 0x00,
        Opcode::BEQ,     0x01, 0x20, 0x00, // BEQ r0, r1, r2 (should jump)
        Opcode::LLI,     0x00, 0xFF, 0x00, // r0 <- 0xFF (should be skipped)
        // jump_target:
        Opcode::HALT,    0x00, 0x00, 0x00,
    };

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (0) == 5); // Should still be 5, not 0xFF
}

TEST_CASE (test_beq_not_taken) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x05, 0x00, // r0 <- 5
        Opcode::LUI,     0x00, 0x00, 0x00,
        Opcode::LLI,     0x10, 0x0A, 0x00, // r1 <- 10
        Opcode::LUI,     0x10, 0x00, 0x00,
        Opcode::LLI,     0x20, 0x20, 0x00, // r2 <- jump_target (0x20)
        Opcode::LUI,     0x20, 0x00, 0x00,
        Opcode::BEQ,     0x01, 0x20, 0x00, // BEQ r0, r1, r2 (should not jump)
        Opcode::LLI,     0x00, 0xFF, 0x00, // r0 <- 0xFF (should execute)
        Opcode::HALT,    0x00, 0x00, 0x00,
    };

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (0) == 0xFF); // Should be modified to 0xFF
}

TEST_CASE (test_bne_taken) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x05, 0x00, // r0 <- 5
        Opcode::LUI,     0x00, 0x00, 0x00,
        Opcode::LLI,     0x10, 0x0A, 0x00, // r1 <- 10
        Opcode::LUI,     0x10, 0x00, 0x00,
        Opcode::LLI,     0x20, 0x20, 0x00, // r2 <- jump_target (0x20)
        Opcode::LUI,     0x20, 0x00, 0x00,
        Opcode::BNE,     0x01, 0x20, 0x00, // BNE r0, r1, r2 (should jump)
        Opcode::LLI,     0x00, 0xFF, 0x00, // r0 <- 0xFF (should be skipped)
        // jump_target:
        Opcode::HALT,    0x00, 0x00, 0x00,
    };

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (0) == 5); // Should still be 5, not 0xFF
}

TEST_CASE (test_bne_not_taken) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x05, 0x00, // r0 <- 5
        Opcode::LUI,     0x00, 0x00, 0x00,
        Opcode::LLI,     0x10, 0x05, 0x00, // r1 <- 5
        Opcode::LUI,     0x10, 0x00, 0x00,
        Opcode::LLI,     0x20, 0x20, 0x00, // r2 <- jump_target (0x20)
        Opcode::LUI,     0x20, 0x00, 0x00,
        Opcode::BNE,     0x01, 0x20, 0x00, // BNE r0, r1, r2 (should not jump)
        Opcode::LLI,     0x00, 0xFF, 0x00, // r0 <- 0xFF (should execute)
        Opcode::HALT,    0x00, 0x00, 0x00,
    };

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (0) == 0xFF); // Should be modified to 0xFF
}

TEST_CASE (test_blt_signed_taken) {
    std::vector<uint8_t> bytecode = {
        // Store -1 (0xFFFFFFFF) at [sp-8]
        Opcode::LLI,     0x20, 0xFF, 0xFF, // r2 <- 0xFFFFFFFF
        Opcode::LUI,     0x20, 0xFF, 0xFF,
        Opcode::STORE32, 0xf2, 0xF8, 0xFF, // [sp-8] <- r2
        // Load -1 with sign-extension into r0
        Opcode::LOAD32,  0x0f, 0xF8, 0xFF, // r0 <- [sp-8] (sign-extended)
        Opcode::LLI,     0x10, 0x05, 0x00, // r1 <- 5
        Opcode::LUI,     0x10, 0x00, 0x00,
        Opcode::LLI,     0x30, 0x2C, 0x00, // r3 <- jump_target (0x2C)
        Opcode::LUI,     0x30, 0x00, 0x00,
        Opcode::BLT,     0x01, 0x30, 0x00, // BLT r0, r1, r3 (signed: -1 < 5, should jump)
        Opcode::LLI,     0x00, 0xAA, 0x00, // r0 <- 0xAA (should be skipped)
        Opcode::LUI,     0x00, 0x00, 0x00,
        // jump_target:
        Opcode::HALT,    0x00, 0x00, 0x00,
    };

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (0) == 0xFFFFFFFFFFFFFFFF); // Should still be -1 (fully sign-extended)
}

TEST_CASE (test_blt_signed_not_taken) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x0A, 0x00, // r0 <- 10
        Opcode::LUI,     0x00, 0x00, 0x00,
        Opcode::LLI,     0x10, 0x05, 0x00, // r1 <- 5
        Opcode::LUI,     0x10, 0x00, 0x00,
        Opcode::LLI,     0x20, 0x20, 0x00, // r2 <- jump_target (0x20)
        Opcode::LUI,     0x20, 0x00, 0x00,
        Opcode::BLT,     0x01, 0x20, 0x00, // BLT r0, r1, r2 (10 < 5 is false, should not jump)
        Opcode::LLI,     0x00, 0xAA, 0x00, // r0 <- 0xAA (should execute)
        Opcode::HALT,    0x00, 0x00, 0x00,
    };

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (0) == 0xAA); // Should be modified to 0xAA
}

TEST_CASE (test_bge_signed_taken) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x05, 0x00, // r0 <- 5
        Opcode::LUI,     0x00, 0x00, 0x00,
        // Store -1 (0xFFFFFFFF) at [sp-8]
        Opcode::LLI,     0x20, 0xFF, 0xFF, // r2 <- 0xFFFFFFFF
        Opcode::LUI,     0x20, 0xFF, 0xFF,
        Opcode::STORE32, 0xf2, 0xF8, 0xFF, // [sp-8] <- r2
        // Load -1 with sign-extension into r1
        Opcode::LOAD32,  0x1f, 0xF8, 0xFF, // r1 <- [sp-8] (sign-extended)
        Opcode::LLI,     0x30, 0x30, 0x00, // r3 <- jump_target (0x30)
        Opcode::LUI,     0x30, 0x00, 0x00,
        Opcode::BGE,     0x01, 0x30, 0x00, // BGE r0, r1, r3 (signed: 5 >= -1, should jump)
        Opcode::LLI,     0x00, 0xAA, 0x00, // r0 <- 0xAA (should be skipped)
        Opcode::LUI,     0x00, 0x00, 0x00,
        // jump_target:
        Opcode::HALT,    0x00, 0x00, 0x00,
    };

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (0) == 5); // Should still be 5
}

TEST_CASE (test_bge_signed_not_taken) {
    std::vector<uint8_t> bytecode = {
        // Store -1 (0xFFFFFFFF) at [sp-8]
        Opcode::LLI,     0x20, 0xFF, 0xFF, // r2 <- 0xFFFFFFFF
        Opcode::LUI,     0x20, 0xFF, 0xFF,
        Opcode::STORE32, 0xf2, 0xF8, 0xFF, // [sp-8] <- r2
        // Load -1 with sign-extension into r0
        Opcode::LOAD32,  0x0f, 0xF8, 0xFF, // r0 <- [sp-8] (sign-extended)
        Opcode::LLI,     0x10, 0x05, 0x00, // r1 <- 5
        Opcode::LUI,     0x10, 0x00, 0x00,
        Opcode::LLI,     0x30, 0x2C, 0x00, // r3 <- jump_target (0x2C)
        Opcode::LUI,     0x30, 0x00, 0x00,
        Opcode::BGE,     0x01, 0x30, 0x00, // BGE r0, r1, r3 (signed: -1 >= 5 is false, should not jump)
        Opcode::XOR64,   0x00, 0x00, 0x00, // r0 <- r0 ^ r0 = 0 (clear register)
        Opcode::LLI,     0x00, 0xAA, 0x00, // r0 <- 0xAA (should execute)
        Opcode::HALT,    0x00, 0x00, 0x00,
    };

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (0) == 0xAA); // Should be modified to 0xAA
}

TEST_CASE (test_bltu_unsigned_taken) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x05, 0x00, // r0 <- 5
        Opcode::LUI,     0x00, 0x00, 0x00,
        Opcode::LLI,     0x10, 0xFF, 0xFF, // r1 <- 0xFFFF (large unsigned value)
        Opcode::LUI,     0x10, 0xFF, 0xFF,
        Opcode::LLI,     0x20, 0x20, 0x00, // r2 <- jump_target (0x20)
        Opcode::LUI,     0x20, 0x00, 0x00,
        Opcode::BLTU,    0x01, 0x20, 0x00, // BLTU r0, r1, r2 (unsigned: 5 < 0xFFFFFFFFFFFFFFFF, should jump)
        Opcode::LLI,     0x00, 0xAA, 0x00, // r0 <- 0xAA (should be skipped)
        // jump_target:
        Opcode::HALT,    0x00, 0x00, 0x00,
    };

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (0) == 5); // Should still be 5
}

TEST_CASE (test_bltu_unsigned_not_taken) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0xFF, 0xFF, // r0 <- 0xFFFF (large unsigned value)
        Opcode::LUI,     0x00, 0xFF, 0xFF,
        Opcode::LLI,     0x10, 0x05, 0x00, // r1 <- 5
        Opcode::LUI,     0x10, 0x00, 0x00,
        Opcode::LLI,     0x20, 0x24, 0x00, // r2 <- jump_target (0x24)
        Opcode::LUI,     0x20, 0x00, 0x00,
        Opcode::BLTU,    0x01, 0x20, 0x00, // BLTU r0, r1, r2 (unsigned: 0xFFFFFFFFFFFFFFFF < 5 is false, should not jump)
        Opcode::LLI,     0x00, 0xAA, 0x00, // r0 <- 0xAA (should execute)
        Opcode::LUI,     0x00, 0x00, 0x00,
        Opcode::HALT,    0x00, 0x00, 0x00,
    };

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (0) == 0xAA); // Should be modified to 0xAA
}

TEST_CASE (test_bgeu_unsigned_taken) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0xFF, 0xFF, // r0 <- 0xFFFF (large unsigned value)
        Opcode::LUI,     0x00, 0xFF, 0xFF,
        Opcode::LLI,     0x10, 0x05, 0x00, // r1 <- 5
        Opcode::LUI,     0x10, 0x00, 0x00,
        Opcode::LLI,     0x20, 0x24, 0x00, // r2 <- jump_target (0x24)
        Opcode::LUI,     0x20, 0x00, 0x00,
        Opcode::BGEU,    0x01, 0x20, 0x00, // BGEU r0, r1, r2 (unsigned: 0xFFFFFFFFFFFFFFFF >= 5, should jump)
        Opcode::LLI,     0x00, 0xAA, 0x00, // r0 <- 0xAA (should be skipped)
        Opcode::LUI,     0x00, 0x00, 0x00,
        // jump_target:
        Opcode::HALT,    0x00, 0x00, 0x00,
    };

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (0) == 0x00000000FFFFFFFF); // Should still be 0xFFFF in lower 32 bits
}

TEST_CASE (test_bgeu_unsigned_not_taken) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x05, 0x00, // r0 <- 5
        Opcode::LUI,     0x00, 0x00, 0x00,
        Opcode::LLI,     0x10, 0xFF, 0xFF, // r1 <- 0xFFFF (large unsigned value)
        Opcode::LUI,     0x10, 0xFF, 0xFF,
        Opcode::LLI,     0x20, 0x20, 0x00, // r2 <- jump_target (0x20)
        Opcode::LUI,     0x20, 0x00, 0x00,
        Opcode::BGEU,    0x01, 0x20, 0x00, // BGEU r0, r1, r2 (unsigned: 5 >= 0xFFFFFFFFFFFFFFFF is false, should not jump)
        Opcode::LLI,     0x00, 0xAA, 0x00, // r0 <- 0xAA (should execute)
        Opcode::HALT,    0x00, 0x00, 0x00,
    };

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (0) == 0xAA); // Should be modified to 0xAA
}

TEST_CASE (test_jmp) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x05, 0x00, // r0 <- 5
        Opcode::LUI,     0x00, 0x00, 0x00,
        Opcode::LLI,     0x10, 0x18, 0x00, // r1 <- jump_target (0x18)
        Opcode::LUI,     0x10, 0x00, 0x00,
        Opcode::JMP,     0x10, 0x00, 0x00, // JMP r1 (unconditional jump)
        Opcode::LLI,     0x00, 0xFF, 0x00, // r0 <- 0xFF (should be skipped)
        // jump_target:
        Opcode::HALT,    0x00, 0x00, 0x00,
    };

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (0) == 5); // Should still be 5, not 0xFF
}
