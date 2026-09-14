#include "test_framework.hpp"
#include "criscvm.hpp"
#include "encoders.hpp"
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

    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, f0bits & 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, (f0bits >> 16) & 0xFFFF));
    pushInstr(bytecode, encodeRRR(Opcode::ADDF32, 2, 1, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<float>(static_cast<uint32_t>(vm.getRegister (2))) == (f0 + f0));
}

TEST_CASE (test_arithmetic_float_add64) {
    double f0 = 3.1415927f;
    uint64_t f0bits = std::bit_cast<uint64_t>(f0);

    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0x14));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRRI(Opcode::LOAD64, 2, 1, 0));
    pushInstr(bytecode, encodeRRR(Opcode::ADDF64, 3, 2, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    pushInstr(bytecode, {
        static_cast<uint8_t>(f0bits & 0xFF),
        static_cast<uint8_t>((f0bits >> 8) & 0xFF),
        static_cast<uint8_t>((f0bits >> 16) & 0xFF),
        static_cast<uint8_t>((f0bits >> 24) & 0xFF)
    });
    pushInstr(bytecode, {
        static_cast<uint8_t>((f0bits >> 32) & 0xFF),
        static_cast<uint8_t>((f0bits >> 40) & 0xFF),
        static_cast<uint8_t>((f0bits >> 48) & 0xFF),
        static_cast<uint8_t>((f0bits >> 56) & 0xFF)
    });

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<double>(vm.getRegister (3)) == (f0 + f0));
}

TEST_CASE (test_arithmetic_float_sub32) {
    float f0 = 3.1415927f;
    uint32_t f0bits = std::bit_cast<uint32_t>(f0);

    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, f0bits & 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, (f0bits >> 16) & 0xFFFF));
    pushInstr(bytecode, encodeRRR(Opcode::SUBF32, 2, 1, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<float>(static_cast<uint32_t>(vm.getRegister (2))) == (f0 - f0));
}

TEST_CASE (test_arithmetic_float_sub64) {
    double f0 = 3.1415927f;
    uint64_t f0bits = std::bit_cast<uint64_t>(f0);

    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0x14));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRRI(Opcode::LOAD64, 2, 1, 0));
    pushInstr(bytecode, encodeRRR(Opcode::SUBF64, 3, 2, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    pushInstr(bytecode, {
        static_cast<uint8_t>(f0bits & 0xFF),
        static_cast<uint8_t>((f0bits >> 8) & 0xFF),
        static_cast<uint8_t>((f0bits >> 16) & 0xFF),
        static_cast<uint8_t>((f0bits >> 24) & 0xFF)
    });
    pushInstr(bytecode, {
        static_cast<uint8_t>((f0bits >> 32) & 0xFF),
        static_cast<uint8_t>((f0bits >> 40) & 0xFF),
        static_cast<uint8_t>((f0bits >> 48) & 0xFF),
        static_cast<uint8_t>((f0bits >> 56) & 0xFF)
    });

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<double>(vm.getRegister (3)) == (f0 - f0));
}

TEST_CASE (test_arithmetic_float_mul32) {
    float f0 = 3.1415927f;
    uint32_t f0bits = std::bit_cast<uint32_t>(f0);

    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, f0bits & 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, (f0bits >> 16) & 0xFFFF));
    pushInstr(bytecode, encodeRRR(Opcode::MULF32, 2, 1, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<float>(static_cast<uint32_t>(vm.getRegister (2))) == (f0 * f0));
}

TEST_CASE (test_arithmetic_float_mul64) {
    double f0 = 3.1415927f;
    uint64_t f0bits = std::bit_cast<uint64_t>(f0);

    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0x14));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRRI(Opcode::LOAD64, 2, 1, 0));
    pushInstr(bytecode, encodeRRR(Opcode::MULF64, 3, 2, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    pushInstr(bytecode, {
        static_cast<uint8_t>(f0bits & 0xFF),
        static_cast<uint8_t>((f0bits >> 8) & 0xFF),
        static_cast<uint8_t>((f0bits >> 16) & 0xFF),
        static_cast<uint8_t>((f0bits >> 24) & 0xFF)
    });
    pushInstr(bytecode, {
        static_cast<uint8_t>((f0bits >> 32) & 0xFF),
        static_cast<uint8_t>((f0bits >> 40) & 0xFF),
        static_cast<uint8_t>((f0bits >> 48) & 0xFF),
        static_cast<uint8_t>((f0bits >> 56) & 0xFF)
    });

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<double>(vm.getRegister (3)) == (f0 * f0));
}

TEST_CASE (test_arithmetic_float_div32) {
    float f0 = 3.1415927f;
    uint32_t f0bits = std::bit_cast<uint32_t>(f0);

    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, f0bits & 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, (f0bits >> 16) & 0xFFFF));
    pushInstr(bytecode, encodeRRR(Opcode::DIVF32, 2, 1, 1));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<float>(static_cast<uint32_t>(vm.getRegister (2))) == (f0 / f0));
}

TEST_CASE (test_arithmetic_float_div64) {
    double f0 = 3.1415927f;
    uint64_t f0bits = std::bit_cast<uint64_t>(f0);

    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0x14));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRRI(Opcode::LOAD64, 2, 1, 0));
    pushInstr(bytecode, encodeRRR(Opcode::DIVF64, 3, 2, 2));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    pushInstr(bytecode, {
        static_cast<uint8_t>(f0bits & 0xFF),
        static_cast<uint8_t>((f0bits >> 8) & 0xFF),
        static_cast<uint8_t>((f0bits >> 16) & 0xFF),
        static_cast<uint8_t>((f0bits >> 24) & 0xFF)
    });
    pushInstr(bytecode, {
        static_cast<uint8_t>((f0bits >> 32) & 0xFF),
        static_cast<uint8_t>((f0bits >> 40) & 0xFF),
        static_cast<uint8_t>((f0bits >> 48) & 0xFF),
        static_cast<uint8_t>((f0bits >> 56) & 0xFF)
    });

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<double>(vm.getRegister (3)) == (f0 / f0));
}

TEST_CASE (test_arithmetic_float_sqrt32) {
    float f0 = 3.1415927f;
    uint32_t f0bits = std::bit_cast<uint32_t>(f0);

    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, f0bits & 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, (f0bits >> 16) & 0xFFFF));
    pushInstr(bytecode, encodeRRR(Opcode::SQRTF32, 2, 1, 0));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<float>(static_cast<uint32_t>(vm.getRegister (2))) == std::sqrt(f0));
}

TEST_CASE (test_arithmetic_float_sqrt64) {
    double f0 = 3.1415927f;
    uint64_t f0bits = std::bit_cast<uint64_t>(f0);

    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0x14));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRRI(Opcode::LOAD64, 2, 1, 0));
    pushInstr(bytecode, encodeRRR(Opcode::SQRTF64, 3, 2, 0));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    pushInstr(bytecode, {
        static_cast<uint8_t>(f0bits & 0xFF),
        static_cast<uint8_t>((f0bits >> 8) & 0xFF),
        static_cast<uint8_t>((f0bits >> 16) & 0xFF),
        static_cast<uint8_t>((f0bits >> 24) & 0xFF)
    });
    pushInstr(bytecode, {
        static_cast<uint8_t>((f0bits >> 32) & 0xFF),
        static_cast<uint8_t>((f0bits >> 40) & 0xFF),
        static_cast<uint8_t>((f0bits >> 48) & 0xFF),
        static_cast<uint8_t>((f0bits >> 56) & 0xFF)
    });

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<double>(vm.getRegister (3)) == std::sqrt(f0));
}

TEST_CASE (test_arithmetic_float_abs32) {
    float f0 = -3.1415927f;
    uint32_t f0bits = std::bit_cast<uint32_t>(f0);

    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, f0bits & 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, (f0bits >> 16) & 0xFFFF));
    pushInstr(bytecode, encodeRRR(Opcode::ABSF32, 2, 1, 0));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<float>(static_cast<uint32_t>(vm.getRegister (2))) == std::fabs(f0));
}

TEST_CASE (test_arithmetic_float_abs64) {
    double f0 = -3.1415927f;
    uint64_t f0bits = std::bit_cast<uint64_t>(f0);

    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0x14));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRRI(Opcode::LOAD64, 2, 1, 0));
    pushInstr(bytecode, encodeRRR(Opcode::ABSF64, 3, 2, 0));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    pushInstr(bytecode, {
        static_cast<uint8_t>(f0bits & 0xFF),
        static_cast<uint8_t>((f0bits >> 8) & 0xFF),
        static_cast<uint8_t>((f0bits >> 16) & 0xFF),
        static_cast<uint8_t>((f0bits >> 24) & 0xFF)
    });
    pushInstr(bytecode, {
        static_cast<uint8_t>((f0bits >> 32) & 0xFF),
        static_cast<uint8_t>((f0bits >> 40) & 0xFF),
        static_cast<uint8_t>((f0bits >> 48) & 0xFF),
        static_cast<uint8_t>((f0bits >> 56) & 0xFF)
    });

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<double>(vm.getRegister (3)) == std::fabs(f0));
}

TEST_CASE (test_arithmetic_float_neg32) {
    float f0 = 3.1415927f;
    uint32_t f0bits = std::bit_cast<uint32_t>(f0);

    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, f0bits & 0xFFFF));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, (f0bits >> 16) & 0xFFFF));
    pushInstr(bytecode, encodeRRR(Opcode::NEGF32, 2, 1, 0));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<float>(static_cast<uint32_t>(vm.getRegister (2))) == -f0);
}

TEST_CASE (test_arithmetic_float_neg64) {
    double f0 = 3.1415927f;
    uint64_t f0bits = std::bit_cast<uint64_t>(f0);

    std::vector<uint8_t> bytecode;
    pushInstr(bytecode, encodeRI(Opcode::LLI, 1, 0x14));
    pushInstr(bytecode, encodeRI(Opcode::LUI, 1, 0));
    pushInstr(bytecode, encodeRRI(Opcode::LOAD64, 2, 1, 0));
    pushInstr(bytecode, encodeRRR(Opcode::NEGF64, 3, 2, 0));
    pushInstr(bytecode, encodeNONE(Opcode::HALT));
    pushInstr(bytecode, {
        static_cast<uint8_t>(f0bits & 0xFF),
        static_cast<uint8_t>((f0bits >> 8) & 0xFF),
        static_cast<uint8_t>((f0bits >> 16) & 0xFF),
        static_cast<uint8_t>((f0bits >> 24) & 0xFF)
    });
    pushInstr(bytecode, {
        static_cast<uint8_t>((f0bits >> 32) & 0xFF),
        static_cast<uint8_t>((f0bits >> 40) & 0xFF),
        static_cast<uint8_t>((f0bits >> 48) & 0xFF),
        static_cast<uint8_t>((f0bits >> 56) & 0xFF)
    });

    CeruleanRISCVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (std::bit_cast<double>(vm.getRegister (3)) == -f0);
}
