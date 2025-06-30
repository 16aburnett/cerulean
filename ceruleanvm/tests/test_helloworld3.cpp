#include "ceruleanvm.hpp"
#include <fstream>
#include <vector>
#include <cstdint>

// Helloworld3 - Uses a loop to print string
int main (int argc, char* argv[]) {
    bool debug = false;
    if (argc > 1 && argv[1][0] == 'd')
        debug = true;
    std::vector<uint8_t> bytecode = {
        Opcode::LUI,     0x00, 0x50, 0x00, // [0x00] r0.0 <- string_addr ; our iterator
        Opcode::LLI,     0x00, 0x00, 0x00, // [0x04] r0.1 <- string_addr ; out iterator
        Opcode::LUI,     0x10, 0x5e, 0x00, // [0x08] r1.0 <- string_end_addr ; end condition
        Opcode::LLI,     0x10, 0x00, 0x00, // [0x0c] r1.1 <- string_end_addr ; end condition
        Opcode::LUI,     0x30, 0x20, 0x00, // [0x10] r3.0 <- loop_cond
        Opcode::LLI,     0x30, 0x00, 0x00, // [0x14] r3.1 <- loop_cond
        Opcode::LUI,     0x40, 0x34, 0x00, // [0x18] r4.0 <- loop_end
        Opcode::LLI,     0x40, 0x00, 0x00, // [0x1c] r4.1 <- loop_end
        // loop_cond:
        Opcode::BGE,     0x01, 0x40, 0x00, // [0x20] bge r0, r1, loop_end; iter >= end
        // loop_body:
        Opcode::LB,      0x20, 0x00, 0x00, // [0x24] lb r2, r0, 0x00 ; load char from mem
        Opcode::PUTCHAR, 0x20, 0x00, 0x00, // [0x28] putchar(r2)
        // loop_update:
        Opcode::ADDI,    0x00, 0x01, 0x00, // [0x2c] addi r0, r0, 1 ; move to next char
        Opcode::JMP,     0x30, 0x00, 0x00, // [0x30] jmp r3 ; jmp loop_cond
        // loop_end:
        Opcode::HALT,    0x00, 0x00, 0x00, // [0x34]
        0x00,            0x00, 0x00, 0x00, // [0x38] buffer
        0x00,            0x00, 0x00, 0x00, // [0x3c] buffer
        0x00,            0x00, 0x00, 0x00, // [0x40] buffer
        0x00,            0x00, 0x00, 0x00, // [0x44] buffer
        0x00,            0x00, 0x00, 0x00, // [0x48] buffer
        0x00,            0x00, 0x00, 0x00, // [0x4c] buffer
        'H',              'e',  'l',  'l', // [0x50] string_addr
        'o',              ',',  ' ',  'W', // [0x54]
        'o',              'r',  'l',  'd', // [0x58]
        '!',             '\n', 0x00, 0x00, // [0x5c]
    };

    CeruleanVM vm (bytecode, debug);
    vm.run ();

    return 0;
}