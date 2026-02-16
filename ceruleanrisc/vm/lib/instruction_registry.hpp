#pragma once
#include <unordered_map>
#include "instruction_info.hpp"
#include "opcode.hpp"

extern const std::unordered_map<Opcode, InstructionInfo> instructionRegistry;

const InstructionInfo* getInstructionInfo(Opcode opcode);