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

TEST_CASE (test_control_flow_conditional) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 10));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 15));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0x20));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::BGE, 1, 5, 2)); // BGE r1, r5, r2(0x20)
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (5) == 10);
}

TEST_CASE (test_control_flow_loop) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0)); // i = 0
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 10)); // N = 10
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0x40)); // loop_end
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 3, 0x30)); // loop_cond
    pushInstr(bytecode, encodeRI(Opcode::LUI, 3, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 4, '*'));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 4, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 6, '\n'));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 6, 0));

    // [0x30] loop_cond: bge r5, r1, r2
    pushInstr(bytecode, encodeRRR(Opcode::BGE, 5, 1, 2));
    // [0x34] putchar(r4)
    pushInstr(bytecode, encodeR(Opcode::PUTCHAR, 4));
    // [0x38] addi r5, r5, 1
    pushInstr(bytecode, encodeRRI(Opcode::ADD32I, 5, 5, 1));
    // [0x3C] jmp r3
    pushInstr(bytecode, encodeR(Opcode::JMP, 3));
    // [0x40] loop_end: putchar(r6); halt
    pushInstr(bytecode, encodeR(Opcode::PUTCHAR, 6));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    std::ostringstream captured;
    TeeBuf tee(std::cout.rdbuf(), captured);
    std::ostream dualOut(&tee);
    auto* originalBuf = std::cout.rdbuf();
    std::cout.rdbuf(dualOut.rdbuf());

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    std::cout.rdbuf(originalBuf);

    REQUIRE(captured.str() == "**********\n");
    REQUIRE (vm.getRegister (5) == 10);
}

TEST_CASE (test_beq_taken) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 5));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 5));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0x20));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::BEQ, 5, 1, 2));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0xFF));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (5) == 5);
}

TEST_CASE (test_beq_not_taken) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 5));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 10));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0x20));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::BEQ, 5, 1, 2));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0xFF));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (5) == 0xFF);
}

TEST_CASE (test_bne_taken) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 5));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 10));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0x20));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::BNE, 5, 1, 2));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0xFF));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (5) == 5);
}

TEST_CASE (test_bne_not_taken) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 5));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 5));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0x20));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::BNE, 5, 1, 2));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0xFF));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (5) == 0xFF);
}

TEST_CASE (test_blt_signed_taken) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0xFFFF));
    pushInstr(bytecode, encodeRRI(Opcode::STORE32, 31, 2, -8));
    pushInstr(bytecode, encodeRRI(Opcode::LOAD32, 5, 31, -8));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 5));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 3, 0x2C));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 3, 0));
    pushInstr(bytecode, encodeRRR(Opcode::BLT, 5, 1, 3));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0xAA));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (5) == 0xFFFFFFFFFFFFFFFF);
}

TEST_CASE (test_blt_signed_not_taken) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 10));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 5));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0x20));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::BLT, 5, 1, 2));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0xAA));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (5) == 0xAA);
}

TEST_CASE (test_bge_signed_taken) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 5));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0xFFFF));
    pushInstr(bytecode, encodeRRI(Opcode::STORE32, 31, 2, -8));
    pushInstr(bytecode, encodeRRI(Opcode::LOAD32, 1, 31, -8));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 3, 0x30));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 3, 0));
    pushInstr(bytecode, encodeRRR(Opcode::BGE, 5, 1, 3));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0xAA));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (5) == 5);
}

TEST_CASE (test_bge_signed_not_taken) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0xFFFF));
    pushInstr(bytecode, encodeRRI(Opcode::STORE32, 31, 2, -8));
    pushInstr(bytecode, encodeRRI(Opcode::LOAD32, 5, 31, -8));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 5));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 3, 0x30));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 3, 0));
    pushInstr(bytecode, encodeRRR(Opcode::BGE, 5, 1, 3));
    pushInstr(bytecode, encodeRRR(Opcode::XOR64, 5, 5, 5));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0xAA));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (5) == 0xAA);
}

TEST_CASE (test_bltu_unsigned_taken) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 5));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0x20));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::BLTU, 5, 1, 2));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0xAA));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (5) == 5);
}

TEST_CASE (test_bltu_unsigned_not_taken) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 5));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0x28));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::BLTU, 5, 1, 2));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0xAA));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (5) == 0xAA);
}

TEST_CASE (test_bgeu_unsigned_taken) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 5));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0x28));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::BGEU, 5, 1, 2));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0xAA));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (5) == 0x00000000FFFFFFFF);
}

TEST_CASE (test_bgeu_unsigned_not_taken) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 5));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 2, 0x20));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 2, 0));
    pushInstr(bytecode, encodeRRR(Opcode::BGEU, 5, 1, 2));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0xAA));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (5) == 0xAA);
}

TEST_CASE (test_jmp) {
    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 5));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 5, 0));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0x18));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeR(Opcode::JMP, 1));
    pushInstr(bytecode, encodeRI(Opcode::LLI, 5, 0xFF));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();
    REQUIRE (vm.getRegister (5) == 5);
}
