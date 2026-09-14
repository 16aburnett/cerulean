#include <ios>
#include <iomanip>
#include "disassembler.hpp"
#include "instruction_registry.hpp" // Your opcode metadata

// Stores a mapping of Register IDs/Indices to the human-readable names
// NOTE: This should probably be moved elsewhere
const std::vector<std::string> regIDToString = {
    "r0",  "r1",  "r2",  "r3",  "r4",  "r5",  "r6",  "r7",
    "r8",  "r9",  "r10", "r11", "r12", "r13", "r14", "r15",
    "r16", "r17", "r18", "r19", "r20", "r21", "r22", "r23",
    "r24", "r25", "r26", "r27", "r28", "ra",  "bp",  "sp"
};

std::string disassemble (const std::vector<uint8_t>& bytes) {
    if (bytes.size() < 4) return "???";

    Opcode opcode = static_cast<Opcode>(bytes[0]);
    const InstructionInfo* info = getInstructionInfo(opcode);
    if (!info) return "???";

    uint32_t word = (static_cast<uint32_t>(bytes[0]) << 24) |
                    (static_cast<uint32_t>(bytes[1]) << 16) |
                    (static_cast<uint32_t>(bytes[2]) << 8)  |
                     static_cast<uint32_t>(bytes[3]);

    std::ostringstream oss;
    oss << std::hex;
    oss << info->mnemonic << " ";

    std::string type = info->operandTypes;

    if (type == "R")
    {
        uint8_t reg = (word >> 19) & 0x1F;
        oss << regIDToString[reg];
    }
    else if (type == "I")
    {
        uint16_t imm = word & 0xFFFF;
        oss << "0x" << static_cast<int>(imm);
    }
    else if (type == "RR")
    {
        uint8_t reg0 = (word >> 19) & 0x1F;
        uint8_t reg1 = (word >> 14) & 0x1F;
        oss << regIDToString[reg0] << ", ";
        oss << regIDToString[reg1];
    }
    else if (type == "RI")
    {
        uint8_t reg0 = (word >> 19) & 0x1F;
        uint16_t imm = word & 0xFFFF;
        oss << regIDToString[reg0] << ", ";
        oss << "0x" << static_cast<int>(imm);
    }
    else if (type == "RRR")
    {
        uint8_t reg0 = (word >> 19) & 0x1F;
        uint8_t reg1 = (word >> 14) & 0x1F;
        uint8_t reg2 = (word >> 9) & 0x1F;
        oss << regIDToString[reg0] << ", ";
        oss << regIDToString[reg1] << ", ";
        oss << regIDToString[reg2];
    }
    else if (type == "RRI")
    {
        uint8_t reg0 = (word >> 19) & 0x1F;
        uint8_t reg1 = (word >> 14) & 0x1F;
        uint16_t raw_imm = word & 0x3FFF;
        int16_t imm = (raw_imm & 0x2000) ? static_cast<int16_t>(raw_imm | 0xC000) : static_cast<int16_t>(raw_imm);
        oss << regIDToString[reg0] << ", ";
        oss << regIDToString[reg1] << ", ";
        oss << "0x" << static_cast<int>(imm);
    }

    return oss.str();
}
