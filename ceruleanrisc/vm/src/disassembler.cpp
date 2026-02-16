#include <ios>
#include <iomanip>
#include "disassembler.hpp"
#include "instruction_registry.hpp" // Your opcode metadata

// Stores a mapping of Register IDs/Indices to the human-readable names
// NOTE: This should probably be moved elsewhere
const std::vector<std::string> regIDToString = {
    "r0",
    "r1",
    "r2",
    "r3",
    "r4",
    "r5",
    "r6",
    "r7",
    "r8",
    "r9",
    "r10",
    "r11",
    "r12",
    "ra",
    "bp",
    "sp",
};

std::string disassemble (const std::vector<uint8_t>& bytes) {
    if (bytes.empty ()) return "???";

    Opcode opcode = static_cast<Opcode>(bytes[0]);
    const InstructionInfo* info = getInstructionInfo(opcode);
    if (!info) return "???";

    std::ostringstream oss;
    oss << std::hex;
    oss << info->mnemonic << " ";

    std::string type = info->operandTypes;

    if (type == "R")
    {
        // oooooooo rrrr0000 00000000 00000000
        uint8_t reg = (bytes[1] >> 4) & 0x0F;
        oss << regIDToString[reg];
    }
    else if (type == "I")
    {
        // oooooooo 00000000 iiiiiiii iiiiiiii
        uint16_t imm = (static_cast<uint16_t>(bytes[3]) << 8) |
                static_cast<uint16_t>(bytes[2]);
        oss << "0x" << static_cast<int>(imm);
    }
    else if (type == "RR")
    {
        // oooooooo rrrrrrrr 00000000 00000000
        uint8_t reg0 = (bytes[1] >> 4) & 0x0F;
        uint8_t reg1 = (bytes[1] >> 0) & 0x0F;
        oss << regIDToString[reg0] << ", ";
        oss << regIDToString[reg1];
    }
    else if (type == "RI")
    {
        // oooooooo rrrr0000 iiiiiiii iiiiiiii
        uint8_t reg0 = (bytes[1] >> 4) & 0x0F;
        uint16_t imm = (static_cast<uint16_t>(bytes[3]) << 8) |
                static_cast<uint16_t>(bytes[2]);
        oss << regIDToString[reg0] << ", ";
        oss << "0x" << static_cast<int>(imm);
    }
    else if (type == "RRR")
    {
        // oooooooo rrrrrrrr rrrr0000 00000000
        uint8_t reg0 = (bytes[1] >> 4) & 0x0F;
        uint8_t reg1 = (bytes[1] >> 0) & 0x0F;
        uint8_t reg2 = (bytes[2] >> 4) & 0x0F;
        oss << regIDToString[reg0] << ", ";
        oss << regIDToString[reg1] << ", ";
        oss << regIDToString[reg2];
    }
    else if (type == "RRI")
    {
        // oooooooo rrrrrrrr iiiiiiii iiiiiiii
        uint8_t reg0 = (bytes[1] >> 4) & 0x0F;
        uint8_t reg1 = (bytes[1] >> 0) & 0x0F;
        uint16_t imm = (static_cast<uint16_t>(bytes[3]) << 8) |
                static_cast<uint16_t>(bytes[2]);
        oss << regIDToString[reg0] << ", ";
        oss << regIDToString[reg1] << ", ";
        oss << "0x" << static_cast<int>(imm);
    }

    return oss.str();
}
