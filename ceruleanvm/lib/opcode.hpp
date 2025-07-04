#pragma once

enum Opcode : const uint8_t {
    // Invalid Instruction - 0x00
    // This is a good sanity for if the control flow ends up in uninitialized memory
    INVALID = 0x00,

    // Memory Instructions - 0x01-0x10
    // LUI dest, imm        - loads upper immediate 16 bits into given register
    // XXXXXXXX dddd0000 iiiiiiii iiiiiiii
    LUI = 0x01,
    // LLI dest, imm        - loads lower immediate 16 bits into given register
    // XXXXXXXX dddd0000 iiiiiiii iiiiiiii
    LLI = 0x02,
    // LB dest, offset(src) - load 
    // XXXXXXXX ddddssss oooooooo oooooooo
    LB = 0x03,
    // LH dest, offset(src) - load half (2 bytes)
    // XXXXXXXX ddddssss oooooooo oooooooo
    LH = 0x04,
    // LW dest, offset(src) - load word (4 bytes)
    // XXXXXXXX ddddssss oooooooo oooooooo
    LW = 0x05,
    // LD dest, offset(src) - load double word (8 bytes)
    // XXXXXXXX ddddssss oooooooo oooooooo
    LD = 0x06,
    // SB offset(dest), src - store byte
    // XXXXXXXX ddddssss oooooooo oooooooo
    SB = 0x07,
    // SH offset(dest), src - store half (2 bytes)
    // XXXXXXXX ddddssss oooooooo oooooooo
    SH = 0x08,
    // SW offset(dest), src - store word (4 bytes)
    // XXXXXXXX ddddssss oooooooo oooooooo
    SW = 0x09,
    // SD offset(dest), src - store double word (8 bytes)
    // XXXXXXXX ddddssss oooooooo oooooooo
    SD = 0x0a,

    // Integer Arithmetic - 0x10-0x20
    // ADD dest, src1, src2 - integer addition
    // XXXXXXXX ddddssss ssss0000 00000000
    ADD = 0x10,
    // SUB dest, src1, src2 - integer subtraction
    // XXXXXXXX ddddssss ssss0000 00000000
    SUB = 0x11,
    // MUL dest, src1, src2 - integer multiplication
    // XXXXXXXX ddddssss ssss0000 00000000
    MUL = 0x12,
    // DIV dest, src1, src2 - integer division
    // XXXXXXXX ddddssss ssss0000 00000000
    DIV = 0x13,
    // MOD dest, src1, src2 - integer division remainder
    // XXXXXXXX ddddssss ssss0000 00000000
    MOD = 0x14,
    // immediate integer arithmetic instructions
    // immediate values are 16-bit signed
    // ADDI dest, src1, imm - integer addition with immediate
    // - can be used to load immediate into register 
    // - that's why there is no load immediate 
    // - ADDI r0, rzero, 42 : r0 <- 0 + 42
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    ADDI = 0x15,
    // SUBI dest, src1, imm - integer subtraction with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    SUBI = 0x16,
    // MULI dest, src1, imm - integer multiplication with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    MULI = 0x17,
    // DIVI dest, src1, imm - integer division with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    DIVI = 0x18,
    // MODI dest, src1, imm - integer division remainder with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    MODI = 0x19,

    // Floating Point Arithmetic Instructions - 0x20-0x30
    // ADDF32 dest, src1 - floating point add - single 32bit precision
    // XXXXXXXX ddddssss ssss0000 00000000
    ADDF32 = 0x20,
    // ADDF64 dest, src1, src2 - floating point add - double 64bit precision
    // XXXXXXXX ddddssss ssss0000 00000000
    ADDF64 = 0x21,
    // SUBF32 dest, src1, src2 - floating point sub - single 32bit precision
    // XXXXXXXX ddddssss ssss0000 00000000
    SUBF32 = 0x22,
    // SUBF64 dest, src1, src2 - floating point sub - double 64bit precision
    // XXXXXXXX ddddssss ssss0000 00000000
    SUBF64 = 0x23,
    // MULF32 dest, src1, src2 - floating point mul - single 32bit precision
    // XXXXXXXX ddddssss ssss0000 00000000
    MULF32 = 0x24,
    // MULF64 dest, src1, src2 - floating point mul - double 64bit precision
    // XXXXXXXX ddddssss ssss0000 00000000
    MULF64 = 0x25,
    // DIVF32 dest, src1, src2 - floating point div - single 32bit precision
    // XXXXXXXX ddddssss ssss0000 00000000
    DIVF32 = 0x26,
    // DIVF64 dest, src1, src2 - floating point div - double 64bit precision
    // XXXXXXXX ddddssss ssss0000 00000000
    DIVF64 = 0x27,
    // SQRTF32 dest, src1 - floating point sqrt - single 32bit precision
    // XXXXXXXX ddddssss 00000000 00000000
    SQRTF32 = 0x28,
    // SQRTF64 dest, src1 - floating point sqrt - double 64bit precision
    // XXXXXXXX ddddssss 00000000 00000000
    SQRTF64 = 0x29,
    // ABSF32 dest, src1 - floating point abs - single 32bit precision
    // XXXXXXXX ddddssss 00000000 00000000
    ABSF32 = 0x2a,
    // ABSF64 dest, src1 - floating point abs - double 64bit precision
    // XXXXXXXX ddddssss 00000000 00000000
    ABSF64 = 0x2b,
    // NEGF32 dest, src1 - floating point neg - single 32bit precision
    // XXXXXXXX ddddssss 00000000 00000000
    NEGF32 = 0x2c,
    // NEGF64 dest, src1 - floating point neg - double 64bit precision
    // XXXXXXXX ddddssss 00000000 00000000
    NEGF64 = 0x2d,

    // Int-Int Conversions - 0x30-0x50
    // CVTI32I64 dest, src1 - convert int32 to int64
    // XXXXXXXX ddddssss 00000000 00000000
    CVTI32I64 = 0x30,
    // CVTI64I32 dest, src1 - convert int64 to int32
    // XXXXXXXX ddddssss 00000000 00000000
    CVTI64I32 = 0x31,
    // Uint-Uint Conversions
    // CVTU32U64 dest, src1 - convert uint32 to uint64
    // XXXXXXXX ddddssss 00000000 00000000
    CVTU32U64 = 0x32,
    // CVTU64U32 dest, src1 - convert uint64 to uint32
    // XXXXXXXX ddddssss 00000000 00000000
    CVTU64U32 = 0x33,
    // Int-Float Conversions
    // CVTF32I32 dest, src1 - convert float32 to int32
    // XXXXXXXX ddddssss 00000000 00000000
    CVTF32I32 = 0x34,
    // CVTI32F32 dest, src1 - convert int32 to float32
    // XXXXXXXX ddddssss 00000000 00000000
    CVTI32F32 = 0x35,
    // CVTF64I64 dest, src1 - convert float64 to int64
    // XXXXXXXX ddddssss 00000000 00000000
    CVTF64I64 = 0x36,
    // CVTI64F64 dest, src1 - convert int64 to float64
    // XXXXXXXX ddddssss 00000000 00000000
    CVTI64F64 = 0x37,
    // CVTF32U32 dest, src1 - convert float32 to uint32
    // XXXXXXXX ddddssss 00000000 00000000
    CVTF32U32 = 0x38,
    // CVTU32F32 dest, src1 - convert uint32 to float32
    // XXXXXXXX ddddssss 00000000 00000000
    CVTU32F32 = 0x39,
    // CVTF64U64 dest, src1 - convert float64 to uint64
    // XXXXXXXX ddddssss 00000000 00000000
    CVTF64U64 = 0x3a,
    // CVTU64F64 dest, src1 - convert uint64 to float64
    // XXXXXXXX ddddssss 00000000 00000000
    CVTU64F64 = 0x3b,
    // Float-Float Conversions
    // CVTF32F64 dest, src1 - convert float32 to float64
    // XXXXXXXX ddddssss 00000000 00000000
    CVTF32F64 = 0x3c,
    // CVTF64F32 dest, src1 - convert float64 to float32
    // XXXXXXXX ddddssss 00000000 00000000
    CVTF64F32 = 0x3d,

    // Logical/Bitwise Instructions - 0x50-0x60
    // SLL dest, src1, src2 - shift left logical
    // XXXXXXXX ddddssss ssss0000 00000000
    SLL = 0x50,
    // SRL dest, src1, src2 - shift right logical
    // XXXXXXXX ddddssss ssss0000 00000000
    SRL = 0x51,
    // SRA dest, src1, src2 - shift right arithmetic
    // XXXXXXXX ddddssss ssss0000 00000000
    SRA = 0x52,
    // OR  dest, src1, src2 - bitwise or
    // XXXXXXXX ddddssss ssss0000 00000000
    OR  = 0x53,
    // AND dest, src1, src2 - bitwise and
    // XXXXXXXX ddddssss ssss0000 00000000
    AND = 0x54,
    // XOR dest, src1, src2 - bitwise xor 
    // XXXXXXXX ddddssss ssss0000 00000000
    XOR = 0x55,
    // SLLI dest, src1, imm - shift left logical with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    SLLI = 0x56,
    // SRLI dest, src1, imm - shift right logical with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    SRLI = 0x57,
    // SRAI dest, src1, imm - shift right arithmetic with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    SRAI = 0x58,
    // ORI  dest, src1, imm - bitwise or with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    ORI  = 0x59,
    // ANDI dest, src1, imm - bitwise and with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    ANDI = 0x5a,
    // XORI dest, src1, imm - bitwise xor  with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    XORI = 0x5b,

    // Control flow - 0x60-0x70
    // BEQ src1, src2, addr - if src1 == src2 then pc <- addr
    // XXXXXXXX ssssssss aaaa0000 00000000
    BEQ = 0x60,
    // BNE src1, src2, addr - if src1 != src2 then pc <- addr
    // XXXXXXXX ssssssss aaaa0000 00000000
    BNE = 0x61,
    // BLT src1, src2, addr - if src1 <  src2 then pc <- addr
    // XXXXXXXX ssssssss aaaa0000 00000000
    BLT = 0x62,
    // BLE src1, src2, addr - if src1 <= src2 then pc <- addr
    // XXXXXXXX ssssssss aaaa0000 00000000
    BLE = 0x63,
    // BGT src1, src2, addr - if src1 >  src2 then pc <- addr
    // XXXXXXXX ssssssss aaaa0000 00000000
    BGT = 0x64,
    // BGE src1, src2, addr - if src1 >= src2 then pc <- addr
    // XXXXXXXX ssssssss aaaa0000 00000000
    BGE = 0x65,
    // JMP addr - pc <- addr
    // XXXXXXXX aaaa0000 00000000 00000000
    JMP = 0x66,

    // Function instructions - 0x70-0x80
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
    CALL = 0x70,
    // Similar to CALL but takes in an a Syscall enum for calling libc functions
    // SYSCALL Syscall.PUTS
    // SYSCALL syscall
    // XXXXXXXX aaaa0000 00000000 00000000
    SYSCALL = 0x71,
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
    RET = 0x72,
    // PUSH src - sp -= 4 ; [sp] <- src
    // 1. decrements sp by 4 (bytes)
    // 2. places src onto stack at [sp]
    // XXXXXXXX ssss0000 00000000 00000000
    PUSH = 0x73,
    // POP dest - dest <- [sp] ; sp += 4
    // 1. moves [sp] into dest 
    // 2. increments sp by 4 (bytes)
    // XXXXXXXX dddd0000 00000000 00000000
    POP = 0x74,

    // other instructions - 0x80-0x90
    // NOP - no operation
    // XXXXXXXX 000000000 00000000 00000000
    NOP = 0x80,
    // HALT - halts the computer
    // XXXXXXXX 000000000 00000000 00000000
    HALT = 0x81,
    // GETCHAR - reads (from stdin) a char (1-byte) and stores it in the 
    // given register
    // NOTE: THIS IS TEMPORARY - SYSCALL SHOULD BE USED INSTEAD
    // XXXXXXXX dddd00000 00000000 00000000
    GETCHAR = 0x82,
    // PUTCHAR - outputs (to stdout) a char (1-byte) from the given register
    // NOTE: THIS IS TEMPORARY - SYSCALL SHOULD BE USED INSTEAD
    // XXXXXXXX ssss00000 00000000 00000000
    PUTCHAR = 0x83,

};
