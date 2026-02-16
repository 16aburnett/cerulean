#include "test_framework.hpp"
#include "criscvm.hpp"
#include <vector>
#include <cstdint>
#include <cmath>

extern bool g_debug;

// ========================================================================================
// Sign Extension Tests
// ========================================================================================

TEST_CASE (test_sext8_positive) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 127 (0x7F) - positive byte
        Opcode::LLI, 0x10, 0x7F, 0x00,
        // SEXT8 r2, r1 - sign extend byte
        Opcode::SEXT8, 0x21, 0x00, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    // Positive byte should remain positive: 0x7F -> 0x000000000000007F
    REQUIRE(vm.getRegister(2) == 127);
}

TEST_CASE (test_sext8_negative) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 255 (0xFF) - negative byte (-1)
        Opcode::LLI, 0x10, 0xFF, 0x00,
        // SEXT8 r2, r1 - sign extend byte
        Opcode::SEXT8, 0x21, 0x00, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    // 0xFF should sign-extend to -1: 0xFF -> 0xFFFFFFFFFFFFFFFF
    REQUIRE(vm.getRegister(2) == 0xFFFFFFFFFFFFFFFFULL);
}

TEST_CASE (test_sext16_positive) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 32767 (0x7FFF) - positive halfword
        Opcode::LLI, 0x10, 0xFF, 0x7F,
        // SEXT16 r2, r1 - sign extend halfword
        Opcode::SEXT16, 0x21, 0x00, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    // Positive halfword should remain positive: 0x7FFF -> 0x0000000000007FFF
    REQUIRE(vm.getRegister(2) == 32767);
}

TEST_CASE (test_sext16_negative) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 65535 (0xFFFF) - negative halfword (-1)
        Opcode::LLI, 0x10, 0xFF, 0xFF,
        // SEXT16 r2, r1 - sign extend halfword
        Opcode::SEXT16, 0x21, 0x00, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    // 0xFFFF should sign-extend to -1: 0xFFFF -> 0xFFFFFFFFFFFFFFFF
    REQUIRE(vm.getRegister(2) == 0xFFFFFFFFFFFFFFFFULL);
}

TEST_CASE (test_sext32_positive) {
    std::vector<uint8_t> bytecode = {
        // LUI r1, 32767 (0x7FFF) - upper halfword
        Opcode::LUI, 0x10, 0xFF, 0x7F,
        // LLI r1, 65535 (0xFFFF) - lower halfword
        Opcode::LLI, 0x10, 0xFF, 0xFF,
        // SEXT32 r2, r1 - sign extend word
        Opcode::SEXT32, 0x21, 0x00, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    // Positive word should remain positive: 0x7FFFFFFF -> 0x000000007FFFFFFF
    REQUIRE(vm.getRegister(2) == 2147483647);
}

TEST_CASE (test_sext32_negative) {
    std::vector<uint8_t> bytecode = {
        // LUI r1, 65535 (0xFFFF) - upper halfword
        Opcode::LUI, 0x10, 0xFF, 0xFF,
        // LLI r1, 65535 (0xFFFF) - lower halfword
        Opcode::LLI, 0x10, 0xFF, 0xFF,
        // SEXT32 r2, r1 - sign extend word
        Opcode::SEXT32, 0x21, 0x00, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    // 0xFFFFFFFF should sign-extend to -1: 0xFFFFFFFF -> 0xFFFFFFFFFFFFFFFF
    REQUIRE(vm.getRegister(2) == 0xFFFFFFFFFFFFFFFFULL);
}

// ========================================================================================
// Zero Extension Tests
// ========================================================================================

TEST_CASE (test_zext8) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 255 (0xFF) - byte value
        Opcode::LLI, 0x10, 0xFF, 0x00,
        // ZEXT8 r2, r1 - zero extend byte
        Opcode::ZEXT8, 0x21, 0x00, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    // 0xFF should zero-extend: 0xFF -> 0x00000000000000FF
    REQUIRE(vm.getRegister(2) == 255);
}

TEST_CASE (test_zext16) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 65535 (0xFFFF) - halfword value
        Opcode::LLI, 0x10, 0xFF, 0xFF,
        // ZEXT16 r2, r1 - zero extend halfword
        Opcode::ZEXT16, 0x21, 0x00, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    // 0xFFFF should zero-extend: 0xFFFF -> 0x000000000000FFFF
    REQUIRE(vm.getRegister(2) == 65535);
}

TEST_CASE (test_zext32) {
    std::vector<uint8_t> bytecode = {
        // LUI r1, 65535 (0xFFFF) - upper halfword
        Opcode::LUI, 0x10, 0xFF, 0xFF,
        // LLI r1, 65535 (0xFFFF) - lower halfword
        Opcode::LLI, 0x10, 0xFF, 0xFF,
        // ZEXT32 r2, r1 - zero extend word
        Opcode::ZEXT32, 0x21, 0x00, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    // 0xFFFFFFFF should zero-extend: 0xFFFFFFFF -> 0x00000000FFFFFFFF
    REQUIRE(vm.getRegister(2) == 4294967295ULL);
}

// ========================================================================================
// Integer to Float Conversion Tests
// ========================================================================================

TEST_CASE (test_cvti32f32_positive) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 100
        Opcode::LLI, 0x10, 0x64, 0x00,
        // CVTI32F32 r2, r1 - convert int32 to float32
        Opcode::CVTI32F32, 0x21, 0x00, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    // 100 (int32) -> 100.0 (float32)
    // Reinterpret the register as float
    uint64_t raw = vm.getRegister(2);
    float value = *reinterpret_cast<float*>(&raw);
    REQUIRE(std::abs(value - 100.0f) < 0.001f);
}

TEST_CASE (test_cvti64f64_positive) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 1000
        Opcode::LLI, 0x10, 0xE8, 0x03,
        // CVTI64F64 r2, r1 - convert int64 to float64
        Opcode::CVTI64F64, 0x21, 0x00, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    // 1000 (int64) -> 1000.0 (float64)
    uint64_t raw = vm.getRegister(2);
    double value = *reinterpret_cast<double*>(&raw);
    REQUIRE(std::abs(value - 1000.0) < 0.001);
}

// ========================================================================================
// Float to Integer Conversion Tests
// ========================================================================================

TEST_CASE (test_cvtf32i32_roundtrip) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 100
        Opcode::LLI, 0x10, 0x64, 0x00,
        // CVTI32F32 r1, r1 - convert to float first
        Opcode::CVTI32F32, 0x11, 0x00, 0x00,
        // CVTF32I32 r2, r1 - convert float32 back to int32
        Opcode::CVTF32I32, 0x21, 0x00, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    // 100 -> 100.0 -> 100 (should round-trip)
    REQUIRE(vm.getRegister(2) == 100);
}

TEST_CASE (test_cvtf64i64_roundtrip) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 1000
        Opcode::LLI, 0x10, 0xE8, 0x03,
        // CVTI64F64 r1, r1 - convert to double first
        Opcode::CVTI64F64, 0x11, 0x00, 0x00,
        // CVTF64I64 r2, r1 - convert float64 back to int64
        Opcode::CVTF64I64, 0x21, 0x00, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    // 1000 -> 1000.0 -> 1000 (should round-trip)
    REQUIRE(vm.getRegister(2) == 1000);
}

// ========================================================================================
// Float Precision Conversion Tests
// ========================================================================================

TEST_CASE (test_cvtf32f64) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 100
        Opcode::LLI, 0x10, 0x64, 0x00,
        // CVTI32F32 r1, r1 - convert to float32: 100.0f
        Opcode::CVTI32F32, 0x11, 0x00, 0x00,
        // CVTF32F64 r2, r1 - convert float32 to float64
        Opcode::CVTF32F64, 0x21, 0x00, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    // 100.0f (float32) -> 100.0 (float64)
    uint64_t raw = vm.getRegister(2);
    double value = *reinterpret_cast<double*>(&raw);
    REQUIRE(std::abs(value - 100.0) < 0.001);
}

TEST_CASE (test_cvtf64f32) {
    std::vector<uint8_t> bytecode = {
        // LLI r1, 1000
        Opcode::LLI, 0x10, 0xE8, 0x03,
        // CVTI64F64 r1, r1 - convert to float64: 1000.0
        Opcode::CVTI64F64, 0x11, 0x00, 0x00,
        // CVTF64F32 r2, r1 - convert float64 to float32
        Opcode::CVTF64F32, 0x21, 0x00, 0x00,
        // HALT
        Opcode::HALT, 0x00, 0x00, 0x00
    };
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    
    // 1000.0 (float64) -> 1000.0f (float32)
    uint64_t raw = vm.getRegister(2);
    float value = *reinterpret_cast<float*>(&raw);
    REQUIRE(std::abs(value - 1000.0f) < 0.001f);
}
