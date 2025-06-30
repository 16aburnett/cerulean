#include "ceruleanvm.hpp"
#include <fstream>
#include <vector>
#include <cstdint>

// Helloworld3 - Uses a function to print a null-terminated string
int main (int argc, char* argv[]) {
    bool debug = false;
    if (argc > 1 && argv[1][0] == 'd')
        debug = true;
    std::vector<uint8_t> bytecode = {
        Opcode::LUI,     0x00, 0xcc, 0x00, // [0x00] r0.0 <- string_addr
        Opcode::LLI,     0x00, 0x00, 0x00, // [0x04] r0.1 <- string_addr
        // Call print_string
        Opcode::PUSH,    0x00, 0x00, 0x00, // [0x08] push r0
        Opcode::LUI,     0x90, 0x2c, 0x00, // [0x0c] lui r9, print_string
        Opcode::CALL,    0x90, 0x00, 0x00, // [0x10] call r9(print_string)
        Opcode::POP,     0x00, 0x00, 0x00, // [0x14] pop
        Opcode::HALT,    0x00, 0x00, 0x00, // [0x18]
        0x00,            0x00, 0x00, 0x00, // [0x1c] buffer
        0x00,            0x00, 0x00, 0x00, // [0x20] buffer
        0x00,            0x00, 0x00, 0x00, // [0x24] buffer
        0x00,            0x00, 0x00, 0x00, // [0x28] buffer

        // Function void print_string (ptr string_addr)
        // function_prologue: 
        Opcode::PUSH,    0xe0, 0x00, 0x00, // [0x2c] push bp - save caller's bp 
        Opcode::ADDI,    0xef, 0x00, 0x00, // [0x30] bp <- sp + 0
        Opcode::PUSH,    0x00, 0x00, 0x00, // [0x34] push r0 - save caller's r0
        Opcode::PUSH,    0x10, 0x00, 0x00, // [0x38] push r1 - save caller's r1 
        Opcode::PUSH,    0x20, 0x00, 0x00, // [0x3c] push r2 - save caller's r2 
        Opcode::PUSH,    0x30, 0x00, 0x00, // [0x40] push r3 - save caller's r3 
        Opcode::PUSH,    0x40, 0x00, 0x00, // [0x44] push r4 - save caller's r4 
        Opcode::PUSH,    0x50, 0x00, 0x00, // [0x48] push r5 - save caller's r5 
        Opcode::PUSH,    0x60, 0x00, 0x00, // [0x4c] push r6 - save caller's r6 
        Opcode::PUSH,    0x70, 0x00, 0x00, // [0x50] push r7 - save caller's r7 
        Opcode::PUSH,    0x80, 0x00, 0x00, // [0x54] push r8 - save caller's r8 
        Opcode::PUSH,    0x90, 0x00, 0x00, // [0x58] push r9 - save caller's r9 
        // function_body:
        Opcode::LW,      0x0e, 0x10, 0x00, // [0x5c] r0 <- [bp + 16] - get param string_addr
        Opcode::LUI,     0x30, 0x74, 0x00, // [0x60] r3.0 <- loop_cond
        Opcode::LLI,     0x30, 0x00, 0x00, // [0x64] r3.1 <- loop_cond
        Opcode::LUI,     0x40, 0x88, 0x00, // [0x68] r4.0 <- loop_end
        Opcode::LLI,     0x40, 0x00, 0x00, // [0x6c] r4.1 <- loop_end
        Opcode::LUI,     0x50, 0x00, 0x00, // [0x70] r5.0 <- 0 ; null-byte
        // loop_cond:
        Opcode::LB,      0x20, 0x00, 0x00, // [0x74] lb r2, r0, 0x00 ; load char from mem
        Opcode::BEQ,     0x25, 0x40, 0x00, // [0x78] beq r2, r5, r4(loop_end) ; *str == null
        // loop_body:
        Opcode::PUTCHAR, 0x20, 0x00, 0x00, // [0x7c] putchar(r2)
        // loop_update:
        Opcode::ADDI,    0x00, 0x01, 0x00, // [0x80] addi r0, r0, 1 ; move to next char
        Opcode::JMP,     0x30, 0x00, 0x00, // [0x84] jmp r3 ; jmp loop_cond
        // loop_end:
        // function_epilogue: 
        Opcode::POP,     0x90, 0x00, 0x00, // [0x88] pop r9 - restore caller's r9
        Opcode::POP,     0x80, 0x00, 0x00, // [0x8c] pop r8 - restore caller's r8
        Opcode::POP,     0x70, 0x00, 0x00, // [0x90] pop r7 - restore caller's r7
        Opcode::POP,     0x60, 0x00, 0x00, // [0x94] pop r6 - restore caller's r6
        Opcode::POP,     0x50, 0x00, 0x00, // [0x98] pop r5 - restore caller's r5
        Opcode::POP,     0x40, 0x00, 0x00, // [0x9c] pop r4 - restore caller's r4
        Opcode::POP,     0x30, 0x00, 0x00, // [0xa0] pop r3 - restore caller's r3
        Opcode::POP,     0x20, 0x00, 0x00, // [0xa4] pop r2 - restore caller's r2
        Opcode::POP,     0x10, 0x00, 0x00, // [0xa8] pop r1 - restore caller's r1
        Opcode::POP,     0x00, 0x00, 0x00, // [0xac] pop r0 - restore caller's r0 
        Opcode::ADDI,    0xfe, 0x00, 0x00, // [0xb0] sp <- bp - remove local vars 
        Opcode::POP,     0xe0, 0x00, 0x00, // [0xb4] bp <- [sp] - restore caller bp
        Opcode::RET,     0x00, 0x00, 0x00, // [0xb8] return from function
        // End function
        0x00,            0x00, 0x00, 0x00, // [0xbc] buffer
        0x00,            0x00, 0x00, 0x00, // [0xc0] buffer
        0x00,            0x00, 0x00, 0x00, // [0xc4] buffer
        0x00,            0x00, 0x00, 0x00, // [0xc8] buffer
        'H',              'e',  'l',  'l', // [0xcc] string_addr
        'o',              ',',  ' ',  'W', // [0xd0]
        'o',              'r',  'l',  'd', // [0xd4]
        '!',             '\n', 0x00, 0x00, // [0xd8]
    };

    CeruleanVM vm (bytecode, debug);
    vm.run ();

    return 0;
}