#include "test_framework.hpp"
#include "criscvm.hpp"
#include <vector>
#include <cstdint>

extern bool g_debug;

// ========================================================================================
// Integer Comparison Tests
// ========================================================================================

TEST_CASE (test_eq_equal) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 42
        Opcode::LLI, 0x10, 0x2A, 0x00,
        // LLI r2, 42
        Opcode::LLI, 0x20, 0x2A, 0x00,
        // EQ r3, r1, r2 - should set r3 to 1
        Opcode::EQ, 0x31, 0x20, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_eq_not_equal) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 42
        Opcode::LLI, 0x10, 0x2A, 0x00,
        // LLI r2, 43
        Opcode::LLI, 0x20, 0x2B, 0x00,
        // EQ r3, r1, r2 - should set r3 to 0
        Opcode::EQ, 0x31, 0x20, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    REQUIRE(vm.getRegister(3) == 0);
}

TEST_CASE (test_lt_signed_true) {
    std::vector<uint8_t> bytecode = {
        // Load -5 into r1 using sign-extension
        Opcode::LUI, 0x10, 0xFF, 0xFF,  // Upper word = 0xFFFF
        Opcode::LLI, 0x10, 0xFB, 0xFF,  // Lower word = 0xFFFB (-5 in 32-bit)
        Opcode::SEXT32, 0x11, 0x00, 0x00, // Sign-extend to 64-bit
        // LLI r2, 10
        Opcode::LLI, 0x20, 0x0A, 0x00,
        // LT r3, r1, r2 - should set r3 to 1 (-5 < 10)
        Opcode::LT, 0x31, 0x20, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_lt_signed_false) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 10
        Opcode::LLI, 0x10, 0x0A, 0x00,
        // Load -5 into r2
        Opcode::LUI, 0x20, 0xFF, 0xFF,
        Opcode::LLI, 0x20, 0xFB, 0xFF,
        Opcode::SEXT32, 0x22, 0x00, 0x00,
        // LT r3, r1, r2 - should set r3 to 0 (10 < -5 is false)
        Opcode::LT, 0x31, 0x20, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    REQUIRE(vm.getRegister(3) == 0);
}

TEST_CASE (test_ltu_unsigned_true) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 5
        Opcode::LLI, 0x10, 0x05, 0x00,
        // LUI r2, 0xFFFF, LLI r2, 0xFFFF (large unsigned value)
        Opcode::LUI, 0x20, 0xFF, 0xFF,
        Opcode::LLI, 0x20, 0xFF, 0xFF,
        // LTU r3, r1, r2 - should set r3 to 1 (5 < 0xFFFFFFFF unsigned)
        Opcode::LTU, 0x31, 0x20, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_ltu_unsigned_false) {
    std::vector<uint8_t> bytecode = {
        // LUI r1, 0xFFFF, LLI r1, 0xFFFF (large unsigned)
        Opcode::LUI, 0x10, 0xFF, 0xFF,
        Opcode::LLI, 0x10, 0xFF, 0xFF,
        // LLI r2, 5
        Opcode::LLI, 0x20, 0x05, 0x00,
        // LTU r3, r1, r2 - should set r3 to 0 (0xFFFFFFFF < 5 is false unsigned)
        Opcode::LTU, 0x31, 0x20, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    REQUIRE(vm.getRegister(3) == 0);
}

// ========================================================================================
// Floating-Point Comparison Tests
// ========================================================================================

TEST_CASE (test_eqf32_equal) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 100
        Opcode::LLI, 0x10, 0x64, 0x00,
        // CVTI32F32 r1, r1 - convert to float32
        Opcode::CVTI32F32, 0x11, 0x00, 0x00,
        // LLI r2, 100
        Opcode::LLI, 0x20, 0x64, 0x00,
        // CVTI32F32 r2, r2 - convert to float32
        Opcode::CVTI32F32, 0x22, 0x00, 0x00,
        // EQF32 r3, r1, r2 - should set r3 to 1
        Opcode::EQF32, 0x31, 0x20, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_eqf32_not_equal) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 100
        Opcode::LLI, 0x10, 0x64, 0x00,
        // CVTI32F32 r1, r1
        Opcode::CVTI32F32, 0x11, 0x00, 0x00,
        // LLI r2, 101
        Opcode::LLI, 0x20, 0x65, 0x00,
        // CVTI32F32 r2, r2
        Opcode::CVTI32F32, 0x22, 0x00, 0x00,
        // EQF32 r3, r1, r2 - should set r3 to 0
        Opcode::EQF32, 0x31, 0x20, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    REQUIRE(vm.getRegister(3) == 0);
}

TEST_CASE (test_eqf64_equal) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 1000
        Opcode::LLI, 0x10, 0xE8, 0x03,
        // CVTI64F64 r1, r1
        Opcode::CVTI64F64, 0x11, 0x00, 0x00,
        // LLI r2, 1000
        Opcode::LLI, 0x20, 0xE8, 0x03,
        // CVTI64F64 r2, r2
        Opcode::CVTI64F64, 0x22, 0x00, 0x00,
        // EQF64 r3, r1, r2 - should set r3 to 1
        Opcode::EQF64, 0x31, 0x20, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_ltf32_true) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 10
        Opcode::LLI, 0x10, 0x0A, 0x00,
        // CVTI32F32 r1, r1
        Opcode::CVTI32F32, 0x11, 0x00, 0x00,
        // LLI r2, 20
        Opcode::LLI, 0x20, 0x14, 0x00,
        // CVTI32F32 r2, r2
        Opcode::CVTI32F32, 0x22, 0x00, 0x00,
        // LTF32 r3, r1, r2 - should set r3 to 1 (10.0 < 20.0)
        Opcode::LTF32, 0x31, 0x20, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_ltf32_false) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 20
        Opcode::LLI, 0x10, 0x14, 0x00,
        // CVTI32F32 r1, r1
        Opcode::CVTI32F32, 0x11, 0x00, 0x00,
        // LLI r2, 10
        Opcode::LLI, 0x20, 0x0A, 0x00,
        // CVTI32F32 r2, r2
        Opcode::CVTI32F32, 0x22, 0x00, 0x00,
        // LTF32 r3, r1, r2 - should set r3 to 0 (20.0 < 10.0 is false)
        Opcode::LTF32, 0x31, 0x20, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    REQUIRE(vm.getRegister(3) == 0);
}

TEST_CASE (test_ltf64_true) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 100
        Opcode::LLI, 0x10, 0x64, 0x00,
        // CVTI64F64 r1, r1
        Opcode::CVTI64F64, 0x11, 0x00, 0x00,
        // LLI r2, 200
        Opcode::LLI, 0x20, 0xC8, 0x00,
        // CVTI64F64 r2, r2
        Opcode::CVTI64F64, 0x22, 0x00, 0x00,
        // LTF64 r3, r1, r2 - should set r3 to 1 (100.0 < 200.0)
        Opcode::LTF64, 0x31, 0x20, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_lef32_less_than) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 10
        Opcode::LLI, 0x10, 0x0A, 0x00,
        // CVTI32F32 r1, r1
        Opcode::CVTI32F32, 0x11, 0x00, 0x00,
        // LLI r2, 20
        Opcode::LLI, 0x20, 0x14, 0x00,
        // CVTI32F32 r2, r2
        Opcode::CVTI32F32, 0x22, 0x00, 0x00,
        // LEF32 r3, r1, r2 - should set r3 to 1 (10.0 <= 20.0)
        Opcode::LEF32, 0x31, 0x20, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_lef32_equal) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 15
        Opcode::LLI, 0x10, 0x0F, 0x00,
        // CVTI32F32 r1, r1
        Opcode::CVTI32F32, 0x11, 0x00, 0x00,
        // LLI r2, 15
        Opcode::LLI, 0x20, 0x0F, 0x00,
        // CVTI32F32 r2, r2
        Opcode::CVTI32F32, 0x22, 0x00, 0x00,
        // LEF32 r3, r1, r2 - should set r3 to 1 (15.0 <= 15.0)
        Opcode::LEF32, 0x31, 0x20, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_lef32_false) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 20
        Opcode::LLI, 0x10, 0x14, 0x00,
        // CVTI32F32 r1, r1
        Opcode::CVTI32F32, 0x11, 0x00, 0x00,
        // LLI r2, 10
        Opcode::LLI, 0x20, 0x0A, 0x00,
        // CVTI32F32 r2, r2
        Opcode::CVTI32F32, 0x22, 0x00, 0x00,
        // LEF32 r3, r1, r2 - should set r3 to 0 (20.0 <= 10.0 is false)
        Opcode::LEF32, 0x31, 0x20, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    REQUIRE(vm.getRegister(3) == 0);
}

TEST_CASE (test_lef64_less_than) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 100
        Opcode::LLI, 0x10, 0x64, 0x00,
        // CVTI64F64 r1, r1
        Opcode::CVTI64F64, 0x11, 0x00, 0x00,
        // LLI r2, 200
        Opcode::LLI, 0x20, 0xC8, 0x00,
        // CVTI64F64 r2, r2
        Opcode::CVTI64F64, 0x22, 0x00, 0x00,
        // LEF64 r3, r1, r2 - should set r3 to 1 (100.0 <= 200.0)
        Opcode::LEF64, 0x31, 0x20, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_lef64_equal) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 150
        Opcode::LLI, 0x10, 0x96, 0x00,
        // CVTI64F64 r1, r1
        Opcode::CVTI64F64, 0x11, 0x00, 0x00,
        // LLI r2, 150
        Opcode::LLI, 0x20, 0x96, 0x00,
        // CVTI64F64 r2, r2
        Opcode::CVTI64F64, 0x22, 0x00, 0x00,
        // LEF64 r3, r1, r2 - should set r3 to 1 (150.0 <= 150.0)
        Opcode::LEF64, 0x31, 0x20, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    REQUIRE(vm.getRegister(3) == 1);
}
