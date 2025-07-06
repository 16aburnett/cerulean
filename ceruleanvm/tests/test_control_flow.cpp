#include "test_framework.hpp"
#include "ceruleanvm.hpp"
#include "tee_buf.hpp"
#include <fstream>
#include <vector>
#include <cstdint>
#include <sstream>
#include <iostream>

extern bool g_debug;

TEST_CASE (test_control_flow_conditional) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x0a, 0x00, // [0x00] r0.0 <- 10
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x04] r0.1 <- 0
        Opcode::LLI,     0x10, 0x0f, 0x00, // [0x08] r1.0 <- 15
        Opcode::LUI,     0x10, 0x00, 0x00, // [0x0c] r1.1 <- 0
        Opcode::LLI,     0x20, 0x20, 0x00, // [0x10] r2.0 <- cond_end
        Opcode::LUI,     0x20, 0x00, 0x00, // [0x14] r2.1 <- 0
        Opcode::BLE,     0x01, 0x20, 0x00, // [0x18] BLE r0, r1, r2(cond_end) // if r0 <= r1, jump to cond_end
        // cond_true: if r0 > 15
        Opcode::LLI,     0x00, 0x01, 0x00, // [0x1c] r0.0 <- 1
        // cond_end:
        Opcode::HALT,    0x00, 0x00, 0x00, // [0x20]
    };

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    REQUIRE (vm.getRegister (0) == 10);
}

TEST_CASE (test_control_flow_loop) {
    std::vector<uint8_t> bytecode = {
        Opcode::LLI,     0x00, 0x00, 0x00, // [0x00] r0.0 <- 0 ; i = 0
        Opcode::LUI,     0x00, 0x00, 0x00, // [0x04] r0.1 <- 0
        Opcode::LLI,     0x10, 0x0a, 0x00, // [0x08] r1.0 <- 10 ; N = 10
        Opcode::LUI,     0x10, 0x00, 0x00, // [0x0c] r1.1 <- 0
        Opcode::LLI,     0x20, 0x40, 0x00, // [0x10] r2.0 <- loop_end
        Opcode::LUI,     0x20, 0x00, 0x00, // [0x14] r2.1 <- 0
        Opcode::LLI,     0x30, 0x30, 0x00, // [0x18] r3.0 <- loop_cond
        Opcode::LUI,     0x30, 0x00, 0x00, // [0x1c] r3.1 <- 0
        Opcode::LLI,     0x40,  '*', 0x00, // [0x20] r4.0 <- '*'
        Opcode::LUI,     0x40, 0x00, 0x00, // [0x24] r4.1 <- 0
        Opcode::LLI,     0x50, '\n', 0x00, // [0x28] r5.0 <- '\n'
        Opcode::LUI,     0x50, 0x00, 0x00, // [0x2c] r5.1 <- 0
        // loop_cond:
        Opcode::BGE,     0x01, 0x20, 0x00, // [0x30] beq r0, r1, r2(loop_end) ; i >= N
        // loop_body:
        Opcode::PUTCHAR, 0x40, 0x00, 0x00, // [0x34] putchar(r4) ; print '*'
        // loop_update:
        Opcode::ADD32I,  0x00, 0x01, 0x00, // [0x38] addi r0, r0, 1 ; i = i + 1
        Opcode::JMP,     0x30, 0x00, 0x00, // [0x3c] jmp r3 ; jmp loop_cond
        // loop_end:
        Opcode::PUTCHAR, 0x50, 0x00, 0x00, // [0x40] putchar(r5) ; print '\n'
        Opcode::HALT,    0x00, 0x00, 0x00, // [0x44]
    };

    // Temporarily redirect std::cout to dualOut
    std::ostringstream captured;
    TeeBuf tee(std::cout.rdbuf(), captured);
    std::ostream dualOut(&tee);
    auto* originalBuf = std::cout.rdbuf();
    std::cout.rdbuf(dualOut.rdbuf());

    CeruleanVM vm (bytecode, g_debug);
    vm.run ();

    // Restore std::cout
    std::cout.rdbuf(originalBuf);

    // Ensure stdout matches expected output
    REQUIRE(captured.str() == "**********\n");
    REQUIRE (vm.getRegister (0) == 10); // Ensure i == N
}
