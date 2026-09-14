#include "test_framework.hpp"
#include "criscvm.hpp"
#include "encoders.hpp"
#include <vector>
#include <cstdint>

extern bool g_debug;

TEST_CASE (test_eq_equal) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 42));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 42));
    pushInstr(bytecode, encodeRRR(Opcode::EQ, 3, 1, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_eq_not_equal) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 42));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 43));
    pushInstr(bytecode, encodeRRR(Opcode::EQ, 3, 1, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(3) == 0);
}

TEST_CASE (test_lt_signed_true) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0xFFFB));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0xFFFF));
    pushInstr(bytecode, encodeRR(Opcode::SEXT32, 1, 1));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 10));
    pushInstr(bytecode, encodeRRR(Opcode::LT, 3, 1, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_lt_signed_false) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 10));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0xFFFB));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0xFFFF));
    pushInstr(bytecode, encodeRR(Opcode::SEXT32, 2, 2));
    pushInstr(bytecode, encodeRRR(Opcode::LT, 3, 1, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(3) == 0);
}

TEST_CASE (test_ltu_unsigned_true) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 5));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0xFFFF));
    pushInstr(bytecode, encodeRRR(Opcode::LTU, 3, 1, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_ltu_unsigned_false) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 5));
    pushInstr(bytecode, encodeRRR(Opcode::LTU, 3, 1, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(3) == 0);
}

TEST_CASE (test_eqf32_equal) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 100));
    pushInstr(bytecode, encodeRR(Opcode::CVTI32F32, 1, 1));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 100));
    pushInstr(bytecode, encodeRR(Opcode::CVTI32F32, 2, 2));
    pushInstr(bytecode, encodeRRR(Opcode::EQF32, 3, 1, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_eqf32_not_equal) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 100));
    pushInstr(bytecode, encodeRR(Opcode::CVTI32F32, 1, 1));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 101));
    pushInstr(bytecode, encodeRR(Opcode::CVTI32F32, 2, 2));
    pushInstr(bytecode, encodeRRR(Opcode::EQF32, 3, 1, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(3) == 0);
}

TEST_CASE (test_eqf64_equal) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 1000));
    pushInstr(bytecode, encodeRR(Opcode::CVTI64F64, 1, 1));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 1000));
    pushInstr(bytecode, encodeRR(Opcode::CVTI64F64, 2, 2));
    pushInstr(bytecode, encodeRRR(Opcode::EQF64, 3, 1, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_ltf32_true) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 10));
    pushInstr(bytecode, encodeRR(Opcode::CVTI32F32, 1, 1));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 20));
    pushInstr(bytecode, encodeRR(Opcode::CVTI32F32, 2, 2));
    pushInstr(bytecode, encodeRRR(Opcode::LTF32, 3, 1, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_ltf32_false) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 20));
    pushInstr(bytecode, encodeRR(Opcode::CVTI32F32, 1, 1));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 10));
    pushInstr(bytecode, encodeRR(Opcode::CVTI32F32, 2, 2));
    pushInstr(bytecode, encodeRRR(Opcode::LTF32, 3, 1, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(3) == 0);
}

TEST_CASE (test_ltf64_true) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 100));
    pushInstr(bytecode, encodeRR(Opcode::CVTI64F64, 1, 1));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 200));
    pushInstr(bytecode, encodeRR(Opcode::CVTI64F64, 2, 2));
    pushInstr(bytecode, encodeRRR(Opcode::LTF64, 3, 1, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_lef32_less_than) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 10));
    pushInstr(bytecode, encodeRR(Opcode::CVTI32F32, 1, 1));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 20));
    pushInstr(bytecode, encodeRR(Opcode::CVTI32F32, 2, 2));
    pushInstr(bytecode, encodeRRR(Opcode::LEF32, 3, 1, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_lef32_equal) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 15));
    pushInstr(bytecode, encodeRR(Opcode::CVTI32F32, 1, 1));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 15));
    pushInstr(bytecode, encodeRR(Opcode::CVTI32F32, 2, 2));
    pushInstr(bytecode, encodeRRR(Opcode::LEF32, 3, 1, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_lef32_false) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 20));
    pushInstr(bytecode, encodeRR(Opcode::CVTI32F32, 1, 1));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 10));
    pushInstr(bytecode, encodeRR(Opcode::CVTI32F32, 2, 2));
    pushInstr(bytecode, encodeRRR(Opcode::LEF32, 3, 1, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(3) == 0);
}

TEST_CASE (test_lef64_less_than) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 100));
    pushInstr(bytecode, encodeRR(Opcode::CVTI64F64, 1, 1));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 200));
    pushInstr(bytecode, encodeRR(Opcode::CVTI64F64, 2, 2));
    pushInstr(bytecode, encodeRRR(Opcode::LEF64, 3, 1, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(3) == 1);
}

TEST_CASE (test_lef64_equal) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 150));
    pushInstr(bytecode, encodeRR(Opcode::CVTI64F64, 1, 1));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 150));
    pushInstr(bytecode, encodeRR(Opcode::CVTI64F64, 2, 2));
    pushInstr(bytecode, encodeRRR(Opcode::LEF64, 3, 1, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    
    CeruleanRISCVM vm(bytecode, g_debug);
    vm.run();
    REQUIRE(vm.getRegister(3) == 1);
}
