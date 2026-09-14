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

TEST_CASE (test_arithmetic_add) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 10));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 15));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::ADD32, 3, 1, 2));
    pushInstr(bytecode, encodeRRI(Opcode::ADD32I, 4, 1, 3));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));
    pushInstr(bytecode, encodeRRI(Opcode::SUB64I, 5, 5, 1));
    pushInstr(bytecode, encodeRRR(Opcode::ADD64, 7, 5, 5));
    pushInstr(bytecode, encodeRRI(Opcode::ADD64I, 6, 5, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (3) == 25); // 10 + 15 = 25
    REQUIRE (vm.getRegister (4) == 13); // 10 + 3 = 13
    REQUIRE (vm.getRegister (7) == (-1ul + -1ul));
    REQUIRE (vm.getRegister (6) == 0ul); // -1 + 1 = 0
}

TEST_CASE (test_arithmetic_sub) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 10));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 15));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::SUB32, 3, 1, 2));
    pushInstr(bytecode, encodeRRI(Opcode::SUB32I, 4, 1, 3));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));
    pushInstr(bytecode, encodeRRR(Opcode::SUB64, 6, 5, 5));
    pushInstr(bytecode, encodeRRI(Opcode::SUB64I, 7, 5, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (static_cast<int32_t>(vm.getRegister (3)) == -5); // 10 - 15 = -5
    REQUIRE (static_cast<int32_t>(vm.getRegister (4)) == 7); // 10 - 3 = 7
    REQUIRE (static_cast<int32_t>(vm.getRegister (6)) == 0ul); // -1 - -1 = 0
    REQUIRE (static_cast<int32_t>(vm.getRegister (7)) == 0xfffffffffffffffful);
}

TEST_CASE (test_arithmetic_mul) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 10));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 15));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::MUL32, 3, 1, 2));
    pushInstr(bytecode, encodeRRI(Opcode::MUL32I, 4, 1, 3));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0xFFFF));
    pushInstr(bytecode, encodeRRR(Opcode::MUL64, 6, 5, 5));
    pushInstr(bytecode, encodeRRI(Opcode::MUL64I, 7, 5, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (3) == 150); // 10 * 15 = 150
    REQUIRE (vm.getRegister (4) == 30); // 10 * 3 = 30
    REQUIRE (vm.getRegister (6) == (0xfffffffful * 0xfffffffful));
    REQUIRE (vm.getRegister (7) == (0xfffffffful * 2ul));
}

TEST_CASE (test_arithmetic_divi) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 10));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 15));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::DIVI32, 3, 1, 2));
    pushInstr(bytecode, encodeRRI(Opcode::DIVI32I, 4, 1, 3));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0xF000));
    pushInstr(bytecode, encodeRRI(Opcode::MUL64I, 5, 5, 2));
    pushInstr(bytecode, encodeRRR(Opcode::DIVI64, 6, 5, 1));
    pushInstr(bytecode, encodeRRI(Opcode::DIVI64I, 7, 5, 2));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 9, 0));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 9, 0));
    pushInstr(bytecode, encodeRRI(Opcode::SUB64I, 9, 9, 1));
    pushInstr(bytecode, encodeRRR(Opcode::DIVI64, 10, 5, 9));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (3) == 0l); // 10 / 15 = 0
    REQUIRE (vm.getRegister (4) == 3l); // 10 / 3 = 3
    REQUIRE (vm.getRegister (6) == (0xf0000000l * 2l / 10l));
    REQUIRE (vm.getRegister (7) == (0xf0000000l * 2l / 2l));
    REQUIRE (vm.getRegister (10) == (0xf0000000l * 2l / -1l));
}

TEST_CASE (test_arithmetic_divu) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 10));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 15));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::DIVU32, 3, 1, 2));
    pushInstr(bytecode, encodeRRI(Opcode::DIVU32I, 4, 1, 3));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0xF000));
    pushInstr(bytecode, encodeRRI(Opcode::MUL64I, 5, 5, 2));
    pushInstr(bytecode, encodeRRR(Opcode::DIVU64, 6, 5, 1));
    pushInstr(bytecode, encodeRRI(Opcode::DIVU64I, 7, 5, 2));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 9, 0));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 9, 0));
    pushInstr(bytecode, encodeRRI(Opcode::SUB64I, 9, 9, 1));
    pushInstr(bytecode, encodeRRR(Opcode::DIVU64, 10, 5, 9));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (3) == 0l); // 10 / 15 = 0
    REQUIRE (vm.getRegister (4) == 3l); // 10 / 3 = 3
    REQUIRE (vm.getRegister (6) == (0xf0000000ul * 2ul / 10ul));
    REQUIRE (vm.getRegister (7) == (0xf0000000ul * 2ul / 2ul));
    REQUIRE (vm.getRegister (10) == (0xf0000000ul * 2ul / -1ul));
}

TEST_CASE (test_arithmetic_modi) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 10));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 15));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::MODI32, 3, 1, 2));
    pushInstr(bytecode, encodeRRI(Opcode::MODI32I, 4, 1, 3));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0xF000));
    pushInstr(bytecode, encodeRRI(Opcode::MUL64I, 5, 5, 2));
    pushInstr(bytecode, encodeRRR(Opcode::MODI64, 6, 5, 1));
    pushInstr(bytecode, encodeRRI(Opcode::MODI64I, 7, 5, 2));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 9, 0));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 9, 0));
    pushInstr(bytecode, encodeRRI(Opcode::SUB64I, 9, 9, 1));
    pushInstr(bytecode, encodeRRR(Opcode::MODI64, 10, 5, 9));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (3) == 10); // 10 % 15 = 10
    REQUIRE (vm.getRegister (4) == 1); // 10 % 3 = 1
    REQUIRE (vm.getRegister (6) == (0xf0000000l * 2l % 10l));
    REQUIRE (vm.getRegister (7) == (0xf0000000l * 2l % 2l));
    REQUIRE (vm.getRegister (10) == (0xf0000000l * 2l % -1l));
}

TEST_CASE (test_arithmetic_modu) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 10));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 15));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::MODU32, 3, 1, 2));
    pushInstr(bytecode, encodeRRI(Opcode::MODU32I, 4, 1, 3));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0xF000));
    pushInstr(bytecode, encodeRRI(Opcode::MUL64I, 5, 5, 2));
    pushInstr(bytecode, encodeRRR(Opcode::MODU64, 6, 5, 1));
    pushInstr(bytecode, encodeRRI(Opcode::MODU64I, 7, 5, 2));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 9, 0));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 9, 0));
    pushInstr(bytecode, encodeRRI(Opcode::SUB64I, 9, 9, 1));
    pushInstr(bytecode, encodeRRR(Opcode::MODU64, 10, 5, 9));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (3) == 10); // 10 % 15 = 10
    REQUIRE (vm.getRegister (4) == 1); // 10 % 3 = 1
    REQUIRE (vm.getRegister (6) == (0xf0000000ul * 2ul % 10ul));
    REQUIRE (vm.getRegister (7) == (0xf0000000ul * 2ul % 2ul));
    REQUIRE (vm.getRegister (10) == (0xf0000000ul * 2ul % -1ul));
}

TEST_CASE (test_arithmetic_sll) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 10));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 2));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::SLL32, 3, 1, 2));
    pushInstr(bytecode, encodeRRI(Opcode::SLL32I, 4, 1, 3));
    pushInstr(bytecode, encodeRRI(Opcode::SLL32I, 5, 1, 31));
    pushInstr(bytecode, encodeRRR(Opcode::SLL64, 6, 1, 1));
    pushInstr(bytecode, encodeRRI(Opcode::SLL64I, 7, 1, 31));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (3) == 40); // 10 << 2 = 40
    REQUIRE (vm.getRegister (4) == 80); // 10 << 3 = 80
    REQUIRE (vm.getRegister (5) == 0); // 10 << 31 = 0 // shifting past 32bit
    REQUIRE (vm.getRegister (6) == (10ul << 10ul)); // 10 << 10
    REQUIRE (vm.getRegister (7) == (10ul << 31ul)); // 10 << 31 = 0 // shifting past 32bit but with 64bit
}

TEST_CASE (test_arithmetic_srl) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 10));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 2));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::SRL32, 3, 1, 2));
    pushInstr(bytecode, encodeRRI(Opcode::SRL32I, 4, 1, 3));
    pushInstr(bytecode, encodeRRI(Opcode::SLL64I, 5, 1, 31));
    pushInstr(bytecode, encodeRRR(Opcode::SRL64, 6, 5, 2));
    pushInstr(bytecode, encodeRRI(Opcode::SRL64I, 7, 5, 3));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (3) == 2); // 10 >> 2 = 2
    REQUIRE (vm.getRegister (4) == 1); // 10 >> 3 = 1
    REQUIRE (vm.getRegister (5) == (10ul << 31ul));
    REQUIRE (vm.getRegister (6) == (10ul << 31ul >> 2ul));
    REQUIRE (vm.getRegister (7) == (10ul << 31ul >> 3ul));
}

TEST_CASE (test_arithmetic_sra) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 10));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 2));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::SRA32, 3, 1, 2));
    pushInstr(bytecode, encodeRRI(Opcode::SRA32I, 4, 1, 3));
    pushInstr(bytecode, encodeRRI(Opcode::SLL64I, 5, 1, 31));
    pushInstr(bytecode, encodeRRR(Opcode::SRA64, 6, 5, 2));
    pushInstr(bytecode, encodeRRI(Opcode::SRA64I, 7, 5, 3));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (3) == 2); // 10 >> 2 = 2
    REQUIRE (vm.getRegister (4) == 1); // 10 >> 3 = 1
    REQUIRE (vm.getRegister (5) == (10l << 31l));
    REQUIRE (vm.getRegister (6) == (10l << 31l >> 2l));
    REQUIRE (vm.getRegister (7) == (10l << 31l >> 3l));
}

TEST_CASE (test_arithmetic_or) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 16));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 2));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::OR64, 3, 1, 2));
    pushInstr(bytecode, encodeRRI(Opcode::OR64I, 4, 1, 7));
    pushInstr(bytecode, encodeRRR(Opcode::OR64, 5, 1, 2));
    pushInstr(bytecode, encodeRRI(Opcode::OR64I, 6, 1, 7));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (3) == 18); // 16 | 2 = 18
    REQUIRE (vm.getRegister (4) == 23); // 16 | 7 = 23
    REQUIRE (vm.getRegister (5) == 18); // 16 | 2 = 18
    REQUIRE (vm.getRegister (6) == 23); // 16 | 7 = 23
}

TEST_CASE (test_arithmetic_and) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 15));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 2));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::AND64, 3, 1, 2));
    pushInstr(bytecode, encodeRRI(Opcode::AND64I, 4, 1, 7));
    pushInstr(bytecode, encodeRRR(Opcode::AND64, 5, 1, 2));
    pushInstr(bytecode, encodeRRI(Opcode::AND64I, 6, 1, 7));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (3) == 2); // 15 & 2 = 2
    REQUIRE (vm.getRegister (4) == 7); // 15 & 7 = 7
    REQUIRE (vm.getRegister (5) == 2); // 15 & 2 = 2
    REQUIRE (vm.getRegister (6) == 7); // 15 & 7 = 7
}

TEST_CASE (test_arithmetic_xor) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 15));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 2));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::XOR64, 3, 1, 2));
    pushInstr(bytecode, encodeRRI(Opcode::XOR64I, 4, 1, 7));
    pushInstr(bytecode, encodeRRR(Opcode::XOR64, 5, 1, 2));
    pushInstr(bytecode, encodeRRI(Opcode::XOR64I, 6, 1, 7));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (3) == 13); // 15 ^ 2 = 13
    REQUIRE (vm.getRegister (4) == 8); // 15 ^ 7 = 8
    REQUIRE (vm.getRegister (5) == 13); // 15 ^ 2 = 13
    REQUIRE (vm.getRegister (6) == 8); // 15 ^ 7 = 8
}

TEST_CASE (test_r0_hardwired_zero) {
    std::vector<uint8_t> bytecode;
    // Attempt to store 42 in r0
    pushInstr(bytecode, encodeRI(Opcode::LLI, 0, 42));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 0, 100));
    // Read r0 into r1 -> r1 should be 0
    pushInstr(bytecode, encodeRRR(Opcode::ADD64, 1, 0, 0));
    // Add 10 to r0 and store in r2 -> r2 = 0 + 10 = 10
    pushInstr(bytecode, encodeRRI(Opcode::ADD64I, 2, 0, 10));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (0) == 0);
    REQUIRE (vm.getRegister (1) == 0);
    REQUIRE (vm.getRegister (2) == 10);
}
