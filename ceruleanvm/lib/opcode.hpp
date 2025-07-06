#pragma once

enum Opcode : const uint8_t {
    // ============================================================================================
    // Invalid Instruction - 0x00
    // This is a good sanity for if the control flow ends up in uninitialized memory
    INVALID = 0x00,

    // ============================================================================================
    // Memory Instructions - 0x01-0x10
    // LUI dest, imm        - loads upper immediate 16 bits into given register
    // XXXXXXXX dddd0000 iiiiiiii iiiiiiii
    LUI = 0x01,
    // LLI dest, imm        - loads lower immediate 16 bits into given register
    // XXXXXXXX dddd0000 iiiiiiii iiiiiiii
    LLI = 0x02,
    // LOAD8 dest, offset(src) - load 
    // XXXXXXXX ddddssss oooooooo oooooooo
    LOAD8 = 0x03,
    // LOAD16 dest, offset(src) - load half (2 bytes)
    // XXXXXXXX ddddssss oooooooo oooooooo
    LOAD16 = 0x04,
    // LOAD32 dest, offset(src) - load word (4 bytes)
    // XXXXXXXX ddddssss oooooooo oooooooo
    LOAD32 = 0x05,
    // LOAD64 dest, offset(src) - load double word (8 bytes)
    // XXXXXXXX ddddssss oooooooo oooooooo
    LOAD64 = 0x06,
    // STORE8 offset(dest), src - store byte
    // XXXXXXXX ddddssss oooooooo oooooooo
    STORE8 = 0x07,
    // STORE16 offset(dest), src - store half (2 bytes)
    // XXXXXXXX ddddssss oooooooo oooooooo
    STORE16 = 0x08,
    // STORE32 offset(dest), src - store word (4 bytes)
    // XXXXXXXX ddddssss oooooooo oooooooo
    STORE32 = 0x09,
    // STORE64 offset(dest), src - store double word (8 bytes)
    // XXXXXXXX ddddssss oooooooo oooooooo
    STORE64 = 0x0a,

    // ============================================================================================
    // Integer Arithmetic - 0x10-0x20
    // ADD32 dest, src1, src2 - integer addition (sign-agnostic 32-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    ADD32 = 0x10,
    // ADD64 dest, src1, src2 - integer addition (sign-agnostic 64-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    ADD64 = 0x11,
    // SUB32 dest, src1, src2 - integer subtraction (sign-agnostic 32-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    SUB32 = 0x12,
    // SUB64 dest, src1, src2 - integer subtraction (sign-agnostic 64-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    SUB64 = 0x13,
    // MUL32 dest, src1, src2 - integer multiplication (sign-agnostic 32-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    MUL32 = 0x14,
    // MUL64 dest, src1, src2 - integer multiplication (sign-agnostic 64-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    MUL64 = 0x15,
    // DIVI32 dest, src1, src2 - integer division (signed 32-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    DIVI32 = 0x16,
    // DIVI64 dest, src1, src2 - integer division (signed 64-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    DIVI64 = 0x17,
    // DIVU32 dest, src1, src2 - integer division (unsigned 32-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    DIVU32 = 0x18,
    // DIVU64 dest, src1, src2 - integer division (unsigned 64-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    DIVU64 = 0x19,
    // MODI32 dest, src1, src2 - integer division remainder (signed 32-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    MODI32 = 0x1a,
    // MODI64 dest, src1, src2 - integer division remainder (signed 64-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    MODI64 = 0x1b,
    // MODU32 dest, src1, src2 - integer division remainder (unsigned 32-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    MODU32 = 0x1c,
    // MODU64 dest, src1, src2 - integer division remainder (unsigned 64-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    MODU64 = 0x1d,

    // ============================================================================================
    // Integer arithmetic with immediates - 0x20-0x30
    // immediate values are 16-bit signed
    // ADD32I dest, src1, imm - integer addition with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    ADD32I = 0x20,
    // ADD64I dest, src1, imm - integer addition with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    ADD64I = 0x21,
    // SUB32I dest, src1, imm - integer subtraction with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    SUB32I = 0x22,
    // SUB64I dest, src1, imm - integer subtraction with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    SUB64I = 0x23,
    // MUL32I dest, src1, imm - integer multiplication with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    MUL32I = 0x24,
    // MUL64I dest, src1, imm - integer multiplication with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    MUL64I = 0x25,
    // DIVI32I dest, src1, imm - integer division with immediate (signed 32-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    DIVI32I = 0x26,
    // DIVI64I dest, src1, imm - integer division with immediate (signed 64-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    DIVI64I = 0x27,
    // DIVU32I dest, src1, imm - integer division with immediate (unsigned 32-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    DIVU32I = 0x28,
    // DIVU64I dest, src1, imm - integer division with immediate (unsigned 64-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    DIVU64I = 0x29,
    // MODI32I dest, src1, imm - integer division remainder with immediate (signed 32-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    MODI32I = 0x2a,
    // MODI64I dest, src1, imm - integer division remainder with immediate (signed 64-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    MODI64I = 0x2b,
    // MODU32I dest, src1, imm - integer division remainder with immediate (unsigned 32-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    MODU32I = 0x2c,
    // MODU64I dest, src1, imm - integer division remainder with immediate (unsigned 64-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    MODU64I = 0x2d,

    // ============================================================================================
    // Floating Point Arithmetic Instructions - 0x30-0x40
    // ADDF32 dest, src1 - floating point add - single 32bit precision
    // XXXXXXXX ddddssss ssss0000 00000000
    ADDF32 = 0x30,
    // ADDF64 dest, src1, src2 - floating point add - double 64bit precision
    // XXXXXXXX ddddssss ssss0000 00000000
    ADDF64 = 0x31,
    // SUBF32 dest, src1, src2 - floating point sub - single 32bit precision
    // XXXXXXXX ddddssss ssss0000 00000000
    SUBF32 = 0x32,
    // SUBF64 dest, src1, src2 - floating point sub - double 64bit precision
    // XXXXXXXX ddddssss ssss0000 00000000
    SUBF64 = 0x33,
    // MULF32 dest, src1, src2 - floating point mul - single 32bit precision
    // XXXXXXXX ddddssss ssss0000 00000000
    MULF32 = 0x34,
    // MULF64 dest, src1, src2 - floating point mul - double 64bit precision
    // XXXXXXXX ddddssss ssss0000 00000000
    MULF64 = 0x35,
    // DIVF32 dest, src1, src2 - floating point div - single 32bit precision
    // XXXXXXXX ddddssss ssss0000 00000000
    DIVF32 = 0x36,
    // DIVF64 dest, src1, src2 - floating point div - double 64bit precision
    // XXXXXXXX ddddssss ssss0000 00000000
    DIVF64 = 0x37,
    // SQRTF32 dest, src1 - floating point sqrt - single 32bit precision
    // XXXXXXXX ddddssss 00000000 00000000
    SQRTF32 = 0x38,
    // SQRTF64 dest, src1 - floating point sqrt - double 64bit precision
    // XXXXXXXX ddddssss 00000000 00000000
    SQRTF64 = 0x39,
    // ABSF32 dest, src1 - floating point abs - single 32bit precision
    // XXXXXXXX ddddssss 00000000 00000000
    ABSF32 = 0x3a,
    // ABSF64 dest, src1 - floating point abs - double 64bit precision
    // XXXXXXXX ddddssss 00000000 00000000
    ABSF64 = 0x3b,
    // NEGF32 dest, src1 - floating point neg - single 32bit precision
    // XXXXXXXX ddddssss 00000000 00000000
    NEGF32 = 0x3c,
    // NEGF64 dest, src1 - floating point neg - double 64bit precision
    // XXXXXXXX ddddssss 00000000 00000000
    NEGF64 = 0x3d,

    // ============================================================================================
    // Type Conversion - 0x40-0x50
    // Int-Int Conversions
    // CVTI32I64 dest, src1 - convert int32 to int64
    // XXXXXXXX ddddssss 00000000 00000000
    CVTI32I64 = 0x40,
    // CVTI64I32 dest, src1 - convert int64 to int32
    // XXXXXXXX ddddssss 00000000 00000000
    CVTI64I32 = 0x41,
    // Uint-Uint Conversions
    // CVTU32U64 dest, src1 - convert uint32 to uint64
    // XXXXXXXX ddddssss 00000000 00000000
    CVTU32U64 = 0x42,
    // CVTU64U32 dest, src1 - convert uint64 to uint32
    // XXXXXXXX ddddssss 00000000 00000000
    CVTU64U32 = 0x43,
    // Int-Float Conversions
    // CVTF32I32 dest, src1 - convert float32 to int32
    // XXXXXXXX ddddssss 00000000 00000000
    CVTF32I32 = 0x44,
    // CVTI32F32 dest, src1 - convert int32 to float32
    // XXXXXXXX ddddssss 00000000 00000000
    CVTI32F32 = 0x45,
    // CVTF64I64 dest, src1 - convert float64 to int64
    // XXXXXXXX ddddssss 00000000 00000000
    CVTF64I64 = 0x46,
    // CVTI64F64 dest, src1 - convert int64 to float64
    // XXXXXXXX ddddssss 00000000 00000000
    CVTI64F64 = 0x47,
    // CVTF32U32 dest, src1 - convert float32 to uint32
    // XXXXXXXX ddddssss 00000000 00000000
    CVTF32U32 = 0x48,
    // CVTU32F32 dest, src1 - convert uint32 to float32
    // XXXXXXXX ddddssss 00000000 00000000
    CVTU32F32 = 0x49,
    // CVTF64U64 dest, src1 - convert float64 to uint64
    // XXXXXXXX ddddssss 00000000 00000000
    CVTF64U64 = 0x4a,
    // CVTU64F64 dest, src1 - convert uint64 to float64
    // XXXXXXXX ddddssss 00000000 00000000
    CVTU64F64 = 0x4b,
    // Float-Float Conversions
    // CVTF32F64 dest, src1 - convert float32 to float64
    // XXXXXXXX ddddssss 00000000 00000000
    CVTF32F64 = 0x4c,
    // CVTF64F32 dest, src1 - convert float64 to float32
    // XXXXXXXX ddddssss 00000000 00000000
    CVTF64F32 = 0x4d,

    // ============================================================================================
    // Logical/Bitwise Instructions - 0x50-0x60
    // SLL32 dest, src1, src2 - shift left logical (32-bit)
    // NOTE: it is undefined behavior if rhs is outside [0,31]
    // XXXXXXXX ddddssss ssss0000 00000000
    SLL32 = 0x50,
    // SLL64 dest, src1, src2 - shift left logical (64-bit)
    // NOTE: it is undefined behavior if rhs is outside [0,63]
    // XXXXXXXX ddddssss ssss0000 00000000
    SLL64 = 0x51,
    // SRL32 dest, src1, src2 - shift right logical (fills with 0s) (32-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    SRL32 = 0x52,
    // SRL64 dest, src1, src2 - shift right logical (fills with 0s) (64-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    SRL64 = 0x53,
    // SRA32 dest, src1, src2 - shift right arithmetic (fills with sign bit) (32-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    SRA32 = 0x54,
    // SRA64 dest, src1, src2 - shift right arithmetic (fills with sign bit) (64-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    SRA64 = 0x55,
    // OR32  dest, src1, src2 - bitwise OR (32-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    OR32  = 0x56,
    // OR64  dest, src1, src2 - bitwise OR (64-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    OR64  = 0x57,
    // AND32 dest, src1, src2 - bitwise AND (32-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    AND32 = 0x58,
    // AND64 dest, src1, src2 - bitwise AND (64-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    AND64 = 0x59,
    // XOR32 dest, src1, src2 - bitwise XOR (32-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    XOR32 = 0x5a,
    // XOR64 dest, src1, src2 - bitwise XOR (64-bit)
    // XXXXXXXX ddddssss ssss0000 00000000
    XOR64 = 0x5b,
    // NOT32 dest, src1 - bitwise NOT (32-bit)
    // XXXXXXXX ddddssss 00000000 00000000
    NOT32 = 0x5c,
    // NOT64 dest, src1 - bitwise NOT (64-bit)
    // XXXXXXXX ddddssss 00000000 00000000
    NOT64 = 0x5d,

    // ============================================================================================
    // Logical/Bitwise Instructions with immediates - 0x60-0x70
    // SLL32I dest, src1, imm - shift left logical with immediate (32-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    SLL32I = 0x60,
    // SLL64I dest, src1, imm - shift left logical with immediate (64-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    SLL64I = 0x61,
    // SRL32I dest, src1, imm - shift right logical with immediate (32-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    SRL32I = 0x62,
    // SRL64I dest, src1, imm - shift right logical with immediate (64-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    SRL64I = 0x63,
    // SRA32I dest, src1, imm - shift right arithmetic with immediate (32-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    SRA32I = 0x64,
    // SRA64I dest, src1, imm - shift right arithmetic with immediate (64-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    SRA64I = 0x65,
    // OR32I  dest, src1, imm - bitwise or with immediate (32-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    OR32I  = 0x66,
    // OR64I  dest, src1, imm - bitwise or with immediate (64-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    OR64I  = 0x67,
    // AND32I dest, src1, imm - bitwise and with immediate (32-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    AND32I = 0x68,
    // AND64I dest, src1, imm - bitwise and with immediate (64-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    AND64I = 0x69,
    // XOR32I dest, src1, imm - bitwise xor  with immediate (32-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    XOR32I = 0x6a,
    // XOR64I dest, src1, imm - bitwise xor  with immediate (64-bit)
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    XOR64I = 0x6b,

    // ============================================================================================
    // Control flow / Branching Instructions - 0x70-0x80
    // BEQ src1, src2, addr - if src1 == src2 then pc <- addr
    // XXXXXXXX ssssssss aaaa0000 00000000
    BEQ = 0x70,
    // BNE src1, src2, addr - if src1 != src2 then pc <- addr
    // XXXXXXXX ssssssss aaaa0000 00000000
    BNE = 0x71,
    // BLT src1, src2, addr - if src1 <  src2 then pc <- addr
    // XXXXXXXX ssssssss aaaa0000 00000000
    BLT = 0x72,
    // BLE src1, src2, addr - if src1 <= src2 then pc <- addr
    // XXXXXXXX ssssssss aaaa0000 00000000
    BLE = 0x73,
    // BGT src1, src2, addr - if src1 >  src2 then pc <- addr
    // XXXXXXXX ssssssss aaaa0000 00000000
    BGT = 0x74,
    // BGE src1, src2, addr - if src1 >= src2 then pc <- addr
    // XXXXXXXX ssssssss aaaa0000 00000000
    BGE = 0x75,
    // JMP addr - pc <- addr
    // XXXXXXXX aaaa0000 00000000 00000000
    JMP = 0x76,

    // ============================================================================================
    // Function instructions - 0x80-0x90
    // CALL addr
    // 1. pushes return address on to the stack
    // 2. changes pc to addr
    // base pointer should be pushed on the stack by the callee
    // push bp
    // mov bp, sp
    // Caller's actions
    // 1. push caller saved registers
    // 2. push args in reverse order (callee can access with arg0 = [bp+8], arg1 = [bp+12])
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
    CALL = 0x80,
    // Similar to CALL but takes in an a Syscall enum for calling libc functions
    // SYSCALL Syscall.PUTS
    // SYSCALL syscall
    // YYYYYYYY - 8bits for indexing a max of 256 different syscalls
    // XXXXXXXX YYYYYYYY 00000000 00000000
    SYSCALL = 0x81,
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
    RET = 0x82,
    // PUSH src - sp -= 4 ; [sp] <- src
    // 1. decrements sp by 4 (bytes)
    // 2. places src onto stack at [sp]
    // XXXXXXXX ssss0000 00000000 00000000
    PUSH = 0x83,
    // POP dest - dest <- [sp] ; sp += 4
    // 1. moves [sp] into dest 
    // 2. increments sp by 4 (bytes)
    // XXXXXXXX dddd0000 00000000 00000000
    POP = 0x84,

    // ============================================================================================
    // other instructions - 0x90-0xa0
    // NOP - no operation
    // XXXXXXXX 000000000 00000000 00000000
    NOP = 0x90,
    // HALT - halts the computer
    // XXXXXXXX 000000000 00000000 00000000
    HALT = 0x91,
    // GETCHAR - reads (from stdin) a char (1-byte) and stores it in the 
    // given register
    // NOTE: THIS IS TEMPORARY - SYSCALL SHOULD BE USED INSTEAD
    // XXXXXXXX dddd00000 00000000 00000000
    GETCHAR = 0x92,
    // PUTCHAR - outputs (to stdout) a char (1-byte) from the given register
    // NOTE: THIS IS TEMPORARY - SYSCALL SHOULD BE USED INSTEAD
    // XXXXXXXX ssss00000 00000000 00000000
    PUTCHAR = 0x93,

};
