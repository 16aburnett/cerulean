#include "test_framework.hpp"
#include "ceruleanvm.hpp"
#include "tee_buf.hpp"
#include <fstream>
#include <vector>
#include <cstdint>
#include <sstream>
#include <iostream>
#include <cmath>

extern bool g_debug;

TEST_CASE (test_arithmetic_float_add32) {
    float f0 = 3.1415927f;
    uint32_t f0bits = std::bit_cast<uint32_t>(f0);

    // Write bytes in little-endian order
    uint8_t f0b0 = f0bits & 0xFF;
    uint8_t f0b1 = (f0bits >> 8) & 0xFF;
    uint8_t f0b2 = (f0bits >> 16) & 0xFF;
    uint8_t f0b3 = (f0bits >> 24) & 0xFF;

    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, f0b0, f0b1, // [0x] r0.01 <- 3.14
        Opcode::LUI,     0x00, f0b2, f0b3, // [0x] r0.23 <- 3.14
        Opcode::ADDF32,  0x20, 0x00, 0x00, // [0x] r2 <- r0 + r0
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<float>(static_cast<uint32_t>(vm.getRegister (2))) == (f0 + f0)); // 3.1415927f + 3.1415927f
}

TEST_CASE (test_arithmetic_float_add64) {
    double f0 = 3.1415927f;
    uint64_t f0bits = std::bit_cast<uint64_t>(f0);

    // Write bytes in little-endian order
    uint8_t f0b0 = f0bits & 0xFF;
    uint8_t f0b1 = (f0bits >> 8) & 0xFF;
    uint8_t f0b2 = (f0bits >> 16) & 0xFF;
    uint8_t f0b3 = (f0bits >> 24) & 0xFF;
    uint8_t f0b4 = (f0bits >> 32) & 0xFF;
    uint8_t f0b5 = (f0bits >> 40) & 0xFF;
    uint8_t f0b6 = (f0bits >> 48) & 0xFF;
    uint8_t f0b7 = (f0bits >> 56) & 0xFF;

    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x10, 0x00, // [0x00] r0 <- float_const
        Opcode::LD,      0x10, 0x00, 0x00, // [0x04] r1 <- r0[0]
        Opcode::ADDF64,  0x21, 0x10, 0x00, // [0x08] r2 <- r1 + r1
        Opcode::HALT,    0x00, 0x00, 0x00, // [0x0c] halt
        f0b0,            f0b1, f0b2, f0b3, // [0x10] float_const
        f0b4,            f0b5, f0b6, f0b7, // [0x14]
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<double>(vm.getRegister (2)) == (f0 + f0)); // 3.1415927f + 3.1415927f
}

TEST_CASE (test_arithmetic_float_sub32) {
    float f0 = 3.1415927f;
    uint32_t f0bits = std::bit_cast<uint32_t>(f0);

    // Write bytes in little-endian order
    uint8_t f0b0 = f0bits & 0xFF;
    uint8_t f0b1 = (f0bits >> 8) & 0xFF;
    uint8_t f0b2 = (f0bits >> 16) & 0xFF;
    uint8_t f0b3 = (f0bits >> 24) & 0xFF;

    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, f0b0, f0b1, // [0x] r0.01 <- 3.14
        Opcode::LUI,     0x00, f0b2, f0b3, // [0x] r0.23 <- 3.14
        Opcode::SUBF32,  0x20, 0x00, 0x00, // [0x] r2 <- r0 - r0
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<float>(static_cast<uint32_t>(vm.getRegister (2))) == (f0 - f0)); // 3.1415927f - 3.1415927f
}

TEST_CASE (test_arithmetic_float_sub64) {
    double f0 = 3.1415927f;
    uint64_t f0bits = std::bit_cast<uint64_t>(f0);

    // Write bytes in little-endian order
    uint8_t f0b0 = f0bits & 0xFF;
    uint8_t f0b1 = (f0bits >> 8) & 0xFF;
    uint8_t f0b2 = (f0bits >> 16) & 0xFF;
    uint8_t f0b3 = (f0bits >> 24) & 0xFF;
    uint8_t f0b4 = (f0bits >> 32) & 0xFF;
    uint8_t f0b5 = (f0bits >> 40) & 0xFF;
    uint8_t f0b6 = (f0bits >> 48) & 0xFF;
    uint8_t f0b7 = (f0bits >> 56) & 0xFF;

    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x10, 0x00, // [0x00] r0 <- float_const
        Opcode::LD,      0x10, 0x00, 0x00, // [0x04] r1 <- r0[0]
        Opcode::SUBF64,  0x21, 0x10, 0x00, // [0x08] r2 <- r1 - r1
        Opcode::HALT,    0x00, 0x00, 0x00, // [0x0c] halt
        f0b0,            f0b1, f0b2, f0b3, // [0x10] float_const
        f0b4,            f0b5, f0b6, f0b7, // [0x14]
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<double>(vm.getRegister (2)) == (f0 - f0)); // 3.1415927f - 3.1415927f
}

TEST_CASE (test_arithmetic_float_mul32) {
    float f0 = 3.1415927f;
    uint32_t f0bits = std::bit_cast<uint32_t>(f0);

    // Write bytes in little-endian order
    uint8_t f0b0 = f0bits & 0xFF;
    uint8_t f0b1 = (f0bits >> 8) & 0xFF;
    uint8_t f0b2 = (f0bits >> 16) & 0xFF;
    uint8_t f0b3 = (f0bits >> 24) & 0xFF;

    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, f0b0, f0b1, // [0x] r0.01 <- 3.14
        Opcode::LUI,     0x00, f0b2, f0b3, // [0x] r0.23 <- 3.14
        Opcode::MULF32,  0x20, 0x00, 0x00, // [0x] r2 <- r0 * r0
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<float>(static_cast<uint32_t>(vm.getRegister (2))) == (f0 * f0)); // 3.1415927f * 3.1415927f
}

TEST_CASE (test_arithmetic_float_mul64) {
    double f0 = 3.1415927f;
    uint64_t f0bits = std::bit_cast<uint64_t>(f0);

    // Write bytes in little-endian order
    uint8_t f0b0 = f0bits & 0xFF;
    uint8_t f0b1 = (f0bits >> 8) & 0xFF;
    uint8_t f0b2 = (f0bits >> 16) & 0xFF;
    uint8_t f0b3 = (f0bits >> 24) & 0xFF;
    uint8_t f0b4 = (f0bits >> 32) & 0xFF;
    uint8_t f0b5 = (f0bits >> 40) & 0xFF;
    uint8_t f0b6 = (f0bits >> 48) & 0xFF;
    uint8_t f0b7 = (f0bits >> 56) & 0xFF;

    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x10, 0x00, // [0x00] r0 <- float_const
        Opcode::LD,      0x10, 0x00, 0x00, // [0x04] r1 <- r0[0]
        Opcode::MULF64,  0x21, 0x10, 0x00, // [0x08] r2 <- r1 * r1
        Opcode::HALT,    0x00, 0x00, 0x00, // [0x0c] halt
        f0b0,            f0b1, f0b2, f0b3, // [0x10] float_const
        f0b4,            f0b5, f0b6, f0b7, // [0x14]
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<double>(vm.getRegister (2)) == (f0 * f0)); // 3.1415927f * 3.1415927f
}

TEST_CASE (test_arithmetic_float_div32) {
    float f0 = 3.1415927f;
    uint32_t f0bits = std::bit_cast<uint32_t>(f0);

    // Write bytes in little-endian order
    uint8_t f0b0 = f0bits & 0xFF;
    uint8_t f0b1 = (f0bits >> 8) & 0xFF;
    uint8_t f0b2 = (f0bits >> 16) & 0xFF;
    uint8_t f0b3 = (f0bits >> 24) & 0xFF;

    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, f0b0, f0b1, // [0x] r0.01 <- 3.14
        Opcode::LUI,     0x00, f0b2, f0b3, // [0x] r0.23 <- 3.14
        Opcode::DIVF32,  0x20, 0x00, 0x00, // [0x] r2 <- r0 / r0
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<float>(static_cast<uint32_t>(vm.getRegister (2))) == (f0 / f0)); // 3.1415927f / 3.1415927f
}

TEST_CASE (test_arithmetic_float_div64) {
    double f0 = 3.1415927f;
    uint64_t f0bits = std::bit_cast<uint64_t>(f0);

    // Write bytes in little-endian order
    uint8_t f0b0 = f0bits & 0xFF;
    uint8_t f0b1 = (f0bits >> 8) & 0xFF;
    uint8_t f0b2 = (f0bits >> 16) & 0xFF;
    uint8_t f0b3 = (f0bits >> 24) & 0xFF;
    uint8_t f0b4 = (f0bits >> 32) & 0xFF;
    uint8_t f0b5 = (f0bits >> 40) & 0xFF;
    uint8_t f0b6 = (f0bits >> 48) & 0xFF;
    uint8_t f0b7 = (f0bits >> 56) & 0xFF;

    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x10, 0x00, // [0x00] r0 <- float_const
        Opcode::LD,      0x10, 0x00, 0x00, // [0x04] r1 <- r0[0]
        Opcode::DIVF64,  0x21, 0x10, 0x00, // [0x08] r2 <- r1 / r1
        Opcode::HALT,    0x00, 0x00, 0x00, // [0x0c] halt
        f0b0,            f0b1, f0b2, f0b3, // [0x10] float_const
        f0b4,            f0b5, f0b6, f0b7, // [0x14]
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<double>(vm.getRegister (2)) == (f0 / f0)); // 3.1415927f / 3.1415927f
}

TEST_CASE (test_arithmetic_float_sqrt32) {
    float f0 = 3.1415927f;
    uint32_t f0bits = std::bit_cast<uint32_t>(f0);

    // Write bytes in little-endian order
    uint8_t f0b0 = f0bits & 0xFF;
    uint8_t f0b1 = (f0bits >> 8) & 0xFF;
    uint8_t f0b2 = (f0bits >> 16) & 0xFF;
    uint8_t f0b3 = (f0bits >> 24) & 0xFF;

    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, f0b0, f0b1, // [0x] r0.01 <- 3.14
        Opcode::LUI,     0x00, f0b2, f0b3, // [0x] r0.23 <- 3.14
        Opcode::SQRTF32, 0x20, 0x00, 0x00, // [0x] r2 <- sqrt(r0)
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<float>(static_cast<uint32_t>(vm.getRegister (2))) == std::sqrt(f0));
}

TEST_CASE (test_arithmetic_float_sqrt64) {
    double f0 = 3.1415927f;
    uint64_t f0bits = std::bit_cast<uint64_t>(f0);

    // Write bytes in little-endian order
    uint8_t f0b0 = f0bits & 0xFF;
    uint8_t f0b1 = (f0bits >> 8) & 0xFF;
    uint8_t f0b2 = (f0bits >> 16) & 0xFF;
    uint8_t f0b3 = (f0bits >> 24) & 0xFF;
    uint8_t f0b4 = (f0bits >> 32) & 0xFF;
    uint8_t f0b5 = (f0bits >> 40) & 0xFF;
    uint8_t f0b6 = (f0bits >> 48) & 0xFF;
    uint8_t f0b7 = (f0bits >> 56) & 0xFF;

    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x10, 0x00, // [0x00] r0 <- float_const
        Opcode::LD,      0x10, 0x00, 0x00, // [0x04] r1 <- r0[0]
        Opcode::SQRTF64, 0x21, 0x10, 0x00, // [0x08] r2 <- sqrt(r1)
        Opcode::HALT,    0x00, 0x00, 0x00, // [0x0c] halt
        f0b0,            f0b1, f0b2, f0b3, // [0x10] float_const
        f0b4,            f0b5, f0b6, f0b7, // [0x14]
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<double>(vm.getRegister (2)) == std::sqrt(f0));
}

TEST_CASE (test_arithmetic_float_abs32) {
    float f0 = -3.1415927f;
    uint32_t f0bits = std::bit_cast<uint32_t>(f0);

    // Write bytes in little-endian order
    uint8_t f0b0 = f0bits & 0xFF;
    uint8_t f0b1 = (f0bits >> 8) & 0xFF;
    uint8_t f0b2 = (f0bits >> 16) & 0xFF;
    uint8_t f0b3 = (f0bits >> 24) & 0xFF;

    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, f0b0, f0b1, // [0x] r0.01 <- -3.14
        Opcode::LUI,     0x00, f0b2, f0b3, // [0x] r0.23 <- -3.14
        Opcode::ABSF32,  0x20, 0x00, 0x00, // [0x] r2 <- abs(r0)
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<float>(static_cast<uint32_t>(vm.getRegister (2))) == std::fabs(f0));
}

TEST_CASE (test_arithmetic_float_abs64) {
    double f0 = -3.1415927f;
    uint64_t f0bits = std::bit_cast<uint64_t>(f0);

    // Write bytes in little-endian order
    uint8_t f0b0 = f0bits & 0xFF;
    uint8_t f0b1 = (f0bits >> 8) & 0xFF;
    uint8_t f0b2 = (f0bits >> 16) & 0xFF;
    uint8_t f0b3 = (f0bits >> 24) & 0xFF;
    uint8_t f0b4 = (f0bits >> 32) & 0xFF;
    uint8_t f0b5 = (f0bits >> 40) & 0xFF;
    uint8_t f0b6 = (f0bits >> 48) & 0xFF;
    uint8_t f0b7 = (f0bits >> 56) & 0xFF;

    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x10, 0x00, // [0x00] r0 <- float_const
        Opcode::LD,      0x10, 0x00, 0x00, // [0x04] r1 <- r0[0]
        Opcode::ABSF64,  0x21, 0x10, 0x00, // [0x08] r2 <- abs(r1)
        Opcode::HALT,    0x00, 0x00, 0x00, // [0x0c] halt
        f0b0,            f0b1, f0b2, f0b3, // [0x10] float_const
        f0b4,            f0b5, f0b6, f0b7, // [0x14]
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<double>(vm.getRegister (2)) == std::fabs(f0));
}

TEST_CASE (test_arithmetic_float_neg32) {
    float f0 = 3.1415927f;
    uint32_t f0bits = std::bit_cast<uint32_t>(f0);

    // Write bytes in little-endian order
    uint8_t f0b0 = f0bits & 0xFF;
    uint8_t f0b1 = (f0bits >> 8) & 0xFF;
    uint8_t f0b2 = (f0bits >> 16) & 0xFF;
    uint8_t f0b3 = (f0bits >> 24) & 0xFF;

    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, f0b0, f0b1, // [0x] r0.01 <- 3.14
        Opcode::LUI,     0x00, f0b2, f0b3, // [0x] r0.23 <- 3.14
        Opcode::NEGF32,  0x20, 0x00, 0x00, // [0x] r2 <- -r0
        Opcode::HALT
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<float>(static_cast<uint32_t>(vm.getRegister (2))) == -f0);
}

TEST_CASE (test_arithmetic_float_neg64) {
    double f0 = 3.1415927f;
    uint64_t f0bits = std::bit_cast<uint64_t>(f0);

    // Write bytes in little-endian order
    uint8_t f0b0 = f0bits & 0xFF;
    uint8_t f0b1 = (f0bits >> 8) & 0xFF;
    uint8_t f0b2 = (f0bits >> 16) & 0xFF;
    uint8_t f0b3 = (f0bits >> 24) & 0xFF;
    uint8_t f0b4 = (f0bits >> 32) & 0xFF;
    uint8_t f0b5 = (f0bits >> 40) & 0xFF;
    uint8_t f0b6 = (f0bits >> 48) & 0xFF;
    uint8_t f0b7 = (f0bits >> 56) & 0xFF;

    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x10, 0x00, // [0x00] r0 <- float_const
        Opcode::LD,      0x10, 0x00, 0x00, // [0x04] r1 <- r0[0]
        Opcode::NEGF64,  0x21, 0x10, 0x00, // [0x08] r2 <- -r1
        Opcode::HALT,    0x00, 0x00, 0x00, // [0x0c] halt
        f0b0,            f0b1, f0b2, f0b3, // [0x10] float_const
        f0b4,            f0b5, f0b6, f0b7, // [0x14]
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<double>(vm.getRegister (2)) == -f0);
}
