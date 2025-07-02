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
    // SB offset(dest), src - store byte
    // XXXXXXXX ddddssss oooooooo oooooooo
    SB = 0x06,
    // SH offset(dest), src - store half (2 bytes)
    // XXXXXXXX ddddssss oooooooo oooooooo
    SH = 0x07,
    // SW offset(dest), src - store word (4 bytes)
    // XXXXXXXX ddddssss oooooooo oooooooo
    SW = 0x08,

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
    // MULI dest, src1, src2 - integer multiplication with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    MULI = 0x17,
    // DIVI dest, src1, src2 - integer division with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    DIVI = 0x18,
    // MODI dest, src1, src2 - integer division remainder with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    MODI = 0x19,

    // Logical/Bitwise Instructions - 0x20-0x30
    // SLL dest, src1, src2 - shift left logical
    // XXXXXXXX ddddssss ssss0000 00000000
    SLL = 0x20,
    // SRL dest, src1, src2 - shift right logical
    // XXXXXXXX ddddssss ssss0000 00000000
    SRL = 0x21,
    // SRA dest, src1, src2 - shift right arithmetic
    // XXXXXXXX ddddssss ssss0000 00000000
    SRA = 0x22,
    // OR  dest, src1, src2 - bitwise or
    // XXXXXXXX ddddssss ssss0000 00000000
    OR  = 0x23,
    // AND dest, src1, src2 - bitwise and
    // XXXXXXXX ddddssss ssss0000 00000000
    AND = 0x24,
    // XOR dest, src1, src2 - bitwise xor 
    // XXXXXXXX ddddssss ssss0000 00000000
    XOR = 0x25,
    // SLLI dest, src1, imm - shift left logical with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    SLLI = 0x26,
    // SRLI dest, src1, imm - shift right logical with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    SRLI = 0x27,
    // SRAI dest, src1, imm - shift right arithmetic with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    SRAI = 0x28,
    // ORI  dest, src1, imm - bitwise or with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    ORI  = 0x29,
    // ANDI dest, src1, imm - bitwise and with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    ANDI = 0x2a,
    // XORI dest, src1, imm - bitwise xor  with immediate
    // XXXXXXXX ddddssss iiiiiiii iiiiiiii
    XORI = 0x2b,

    // Control flow - 0x30-0x40
    // BEQ src1, src2, addr - if src1 == src2 then pc <- addr
    // XXXXXXXX ssssssss aaaa0000 00000000
    BEQ = 0x30,
    // BNE src1, src2, addr - if src1 != src2 then pc <- addr
    // XXXXXXXX ssssssss aaaa0000 00000000
    BNE = 0x31,
    // BLT src1, src2, addr - if src1 <  src2 then pc <- addr
    // XXXXXXXX ssssssss aaaa0000 00000000
    BLT = 0x32,
    // BLE src1, src2, addr - if src1 <= src2 then pc <- addr
    // XXXXXXXX ssssssss aaaa0000 00000000
    BLE = 0x33,
    // BGT src1, src2, addr - if src1 >  src2 then pc <- addr
    // XXXXXXXX ssssssss aaaa0000 00000000
    BGT = 0x34,
    // BGE src1, src2, addr - if src1 >= src2 then pc <- addr
    // XXXXXXXX ssssssss aaaa0000 00000000
    BGE = 0x35,
    // JMP addr - pc <- addr
    // XXXXXXXX aaaa0000 00000000 00000000
    JMP = 0x36,

    // Function instructions - 0x40-0x50
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
    CALL = 0x40,
    // Similar to CALL but takes in an a Syscall enum for calling libc functions
    // SYSCALL Syscall.PUTS
    // SYSCALL syscall
    // XXXXXXXX aaaa0000 00000000 00000000
    SYSCALL = 0x41,
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
    RET = 0x42,
    // PUSH src - sp -= 4 ; [sp] <- src
    // 1. decrements sp by 4 (bytes)
    // 2. places src onto stack at [sp]
    // XXXXXXXX ssss0000 00000000 00000000
    PUSH = 0x43,
    // POP dest - dest <- [sp] ; sp += 4
    // 1. moves [sp] into dest 
    // 2. increments sp by 4 (bytes)
    // XXXXXXXX dddd0000 00000000 00000000
    POP = 0x44,

    // other instructions - 0x50-0xff
    // NOP - no operation
    // XXXXXXXX 000000000 00000000 00000000
    NOP = 0x50,
    // HALT - halts the computer
    // XXXXXXXX 000000000 00000000 00000000
    HALT = 0x51,
    // GETCHAR - reads (from stdin) a char (1-byte) and stores it in the 
    // given register
    // NOTE: THIS IS TEMPORARY - SYSCALL SHOULD BE USED INSTEAD
    // XXXXXXXX dddd00000 00000000 00000000
    GETCHAR = 0x52,
    // PUTCHAR - outputs (to stdout) a char (1-byte) from the given register
    // NOTE: THIS IS TEMPORARY - SYSCALL SHOULD BE USED INSTEAD
    // XXXXXXXX ssss00000 00000000 00000000
    PUTCHAR = 0x53,

};
