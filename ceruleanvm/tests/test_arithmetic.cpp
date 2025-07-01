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
        Opcode::LUI,     0x00, 0x0a, 0x00, // [0x] r0.0 <- 10
        Opcode::LLI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LUI,     0x10, 0x0f, 0x00, // [0x] r1.0 <- 15
        Opcode::LLI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::ADD,     0x20, 0x10, 0x00, // [0x] r2 <- r0 + r1
        Opcode::ADDI,    0x30, 0x03, 0x00, // [0x] r3 <- r0 + 3
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.get_register (2) == 25); // 10 + 15 = 25
    REQUIRE (vm.get_register (3) == 13); // 10 + 3 = 13
}

TEST_CASE (test_arithmetic_sub) {
    std::vector<uint8_t> bytecode = {
        Opcode::LUI,     0x00, 0x0a, 0x00, // [0x] r0.0 <- 10
        Opcode::LLI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LUI,     0x10, 0x0f, 0x00, // [0x] r1.0 <- 15
        Opcode::LLI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::SUB,     0x20, 0x10, 0x00, // [0x] r2 <- r0 - r1
        Opcode::SUBI,    0x30, 0x03, 0x00, // [0x] r3 <- r0 - 3
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (static_cast<int32_t>(vm.get_register (2)) == -5); // 10 - 15 = -5
    REQUIRE (static_cast<int32_t>(vm.get_register (3)) == 7); // 10 - 3 = 7
}

TEST_CASE (test_arithmetic_mul) {
    std::vector<uint8_t> bytecode = {
        Opcode::LUI,     0x00, 0x0a, 0x00, // [0x] r0.0 <- 10
        Opcode::LLI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LUI,     0x10, 0x0f, 0x00, // [0x] r1.0 <- 15
        Opcode::LLI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::MUL,     0x20, 0x10, 0x00, // [0x] r2 <- r0 * r1
        Opcode::MULI,    0x30, 0x03, 0x00, // [0x] r3 <- r0 * 3
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.get_register (2) == 150); // 10 * 15 = 150
    REQUIRE (vm.get_register (3) == 30); // 10 * 3 = 30
}

TEST_CASE (test_arithmetic_div) {
    std::vector<uint8_t> bytecode = {
        Opcode::LUI,     0x00, 0x0a, 0x00, // [0x] r0.0 <- 10
        Opcode::LLI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LUI,     0x10, 0x0f, 0x00, // [0x] r1.0 <- 15
        Opcode::LLI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::DIV,     0x20, 0x10, 0x00, // [0x] r2 <- r0 / r1
        Opcode::DIVI,    0x30, 0x03, 0x00, // [0x] r3 <- r0 / 3
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.get_register (2) == 0); // 10 / 15 = 0
    REQUIRE (vm.get_register (3) == 3); // 10 / 3 = 3
}

TEST_CASE (test_arithmetic_mod) {
    std::vector<uint8_t> bytecode = {
        Opcode::LUI,     0x00, 0x0a, 0x00, // [0x] r0.0 <- 10
        Opcode::LLI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LUI,     0x10, 0x0f, 0x00, // [0x] r1.0 <- 15
        Opcode::LLI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::MOD,     0x20, 0x10, 0x00, // [0x] r2 <- r0 % r1
        Opcode::MODI,    0x30, 0x03, 0x00, // [0x] r3 <- r0 % 3
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.get_register (2) == 10); // 10 % 15 = 10
    REQUIRE (vm.get_register (3) == 1); // 10 % 3 = 1
}

TEST_CASE (test_arithmetic_sll) {
    std::vector<uint8_t> bytecode = {
        Opcode::LUI,     0x00, 0x0a, 0x00, // [0x] r0.0 <- 10
        Opcode::LLI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LUI,     0x10, 0x02, 0x00, // [0x] r1.0 <- 2
        Opcode::LLI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::SLL,     0x20, 0x10, 0x00, // [0x] r2 <- r0 << r1
        Opcode::SLLI,    0x30, 0x03, 0x00, // [0x] r3 <- r0 << 3
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.get_register (2) == 40); // 10 << 2 = 40
    REQUIRE (vm.get_register (3) == 80); // 10 << 3 = 80
}

TEST_CASE (test_arithmetic_srl) {
    std::vector<uint8_t> bytecode = {
        Opcode::LUI,     0x00, 0x0a, 0x00, // [0x] r0.0 <- 10
        Opcode::LLI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LUI,     0x10, 0x02, 0x00, // [0x] r1.0 <- 2
        Opcode::LLI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::SRL,     0x20, 0x10, 0x00, // [0x] r2 <- r0 >> r1
        Opcode::SRAI,    0x30, 0x03, 0x00, // [0x] r3 <- r0 >> 3
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.get_register (2) == 2); // 10 >> 2 = 2
    REQUIRE (vm.get_register (3) == 1); // 10 >> 3 = 1
}

TEST_CASE (test_arithmetic_sra) {
    std::vector<uint8_t> bytecode = {
        Opcode::LUI,     0x00, 0x0a, 0x00, // [0x] r0.0 <- 10
        Opcode::LLI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LUI,     0x10, 0x02, 0x00, // [0x] r1.0 <- 2
        Opcode::LLI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::SRA,     0x20, 0x10, 0x00, // [0x] r2 <- r0 >> r1
        Opcode::SRAI,    0x30, 0x03, 0x00, // [0x] r3 <- r0 >> 3
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.get_register (2) == 2); // 10 >> 2 = 2
    REQUIRE (vm.get_register (3) == 1); // 10 >> 3 = 1
}

TEST_CASE (test_arithmetic_or) {
    std::vector<uint8_t> bytecode = {
        Opcode::LUI,     0x00, 0x10, 0x00, // [0x] r0.0 <- 16
        Opcode::LLI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LUI,     0x10, 0x02, 0x00, // [0x] r1.0 <- 2
        Opcode::LLI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::OR,      0x20, 0x10, 0x00, // [0x] r2 <- r0 | r1
        Opcode::ORI,     0x30, 0x07, 0x00, // [0x] r3 <- r0 | 7
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.get_register (2) == 18); // 16 | 2 = 18
    REQUIRE (vm.get_register (3) == 23); // 16 | 7 = 23
}

TEST_CASE (test_arithmetic_and) {
    std::vector<uint8_t> bytecode = {
        Opcode::LUI,     0x00, 0x0f, 0x00, // [0x] r0.0 <- 15
        Opcode::LLI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LUI,     0x10, 0x02, 0x00, // [0x] r1.0 <- 2
        Opcode::LLI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::AND,     0x20, 0x10, 0x00, // [0x] r2 <- r0 & r1
        Opcode::ANDI,    0x30, 0x07, 0x00, // [0x] r3 <- r0 & 7
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.get_register (2) == 2); // 15 & 2 = 2
    REQUIRE (vm.get_register (3) == 7); // 15 & 7 = 7
}

TEST_CASE (test_arithmetic_xor) {
    std::vector<uint8_t> bytecode = {
        Opcode::LUI,     0x00, 0x0f, 0x00, // [0x] r0.0 <- 15
        Opcode::LLI,     0x00, 0x00, 0x00, // [0x] r0.1 <- 0
        Opcode::LUI,     0x10, 0x02, 0x00, // [0x] r1.0 <- 2
        Opcode::LLI,     0x10, 0x00, 0x00, // [0x] r1.1 <- 0
        Opcode::XOR,     0x20, 0x10, 0x00, // [0x] r2 <- r0 ^ r1
        Opcode::XORI,    0x30, 0x07, 0x00, // [0x] r3 <- r0 ^ 7
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.get_register (2) == 13); // 15 ^ 2 = 13
    REQUIRE (vm.get_register (3) == 8); // 15 ^ 7 = 8
}
