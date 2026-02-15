#include "test_framework.hpp"
#include "ceruleanvm.hpp"
#include "tee_buf.hpp"
#include <fstream>
#include <vector>
#include <cstdint>
#include <sstream>
#include <iostream>

extern bool g_debug;

TEST_CASE (test_arithmetic_add) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x0a, 0x00, // [0x] r0.0 <- 10
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LLI,     0x10, 0x0f, 0x00, // [0x] r1.0 <- 15
        Opcode::LUI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::ADD32,   0x20, 0x10, 0x00, // [0x] r2 <- r0 + r1
        Opcode::ADD32I,  0x30, 0x03, 0x00, // [0x] r3 <- r0 + 3
        Opcode::LLI,     0x50, 0x00, 0x00, // [0x] r5.0 <- 0
        Opcode::LUI,     0x50, 0x00, 0x00, // [0x] r5.1 <- 0
        Opcode::SUB64I,  0x55, 0x01, 0x00, // [0x] r5 <- r5 - 1
        Opcode::ADD64,   0x75, 0x50, 0x00, // [0x] r6 <- r5 + r5
        Opcode::ADD64I,  0x65, 0x01, 0x00, // [0x] r6 <- r5 + 1
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (2) == 25); // 10 + 15 = 25
    REQUIRE (vm.getRegister (3) == 13); // 10 + 3 = 13
    REQUIRE (vm.getRegister (7) == (-1ul + -1ul));
    REQUIRE (vm.getRegister (6) == 0ul); // -1 + 1 = 0
}

TEST_CASE (test_arithmetic_sub) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x0a, 0x00, // [0x] r0.0 <- 10
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LLI,     0x10, 0x0f, 0x00, // [0x] r1.0 <- 15
        Opcode::LUI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::SUB32,   0x20, 0x10, 0x00, // [0x] r2 <- r0 - r1
        Opcode::SUB32I,  0x30, 0x03, 0x00, // [0x] r3 <- r0 - 3
        Opcode::LLI,     0x50, 0x00, 0x00, // [0x] r5.0 <- 0
        Opcode::LUI,     0x50, 0x00, 0x00, // [0x] r5.1 <- 0
        Opcode::SUB64,   0x65, 0x50, 0x00, // [0x] r6 <- r5 - r5
        Opcode::SUB64I,  0x75, 0x01, 0x00, // [0x] r7 <- r5 - 1
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (static_cast<int32_t>(vm.getRegister (2)) == -5); // 10 - 15 = -5
    REQUIRE (static_cast<int32_t>(vm.getRegister (3)) == 7); // 10 - 3 = 7
    REQUIRE (static_cast<int32_t>(vm.getRegister (6)) == 0ul); // -1 - -1 = 0
    REQUIRE (static_cast<int32_t>(vm.getRegister (7)) == 0xfffffffffffffffful);
}

TEST_CASE (test_arithmetic_mul) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x0a, 0x00, // [0x] r0.0 <- 10
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LLI,     0x10, 0x0f, 0x00, // [0x] r1.0 <- 15
        Opcode::LUI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::MUL32,   0x20, 0x10, 0x00, // [0x] r2 <- r0 * r1
        Opcode::MUL32I,  0x30, 0x03, 0x00, // [0x] r3 <- r0 * 3
        Opcode::LLI,     0x50, 0xff, 0xff, // [0x] r5.0 <- 0xffff
        Opcode::LUI,     0x50, 0xff, 0xff, // [0x] r5.1 <- 0xffff
        Opcode::MUL64,   0x65, 0x50, 0x00, // [0x] r6 <- r5 * r5
        Opcode::MUL64I,  0x75, 0x02, 0x00, // [0x] r7 <- r5 * 2
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (2) == 150); // 10 * 15 = 150
    REQUIRE (vm.getRegister (3) == 30); // 10 * 3 = 30
    REQUIRE (vm.getRegister (6) == (0xfffffffful * 0xfffffffful));
    REQUIRE (vm.getRegister (7) == (0xfffffffful * 2ul));
}

TEST_CASE (test_arithmetic_divi) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x0a, 0x00, // [0x] r0.0 <- 10
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LLI,     0x10, 0x0f, 0x00, // [0x] r1.0 <- 15
        Opcode::LUI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::DIVI32,  0x20, 0x10, 0x00, // [0x] r2 <- r0 / r1
        Opcode::DIVI32I, 0x30, 0x03, 0x00, // [0x] r3 <- r0 / 3
        Opcode::LLI,     0x50, 0x00, 0x00, // [0x] r5.0 <-
        Opcode::LUI,     0x50, 0x00, 0xf0, // [0x] r5.1 <- 0xf0000000
        Opcode::MUL64I,  0x55, 0x02, 0x00, // [0x] r5 <- r5 * 2
        Opcode::DIVI64,  0x65, 0x00, 0x00, // [0x] r6 <- r5 / r0
        Opcode::DIVI64I, 0x75, 0x02, 0x00, // [0x] r7 <- r5 / 2
        Opcode::LLI,     0x90, 0x00, 0x00, // [0x] r9.0 <- 0
        Opcode::LUI,     0x90, 0x00, 0x00, // [0x] r9.1 <- 0
        Opcode::SUB64I,  0x99, 0x01, 0x00, // [0x] r9 <- r9 - 1
        Opcode::DIVI64,  0xa5, 0x90, 0x00, // [0x] r10 <- r5 / r9
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (2) == 0l); // 10 / 15 = 0
    REQUIRE (vm.getRegister (3) == 3l); // 10 / 3 = 3
    REQUIRE (vm.getRegister (6) == (0xf0000000l * 2l / 10l));
    REQUIRE (vm.getRegister (7) == (0xf0000000l * 2l / 2l));
    REQUIRE (vm.getRegister (10) == (0xf0000000l * 2l / -1l));
}

TEST_CASE (test_arithmetic_divu) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x0a, 0x00, // [0x] r0.0 <- 10
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LLI,     0x10, 0x0f, 0x00, // [0x] r1.0 <- 15
        Opcode::LUI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::DIVU32,  0x20, 0x10, 0x00, // [0x] r2 <- r0 / r1
        Opcode::DIVU32I, 0x30, 0x03, 0x00, // [0x] r3 <- r0 / 3
        Opcode::LLI,     0x50, 0x00, 0x00, // [0x] r5.0 <-
        Opcode::LUI,     0x50, 0x00, 0xf0, // [0x] r5.1 <- 0xf0000000
        Opcode::MUL64I,  0x55, 0x02, 0x00, // [0x] r5 <- r5 * 2
        Opcode::DIVU64,  0x65, 0x00, 0x00, // [0x] r6 <- r5 / r0
        Opcode::DIVU64I, 0x75, 0x02, 0x00, // [0x] r7 <- r5 / 2
        Opcode::LLI,     0x90, 0x00, 0x00, // [0x] r9.0 <- 0
        Opcode::LUI,     0x90, 0x00, 0x00, // [0x] r9.1 <- 0
        Opcode::SUB64I,  0x99, 0x01, 0x00, // [0x] r9 <- r9 - 1
        Opcode::DIVU64,  0xa5, 0x90, 0x00, // [0x] r10 <- r5 / r9
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (2) == 0l); // 10 / 15 = 0
    REQUIRE (vm.getRegister (3) == 3l); // 10 / 3 = 3
    REQUIRE (vm.getRegister (6) == (0xf0000000ul * 2ul / 10ul));
    REQUIRE (vm.getRegister (7) == (0xf0000000ul * 2ul / 2ul));
    REQUIRE (vm.getRegister (10) == (0xf0000000ul * 2ul / -1ul));
}

TEST_CASE (test_arithmetic_modi) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x0a, 0x00, // [0x] r0.0 <- 10
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LLI,     0x10, 0x0f, 0x00, // [0x] r1.0 <- 15
        Opcode::LUI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::MODI32,  0x20, 0x10, 0x00, // [0x] r2 <- r0 % r1
        Opcode::MODI32I, 0x30, 0x03, 0x00, // [0x] r3 <- r0 % 3
        Opcode::LLI,     0x50, 0x00, 0x00, // [0x] r5.0 <-
        Opcode::LUI,     0x50, 0x00, 0xf0, // [0x] r5.1 <- 0xf0000000
        Opcode::MUL64I,  0x55, 0x02, 0x00, // [0x] r5 <- r5 * 2
        Opcode::MODI64,  0x65, 0x00, 0x00, // [0x] r6 <- r5 % r0
        Opcode::MODI64I, 0x75, 0x02, 0x00, // [0x] r7 <- r5 % 2
        Opcode::LLI,     0x90, 0x00, 0x00, // [0x] r9.0 <- 0
        Opcode::LUI,     0x90, 0x00, 0x00, // [0x] r9.1 <- 0
        Opcode::SUB64I,  0x99, 0x01, 0x00, // [0x] r9 <- r9 - 1
        Opcode::MODI64,  0xa5, 0x90, 0x00, // [0x] r10 <- r5 % r9
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (2) == 10); // 10 % 15 = 10
    REQUIRE (vm.getRegister (3) == 1); // 10 % 3 = 1
    REQUIRE (vm.getRegister (6) == (0xf0000000l * 2l % 10l));
    REQUIRE (vm.getRegister (7) == (0xf0000000l * 2l % 2l));
    REQUIRE (vm.getRegister (10) == (0xf0000000l * 2l % -1l));
}

TEST_CASE (test_arithmetic_modu) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x0a, 0x00, // [0x] r0.0 <- 10
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LLI,     0x10, 0x0f, 0x00, // [0x] r1.0 <- 15
        Opcode::LUI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::MODU32,  0x20, 0x10, 0x00, // [0x] r2 <- r0 % r1
        Opcode::MODU32I, 0x30, 0x03, 0x00, // [0x] r3 <- r0 % 3
        Opcode::LLI,     0x50, 0x00, 0x00, // [0x] r5.0 <-
        Opcode::LUI,     0x50, 0x00, 0xf0, // [0x] r5.1 <- 0xf0000000
        Opcode::MUL64I,  0x55, 0x02, 0x00, // [0x] r5 <- r5 * 2
        Opcode::MODU64,  0x65, 0x00, 0x00, // [0x] r6 <- r5 % r0
        Opcode::MODU64I, 0x75, 0x02, 0x00, // [0x] r7 <- r5 % 2
        Opcode::LLI,     0x90, 0x00, 0x00, // [0x] r9.0 <- 0
        Opcode::LUI,     0x90, 0x00, 0x00, // [0x] r9.1 <- 0
        Opcode::SUB64I,  0x99, 0x01, 0x00, // [0x] r9 <- r9 - 1
        Opcode::MODU64,  0xa5, 0x90, 0x00, // [0x] r10 <- r5 % r9
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (2) == 10); // 10 % 15 = 10
    REQUIRE (vm.getRegister (3) == 1); // 10 % 3 = 1
    REQUIRE (vm.getRegister (6) == (0xf0000000ul * 2ul % 10ul));
    REQUIRE (vm.getRegister (7) == (0xf0000000ul * 2ul % 2ul));
    REQUIRE (vm.getRegister (10) == (0xf0000000ul * 2ul % -1ul));
}

TEST_CASE (test_arithmetic_sll) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x0a, 0x00, // [0x] r0.0 <- 10
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LLI,     0x10, 0x02, 0x00, // [0x] r1.0 <- 2
        Opcode::LUI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::SLL32,   0x20, 0x10, 0x00, // [0x] r2 <- r0 << r1
        Opcode::SLL32I,  0x30, 0x03, 0x00, // [0x] r3 <- r0 << 3
        Opcode::SLL32I,  0x40, 0x1f, 0x00, // [0x] r4 <- r0 << 31
        Opcode::SLL64,   0x50, 0x00, 0x00, // [0x] r5 <- r0 << r0
        Opcode::SLL64I,  0x60, 0x1f, 0x00, // [0x] r6 <- r0 << 31
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (2) == 40); // 10 << 2 = 40
    REQUIRE (vm.getRegister (3) == 80); // 10 << 3 = 80
    REQUIRE (vm.getRegister (4) == 0); // 10 << 31 = 0 // shifting past 32bit
    REQUIRE (vm.getRegister (5) == (10ul << 10ul)); // 10 << 10
    REQUIRE (vm.getRegister (6) == (10ul << 31ul)); // 10 << 31 = 0 // shifting past 32bit but with 64bit
}

TEST_CASE (test_arithmetic_srl) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x0a, 0x00, // [0x] r0.0 <- 10
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LLI,     0x10, 0x02, 0x00, // [0x] r1.0 <- 2
        Opcode::LUI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::SRL32,   0x20, 0x10, 0x00, // [0x] r2 <- r0 >> r1
        Opcode::SRL32I,  0x30, 0x03, 0x00, // [0x] r3 <- r0 >> 3

        Opcode::SLL64I,  0x40, 0x1f, 0x00, // [0x] r4 <- r0 << 31
        Opcode::SRL64,   0x54, 0x10, 0x00, // [0x] r5 <- r4 >> r1
        Opcode::SRL64I,  0x64, 0x03, 0x00, // [0x] r6 <- r4 >> 3
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (2) == 2); // 10 >> 2 = 2
    REQUIRE (vm.getRegister (3) == 1); // 10 >> 3 = 1
    REQUIRE (vm.getRegister (4) == (10ul << 31ul));
    REQUIRE (vm.getRegister (5) == (10ul << 31ul >> 2ul));
    REQUIRE (vm.getRegister (6) == (10ul << 31ul >> 3ul));
}

TEST_CASE (test_arithmetic_sra) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x0a, 0x00, // [0x] r0.0 <- 10
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LLI,     0x10, 0x02, 0x00, // [0x] r1.0 <- 2
        Opcode::LUI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::SRA32,   0x20, 0x10, 0x00, // [0x] r2 <- r0 >> r1
        Opcode::SRA32I,  0x30, 0x03, 0x00, // [0x] r3 <- r0 >> 3

        Opcode::SLL64I,  0x40, 0x1f, 0x00, // [0x] r4 <- r0 << 31
        Opcode::SRA64,   0x54, 0x10, 0x00, // [0x] r5 <- r4 >> r1
        Opcode::SRA64I,  0x64, 0x03, 0x00, // [0x] r6 <- r4 >> 3
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (2) == 2); // 10 >> 2 = 2
    REQUIRE (vm.getRegister (3) == 1); // 10 >> 3 = 1
    REQUIRE (vm.getRegister (4) == (10l << 31l));
    REQUIRE (vm.getRegister (5) == (10l << 31l >> 2l));
    REQUIRE (vm.getRegister (6) == (10l << 31l >> 3l));
}

TEST_CASE (test_arithmetic_or) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x10, 0x00, // [0x] r0.0 <- 16
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LLI,     0x10, 0x02, 0x00, // [0x] r1.0 <- 2
        Opcode::LUI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::OR64,    0x20, 0x10, 0x00, // [0x] r2 <- r0 | r1
        Opcode::OR64I,   0x30, 0x07, 0x00, // [0x] r3 <- r0 | 7
        Opcode::OR64,    0x40, 0x10, 0x00, // [0x] r4 <- r0 | r1
        Opcode::OR64I,   0x50, 0x07, 0x00, // [0x] r5 <- r0 | 7
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (2) == 18); // 16 | 2 = 18
    REQUIRE (vm.getRegister (3) == 23); // 16 | 7 = 23
    REQUIRE (vm.getRegister (4) == 18); // 16 | 2 = 18
    REQUIRE (vm.getRegister (5) == 23); // 16 | 7 = 23
}

TEST_CASE (test_arithmetic_and) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x0f, 0x00, // [0x] r0.0 <- 15
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LLI,     0x10, 0x02, 0x00, // [0x] r1.0 <- 2
        Opcode::LUI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::AND64,   0x20, 0x10, 0x00, // [0x] r2 <- r0 & r1
        Opcode::AND64I,  0x30, 0x07, 0x00, // [0x] r3 <- r0 & 7
        Opcode::AND64,   0x40, 0x10, 0x00, // [0x] r4 <- r0 & r1
        Opcode::AND64I,  0x50, 0x07, 0x00, // [0x] r5 <- r0 & 7
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (2) == 2); // 15 & 2 = 2
    REQUIRE (vm.getRegister (3) == 7); // 15 & 7 = 7
    REQUIRE (vm.getRegister (4) == 2); // 15 & 2 = 2
    REQUIRE (vm.getRegister (5) == 7); // 15 & 7 = 7
}

TEST_CASE (test_arithmetic_xor) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x0f, 0x00, // [0x] r0.0 <- 15
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LLI,     0x10, 0x02, 0x00, // [0x] r1.0 <- 2
        Opcode::LUI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::XOR64,   0x20, 0x10, 0x00, // [0x] r2 <- r0 ^ r1
        Opcode::XOR64I,  0x30, 0x07, 0x00, // [0x] r3 <- r0 ^ 7
        Opcode::XOR64,   0x40, 0x10, 0x00, // [0x] r4 <- r0 ^ r1
        Opcode::XOR64I,  0x50, 0x07, 0x00, // [0x] r5 <- r0 ^ 7
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (2) == 13); // 15 ^ 2 = 13
    REQUIRE (vm.getRegister (3) == 8); // 15 ^ 7 = 8
    REQUIRE (vm.getRegister (4) == 13); // 15 ^ 2 = 13
    REQUIRE (vm.getRegister (5) == 8); // 15 ^ 7 = 8
}

TEST_CASE (test_arithmetic_not) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x0f, 0x00, // [0x] r0.0 <- 15
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::NOT32,   0x20, 0x00, 0x00, // [0x] r2 <- ~r0
        Opcode::LLI,     0x10, 0x00, 0x00, // [0x] r1.0 <- 0
        Opcode::LUI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::SUB64I,  0x11, 0x01, 0x00, // [0x] r1 <- r1 - 1
        Opcode::NOT64,   0x31, 0x00, 0x00, // [0x] r3 <- ~r1
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (2) == (~15u));
    REQUIRE (vm.getRegister (3) == (~(-1ul))); 
}
