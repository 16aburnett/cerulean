#include "ceruleanvm.hpp"
#include <iostream>
#include <cstring>
#include <cmath>
#include "disassembler.hpp"

CeruleanVM::CeruleanVM (const std::vector<uint8_t>& bytecode, bool debug_)
    : memory(bytecode.size(), STACK_SIZE, HEAP_SIZE), debug(debug_) {
    code = bytecode;
    // Shift program counter to the start of the code
    pc = 0;

    // Setup memory
    // bytecode is added to memory incase there is any static data
    memory.loadCode (bytecode);
    registers.set<uint64_t>(bp, MemoryManager::STACK_BASE);
    registers.set<uint64_t>(sp, MemoryManager::STACK_BASE);
}

CeruleanVM::~CeruleanVM () {}

uint64_t CeruleanVM::getRegister (uint8_t index) const {
    return registers.get<uint64_t>(index);
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
        for (int32_t i = 0; i < 16; ++i)
        {
            printf ("%lx, ", registers.get<uint64_t>(i));
        }
        // Disassemble
        std::vector<uint8_t> instr_bytes = {code[pc+0], code[pc+1], code[pc+2], code[pc+3]};
        std::string disassembled = disassemble (instr_bytes);
        printf (" | %s", disassembled.c_str());
        printf ("\n");
    }
    switch (opcode) {
        // ========================================================================================
        // Load/Store Instructions
        // ========================================================================================
        case Opcode::LUI: {
            uint8_t dest = (0b00000000111100000000000000000000 & instruction) >> 20;
            int16_t imm  = *(int16_t*)&code[pc+2];
            // imm acts as the upper 16 bits of the register
            uint64_t regContents = registers.get<uint64_t>(dest);
            regContents = (regContents & 0xFFFFFFFF0000FFFFULL) | (static_cast<uint64_t>(imm & 0xFFFF) << 16);
            registers.set<uint64_t>(dest, regContents);
            break;
        }
        case Opcode::LLI: {
            uint8_t dest = (0b00000000111100000000000000000000 & instruction) >> 20;
            int16_t imm  = *(int16_t*)&code[pc+2];
            // imm acts as the lower 16 bits of the register
            uint64_t regContents = registers.get<uint64_t>(dest);
            regContents = (regContents & 0xFFFFFFFFFFFF0000ULL) | (static_cast<uint64_t>(imm & 0xFFFF) << 0);
            registers.set<uint64_t>(dest, regContents);
            break;
        }
        case Opcode::LOAD8: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers.get<uint64_t>(src1);
            // read offset in little endian
            int64_t offset = *(int16_t*)&code[pc + 2];
            // read in byte and sign-extend to 64-bit
            int8_t value = static_cast<int8_t>(memory.read8(address + offset));
            registers.set<int64_t>(dest, static_cast<int64_t>(value));
            break;
        }
        case Opcode::LOADU8: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers.get<uint64_t>(src1);
            // read offset in little endian
            int64_t offset = *(int16_t*)&code[pc + 2];
            // read in byte and zero-extend to 64-bit
            uint8_t value = memory.read8(address + offset);
            registers.set<uint64_t>(dest, static_cast<uint64_t>(value));
            break;
        }
        case Opcode::LOAD16: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers.get<uint64_t>(src1);
            // read offset in little endian
            int64_t offset = *(int16_t*)&code[pc + 2];
            // read in half word (2 bytes) and sign-extend to 64-bit
            int16_t value = static_cast<int16_t>(memory.read16(address + offset));
            registers.set<int64_t>(dest, static_cast<int64_t>(value));
            break;
        }
        case Opcode::LOADU16: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers.get<uint64_t>(src1);
            // read offset in little endian
            int64_t offset = *(int16_t*)&code[pc + 2];
            // read in half word (2 bytes) and zero-extend to 64-bit
            uint16_t value = memory.read16(address + offset);
            registers.set<uint64_t>(dest, static_cast<uint64_t>(value));
            break;
        }
        case Opcode::LOAD32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers.get<uint64_t>(src1);
            // read offset in little endian
            int64_t offset = *(int16_t*)&code[pc + 2];
            // read in word (4 bytes) and sign-extend to 64-bit
            int32_t value = static_cast<int32_t>(memory.read32(address + offset));
            registers.set<int64_t>(dest, static_cast<int64_t>(value));
            break;
        }
        case Opcode::LOADU32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers.get<uint64_t>(src1);
            // read offset in little endian
            int64_t offset = *(int16_t*)&code[pc + 2];
            // read in word (4 bytes) and zero-extend to 64-bit
            uint32_t value = memory.read32(address + offset);
            registers.set<uint64_t>(dest, static_cast<uint64_t>(value));
            break;
        }
        case Opcode::LOAD64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers.get<uint64_t>(src1);
            // read offset in little endian
            int64_t offset = *(int16_t*)&code[pc + 2];
            // read in double word (8 bytes)
            registers.set<uint64_t>(dest, memory.read64(address + offset));
            break;
        }
        case Opcode::STORE8: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers.get<uint64_t>(dest);
            // read offset in little endian
            uint64_t offset = *(int16_t*)&code[pc + 2];
            // store byte
            memory.write8 (address + offset, registers.get<uint8_t>(src1));
            break;
        }
        case Opcode::STORE16: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers.get<uint64_t>(dest);
            // read offset in little endian
            int32_t offset = *(int16_t*)&code[pc + 2];
            // store half word (2 bytes)
            memory.write16 (address + offset, registers.get<uint16_t>(src1));
            break;
        }
        case Opcode::STORE32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers.get<uint64_t>(dest);
            // read offset in little endian
            int32_t offset = *(int16_t*)&code[pc + 2];
            // store word (4 bytes)
            memory.write32 (address + offset, registers.get<uint32_t>(src1));
            break;
        }
        case Opcode::STORE64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t address = registers.get<uint64_t>(dest);
            // read offset in little endian
            int32_t offset = *(int16_t*)&code[pc + 2];
            // store double word (8 bytes)
            memory.write64 (address + offset, registers.get<uint64_t>(src1));
            break;
        }
        // ========================================================================================
        // Integer Arithmetic Instructions
        // ========================================================================================
        case Opcode::ADD32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            int32_t a = registers.get<int32_t>(src1);
            int32_t b = registers.get<int32_t>(src2);
            // Perform instruction
            int32_t c = a + b;
            // Write to register
            registers.set<int32_t>(dest, c);
            break;
        }
        case Opcode::ADD64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            int64_t a = registers.get<int64_t>(src1);
            int64_t b = registers.get<int64_t>(src2);
            // Perform instruction
            int64_t c = a + b;
            // Write to register
            registers.set<int64_t>(dest, c);
            break;
        }
        case Opcode::SUB32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            int32_t a = registers.get<int32_t>(src1);
            int32_t b = registers.get<int32_t>(src2);
            // Perform instruction
            int32_t c = a - b;
            // Write to register
            registers.set<int32_t>(dest, c);
            break;
        }
        case Opcode::SUB64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            int64_t a = registers.get<int64_t>(src1);
            int64_t b = registers.get<int64_t>(src2);
            // Perform instruction
            int64_t c = a - b;
            // Write to register
            registers.set<int64_t>(dest, c);
            break;
        }
        case Opcode::MUL32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            int32_t a = registers.get<int32_t>(src1);
            int32_t b = registers.get<int32_t>(src2);
            // Perform instruction
            int32_t c = a * b;
            // Write to register
            registers.set<int32_t>(dest, c);
            break;
        }
        case Opcode::MUL64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            int64_t a = registers.get<int64_t>(src1);
            int64_t b = registers.get<int64_t>(src2);
            // Perform instruction
            int64_t c = a * b;
            // Write to register
            registers.set<int64_t>(dest, c);
            break;
        }
        case Opcode::DIVI32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            int32_t a = registers.get<int32_t>(src1);
            int32_t b = registers.get<int32_t>(src2);
            // Perform instruction
            int32_t c = a / b;
            // Write to register
            registers.set<int32_t>(dest, c);
            break;
        }
        case Opcode::DIVI64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            int64_t a = registers.get<int64_t>(src1);
            int64_t b = registers.get<int64_t>(src2);
            // Perform instruction
            int64_t c = a / b;
            // Write to register
            registers.set<int64_t>(dest, c);
            break;
        }
        case Opcode::DIVU32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            uint32_t a = registers.get<uint32_t>(src1);
            uint32_t b = registers.get<uint32_t>(src2);
            // Perform instruction
            uint32_t c = a / b;
            // Write to register
            registers.set<uint32_t>(dest, c);
            break;
        }
        case Opcode::DIVU64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            uint64_t a = registers.get<uint64_t>(src1);
            uint64_t b = registers.get<uint64_t>(src2);
            // Perform instruction
            uint64_t c = a / b;
            // Write to register
            registers.set<uint64_t>(dest, c);
            break;
        }
        case Opcode::MODI32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            int32_t a = registers.get<int32_t>(src1);
            int32_t b = registers.get<int32_t>(src2);
            // Perform instruction
            int32_t c = a % b;
            // Write to register
            registers.set<int32_t>(dest, c);
            break;
        }
        case Opcode::MODI64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            int64_t a = registers.get<int64_t>(src1);
            int64_t b = registers.get<int64_t>(src2);
            // Perform instruction
            int64_t c = a % b;
            // Write to register
            registers.set<int64_t>(dest, c);
            break;
        }
        case Opcode::MODU32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            uint32_t a = registers.get<uint32_t>(src1);
            uint32_t b = registers.get<uint32_t>(src2);
            // Perform instruction
            uint32_t c = a % b;
            // Write to register
            registers.set<uint32_t>(dest, c);
            break;
        }
        case Opcode::MODU64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            uint64_t a = registers.get<uint64_t>(src1);
            uint64_t b = registers.get<uint64_t>(src2);
            // Perform instruction
            uint64_t c = a % b;
            // Write to register
            registers.set<uint64_t>(dest, c);
            break;
        }
        // ========================================================================================
        // Integer Arithmetic Instructions with Immediates
        // ========================================================================================
        case Opcode::ADD32I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int32_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int32_t a = registers.get<int32_t>(src1);
            // Perform instruction
            int32_t c = a + imm;
            // Write to register
            registers.set<int32_t>(dest, c);
            break;
        }
        case Opcode::ADD64I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int64_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int64_t a = registers.get<int64_t>(src1);
            // Perform instruction
            int64_t c = a + imm;
            // Write to register
            registers.set<int64_t>(dest, c);
            break;
        }
        case Opcode::SUB32I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int32_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int32_t a = registers.get<int32_t>(src1);
            // Perform instruction
            int32_t c = a - imm;
            // Write to register
            registers.set<int32_t>(dest, c);
            break;
        }
        case Opcode::SUB64I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int64_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int64_t a = registers.get<int64_t>(src1);
            // Perform instruction
            int64_t c = a - imm;
            // Write to register
            registers.set<int64_t>(dest, c);
            break;
        }
        case Opcode::MUL32I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int32_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int32_t a = registers.get<int32_t>(src1);
            // Perform instruction
            int32_t c = a * imm;
            // Write to register
            registers.set<int32_t>(dest, c);
            break;
        }
        case Opcode::MUL64I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int64_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int64_t a = registers.get<int64_t>(src1);
            // Perform instruction
            int64_t c = a * imm;
            // Write to register
            registers.set<int64_t>(dest, c);
            break;
        }
        case Opcode::DIVI32I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int32_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int32_t a = registers.get<int32_t>(src1);
            // Perform instruction
            int32_t c = a / imm;
            // Write to register
            registers.set<int32_t>(dest, c);
            break;
        }
        case Opcode::DIVI64I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int64_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int64_t a = registers.get<int64_t>(src1);
            // Perform instruction
            int64_t c = a / imm;
            // Write to register
            registers.set<int64_t>(dest, c);
            break;
        }
        case Opcode::DIVU32I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint32_t imm   = *(uint16_t*)&code[pc+2];
            // Read from registers
            uint32_t a = registers.get<uint32_t>(src1);
            // Perform instruction
            uint32_t c = a / imm;
            // Write to register
            registers.set<uint32_t>(dest, c);
            break;
        }
        case Opcode::DIVU64I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t imm   = *(uint16_t*)&code[pc+2];
            // Read from registers
            uint64_t a = registers.get<uint64_t>(src1);
            // Perform instruction
            uint64_t c = a / imm;
            // Write to register
            registers.set<uint64_t>(dest, c);
            break;
        }
        case Opcode::MODI32I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int32_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int32_t a = registers.get<int32_t>(src1);
            // Perform instruction
            int32_t c = a % imm;
            // Write to register
            registers.set<int32_t>(dest, c);
            break;
        }
        case Opcode::MODI64I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int64_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int64_t a = registers.get<int64_t>(src1);
            // Perform instruction
            int64_t c = a % imm;
            // Write to register
            registers.set<int64_t>(dest, c);
            break;
        }
        case Opcode::MODU32I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint32_t imm   = *(uint16_t*)&code[pc+2];
            // Read from registers
            uint32_t a = registers.get<uint32_t>(src1);
            // Perform instruction
            uint32_t c = a % imm;
            // Write to register
            registers.set<uint32_t>(dest, c);
            break;
        }
        case Opcode::MODU64I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t imm   = *(uint16_t*)&code[pc+2];
            // Read from registers
            uint64_t a = registers.get<uint64_t>(src1);
            // Perform instruction
            uint64_t c = a % imm;
            // Write to register
            registers.set<uint64_t>(dest, c);
            break;
        }
        // ========================================================================================
        // Floating Point Arithmetic Instructions
        // ========================================================================================
        case Opcode::ADDF32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            float a = registers.get<float>(src1);
            float b = registers.get<float>(src2);
            // Perform instruction
            float c = a + b;
            // Write to register
            registers.set<float>(dest, c);
            break;
        }
        case Opcode::ADDF64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            double a = registers.get<double>(src1);
            double b = registers.get<double>(src2);
            // Perform instruction
            double c = a + b;
            // Write to register
            registers.set<double>(dest, c);
            break;
        }
        case Opcode::SUBF32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            float a = registers.get<float>(src1);
            float b = registers.get<float>(src2);
            // Perform instruction
            float c = a - b;
            // Write to register
            registers.set<float>(dest, c);
            break;
        }
        case Opcode::SUBF64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            double a = registers.get<double>(src1);
            double b = registers.get<double>(src2);
            // Perform instruction
            double c = a - b;
            // Write to register
            registers.set<double>(dest, c);
            break;
        }
        case Opcode::MULF32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            float a = registers.get<float>(src1);
            float b = registers.get<float>(src2);
            // Perform instruction
            float c = a * b;
            // Write to register
            registers.set<float>(dest, c);
            break;
        }
        case Opcode::MULF64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            double a = registers.get<double>(src1);
            double b = registers.get<double>(src2);
            // Perform instruction
            double c = a * b;
            // Write to register
            registers.set<double>(dest, c);
            break;
        }
        case Opcode::DIVF32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            float a = registers.get<float>(src1);
            float b = registers.get<float>(src2);
            // Perform instruction
            float c = a / b;
            // Write to register
            registers.set<float>(dest, c);
            break;
        }
        case Opcode::DIVF64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            double a = registers.get<double>(src1);
            double b = registers.get<double>(src2);
            // Perform instruction
            double c = a / b;
            // Write to register
            registers.set<double>(dest, c);
            break;
        }
        case Opcode::SQRTF32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            // Read from registers
            float a = registers.get<float>(src1);
            // Perform instruction
            float c = std::sqrt (a);
            // Write to register
            registers.set<float>(dest, c);
            break;
        }
        case Opcode::SQRTF64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            // Read from registers
            double a = registers.get<double>(src1);
            // Perform instruction
            double c = std::sqrt (a);
            // Write to register
            registers.set<double>(dest, c);
            break;
        }
        case Opcode::ABSF32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            // Read from registers
            float a = registers.get<float>(src1);
            // Perform instruction
            float c = std::fabs (a);
            // Write to register
            registers.set<float>(dest, c);
            break;
        }
        case Opcode::ABSF64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            // Read from registers
            double a = registers.get<double>(src1);
            // Perform instruction
            double c = std::fabs (a);
            // Write to register
            registers.set<double>(dest, c);
            break;
        }
        case Opcode::NEGF32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            // Read from registers
            float a = registers.get<float>(src1);
            // Perform instruction
            float c = -a;
            // Write to register
            registers.set<float>(dest, c);
            break;
        }
        case Opcode::NEGF64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            // Read from registers
            double a = registers.get<double>(src1);
            // Perform instruction
            double c = -a;
            // Write to register
            registers.set<double>(dest, c);
            break;
        }
        // ========================================================================================
        // Logical/Bitwise Instructions
        // ========================================================================================
        case Opcode::SLL32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            int32_t a = registers.get<int32_t>(src1);
            int32_t b = registers.get<int32_t>(src2);
            // Perform instruction
            int32_t c = a << b;
            // Write to register
            registers.set<int32_t>(dest, c);
            break;
        }
        case Opcode::SLL64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            int64_t a = registers.get<int64_t>(src1);
            int64_t b = registers.get<int64_t>(src2);
            // Perform instruction
            int64_t c = a << b;
            // Write to register
            registers.set<int64_t>(dest, c);
            break;
        }
        case Opcode::SRL32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            uint32_t a = registers.get<uint32_t>(src1);
            uint32_t b = registers.get<uint32_t>(src2);
            // Perform instruction
            uint32_t c = a >> b;
            // Write to register
            registers.set<uint32_t>(dest, c);
            break;
        }
        case Opcode::SRL64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            uint64_t a = registers.get<uint64_t>(src1);
            uint64_t b = registers.get<uint64_t>(src2);
            // Perform instruction
            uint64_t c = a >> b;
            // Write to register
            registers.set<uint64_t>(dest, c);
            break;
        }
        case Opcode::SRA32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            int32_t a = registers.get<int32_t>(src1);
            int32_t b = registers.get<int32_t>(src2);
            // Perform instruction
            int32_t c = a >> b;
            // Write to register
            registers.set<int32_t>(dest, c);
            break;
        }
        case Opcode::SRA64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            int64_t a = registers.get<int64_t>(src1);
            int64_t b = registers.get<int64_t>(src2);
            // Perform instruction
            int64_t c = a >> b;
            // Write to register
            registers.set<int64_t>(dest, c);
            break;
        }
        case Opcode::OR32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            uint32_t a = registers.get<uint32_t>(src1);
            uint32_t b = registers.get<uint32_t>(src2);
            // Perform instruction
            uint32_t c = a | b;
            // Write to register
            registers.set<uint32_t>(dest, c);
            break;
        }
        case Opcode::OR64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            uint64_t a = registers.get<uint64_t>(src1);
            uint64_t b = registers.get<uint64_t>(src2);
            // Perform instruction
            uint64_t c = a | b;
            // Write to register
            registers.set<uint64_t>(dest, c);
            break;
        }
        case Opcode::AND32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            uint32_t a = registers.get<uint32_t>(src1);
            uint32_t b = registers.get<uint32_t>(src2);
            // Perform instruction
            uint32_t c = a & b;
            // Write to register
            registers.set<uint32_t>(dest, c);
            break;
        }
        case Opcode::AND64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            uint64_t a = registers.get<uint64_t>(src1);
            uint64_t b = registers.get<uint64_t>(src2);
            // Perform instruction
            uint64_t c = a & b;
            // Write to register
            registers.set<uint64_t>(dest, c);
            break;
        }
        case Opcode::XOR32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            uint32_t a = registers.get<uint32_t>(src1);
            uint32_t b = registers.get<uint32_t>(src2);
            // Perform instruction
            uint32_t c = a ^ b;
            // Write to register
            registers.set<uint32_t>(dest, c);
            break;
        }
        case Opcode::XOR64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // Read from registers
            uint64_t a = registers.get<uint64_t>(src1);
            uint64_t b = registers.get<uint64_t>(src2);
            // Perform instruction
            uint64_t c = a ^ b;
            // Write to register
            registers.set<uint64_t>(dest, c);
            break;
        }
        case Opcode::NOT32: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            // Read from registers
            uint32_t a = registers.get<uint32_t>(src1);
            // Perform instruction
            uint32_t c = ~a;
            // Write to register
            registers.set<uint32_t>(dest, c);
            break;
        }
        case Opcode::NOT64: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            // Read from registers
            uint64_t a = registers.get<uint64_t>(src1);
            // Perform instruction
            uint64_t c = ~a;
            // Write to register
            registers.set<uint64_t>(dest, c);
            break;
        }
        // ========================================================================================
        // Logical/Bitwise Instructions with Immediates
        // ========================================================================================
        case Opcode::SLL32I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int32_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int32_t a = registers.get<int32_t>(src1);
            // Perform instruction
            int32_t c = a << imm;
            // Write to register
            registers.set<int32_t>(dest, c);
            break;
        }
        case Opcode::SLL64I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int64_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int64_t a = registers.get<int64_t>(src1);
            // Perform instruction
            int64_t c = a << imm;
            // Write to register
            registers.set<int64_t>(dest, c);
            break;
        }
        case Opcode::SRL32I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint32_t imm   = *(int16_t*)&code[pc+2];
            // Read from registers
            uint32_t a = registers.get<uint32_t>(src1);
            // Perform instruction
            uint32_t c = a >> imm;
            // Write to register
            registers.set<uint32_t>(dest, c);
            break;
        }
        case Opcode::SRL64I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint64_t imm   = *(int16_t*)&code[pc+2];
            // Read from registers
            uint64_t a = registers.get<uint64_t>(src1);
            // Perform instruction
            uint64_t c = a >> imm;
            // Write to register
            registers.set<uint64_t>(dest, c);
            break;
        }
        case Opcode::SRA32I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int32_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int32_t a = registers.get<int32_t>(src1);
            // Perform instruction
            int32_t c = a >> imm;
            // Write to register
            registers.set<int32_t>(dest, c);
            break;
        }
        case Opcode::SRA64I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int64_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int64_t a = registers.get<int64_t>(src1);
            // Perform instruction
            int64_t c = a >> imm;
            // Write to register
            registers.set<int64_t>(dest, c);
            break;
        }
        case Opcode::OR32I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int32_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int32_t a = registers.get<int32_t>(src1);
            // Perform instruction
            int32_t c = a | imm;
            // Write to register
            registers.set<int32_t>(dest, c);
            break;
        }
        case Opcode::OR64I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int64_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int64_t a = registers.get<int64_t>(src1);
            // Perform instruction
            int64_t c = a | imm;
            // Write to register
            registers.set<int64_t>(dest, c);
            break;
        }
        case Opcode::AND32I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int32_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int32_t a = registers.get<int32_t>(src1);
            // Perform instruction
            int32_t c = a & imm;
            // Write to register
            registers.set<int32_t>(dest, c);
            break;
        }
        case Opcode::AND64I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int64_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int64_t a = registers.get<int64_t>(src1);
            // Perform instruction
            int64_t c = a & imm;
            // Write to register
            registers.set<int64_t>(dest, c);
            break;
        }
        case Opcode::XOR32I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int32_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int32_t a = registers.get<int32_t>(src1);
            // Perform instruction
            int32_t c = a ^ imm;
            // Write to register
            registers.set<int32_t>(dest, c);
            break;
        }
        case Opcode::XOR64I: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int64_t imm    = *(int16_t*)&code[pc+2];
            // Read from registers
            int64_t a = registers.get<int64_t>(src1);
            // Perform instruction
            int64_t c = a ^ imm;
            // Write to register
            registers.set<int64_t>(dest, c);
            break;
        }
        // ========================================================================================
        // Control Flow / Branching Instructions
        // ========================================================================================
        case Opcode::BEQ: {
            uint8_t src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src2   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t addr   = (0b00000000000000001111000000000000 & instruction) >> 12;
            if (registers.get<uint32_t>(src1) == registers.get<uint32_t>(src2))
                pc = registers.get<uint64_t>(addr) - 4;
            break;
        }
        case Opcode::BNE: {
            uint8_t src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src2   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t addr   = (0b00000000000000001111000000000000 & instruction) >> 12;
            if (registers.get<uint32_t>(src1) != registers.get<uint32_t>(src2))
                pc = registers.get<uint64_t>(addr) - 4;
            break;
        }
        case Opcode::BLT: {
            uint8_t src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src2   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t addr   = (0b00000000000000001111000000000000 & instruction) >> 12;
            if (registers.get<uint32_t>(src1) < registers.get<uint32_t>(src2))
                pc = registers.get<uint64_t>(addr) - 4;
            break;
        }
        case Opcode::BLE: {
            uint8_t src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src2   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t addr   = (0b00000000000000001111000000000000 & instruction) >> 12;
            if (registers.get<uint32_t>(src1) <= registers.get<uint32_t>(src2))
                pc = registers.get<uint64_t>(addr) - 4;
            break;
        }
        case Opcode::BGT: {
            uint8_t src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src2   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t addr   = (0b00000000000000001111000000000000 & instruction) >> 12;
            if (registers.get<uint32_t>(src1) > registers.get<uint32_t>(src2))
                pc = registers.get<uint64_t>(addr) - 4;
            break;
        }
        case Opcode::BGE: {
            uint8_t src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            uint8_t src2   = (0b00000000000011110000000000000000 & instruction) >> 16;
            uint8_t addr   = (0b00000000000000001111000000000000 & instruction) >> 12;
            if (registers.get<uint32_t>(src1) >= registers.get<uint32_t>(src2))
                pc = registers.get<uint64_t>(addr) - 4;
            break;
        }
        case Opcode::JMP: {
            uint8_t addr   = (0b00000000111100000000000000000000 & instruction) >> 20;
            pc = registers.get<uint64_t>(addr) - 4;
            break;
        }
        // ========================================================================================
        // Function Instructions
        // ========================================================================================
        case Opcode::CALL: {
            uint8_t addr   = (0b00000000111100000000000000000000 & instruction) >> 20;
            // push return address onto stack 
            registers.set<uint64_t>(sp, registers.get<uint64_t>(sp) - 8); // stack grows towards 0
            memory.write64 (registers.get<uint64_t>(sp), pc);
            // change program counter to addr
            // -4 to point to the previous instruction since VM will increment later
            pc = registers.get<uint64_t>(addr) - 4;
            break;
        }
        case Opcode::SYSCALL: {
            std::cout << "Error: Opcode::SYSCALL not yet implemented" << std::endl;
            break;
        }
        case Opcode::RET: {
            // pop return address from stack into 
            pc = memory.read64 (registers.get<uint64_t>(sp));
            registers.set<uint64_t>(sp, registers.get<uint64_t>(sp) + 8); // stack shrinks towards MEM_SIZE
            break;
        }
        case Opcode::PUSH: {
            uint8_t src    = (0b00000000111100000000000000000000 & instruction) >> 20;
            registers.set<uint64_t>(sp, registers.get<uint64_t>(sp) - 8); // stack grows towards 0
            memory.write64 (registers.get<uint64_t>(sp), registers.get<uint64_t>(src));
            break;
        }
        case Opcode::POP: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            registers.set<uint64_t>(dest, memory.read64 (registers.get<uint64_t>(sp))); 
            registers.set<uint64_t>(sp, registers.get<uint64_t>(sp) + 8); // stack shrinks towards MEM_SIZE
            break;
        }
        // ========================================================================================
        // Other Instructions
        // ========================================================================================
        case Opcode::NOP: {
            // Do nothing
            break;
        }
        case Opcode::HALT: {
            pc = code.size ();
            break;
        }
        case Opcode::GETCHAR: {
            uint8_t dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            registers.set<uint8_t>(dest, getchar ());
            break;
        }
        case Opcode::PUTCHAR: {
            uint8_t src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            if (debug) printf ("Output = '");
            // Using std::cout so unit tests can capture output
            std::cout << registers.get<uint8_t>(src1);
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
    // switch (sym_id) {
    //     case SYSCALL_PUTS: {
    //         const char* str = reinterpret_cast<const char*> (registers.get<uint64_t>(0));
    //         puts(str);
    //         break;
    //     }
    //     default:
    //         std::cerr << "Unknown syscall: " << static_cast<int32_t> (sym_id) << "\n";
    //         break;
    // }
}
