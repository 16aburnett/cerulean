#include "test_framework.hpp"
#include "criscvm.hpp"
#include "encoders.hpp"
#include <vector>
#include <cstdint>
#include <cmath>

extern bool g_debug;

TEST_CASE (test_sext8_positive) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0x7F));
    pushInstr(bytecode, encodeRR(Opcode::SEXT8, 2, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(2) == 127);
}

TEST_CASE (test_sext8_negative) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0xFF));
    pushInstr(bytecode, encodeRR(Opcode::SEXT8, 2, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(2) == 0xFFFFFFFFFFFFFFFFULL);
}

TEST_CASE (test_sext16_positive) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0x7FFF));
    pushInstr(bytecode, encodeRR(Opcode::SEXT16, 2, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(2) == 32767);
}

TEST_CASE (test_sext16_negative) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, -1));
    pushInstr(bytecode, encodeRR(Opcode::SEXT16, 2, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(2) == 0xFFFFFFFFFFFFFFFFULL);
}

TEST_CASE (test_sext32_positive) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0x7FFF));
    pushInstr(bytecode, encodeRR(Opcode::SEXT32, 2, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(2) == 2147483647);
}

TEST_CASE (test_sext32_negative) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0xFFFF));
    pushInstr(bytecode, encodeRR(Opcode::SEXT32, 2, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(2) == 0xFFFFFFFFFFFFFFFFULL);
}

TEST_CASE (test_zext8) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0xFF));
    pushInstr(bytecode, encodeRR(Opcode::ZEXT8, 2, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(2) == 255);
}

TEST_CASE (test_zext16) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, -1));
    pushInstr(bytecode, encodeRR(Opcode::ZEXT16, 2, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(2) == 65535);
}

TEST_CASE (test_zext32) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0xFFFF));
    pushInstr(bytecode, encodeRR(Opcode::ZEXT32, 2, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(2) == 4294967295ULL);
}

TEST_CASE (test_cvti32f32_positive) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 100));
    pushInstr(bytecode, encodeRR(Opcode::CVTI32F32, 2, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    uint64_t raw = vm.getRegister(2);
    float value = *reinterpret_cast<float*>(&raw);
    REQUIRE(std::abs(value - 100.0f) < 0.001f);
}

TEST_CASE (test_cvti64f64_positive) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 1000));
    pushInstr(bytecode, encodeRR(Opcode::CVTI64F64, 2, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    uint64_t raw = vm.getRegister(2);
    double value = *reinterpret_cast<double*>(&raw);
    REQUIRE(std::abs(value - 1000.0) < 0.001);
}

TEST_CASE (test_cvtf32i32_roundtrip) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 100));
    pushInstr(bytecode, encodeRR(Opcode::CVTI32F32, 1, 1));
    pushInstr(bytecode, encodeRR(Opcode::CVTF32I32, 2, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(2) == 100);
}

TEST_CASE (test_cvtf64i64_roundtrip) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 1000));
    pushInstr(bytecode, encodeRR(Opcode::CVTI64F64, 1, 1));
    pushInstr(bytecode, encodeRR(Opcode::CVTF64I64, 2, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(2) == 1000);
}

TEST_CASE (test_cvtf32f64) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 100));
    pushInstr(bytecode, encodeRR(Opcode::CVTI32F32, 1, 1));
    pushInstr(bytecode, encodeRR(Opcode::CVTF32F64, 2, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    uint64_t raw = vm.getRegister(2);
    double value = *reinterpret_cast<double*>(&raw);
    REQUIRE(std::abs(value - 100.0) < 0.001);
}

TEST_CASE (test_cvtf64f32) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 1000));
    pushInstr(bytecode, encodeRR(Opcode::CVTI64F64, 1, 1));
    pushInstr(bytecode, encodeRR(Opcode::CVTF64F32, 2, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    uint64_t raw = vm.getRegister(2);
    float value = *reinterpret_cast<float*>(&raw);
    REQUIRE(std::abs(value - 1000.0f) < 0.001f);
}
