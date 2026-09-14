#pragma once
#include <cstdint>
#include <vector>

inline std::vector<uint8_t> encodeRRR (uint8_t opcode, uint8_t r0, uint8_t r1, uint8_t r2) {
    uint32_t word = (static_cast<uint32_t>(opcode & 0xFF) << 24) |
                    (static_cast<uint32_t>(r0 & 0x1F) << 19) |
                    (static_cast<uint32_t>(r1 & 0x1F) << 14) |
                    (static_cast<uint32_t>(r2 & 0x1F) << 9);
    return {
        static_cast<uint8_t>((word >> 24) & 0xFF),
        static_cast<uint8_t>((word >> 16) & 0xFF),
        static_cast<uint8_t>((word >> 8) & 0xFF),
        static_cast<uint8_t>(word & 0xFF)
    };
}

inline std::vector<uint8_t> encodeRRI (uint8_t opcode, uint8_t r0, uint8_t r1, int16_t imm) {
    uint32_t word = (static_cast<uint32_t>(opcode & 0xFF) << 24) |
                    (static_cast<uint32_t>(r0 & 0x1F) << 19) |
                    (static_cast<uint32_t>(r1 & 0x1F) << 14) |
                    (static_cast<uint32_t>(imm) & 0x3FFF);
    return {
        static_cast<uint8_t>((word >> 24) & 0xFF),
        static_cast<uint8_t>((word >> 16) & 0xFF),
        static_cast<uint8_t>((word >> 8) & 0xFF),
        static_cast<uint8_t>(word & 0xFF)
    };
}

inline std::vector<uint8_t> encodeRR (uint8_t opcode, uint8_t r0, uint8_t r1) {
    uint32_t word = (static_cast<uint32_t>(opcode & 0xFF) << 24) |
                    (static_cast<uint32_t>(r0 & 0x1F) << 19) |
                    (static_cast<uint32_t>(r1 & 0x1F) << 14);
    return {
        static_cast<uint8_t>((word >> 24) & 0xFF),
        static_cast<uint8_t>((word >> 16) & 0xFF),
        static_cast<uint8_t>((word >> 8) & 0xFF),
        static_cast<uint8_t>(word & 0xFF)
    };
}

inline std::vector<uint8_t> encodeRI (uint8_t opcode, uint8_t r0, int16_t imm) {
    uint32_t word = (static_cast<uint32_t>(opcode & 0xFF) << 24) |
                    (static_cast<uint32_t>(r0 & 0x1F) << 19) |
                    ((static_cast<uint32_t>(imm) & 0xFFFF));
    return {
        static_cast<uint8_t>((word >> 24) & 0xFF),
        static_cast<uint8_t>((word >> 16) & 0xFF),
        static_cast<uint8_t>((word >> 8) & 0xFF),
        static_cast<uint8_t>(word & 0xFF)
    };
}

inline std::vector<uint8_t> encodeR (uint8_t opcode, uint8_t r0) {
    uint32_t word = (static_cast<uint32_t>(opcode & 0xFF) << 24) |
                    (static_cast<uint32_t>(r0 & 0x1F) << 19);
    return {
        static_cast<uint8_t>((word >> 24) & 0xFF),
        static_cast<uint8_t>((word >> 16) & 0xFF),
        static_cast<uint8_t>((word >> 8) & 0xFF),
        static_cast<uint8_t>(word & 0xFF)
    };
}

inline std::vector<uint8_t> encodeI (uint8_t opcode, uint16_t imm) {
    uint32_t word = (static_cast<uint32_t>(opcode & 0xFF) << 24) |
                    ((static_cast<uint32_t>(imm) & 0xFFFF));
    return {
        static_cast<uint8_t>((word >> 24) & 0xFF),
        static_cast<uint8_t>((word >> 16) & 0xFF),
        static_cast<uint8_t>((word >> 8) & 0xFF),
        static_cast<uint8_t>(word & 0xFF)
    };
}

inline std::vector<uint8_t> encodeNONE (uint8_t opcode) {
    uint32_t word = (static_cast<uint32_t>(opcode & 0xFF) << 24);
    return {
        static_cast<uint8_t>((word >> 24) & 0xFF),
        static_cast<uint8_t>((word >> 16) & 0xFF),
        static_cast<uint8_t>((word >> 8) & 0xFF),
        static_cast<uint8_t>(word & 0xFF)
    };
}

inline void pushInstr (std::vector<uint8_t>& code, const std::vector<uint8_t>& instr) {
    code.insert (code.end (), instr.begin (), instr.end ());
}
