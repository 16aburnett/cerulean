#pragma once
#include <string>
#include <vector>
#include <cstdint>
#include "opcode.hpp"

// Disassembles the given instruction in bytes to a more human-readable ASM string
std::string disassemble(const std::vector<uint8_t>& bytes);
