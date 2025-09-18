#pragma once
#include <string>
#include <vector>
#include "opcode.hpp"

struct InstructionInfo {
    // The name of the instruction (ADD, MOV, PUSH, CALL, etc)
    std::string mnemonic;
    // A string encoding of the operand types ("", "RR", "RRI", etc)
    // 'R' - register
    // 'I' - immediate
    std::string operandTypes;
    // Human readable description for the instruction
    // For documentation
    std::string description;
};
