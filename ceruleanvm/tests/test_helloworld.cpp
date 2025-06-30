#include "ceruleanvm.hpp"
#include <fstream>
#include <vector>
#include <cstdint>

int main (int argc, char* argv[]) {

    std::vector<uint8_t> bytecode = {
        Opcode::LUI,     0x90,  'H', 0x00, // [0x00] r9 <- 'H'
        Opcode::LLI,     0x90, 0x00, 0x00, // [0x04] r9 <- 'H'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x08] putchar(r9)
        Opcode::LUI,     0x90,  'e', 0x00, // [0x0c] r9 <- 'e'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x14] putchar(r9)
        Opcode::LUI,     0x90,  'l', 0x00, // [0x18] r9 <- 'l'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x20] putchar(r9)
        Opcode::LUI,     0x90,  'l', 0x00, // [0x24] r9 <- 'l'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x2c] putchar(r9)
        Opcode::LUI,     0x90,  'o', 0x00, // [0x30] r9 <- 'o'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x38] putchar(r9)
        Opcode::LUI,     0x90,  ',', 0x00, // [0x30] r9 <- ','
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x38] putchar(r9)
        Opcode::LUI,     0x90,  ' ', 0x00, // [0x30] r9 <- ' '
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x38] putchar(r9)
        Opcode::LUI,     0x90,  'W', 0x00, // [0x30] r9 <- 'W'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x38] putchar(r9)
        Opcode::LUI,     0x90,  'o', 0x00, // [0x30] r9 <- 'o'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x38] putchar(r9)
        Opcode::LUI,     0x90,  'r', 0x00, // [0x30] r9 <- 'r'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x38] putchar(r9)
        Opcode::LUI,     0x90,  'l', 0x00, // [0x30] r9 <- 'l'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x38] putchar(r9)
        Opcode::LUI,     0x90,  'd', 0x00, // [0x30] r9 <- 'd'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x38] putchar(r9)
        Opcode::LUI,     0x90,  '!', 0x00, // [0x30] r9 <- '!'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x38] putchar(r9)
        Opcode::LUI,     0x90, '\n', 0x00, // [0x3c] r9 <- '\n'
        Opcode::PUTCHAR, 0x90, 0x00, 0x00, // [0x44] putchar(r9)
        Opcode::HALT
    };

    CeruleanVM vm (bytecode);
    vm.run ();

    return 0;
}