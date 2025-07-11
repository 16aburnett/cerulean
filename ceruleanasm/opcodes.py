
INSTRUCTION_MAPPING = {
    "INVALID"   : {"opcode": 0x00, "format": "NONE"},

    "LUI"       : {"opcode": 0x01, "format": "RI"  },
    "LLI"       : {"opcode": 0x02, "format": "RI"  },
    "LOAD8"     : {"opcode": 0x03, "format": "RRI" },
    "LOAD16"    : {"opcode": 0x04, "format": "RRI" },
    "LOAD32"    : {"opcode": 0x05, "format": "RRI" },
    "LOAD64"    : {"opcode": 0x06, "format": "RRI" },
    "STORE8"    : {"opcode": 0x07, "format": "RRI" },
    "STORE16"   : {"opcode": 0x08, "format": "RRI" },
    "STORE32"   : {"opcode": 0x09, "format": "RRI" },
    "STORE64"   : {"opcode": 0x0a, "format": "RRI" },

    "ADD32"     : {"opcode": 0x10, "format": "RRR" },
    "ADD64"     : {"opcode": 0x11, "format": "RRR" },
    "SUB32"     : {"opcode": 0x12, "format": "RRR" },
    "SUB64"     : {"opcode": 0x13, "format": "RRR" },
    "MUL32"     : {"opcode": 0x14, "format": "RRR" },
    "MUL64"     : {"opcode": 0x15, "format": "RRR" },
    "DIVI32"    : {"opcode": 0x16, "format": "RRR" },
    "DIVI64"    : {"opcode": 0x17, "format": "RRR" },
    "DIVU32"    : {"opcode": 0x18, "format": "RRR" },
    "DIVU64"    : {"opcode": 0x19, "format": "RRR" },
    "MODI32"    : {"opcode": 0x1a, "format": "RRR" },
    "MODI64"    : {"opcode": 0x1b, "format": "RRR" },
    "MODU32"    : {"opcode": 0x1c, "format": "RRR" },
    "MODU64"    : {"opcode": 0x1d, "format": "RRR" },

    "ADD32I"    : {"opcode": 0x20, "format": "RRI" },
    "ADD64I"    : {"opcode": 0x21, "format": "RRI" },
    "SUB32I"    : {"opcode": 0x22, "format": "RRI" },
    "SUB64I"    : {"opcode": 0x23, "format": "RRI" },
    "MUL32I"    : {"opcode": 0x24, "format": "RRI" },
    "MUL64I"    : {"opcode": 0x25, "format": "RRI" },
    "DIVI32I"   : {"opcode": 0x26, "format": "RRI" },
    "DIVI64I"   : {"opcode": 0x27, "format": "RRI" },
    "DIVU32I"   : {"opcode": 0x28, "format": "RRI" },
    "DIVU64I"   : {"opcode": 0x29, "format": "RRI" },
    "MODI32I"   : {"opcode": 0x2a, "format": "RRI" },
    "MODI64I"   : {"opcode": 0x2b, "format": "RRI" },
    "MODU32I"   : {"opcode": 0x2c, "format": "RRI" },
    "MODU64I"   : {"opcode": 0x2d, "format": "RRI" },

    "ADDF32"    : {"opcode": 0x30, "format": "RRR" },
    "ADDF64"    : {"opcode": 0x31, "format": "RRR" },
    "SUBF32"    : {"opcode": 0x32, "format": "RRR" },
    "SUBF64"    : {"opcode": 0x33, "format": "RRR" },
    "MULF32"    : {"opcode": 0x34, "format": "RRR" },
    "MULF64"    : {"opcode": 0x35, "format": "RRR" },
    "DIVF32"    : {"opcode": 0x36, "format": "RRR" },
    "DIVF64"    : {"opcode": 0x37, "format": "RRR" },
    "SQRTF32"   : {"opcode": 0x38, "format": "RRR" },
    "SQRTF64"   : {"opcode": 0x39, "format": "RRR" },
    "ABSF32"    : {"opcode": 0x3a, "format": "RRR" },
    "ABSF64"    : {"opcode": 0x3b, "format": "RRR" },
    "NEGF32"    : {"opcode": 0x3c, "format": "RRR" },
    "NEGF64"    : {"opcode": 0x3d, "format": "RRR" },

    "CVTI32I64" : {"opcode": 0x40, "format": "RR"  },
    "CVTI64I32" : {"opcode": 0x41, "format": "RR"  },
    "CVTU32U64" : {"opcode": 0x42, "format": "RR"  },
    "CVTU64U32" : {"opcode": 0x43, "format": "RR"  },
    "CVTF32I32" : {"opcode": 0x44, "format": "RR"  },
    "CVTI32F32" : {"opcode": 0x45, "format": "RR"  },
    "CVTF64I64" : {"opcode": 0x46, "format": "RR"  },
    "CVTI64F64" : {"opcode": 0x47, "format": "RR"  },
    "CVTF32U32" : {"opcode": 0x48, "format": "RR"  },
    "CVTU32F32" : {"opcode": 0x49, "format": "RR"  },
    "CVTF64U64" : {"opcode": 0x4a, "format": "RR"  },
    "CVTU64F64" : {"opcode": 0x4b, "format": "RR"  },
    "CVTF32F64" : {"opcode": 0x4c, "format": "RR"  },
    "CVTF64F32" : {"opcode": 0x4d, "format": "RR"  },

    "SLL32"     : {"opcode": 0x50, "format": "RRR" },
    "SLL64"     : {"opcode": 0x51, "format": "RRR" },
    "SRL32"     : {"opcode": 0x52, "format": "RRR" },
    "SRL64"     : {"opcode": 0x53, "format": "RRR" },
    "SRA32"     : {"opcode": 0x54, "format": "RRR" },
    "SRA64"     : {"opcode": 0x55, "format": "RRR" },
    "OR32"      : {"opcode": 0x56, "format": "RRR" },
    "OR64"      : {"opcode": 0x57, "format": "RRR" },
    "AND32"     : {"opcode": 0x58, "format": "RRR" },
    "AND64"     : {"opcode": 0x59, "format": "RRR" },
    "XOR32"     : {"opcode": 0x5a, "format": "RRR" },
    "XOR64"     : {"opcode": 0x5b, "format": "RRR" },
    "NOT32"     : {"opcode": 0x5c, "format": "RR"  },
    "NOT64"     : {"opcode": 0x5d, "format": "RR"  },

    "SLL32I"    : {"opcode": 0x60, "format": "RRI" },
    "SLL64I"    : {"opcode": 0x61, "format": "RRI" },
    "SRL32I"    : {"opcode": 0x62, "format": "RRI" },
    "SRL64I"    : {"opcode": 0x63, "format": "RRI" },
    "SRA32I"    : {"opcode": 0x64, "format": "RRI" },
    "SRA64I"    : {"opcode": 0x65, "format": "RRI" },
    "OR32I"     : {"opcode": 0x66, "format": "RRI" },
    "OR64I"     : {"opcode": 0x67, "format": "RRI" },
    "AND32I"    : {"opcode": 0x68, "format": "RRI" },
    "AND64I"    : {"opcode": 0x69, "format": "RRI" },
    "XOR32I"    : {"opcode": 0x6a, "format": "RRI" },
    "XOR64I"    : {"opcode": 0x6b, "format": "RRI" },

    "BEQ"       : {"opcode": 0x70, "format": "RRR" },
    "BNE"       : {"opcode": 0x71, "format": "RRR" },
    "BLT"       : {"opcode": 0x72, "format": "RRR" },
    "BLE"       : {"opcode": 0x73, "format": "RRR" },
    "BGT"       : {"opcode": 0x74, "format": "RRR" },
    "BGE"       : {"opcode": 0x75, "format": "RRR" },
    "JMP"       : {"opcode": 0x76, "format": "R"   },

    "CALL"      : {"opcode": 0x80, "format": "R"   },
    "SYSCALL"   : {"opcode": 0x81, "format": "I"   },
    "RET"       : {"opcode": 0x82, "format": "NONE"},
    "PUSH"      : {"opcode": 0x83, "format": "R"   },
    "POP"       : {"opcode": 0x84, "format": "R"   },

    "NOP"       : {"opcode": 0x90, "format": "NONE"},
    "HALT"      : {"opcode": 0x91, "format": "NONE"},
    "GETCHAR"   : {"opcode": 0x92, "format": "R"   },
    "PUTCHAR"   : {"opcode": 0x93, "format": "R"   },
}
