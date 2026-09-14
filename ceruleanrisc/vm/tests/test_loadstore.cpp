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

TEST_CASE (test_loadstore_imm) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0x12));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0x1234));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 3, 0x5678));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 3, 0x1234));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 4, 0x5678));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 4, 0x1234));
    pushInstr(bytecode, encodeRRI(Opcode::SLL64I, 4, 4, 32));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 4, 0xCDEF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 4, 0x90AB));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (1) == 0x12ul);
    REQUIRE (vm.getRegister (2) == 0x1234ul);
    REQUIRE (vm.getRegister (3) == 0x12345678ul);
    REQUIRE (vm.getRegister (4) == 0x1234567890abcdeful);
}

TEST_CASE (test_load8_sign_extend) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0x7F));
    pushInstr(bytecode, encodeRRI(Opcode::STORE8, 31, 2, -8));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 3, 0xFF));
    pushInstr(bytecode, encodeRRI(Opcode::STORE8, 31, 3, -9));
    pushInstr(bytecode, encodeRRI(Opcode::LOAD8, 4, 31, -8));
    pushInstr(bytecode, encodeRRI(Opcode::LOAD8, 5, 31, -9));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (4) == 0x000000000000007Ful);
    REQUIRE (vm.getRegister (5) == 0xFFFFFFFFFFFFFFFFul);
}

TEST_CASE (test_loadu8_zero_extend) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0x7F));
    pushInstr(bytecode, encodeRRI(Opcode::STORE8, 31, 2, -8));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 3, 0xFF));
    pushInstr(bytecode, encodeRRI(Opcode::STORE8, 31, 3, -9));
    pushInstr(bytecode, encodeRRI(Opcode::LOADU8, 4, 31, -8));
    pushInstr(bytecode, encodeRRI(Opcode::LOADU8, 5, 31, -9));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (4) == 0x000000000000007Ful);
    REQUIRE (vm.getRegister (5) == 0x00000000000000FFul);
}

TEST_CASE (test_load16_sign_extend) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0x7FFF));
    pushInstr(bytecode, encodeRRI(Opcode::STORE16, 31, 2, -8));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 3, -1));
    pushInstr(bytecode, encodeRRI(Opcode::STORE16, 31, 3, -16));
    pushInstr(bytecode, encodeRRI(Opcode::LOAD16, 4, 31, -8));
    pushInstr(bytecode, encodeRRI(Opcode::LOAD16, 5, 31, -16));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (4) == 0x0000000000007FFFul);
    REQUIRE (vm.getRegister (5) == 0xFFFFFFFFFFFFFFFFul);
}

TEST_CASE (test_loadu16_zero_extend) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0x7FFF));
    pushInstr(bytecode, encodeRRI(Opcode::STORE16, 31, 2, -8));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 3, -1));
    pushInstr(bytecode, encodeRRI(Opcode::STORE16, 31, 3, -16));
    pushInstr(bytecode, encodeRRI(Opcode::LOADU16, 4, 31, -8));
    pushInstr(bytecode, encodeRRI(Opcode::LOADU16, 5, 31, -16));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (4) == 0x0000000000007FFFul);
    REQUIRE (vm.getRegister (5) == 0x000000000000FFFFul);
}

TEST_CASE (test_load32_sign_extend) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0x7FFF));
    pushInstr(bytecode, encodeRRI(Opcode::STORE32, 31, 2, -8));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 3, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 3, 0xFFFF));
    pushInstr(bytecode, encodeRRI(Opcode::STORE32, 31, 3, -16));
    pushInstr(bytecode, encodeRRI(Opcode::LOAD32, 4, 31, -8));
    pushInstr(bytecode, encodeRRI(Opcode::LOAD32, 5, 31, -16));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (4) == 0x000000007FFFFFFFul);
    REQUIRE (vm.getRegister (5) == 0xFFFFFFFFFFFFFFFFul);
}

TEST_CASE (test_loadu32_zero_extend) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0x7FFF));
    pushInstr(bytecode, encodeRRI(Opcode::STORE32, 31, 2, -8));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 3, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 3, 0xFFFF));
    pushInstr(bytecode, encodeRRI(Opcode::STORE32, 31, 3, -16));
    pushInstr(bytecode, encodeRRI(Opcode::LOADU32, 4, 31, -8));
    pushInstr(bytecode, encodeRRI(Opcode::LOADU32, 5, 31, -16));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (4) == 0x000000007FFFFFFFul);
    REQUIRE (vm.getRegister (5) == 0x00000000FFFFFFFFul);
}

TEST_CASE (test_load64) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0x5678));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0x1234));
    pushInstr(bytecode, encodeRRI(Opcode::SLL64I, 2, 2, 32));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0xDEF0));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0x9ABC));
    pushInstr(bytecode, encodeRRI(Opcode::STORE64, 31, 2, -8));
    pushInstr(bytecode, encodeRRI(Opcode::LOAD64, 3, 31, -8));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (3) == 0x123456789ABCDEF0ul);
}
