#include "ceruleanvm.hpp"
#include <iostream>
#include <cstring>
#include <cmath>

CeruleanVM::CeruleanVM (const std::vector<uint8_t>& bytecode, bool debug_)
    : memory(bytecode.size(), STACK_SIZE, HEAP_SIZE), debug(debug_) {
    code = bytecode;
    // Shift program counter to the start of the code
    pc = 0;
    std::memset (registers, 0, sizeof(registers));

    // Setup memory
    // bytecode is added to memory incase there is any static data
    memory.loadCode (bytecode);
    registers[bp] = MemoryManager::STACK_BASE;
    registers[sp] = MemoryManager::STACK_BASE;
}

CeruleanVM::~CeruleanVM () {}

uint64_t CeruleanVM::get_register (uint8_t index) const {
    return registers[index];
}

uint64_t CeruleanVM::getPC () const {
    return pc;
}

void CeruleanVM::run () {
    if (debug) 
        printf ("%8s | %11s | %s\n", "pc", "instruction", "registers");
    while (!isHalted ()) {
        execute_instruction ();
    }
}

void CeruleanVM::step () {
    execute_instruction ();
}

bool CeruleanVM::isHalted () {
    return pc >= code.size ();
}

void CeruleanVM::execute_instruction () {
    // Instruction is 4 bytes (assuming big-endian)
    uint32_t instruction = 
        (code[pc + 0] << 24) |
        (code[pc + 1] << 16) |
        (code[pc + 2] << 8)  |
        (code[pc + 3]);
    Opcode opcode = static_cast<Opcode> ((0b11111111000000000000000000000000 & instruction) >> 24);
    if (debug)
    {
        // print address
        printf (
            "%lx%lx%lx%lx%lx%lx%lx%lx | ", 
            (0b11110000000000000000000000000000 & pc) >> 28,
            (0b00001111000000000000000000000000 & pc) >> 24,
            (0b00000000111100000000000000000000 & pc) >> 20,
            (0b00000000000011110000000000000000 & pc) >> 16,
            (0b00000000000000001111000000000000 & pc) >> 12,
            (0b00000000000000000000111100000000 & pc) >>  8,
            (0b00000000000000000000000011110000 & pc) >>  4,
            (0b00000000000000000000000000001111 & pc) >>  0
        );
        // print instruction
        printf (
            "%x%x %x%x %x%x %x%x | ", 
            (0b11110000000000000000000000000000 & instruction) >> 28,
            (0b00001111000000000000000000000000 & instruction) >> 24,
            (0b00000000111100000000000000000000 & instruction) >> 20,
            (0b00000000000011110000000000000000 & instruction) >> 16,
            (0b00000000000000001111000000000000 & instruction) >> 12,
            (0b00000000000000000000111100000000 & instruction) >>  8,
            (0b00000000000000000000000011110000 & instruction) >>  4,
            (0b00000000000000000000000000001111 & instruction) >>  0
        );
        // Print registers
        for (int i = 0; i < 16; ++i)
        {
            printf ("%lx, ", registers[i]);
        }
        printf ("\n");
    }
    switch (opcode) {
        // LUI dest, imm        - loads upper immediate 16 bits into given register
        // XXXXXXXX dddd0000 iiiiiiii iiiiiiii
        case Opcode::LUI: {
            uint8_t dest = (0b00000000111100000000000000000000 & instruction) >> 20;
            // imm acts as the upper 16 bits of the register 
            reinterpret_cast<uint8_t*>(&registers[dest])[0] = (0b00000000000000001111111100000000 & instruction) >> 8;
            reinterpret_cast<uint8_t*>(&registers[dest])[1] = (0b00000000000000000000000011111111 & instruction) >> 0; 
            break;
        }
        // LLI dest, imm        - loads lower immediate 16 bits into given register
        // XXXXXXXX dddd0000 iiiiiiii iiiiiiii
        case Opcode::LLI: {
            uint8_t dest = (0b00000000111100000000000000000000 & instruction) >> 20;
            // imm acts as the lower 16 bits of the register 
            reinterpret_cast<uint8_t*>(&registers[dest])[2] = (0b00000000000000001111111100000000 & instruction) >> 8; 
            reinterpret_cast<uint8_t*>(&registers[dest])[3] = (0b00000000000000000000000011111111 & instruction) >> 0; 
            break;
        }
        // LB dest, offset(src) - load byte
        // XXXXXXXX ddddssss oooooooo oooooooo
        // offset should be specified in little endian (least -> most significant byte)
        case Opcode::LB: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers[src1];
            // read offset in little endian
            uint64_t offset = *(int16_t*)&code[pc + 2];
            // clear register bytes
            registers[dest] = 0;
            // read in byte
            registers[dest] = memory.read8 (address + offset);
            break;
        }
        // LH dest, offset(src) - load half (2 bytes)
        // XXXXXXXX ddddssss oooooooo oooooooo
        case Opcode::LH: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers[src1];
            // read offset in little endian
            uint64_t offset = *(int16_t*)&code[pc + 2];
            // clear register bytes
            registers[dest] = 0; 
            // read in half word (2 bytes) 
            registers[dest] = memory.read16 (address + offset);
            break;
        }
        // LW dest, offset(src) - load word (4 bytes)
        // XXXXXXXX ddddssss oooooooo oooooooo
        case Opcode::LW: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers[src1];
            // read offset in little endian
            uint64_t offset = *(int16_t*)&code[pc + 2];
            // clear register bytes
            registers[dest] = 0;
            // read in word (4 bytes) 
            registers[dest] = memory.read32 (address + offset);
            break;
        }
        // LD dest, offset(src) - load double word (8 bytes)
        // XXXXXXXX ddddssss oooooooo oooooooo
        case Opcode::LD: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers[src1];
            // read offset in little endian
            uint64_t offset = *(int16_t*)&code[pc + 2];
            // clear register bytes
            registers[dest] = 0;
            // read in double word (8 bytes) 
            registers[dest] = memory.read64 (address + offset);
            break;
        }
        // SB offset(dest), src - store byte
        // XXXXXXXX ddddssss oooooooo oooooooo
        case Opcode::SB: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers[dest];
            // read offset in little endian
            uint64_t offset = *(int16_t*)&code[pc + 2];
            // store byte
            memory.write8 (address + offset, (uint8_t)registers[src1]);
            break;
        }
        // SH offset(dest), src - store half (2 bytes)
        // XXXXXXXX ddddssss oooooooo oooooooo
        case Opcode::SH: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers[dest];
            // read offset in little endian
            int offset = *(int16_t*)&code[pc + 2];
            // store half word (2 bytes)
            memory.write16 (address + offset, (uint16_t)registers[src1]);
            break;
        }
        // SW offset(dest), src - store word (4 bytes)
        // XXXXXXXX ddddssss oooooooo oooooooo
        case Opcode::SW: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers[dest];
            // read offset in little endian
            int offset = *(int16_t*)&code[pc + 2];
            // store word (4 bytes)
            memory.write32 (address + offset, (uint32_t)registers[src1]);
            break;
        }
        // SD offset(dest), src - store double word (8 bytes)
        // XXXXXXXX ddddssss oooooooo oooooooo
        case Opcode::SD: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers[dest];
            // read offset in little endian
            int offset = *(int16_t*)&code[pc + 2];
            // store double word (8 bytes)
            memory.write64 (address + offset, (uint64_t)registers[src1]);
            break;
        }

        // arithmetic instructions
        // ADD dest, src1, src2 - integer addition
        // XXXXXXXX ddddssss ssss0000 00000000
        case Opcode::ADD: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] + *(int*)&registers[src2];
            break;
        }
        // SUB dest, src1, src2 - integer subtraction
        // XXXXXXXX ddddssss ssss0000 00000000
        case Opcode::SUB: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] - *(int*)&registers[src2];
            break;
        }
        // MUL dest, src1, src2 - integer multiplication
        // XXXXXXXX ddddssss ssss0000 00000000
        case Opcode::MUL: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] * *(int*)&registers[src2];
            break;
        }
        // DIV dest, src1, src2 - integer division
        // XXXXXXXX ddddssss ssss0000 00000000
        case Opcode::DIV: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] / *(int*)&registers[src2];
            break;
        }
        // MOD dest, src1, src2 - integer division remainder
        // XXXXXXXX ddddssss ssss0000 00000000
        case Opcode::MOD: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] % *(int*)&registers[src2];
            break;
        }
        // Floating Point Arithmetic Instructions
        case Opcode::ADDF32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            float a = std::bit_cast<float>(static_cast<uint32_t>(registers[src1]));
            float b = std::bit_cast<float>(static_cast<uint32_t>(registers[src2]));
            // Perform instruction
            float c = a + b;
            // Write to register
            registers[dest] = static_cast<uint64_t>(std::bit_cast<uint32_t>(c));
            break;
        }
        case Opcode::ADDF64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            double a = std::bit_cast<double>(registers[src1]);
            double b = std::bit_cast<double>(registers[src2]);
            // Perform instruction
            double c = a + b;
            // Write to register
            registers[dest] = std::bit_cast<uint64_t>(c);
            break;
        }
        case Opcode::SUBF32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            float a = std::bit_cast<float>(static_cast<uint32_t>(registers[src1]));
            float b = std::bit_cast<float>(static_cast<uint32_t>(registers[src2]));
            // Perform instruction
            float c = a - b;
            // Write to register
            registers[dest] = static_cast<uint64_t>(std::bit_cast<uint32_t>(c));
            break;
        }
        case Opcode::SUBF64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            double a = std::bit_cast<double>(registers[src1]);
            double b = std::bit_cast<double>(registers[src2]);
            // Perform instruction
            double c = a - b;
            // Write to register
            registers[dest] = std::bit_cast<uint64_t>(c);
            break;
        }
        case Opcode::MULF32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            float a = std::bit_cast<float>(static_cast<uint32_t>(registers[src1]));
            float b = std::bit_cast<float>(static_cast<uint32_t>(registers[src2]));
            // Perform instruction
            float c = a * b;
            // Write to register
            registers[dest] = static_cast<uint64_t>(std::bit_cast<uint32_t>(c));
            break;
        }
        case Opcode::MULF64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            double a = std::bit_cast<double>(registers[src1]);
            double b = std::bit_cast<double>(registers[src2]);
            // Perform instruction
            double c = a * b;
            // Write to register
            registers[dest] = std::bit_cast<uint64_t>(c);
            break;
        }
        case Opcode::DIVF32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            float a = std::bit_cast<float>(static_cast<uint32_t>(registers[src1]));
            float b = std::bit_cast<float>(static_cast<uint32_t>(registers[src2]));
            // Perform instruction
            float c = a / b;
            // Write to register
            registers[dest] = static_cast<uint64_t>(std::bit_cast<uint32_t>(c));
            break;
        }
        case Opcode::DIVF64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            double a = std::bit_cast<double>(registers[src1]);
            double b = std::bit_cast<double>(registers[src2]);
            // Perform instruction
            double c = a / b;
            // Write to register
            registers[dest] = std::bit_cast<uint64_t>(c);
            break;
        }
        case Opcode::SQRTF32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            // Read from registers
            float a = std::bit_cast<float>(static_cast<uint32_t>(registers[src1]));
            // Perform instruction
            float c = std::sqrt (a);
            // Write to register
            registers[dest] = static_cast<uint64_t>(std::bit_cast<uint32_t>(c));
            break;
        }
        case Opcode::SQRTF64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            // Read from registers
            double a = std::bit_cast<double>(registers[src1]);
            // Perform instruction
            double c = std::sqrt (a);
            // Write to register
            registers[dest] = std::bit_cast<uint64_t>(c);
            break;
        }
        case Opcode::ABSF32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            // Read from registers
            float a = std::bit_cast<float>(static_cast<uint32_t>(registers[src1]));
            // Perform instruction
            float c = std::fabs (a);
            // Write to register
            registers[dest] = static_cast<uint64_t>(std::bit_cast<uint32_t>(c));
            break;
        }
        case Opcode::ABSF64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            // Read from registers
            double a = std::bit_cast<double>(registers[src1]);
            // Perform instruction
            double c = std::fabs (a);
            // Write to register
            registers[dest] = std::bit_cast<uint64_t>(c);
            break;
        }
        case Opcode::NEGF32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            // Read from registers
            float a = std::bit_cast<float>(static_cast<uint32_t>(registers[src1]));
            // Perform instruction
            float c = -a;
            // Write to register
            registers[dest] = static_cast<uint64_t>(std::bit_cast<uint32_t>(c));
            break;
        }
        case Opcode::NEGF64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            // Read from registers
            double a = std::bit_cast<double>(registers[src1]);
            // Perform instruction
            double c = -a;
            // Write to register
            registers[dest] = std::bit_cast<uint64_t>(c);
            break;
        }
        // SLL dest, src1, src2 - shift left logical
        // XXXXXXXX ddddssss ssss0000 00000000
        case Opcode::SLL: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] << *(int*)&registers[src2];
            break;
        }
        // SRL dest, src1, src2 - shift right logical
        // XXXXXXXX ddddssss ssss0000 00000000
        case Opcode::SRL: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(unsigned int*)&registers[src1] >> *(unsigned int*)&registers[src2];
            break;
        }
        // SRA dest, src1, src2 - shift right arithmetic
        // XXXXXXXX ddddssss ssss0000 00000000
        case Opcode::SRA: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] >> *(int*)&registers[src2];
            break;
        }
        // OR  dest, src1, src2 - bitwise or
        // XXXXXXXX ddddssss ssss0000 00000000
        case Opcode::OR: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] | *(int*)&registers[src2];
            break;
        }
        // AND dest, src1, src2 - bitwise and
        // XXXXXXXX ddddssss ssss0000 00000000
        case Opcode::AND: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] & *(int*)&registers[src2];
            break;
        }
        // XOR dest, src1, src2 - bitwise xor 
        // XXXXXXXX ddddssss ssss0000 00000000
        case Opcode::XOR: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] ^ *(int*)&registers[src2];
            break;
        }

        // immediate arithmetic instructions
        // immediate values are 14-bit signed
        // ADDI dest, src1, imm - integer addition with immediate
        // - can be used to load immediate into register 
        // - that's why there is no load immediate 
        // - ADDI r0, rzero, 42 : r0 <- 0 + 42
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        case Opcode::ADDI: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&code[pc+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] + imm;
            break;
        }
        // SUBI dest, src1, imm - integer subtraction with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        case Opcode::SUBI: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&code[pc+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] - imm;
            break;
        }
        // MULI dest, src1, src2 - integer multiplication with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        case Opcode::MULI: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&code[pc+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] * imm;
            break;
        }
        // DIVI dest, src1, src2 - integer division with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        case Opcode::DIVI: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&code[pc+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] / imm;
            break;
        }
        // MODI dest, src1, src2 - integer division remainder with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        case Opcode::MODI: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&code[pc+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] % imm;
            break;
        }
        // SLLI dest, src1, imm - shift left logical with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        case Opcode::SLLI: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&code[pc+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] << imm;
            break;
        }
        // SRLI dest, src1, imm - shift right logical with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        case Opcode::SRLI: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            unsigned int  imm    = *(int16_t*)&code[pc+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(unsigned int*)&registers[src1] >> imm;
            break;
        }
        // SRAI dest, src1, imm - shift right arithmetic with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        case Opcode::SRAI: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&code[pc+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] >> imm;
            break;
        }
        // ORI  dest, src1, imm - bitwise or with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        case Opcode::ORI: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&code[pc+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] | imm;
            break;
        }
        // ANDI dest, src1, imm - bitwise and with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        case Opcode::ANDI: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&code[pc+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] & imm;
            break;
        }
        // XORI dest, src1, imm - bitwise xor  with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        case Opcode::XORI: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&code[pc+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest]) = *(int*)&registers[src1] ^ imm;
            break;
        }

        // branching
        // BEQ src1, src2, addr - if src1 == src2 then pc <- addr
        // XXXXXXXX ssssssss aaaa0000 00000000
        case Opcode::BEQ: {
            uint8_t src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src2   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t addr   = (0b00000000000000001111000000000000 & instruction) >> 12;
            if (registers[src1] == registers[src2])
                pc = registers[addr] - 4;
            break;
        }
        // BNE src1, src2, addr - if src1 != src2 then pc <- addr
        // XXXXXXXX ssssssss aaaa0000 00000000
        case Opcode::BNE: {
            uint8_t src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src2   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t addr   = (0b00000000000000001111000000000000 & instruction) >> 12;
            if (registers[src1] != registers[src2])
                pc = registers[addr] - 4;
            break;
        }
        // BLT src1, src2, addr - if src1 <  src2 then pc <- addr
        // XXXXXXXX ssssssss aaaa0000 00000000
        case Opcode::BLT: {
            uint8_t src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src2   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t addr   = (0b00000000000000001111000000000000 & instruction) >> 12;
            if (registers[src1] < registers[src2])
                pc = registers[addr] - 4;
            break;
        }
        // BLE src1, src2, addr - if src1 <= src2 then pc <- addr
        // XXXXXXXX ssssssss aaaa0000 00000000
        case Opcode::BLE: {
            uint8_t src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src2   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t addr   = (0b00000000000000001111000000000000 & instruction) >> 12;
            if (registers[src1] <= registers[src2])
                pc = registers[addr] - 4;
            break;
        }
        // BGT src1, src2, addr - if src1 >  src2 then pc <- addr
        // XXXXXXXX ssssssss aaaa0000 00000000
        case Opcode::BGT: {
            uint8_t src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src2   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t addr   = (0b00000000000000001111000000000000 & instruction) >> 12;
            if (registers[src1] > registers[src2])
                pc = registers[addr] - 4;
            break;
        }
        // BGE src1, src2, addr - if src1 >= src2 then pc <- addr
        // XXXXXXXX ssssssss aaaa0000 00000000
        case Opcode::BGE: {
            uint8_t src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src2   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t addr   = (0b00000000000000001111000000000000 & instruction) >> 12;
            if (registers[src1] >= registers[src2])
                pc = registers[addr] - 4;
            break;
        }
        // JMP addr - pc <- addr
        // XXXXXXXX aaaa0000 00000000 00000000
        case Opcode::JMP: {
            uint8_t addr   = (0b00000000111100000000000000000000 & instruction) >> 20;
            pc = registers[addr] - 4;
            break;
        }

        // function instructions 
        // CALL addr
        // 1. pushes return address on to the stack
        // 2. changes pc to addr
        // base pointer should be pushed on the stack by the callee
        // push bp
        // mov bp, sp
        // Caller's actions
        // 1. push caller saved registers
        // 2. push args in reverse order
        // 3. call function
        // Call's actions
        // 1. push return addr
        // 2. pc <- addr 
        // Callee's actions 
        // 1. push caller's bp 
        // 2. align our frame's bp and sp (mov bp, sp)
        // 3. allocate space for local vars (sub sp, sp, <#bytes>)
        //    local vars can be access with bp - 0, bp - 4, bp - 8, etc
        // 4. push callee saved registers onto stack 
        //    these need to be restored because caller 
        //    expects these values to be unchanged. 
        // XXXXXXXX aaaa0000 00000000 00000000
        case Opcode::CALL: {
            uint8_t addr   = (0b00000000111100000000000000000000 & instruction) >> 20;
            // push return address onto stack 
            registers[sp] -= 8; // stack grows towards 0
            memory.write64 (registers[sp], pc);
            // change program counter to addr
            // -4 to point to the previous instruction since VM will increment later
            pc = registers[addr] - 4;
            break;
        }
        // RET - pc <- [bp]
        // changes the current pc to the return address pointed to by bp
        // Callee's actions before returning
        // 1. store any return value in ra (return value register)
        // 2. restore callee-saved registers 
        // 3. pop local vars off of stack (mov sp, bp) (sp <- bp)
        // 4. restore caller's bp (pop bp)
        // Return's actions 
        // 1. pops return address off of stack and stores in pc (pop pc) 
        // Caller's actions after returning 
        // 1. pop any arguments that were pushed onto the stack (add sp, sp, <#bytes>)
        // 2. pop any caller saved registers back into their respective registers (pop r#)
        // XXXXXXXX 00000000 00000000 00000000
        case Opcode::RET: {
            // pop return address from stack into 
            pc = memory.read64 (registers[sp]);
            registers[sp] += 8; // stack shrinks towards MEM_SIZE
            break;
        }
        // PUSH src - sp -= 8 ; [sp] <- src
        // 1. decrements sp by 8 (bytes)
        // 2. places src onto stack at [sp]
        // XXXXXXXX ssss0000 00000000 00000000
        case Opcode::PUSH: {
            uint8_t src    = (0b00000000111100000000000000000000 & instruction) >> 20;
            registers[sp] -= 8; // stack grows towards 0
            memory.write64 (registers[sp], registers[src]);
            break;
        }
        // POP dest - dest <- [sp] ; sp += 8
        // 1. moves [sp] into dest 
        // 2. increments sp by 8 (bytes)
        // XXXXXXXX dddd0000 00000000 00000000
        case Opcode::POP: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            registers[dest] = memory.read64 (registers[sp]); 
            registers[sp] += 8; // stack shrinks towards MEM_SIZE
            break;
        }

        // NOP - no operation
        // XXXXXXXX 000000000 00000000 00000000
        case Opcode::NOP: {
            // Do nothing
            break;
        }
        // other instructions
        // HALT - halts the computer
        // XXXXXXXX 000000000 00000000 00000000
        case Opcode::HALT: {
            pc = code.size ();
            break;
        }
        // GETCHAR - reads (from stdin) a char (1-byte) and stores it in the 
        // given register
        // XXXXXXXX dddd00000 00000000 00000000
        case Opcode::GETCHAR: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            registers[dest] = getchar();
            break;
        }
        // PUTCHAR - outputs (to stdout) a char (1-byte) from the given register
        // XXXXXXXX ssss00000 00000000 00000000
        case Opcode::PUTCHAR: {
            uint8_t src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            if (debug) printf ("Output = '");
            // Using std::cout so unit tests can capture output
            std::cout << (char)registers[src1];
            if (debug) printf ("'\n");
            break;
        }
        // unknown instruction
        default: {
            printf ("Invalid opcode 0x%x\n", (uint)opcode);
            pc = code.size ();
            break;
        }
    }
    
    // Advance to the next instruction
    pc += 4;
}

void CeruleanVM::handle_syscall (uint8_t sym_id) {
    switch (sym_id) {
        case SYSCALL_PUTS: {
            const char* str = reinterpret_cast<const char*> (registers[0]);
            puts(str);
            break;
        }
        default:
            std::cerr << "Unknown syscall: " << static_cast<int> (sym_id) << "\n";
            break;
    }
}
