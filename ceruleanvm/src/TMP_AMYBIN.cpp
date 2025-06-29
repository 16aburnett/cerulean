// 32-bit machine language interpreter 
// that uses a RISC-V-like format 
// By Amy Burnett
//========================================================================

#include <stdio.h>
#include <iostream>
#include <iomanip>
#include <cstring>   //memcpy

//========================================================================

typedef unsigned char byte; 

bool DEBUG = false; 
// 1MB by default 
size_t MEMORY_SIZE_BYTES = 1000000; 

//========================================================================
// Instructions 

// Using a similar language to RISC-V
// all instructions are 32-bit

// makes sure each opcode is unique
// opcode 0 is not defined 
// which will halt the program with an error 
byte opcode_counter = 0b00000001;

// LUI dest, imm        - loads upper immediate 16 bits into given register
// XXXXXXXX dddd0000 iiiiiiii iiiiiiii
byte OPCODE_LUI = opcode_counter++;
// LLI dest, imm        - loads lower immediate 16 bits into given register
// XXXXXXXX dddd0000 iiiiiiii iiiiiiii
byte OPCODE_LLI = opcode_counter++;
// LB dest, offset(src) - load byte 
// XXXXXXXX ddddssss oooooooo oooooooo
byte OPCODE_LB = opcode_counter++;
// LH dest, offset(src) - load half (2 bytes)
// XXXXXXXX ddddssss oooooooo oooooooo
byte OPCODE_LH = opcode_counter++;
// LW dest, offset(src) - load word (4 bytes)
// XXXXXXXX ddddssss oooooooo oooooooo
byte OPCODE_LW = opcode_counter++;
// SB offset(dest), src - store byte
// XXXXXXXX ddddssss oooooooo oooooooo
byte OPCODE_SB = opcode_counter++;
// SH offset(dest), src - store half (2 bytes)
// XXXXXXXX ddddssss oooooooo oooooooo
byte OPCODE_SH = opcode_counter++;
// SW offset(dest), src - store word (4 bytes)
// XXXXXXXX ddddssss oooooooo oooooooo
byte OPCODE_SW = opcode_counter++;

// arithmetic instructions
// ADD dest, src1, src2 - integer addition
// XXXXXXXX ddddssss ssss0000 00000000
byte OPCODE_ADD = opcode_counter++;
// SUB dest, src1, src2 - integer subtraction
// XXXXXXXX ddddssss ssss0000 00000000
byte OPCODE_SUB = opcode_counter++;
// MUL dest, src1, src2 - integer multiplication
// XXXXXXXX ddddssss ssss0000 00000000
byte OPCODE_MUL = opcode_counter++;
// DIV dest, src1, src2 - integer division
// XXXXXXXX ddddssss ssss0000 00000000
byte OPCODE_DIV = opcode_counter++;
// MOD dest, src1, src2 - integer division remainder
// XXXXXXXX ddddssss ssss0000 00000000
byte OPCODE_MOD = opcode_counter++;
// SLL dest, src1, src2 - shift left logical
// XXXXXXXX ddddssss ssss0000 00000000
byte OPCODE_SLL = opcode_counter++;
// SRL dest, src1, src2 - shift right logical
// XXXXXXXX ddddssss ssss0000 00000000
byte OPCODE_SRL = opcode_counter++;
// SRA dest, src1, src2 - shift right arithmetic
// XXXXXXXX ddddssss ssss0000 00000000
byte OPCODE_SRA = opcode_counter++;
// OR  dest, src1, src2 - bitwise or
// XXXXXXXX ddddssss ssss0000 00000000
byte OPCODE_OR  = opcode_counter++;
// AND dest, src1, src2 - bitwise and
// XXXXXXXX ddddssss ssss0000 00000000
byte OPCODE_AND = opcode_counter++;
// XOR dest, src1, src2 - bitwise xor 
// XXXXXXXX ddddssss ssss0000 00000000
byte OPCODE_XOR = opcode_counter++;

// immediate arithmetic instructions
// immediate values are 16-bit signed
// ADDI dest, src1, imm - integer addition with immediate
// - can be used to load immediate into register 
// - that's why there is no load immediate 
// - ADDI r0, rzero, 42 : r0 <- 0 + 42
// XXXXXXXX ddddssss iiiiiiii iiiiiiii
byte OPCODE_ADDI = opcode_counter++;
// SUBI dest, src1, imm - integer subtraction with immediate
// XXXXXXXX ddddssss iiiiiiii iiiiiiii
byte OPCODE_SUBI = opcode_counter++;
// MULI dest, src1, src2 - integer multiplication with immediate
// XXXXXXXX ddddssss iiiiiiii iiiiiiii
byte OPCODE_MULI = opcode_counter++;
// DIVI dest, src1, src2 - integer division with immediate
// XXXXXXXX ddddssss iiiiiiii iiiiiiii
byte OPCODE_DIVI = opcode_counter++;
// MODI dest, src1, src2 - integer division remainder with immediate
// XXXXXXXX ddddssss iiiiiiii iiiiiiii
byte OPCODE_MODI = opcode_counter++;
// SLLI dest, src1, imm - shift left logical with immediate
// XXXXXXXX ddddssss iiiiiiii iiiiiiii
byte OPCODE_SLLI = opcode_counter++;
// SRLI dest, src1, imm - shift right logical with immediate
// XXXXXXXX ddddssss iiiiiiii iiiiiiii
byte OPCODE_SRLI = opcode_counter++;
// SRAI dest, src1, imm - shift right arithmetic with immediate
// XXXXXXXX ddddssss iiiiiiii iiiiiiii
byte OPCODE_SRAI = opcode_counter++;
// ORI  dest, src1, imm - bitwise or with immediate
// XXXXXXXX ddddssss iiiiiiii iiiiiiii
byte OPCODE_ORI  = opcode_counter++;
// ANDI dest, src1, imm - bitwise and with immediate
// XXXXXXXX ddddssss iiiiiiii iiiiiiii
byte OPCODE_ANDI = opcode_counter++;
// XORI dest, src1, imm - bitwise xor  with immediate
// XXXXXXXX ddddssss iiiiiiii iiiiiiii
byte OPCODE_XORI = opcode_counter++;

// branching
// BEQ src1, src2, addr - if src1 == src2 then pc <- addr
// XXXXXXXX ssssssss aaaa0000 00000000
byte OPCODE_BEQ = opcode_counter++;
// BNE src1, src2, addr - if src1 != src2 then pc <- addr
// XXXXXXXX ssssssss aaaa0000 00000000
byte OPCODE_BNE = opcode_counter++;
// BLT src1, src2, addr - if src1 <  src2 then pc <- addr
// XXXXXXXX ssssssss aaaa0000 00000000
byte OPCODE_BLT = opcode_counter++;
// BLE src1, src2, addr - if src1 <= src2 then pc <- addr
// XXXXXXXX ssssssss aaaa0000 00000000
byte OPCODE_BLE = opcode_counter++;
// BGT src1, src2, addr - if src1 >  src2 then pc <- addr
// XXXXXXXX ssssssss aaaa0000 00000000
byte OPCODE_BGT = opcode_counter++;
// BGE src1, src2, addr - if src1 >= src2 then pc <- addr
// XXXXXXXX ssssssss aaaa0000 00000000
byte OPCODE_BGE = opcode_counter++;
// JMP addr - pc <- addr
// XXXXXXXX aaaa0000 00000000 00000000
byte OPCODE_JMP = opcode_counter++;

// function instructions
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
byte OPCODE_CALL = opcode_counter++;
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
byte OPCODE_RET = opcode_counter++;
// PUSH src - sp -= 4 ; [sp] <- src
// 1. decrements sp by 4 (bytes)
// 2. places src onto stack at [sp]
// XXXXXXXX ssss0000 00000000 00000000
byte OPCODE_PUSH = opcode_counter++;
// POP dest - dest <- [sp] ; sp += 4
// 1. moves [sp] into dest 
// 2. increments sp by 4 (bytes)
// XXXXXXXX dddd0000 00000000 00000000
byte OPCODE_POP = opcode_counter++;

// other instructions
// NOP - no operation
// XXXXXXXX 000000000 00000000 00000000
byte OPCODE_NOP = opcode_counter++;
// HLT - halts the computer
// XXXXXXXX 000000000 00000000 00000000
byte OPCODE_HLT = opcode_counter++;
// GETCHAR - reads (from stdin) a char (1-byte) and stores it in the 
// given register
// XXXXXXXX dddd00000 00000000 00000000
byte OPCODE_GETCHAR = opcode_counter++;
// PUTCHAR - outputs (to stdout) a char (1-byte) from the given register
// XXXXXXXX ssss00000 00000000 00000000
byte OPCODE_PUTCHAR = opcode_counter++;


//========================================================================

void 
printMemory (byte* memory, int memory_size, int bytesPerLine=4)
{
    printf ("=== MEMORY ===================================================\n");
    size_t numSameLines = 0; 
    // start prevLine with something that wont be the same as the first line
    int prevLine = (*(int*)&memory[0]) - 1; 
    for (int i = 0; i < memory_size; i+=bytesPerLine)
    {
        // ensure line is new - otherwise ignore the line
        int line = *(int*)&memory[i];
        if (line == prevLine)
        {
            numSameLines++;
            // ignore the line 
            continue; 
        }
        else if (numSameLines > 0)
        {
            printf ("             ^ repeated %lu times\n", numSameLines);
            numSameLines = 0;
        }
        prevLine = line; 

        // print address 
        printf (
            "0x%x%x%x%x%x%x%x%x | ", 
            (0b11110000000000000000000000000000 & i) >> 28,
            (0b00001111000000000000000000000000 & i) >> 24,
            (0b00000000111100000000000000000000 & i) >> 20,
            (0b00000000000011110000000000000000 & i) >> 16,
            (0b00000000000000001111000000000000 & i) >> 12,
            (0b00000000000000000000111100000000 & i) >>  8,
            (0b00000000000000000000000011110000 & i) >>  4,
            (0b00000000000000000000000000001111 & i) >>  0
        );
        // print binary representation (4 bytes per line)
        for (int j = i; j < i+bytesPerLine; ++j)
        {
            printf (
                "%d%d%d%d%d%d%d%d ",
                (0b10000000 & memory[j]) >> 7,
                (0b01000000 & memory[j]) >> 6,
                (0b00100000 & memory[j]) >> 5,
                (0b00010000 & memory[j]) >> 4,
                (0b00001000 & memory[j]) >> 3,
                (0b00000100 & memory[j]) >> 2,
                (0b00000010 & memory[j]) >> 1,
                (0b00000001 & memory[j]) >> 0
            );
        }
        printf ("| ");
        // print hex representation
        for (int j = i; j < i+bytesPerLine; ++j)
        {
            printf (
                "%x%x ",
                (0b11110000 & memory[j]) >> 4,
                (0b00001111 & memory[j]) >> 0
            );
        }
        printf ("\n");
    }
    if (numSameLines > 0)
    {
        printf ("             ^ repeated %lu times\n", numSameLines);
        numSameLines = 0;
    }
    printf ("=== END MEMORY ===============================================\n");
}

//========================================================================

bool isNumber(const char* str)
{
    for (int i = 0; i < strlen(str); ++i) {
        if (std::isdigit(str[i]) == 0) return false;
    }
    return true;
}

int 
main(int argc, char *argv[])
{
    // Parse commandline args 
    if (argc > 1)
    {
        for (int i = 1; i < argc; ++i)
        {
            if (strcmp(argv[i], "-d") == 0) DEBUG = true; 
            // --size <numBytes>
            if (strcmp(argv[i], "--size") == 0) 
            {
                // ensure N was provided and is a number
                if (i+1 < argc && isNumber(argv[i+1]))
                {
                    MEMORY_SIZE_BYTES = atoi(argv[i+1]);
                    // ensure all lines are 4-bytes 
                    MEMORY_SIZE_BYTES = MEMORY_SIZE_BYTES - (MEMORY_SIZE_BYTES % 4) + 4;
                    ++i;
                }
            }
        }
    }


    // allocate memory for the program 
    if (DEBUG) printf ("Allocating %lu Bytes\n", MEMORY_SIZE_BYTES);
    byte* memory = (byte*) malloc(MEMORY_SIZE_BYTES);

    // define instructions 
    // byte instructions[] = {
    //     OPCODE_LUI,     0x00, 0x6a, 0xe3, // [0x00] r0 <- 0x6ae3xxxx
    //     OPCODE_LLI,     0x00, 0xff, 0x57, // [0x04] r0 <- 0xxxxxff57
    //     OPCODE_LUI,     0x40, 0x33, 0x00, // [0x08] r4 <- 0x33
    //     OPCODE_LB,      0x14, 0x01, 0x00, // [0x0c] r1 <- [r4 + 1] (1 byte)
    //     OPCODE_ADD,     0x20, 0x10, 0x00, // [0x10] r2 <- r0 + r1 
    //     OPCODE_ADDI,    0x30, 0x01, 0x00, // [0x14] r2 <- r0 + 1
    //     OPCODE_SW,      0x40, 0x01, 0x00, // [0x18] [r4 + 1] <- r0
    //     OPCODE_ADDI,    0x09, 0x38, 0x00, // [0x1c] r0 <- r9 + 0x38
    //     OPCODE_LW,      0x10, 0x00, 0x00, // [0x20] r1 <- [r0 + 0]
    //     OPCODE_ADDI,    0x29, 0x03, 0x00, // [0x24] r2 <- r9 + 3
    //     OPCODE_SRA,     0x11, 0x20, 0x00, // [0x28] r1 <- r1 >> r2
    //     OPCODE_SW,      0x01, 0x00, 0x00, // [0x2c] [r0 + 0] <- r1
    //     OPCODE_HLT,     0x00, 0x00, 0x00, // [0x30] halt computer
    //     0xef,           0x3f, 0x43, 0xde, // [0x34] data (little endian)
    //     0xaa,           0x00, 0x00, 0xf0  // [0x38] data (little endian)
    // };

    // test branching
    // byte instructions[] = {
    //     OPCODE_LUI,     0x00, 0x00, 0x00, // [0x00] r0 <- 0x0000      - i 
    //     OPCODE_LLI,     0x00, 0x00, 0x00, // [0x04] r0 <- 0x0000      - i
    //     // while r0 < 14
    //     OPCODE_LUI,     0x10, 0x0d, 0x00, // [0x08] r1 <- 0x0e00 (13) - string size
    //     OPCODE_LLI,     0x10, 0x00, 0x00, // [0x0c] r1 <- 0x0000      - string size
    //     OPCODE_LUI,     0x20, 0x40, 0x00, // [0x10] r2 <- 0x4000      - end loop addr
    //     OPCODE_LLI,     0x20, 0x00, 0x00, // [0x14] r2 <- 0x0000      - end loop addr
    //     OPCODE_BGE,     0x01, 0x20, 0x00, // [0x18] if r0 >= r1 then pc <- r2
    //     // body 
    //     OPCODE_LUI,     0x30, 0x44, 0x00, // [0x1c] r3 <- 0x4400      - string addr
    //     OPCODE_LLI,     0x30, 0x00, 0x00, // [0x20] r3 <- 0x0000      - string addr
    //     OPCODE_ADD,     0x33, 0x00, 0x00, // [0x24] r3 <- r3 + r0     - string addr + i
    //     OPCODE_LB,      0x53, 0x00, 0x00, // [0x28] r5 <- [r3 + 0]
    //     OPCODE_PUTCHAR, 0x50, 0x00, 0x00, // [0x2c] putchar(r5)
    //     // update 
    //     OPCODE_ADDI,    0x00, 0x01, 0x00, // [0x30] r0 <- r0 + 1
    //     // repeat 
    //     OPCODE_LUI,     0x20, 0x08, 0x00, // [0x34] r2 <- 0x0800      - start loop addr
    //     OPCODE_LLI,     0x20, 0x00, 0x00, // [0x38] r2 <- 0x0000      - start loop addr
    //     OPCODE_JMP,     0x20, 0x00, 0x00, // [0x3c] pc <- [r2]
    //     // endwhile
    //     OPCODE_HLT,     0x00, 0x00, 0x00, // [0x40] end of program
    //     // static data
    //     'H',             'e',  'l',  'l', // [0x44] 
    //     'o',             ' ',  'W',  'o', // [0x48] 
    //     'r',             'l',  'd',  '!', // [0x4c] 
    //     '\n',           '\0', 0x00, 0x00  // [0x50] 
    // };

    // test functions 
    // byte instructions[] = {
    // // main:
    //     OPCODE_LUI,     0x00, 0x03, 0x00, // [0x00] r0 <- 0x0300      - a = 3
    //     OPCODE_LLI,     0x00, 0x00, 0x00, // [0x04] r0 <- 0x0000      - a = 3
    //     OPCODE_LUI,     0x10, 0x05, 0x00, // [0x08] r1 <- 0x0500      - b = 5
    //     OPCODE_LLI,     0x10, 0x00, 0x00, // [0x0c] r1 <- 0x0000      - b = 5
    //     OPCODE_LUI,     0x20, 0x40, 0x00, // [0x10] r2 <- 0x4000      - add function
    //     OPCODE_LLI,     0x20, 0x00, 0x00, // [0x14] r2 <- 0x0000      - add function
    //     OPCODE_PUSH,    0x10, 0x00, 0x00, // [0x18] push r1           - push arg1
    //     OPCODE_PUSH,    0x00, 0x00, 0x00, // [0x1c] push r0           - push arg0
    //     OPCODE_CALL,    0x20, 0x00, 0x00, // [0x20] call r2           - call add
    //     OPCODE_POP,     0x30, 0x00, 0x00, // [0x24] pop r3            - pop arg0
    //     OPCODE_POP,     0x30, 0x00, 0x00, // [0x28] pop r3            - pop arg1
    //     OPCODE_ADDI,    0xdd,  '0', 0x00, // [0x2c] ra <- ra + '0'    - convert to char
    //     OPCODE_PUTCHAR, 0xd0, 0x00, 0x00, // [0x30] putchar(ra)
    //     OPCODE_LUI,     0x40, '\n', 0x00, // [0x34] r4 <- '\n'
    //     OPCODE_PUTCHAR, 0x40, 0x00, 0x00, // [0x38] putchar(r4)
    //     OPCODE_HLT,     0x00, 0x00, 0x00, // [0x3c] end of program 
    // // add:
    //     // function prologue 
    //     OPCODE_PUSH,    0xe0, 0x00, 0x00, // [0x40] push bp - save caller's bp 
    //     OPCODE_ADDI,    0xef, 0x00, 0x00, // [0x44] bp <- sp + 0
    //     OPCODE_PUSH,    0x00, 0x00, 0x00, // [0x48] push r0 - save caller's r0
    //     OPCODE_PUSH,    0x10, 0x00, 0x00, // [0x4c] push r1 - save caller's r1 
    //     // body 
    //     OPCODE_LW,      0x0e, 0x08, 0x00, // [0x50] r0 <- [bp+8] - arg a
    //     OPCODE_LW,      0x1e, 0x0c, 0x00, // [0x54] r1 <- [bp+12] - arg b
    //     OPCODE_ADD,     0xd0, 0x10, 0x00, // [0x58] ra <- r0 + r1 - retval = a + b;
    //     // function epilogue 
    //     OPCODE_POP,     0x10, 0x00, 0x00, // [0x5c] push r1 - restore caller's r1
    //     OPCODE_POP,     0x00, 0x00, 0x00, // [0x60] push r0 - restore caller's r0 
    //     OPCODE_ADDI,    0xfe, 0x00, 0x00, // [0x64] sp <- bp - remove local vars 
    //     OPCODE_POP,     0xe0, 0x00, 0x00, // [0x68] bp <- [sp] - restore caller bp
    //     OPCODE_RET,     0x00, 0x00, 0x00, // [0x6c] return from function
    // // endadd
    // };
    
    byte instructions[] = {
    // // Piece of Cake Kattis problem
    // // Solution in AmyAssembly
    // // By Amy Burnett
    // //========================================================================

    // // start at main
    //     jump main
        OPCODE_LUI,     0x00, 0xf4, 0x03, // [0x00] r0 <- 0x03f4
        OPCODE_LLI,     0x00, 0x00, 0x00, // [0x04] r0 <- 0x0000
        OPCODE_JMP,     0x00, 0x00, 0x00, // [0x08] jump to main 0x3f4

    // //========================================================================
    // // converts string range to integer
    // // param1 - string pointer
    // // param2 - starting position to read int from
    // // param3 - end position to stop reading 
    // int stringToInt (char[] string, int start, int end);
    // stringToInt:
        // function prologue 
        OPCODE_PUSH,    0xe0, 0x00, 0x00, // [0x0c] push bp - save caller's bp 
        OPCODE_ADDI,    0xef, 0x00, 0x00, // [0x10] bp <- sp + 0
        OPCODE_PUSH,    0x00, 0x00, 0x00, // [0x14] push r0 - save caller's r0
        OPCODE_PUSH,    0x10, 0x00, 0x00, // [0x18] push r1 - save caller's r1 
        OPCODE_PUSH,    0x20, 0x00, 0x00, // [0x1c] push r2 - save caller's r2 
        OPCODE_PUSH,    0x30, 0x00, 0x00, // [0x20] push r3 - save caller's r3 
        OPCODE_PUSH,    0x40, 0x00, 0x00, // [0x24] push r4 - save caller's r4 
        OPCODE_PUSH,    0x50, 0x00, 0x00, // [0x28] push r5 - save caller's r5 
        OPCODE_PUSH,    0x60, 0x00, 0x00, // [0x2c] push r6 - save caller's r6 
        OPCODE_PUSH,    0x70, 0x00, 0x00, // [0x30] push r7 - save caller's r7 
        OPCODE_PUSH,    0x80, 0x00, 0x00, // [0x34] push r8 - save caller's r8 
        OPCODE_PUSH,    0x90, 0x00, 0x00, // [0x38] push r9 - save caller's r9 
    //     stackget string 0
        OPCODE_LW,      0x0e, 0x08, 0x00, // [0x3c] r0 <- [bp+8] - arg string
    //     stackget start 1
        OPCODE_LW,      0x1e, 0x0c, 0x00, // [0x40] r1 <- [bp+12] - arg start
    //     stackget end 2
        OPCODE_LW,      0x2e, 0x10, 0x00, // [0x44] r2 <- [bp+16] - arg end
    //     assign val 0
        OPCODE_LUI,     0x30, 0x00, 0x00, // [0x48] r3 <- 0 - val = 0
        OPCODE_LLI,     0x30, 0x00, 0x00, // [0x4c] r3 <- 0 - val = 0
    //     assign i start
        OPCODE_ADDI,    0x41, 0x00, 0x00, // [0x50] r4 <- r1 + 0 - i = start
    // while00:
    //     cmp i end
    //     jge endwhile00
        OPCODE_LUI,     0x50, 0x30, 0x02, // [0x54] r5 <- 0x0230 - endwhile00
        OPCODE_LLI,     0x50, 0x00, 0x00, // [0x58] r5 <- 0x0000 - endwhile00
        OPCODE_BGE,     0x42, 0x50, 0x00, // [0x5c] if r4 >= r2 then pc <- r5 - endwhile00

    //     // shift nums
    //     multiply val val 10
        OPCODE_MULI,    0x33, 0x0a, 0x00, // [0x60] r3 <- r3 * 10

        OPCODE_ADD,     0x60, 0x40, 0x00, // [0x64] r6 <- r0 + r4 - string + i
        OPCODE_LB,      0x76, 0x00, 0x00, // [0x68] r7 <- [r6 + 0] - r7 = string[i]
    //     cmp string[i] '1'
    //     jneq notOne
        OPCODE_LUI,     0x90,  '1', 0x00, // [0x6c] r9 <- '1' 
        OPCODE_LLI,     0x90, 0x00, 0x00, // [0x70] r9 <- '1' 
        OPCODE_LUI,     0x80, 0x90, 0x00, // [0x74] r8 <- 0x0090 - notOne
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x78] r8 <- 0x0000 - notOne
        OPCODE_BNE,     0x79, 0x80, 0x00, // [0x7c] if r7 != r9 then pc <- r8
    //     add val val 1 
        OPCODE_ADDI,    0x33, 0x01, 0x00, // [0x80] r3 <- r3 + 1 - val += 1
    //     jump continue
        OPCODE_LUI,     0x80, 0x20, 0x02, // [0x84] r8 <- 0x0220 - continue
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x88] r8 <- 0x0000 - continue
        OPCODE_JMP,     0x80, 0x00, 0x00, // [0x8c] jump continue
    // notOne:
    //     cmp string[i] '2'
    //     jneq notTwo
        OPCODE_LUI,     0x90,  '2', 0x00, // [0x90] r9 <- '2' 
        OPCODE_LLI,     0x90, 0x00, 0x00, // [0x94] r9 <- '2' 
        OPCODE_LUI,     0x80, 0xb4, 0x00, // [0x98] r8 <- 0x00b4 - notTwo
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x9c] r8 <- 0x0000 - notTwo
        OPCODE_BNE,     0x79, 0x80, 0x00, // [0xa0] if r7 != r9 then pc <- r8
    //     add val val 2 
        OPCODE_ADDI,    0x33, 0x02, 0x00, // [0xa4] r3 <- r3 + 2 - val += 2
    //     jump continue
        OPCODE_LUI,     0x80, 0x20, 0x02, // [0xa8] r8 <- 0x0220 - continue
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0xac] r8 <- 0x0000 - continue
        OPCODE_JMP,     0x80, 0x00, 0x00, // [0xb0] jump continue
    // notTwo:
    //     cmp string[i] '3'
    //     jneq notThree
        OPCODE_LUI,     0x90,  '3', 0x00, // [0xb4] r9 <- '3' 
        OPCODE_LLI,     0x90, 0x00, 0x00, // [0xb8] r9 <- '3' 
        OPCODE_LUI,     0x80, 0xd8, 0x00, // [0xbc] r8 <- 0x00d8 - notThree
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0xc0] r8 <- 0x0000 - notThree
        OPCODE_BNE,     0x79, 0x80, 0x00, // [0xc4] if r7 != r9 then pc <- r8
    //     add val val 3 
        OPCODE_ADDI,    0x33, 0x03, 0x00, // [0xc8] r3 <- r3 + 3 - val += 3
    //     jump continue
        OPCODE_LUI,     0x80, 0x20, 0x02, // [0xcc] r8 <- 0x0220 - continue
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0xd0] r8 <- 0x0000 - continue
        OPCODE_JMP,     0x80, 0x00, 0x00, // [0xd4] jump continue
    // notThree:
    //     cmp string[i] '4'
    //     jneq notFour
        OPCODE_LUI,     0x90,  '4', 0x00, // [0xd8] r9 <- '4' 
        OPCODE_LLI,     0x90, 0x00, 0x00, // [0xdc] r9 <- '4' 
        OPCODE_LUI,     0x80, 0xfc, 0x00, // [0xe0] r8 <- 0x00fc - notFour
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0xe4] r8 <- 0x0000 - notFour
        OPCODE_BNE,     0x79, 0x80, 0x00, // [0xe8] if r7 != r9 then pc <- r8
    //     add val val 4 
        OPCODE_ADDI,    0x33, 0x04, 0x00, // [0xec] r3 <- r3 + 4 - val += 4
    //     jump continue
        OPCODE_LUI,     0x80, 0x20, 0x02, // [0xf0] r8 <- 0x0220 - continue
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0xf4] r8 <- 0x0000 - continue
        OPCODE_JMP,     0x80, 0x00, 0x00, // [0xf8] jump continue
    // notFour:
    //     cmp string[i] '5'
    //     jneq notFive
        OPCODE_LUI,     0x90,  '5', 0x00, // [0xfc] r9 <- '5' 
        OPCODE_LLI,     0x90, 0x00, 0x00, // [0x100] r9 <- '5' 
        OPCODE_LUI,     0x80, 0x20, 0x01, // [0x104] r8 <- 0x0120 - notFive
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x108] r8 <- 0x0000 - notFive
        OPCODE_BNE,     0x79, 0x80, 0x00, // [0x10c] if r7 != r9 then pc <- r8
    //     add val val 5 
        OPCODE_ADDI,    0x33, 0x05, 0x00, // [0x110] r3 <- r3 + 5 - val += 5
    //     jump continue
        OPCODE_LUI,     0x80, 0x20, 0x02, // [0x114] r8 <- 0x0220 - continue
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x118] r8 <- 0x0000 - continue
        OPCODE_JMP,     0x80, 0x00, 0x00, // [0x11c] jump continue
    // notFive:
    //     cmp string[i] '6'
    //     jneq notSix
        OPCODE_LUI,     0x90,  '6', 0x00, // [0x120] r9 <- '6' 
        OPCODE_LLI,     0x90, 0x00, 0x00, // [0x124] r9 <- '6' 
        OPCODE_LUI,     0x80, 0x44, 0x01, // [0x128] r8 <- 0x0144 - notSix
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x12c] r8 <- 0x0000 - notSix
        OPCODE_BNE,     0x79, 0x80, 0x00, // [0x130] if r7 != r9 then pc <- r8
    //     add val val 6 
        OPCODE_ADDI,    0x33, 0x06, 0x00, // [0x134] r3 <- r3 + 6 - val += 6
    //     jump continue
        OPCODE_LUI,     0x80, 0x20, 0x02, // [0x138] r8 <- 0x0220 - continue
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x13c] r8 <- 0x0000 - continue
        OPCODE_JMP,     0x80, 0x00, 0x00, // [0x140] jump continue
    // notSix:
    //     cmp string[i] '7'
    //     jneq notSeven
        OPCODE_LUI,     0x90,  '7', 0x00, // [0x144] r9 <- '7' 
        OPCODE_LLI,     0x90, 0x00, 0x00, // [0x148] r9 <- '7' 
        OPCODE_LUI,     0x80, 0x68, 0x01, // [0x14c] r8 <- 0x0168 - notSeven
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x150] r8 <- 0x0000 - notSeven
        OPCODE_BNE,     0x79, 0x80, 0x00, // [0x154] if r7 != r9 then pc <- r8
    //     add val val 7 
        OPCODE_ADDI,    0x33, 0x07, 0x00, // [0x158] r3 <- r3 + 7 - val += 7
    //     jump continue
        OPCODE_LUI,     0x80, 0x20, 0x02, // [0x15c] r8 <- 0x0220 - continue
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x160] r8 <- 0x0000 - continue
        OPCODE_JMP,     0x80, 0x00, 0x00, // [0x164] jump continue
    // notSeven:
    //     cmp string[i] '8'
    //     jneq notEight
        OPCODE_LUI,     0x90,  '8', 0x00, // [0x168] r9 <- '8' 
        OPCODE_LLI,     0x90, 0x00, 0x00, // [0x16c] r9 <- '8' 
        OPCODE_LUI,     0x80, 0x8c, 0x01, // [0x170] r8 <- 0x018c - notEight
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x174] r8 <- 0x0000 - notEight
        OPCODE_BNE,     0x79, 0x80, 0x00, // [0x178] if r7 != r9 then pc <- r8
    //     add val val 8 
        OPCODE_ADDI,    0x33, 0x08, 0x00, // [0x17c] r3 <- r3 + 8 - val += 8
    //     jump continue
        OPCODE_LUI,     0x80, 0x20, 0x02, // [0x180] r8 <- 0x0220 - continue
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x184] r8 <- 0x0000 - continue
        OPCODE_JMP,     0x80, 0x00, 0x00, // [0x188] jump continue
    // notEight:
    //     cmp string[i] '9'
    //     jneq notNine
        OPCODE_LUI,     0x90,  '9', 0x00, // [0x18c] r9 <- '9' 
        OPCODE_LLI,     0x90, 0x00, 0x00, // [0x190] r9 <- '9' 
        OPCODE_LUI,     0x80, 0xb0, 0x01, // [0x194] r8 <- 0x01b0 - notNine
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x198] r8 <- 0x0000 - notNine
        OPCODE_BNE,     0x79, 0x80, 0x00, // [0x19c] if r7 != r9 then pc <- r8
    //     add val val 9 
        OPCODE_ADDI,    0x33, 0x09, 0x00, // [0x1a0] r3 <- r3 + 9 - val += 9
    //     jump continue
        OPCODE_LUI,     0x80, 0x20, 0x02, // [0x1a4] r8 <- 0x0220 - continue
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x1a8] r8 <- 0x0000 - continue
        OPCODE_JMP,     0x80, 0x00, 0x00, // [0x1ac] jump continue
    // notNine:
    //     cmp string[i] '0'
    //     jneq error
        OPCODE_LUI,     0x90,  '0', 0x00, // [0x1b0] r9 <- '0' 
        OPCODE_LLI,     0x90, 0x00, 0x00, // [0x1b4] r9 <- '0' 
        OPCODE_LUI,     0x80, 0xd4, 0x01, // [0x1b8] r8 <- 0x01d4 - error
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x1bc] r8 <- 0x0000 - error
        OPCODE_BNE,     0x79, 0x80, 0x00, // [0x1c0] if r7 != r9 then pc <- r8
    //     add val val 0 
        OPCODE_ADDI,    0x33, 0x00, 0x00, // [0x1c4] r3 <- r3 + 0 - val += 0
    //     jump continue
        OPCODE_LUI,     0x80, 0x20, 0x02, // [0x1c8] r8 <- 0x0220 - continue
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x1cc] r8 <- 0x0000 - continue
        OPCODE_JMP,     0x80, 0x00, 0x00, // [0x1d0] jump continue
    // error:
    //     print 'e'
        OPCODE_LUI,     0x90,  'e', 0x00, // [0x1d4] r9 <- 'e' 
        OPCODE_LLI,     0x90, 0x00, 0x00, // [0x1d8] r9 <- 'e' 
        OPCODE_PUTCHAR, 0x90, 0x00, 0x00, // [0x1dc] putchar(r9)
    //     print 'r'
        OPCODE_LUI,     0x90,  'r', 0x00, // [0x1e0] r9 <- 'r' 
        OPCODE_LLI,     0x90, 0x00, 0x00, // [0x1e4] r9 <- 'r' 
        OPCODE_PUTCHAR, 0x90, 0x00, 0x00, // [0x1e8] putchar(r9)
    //     print 'r'
        OPCODE_LUI,     0x90,  'r', 0x00, // [0x1ec] r9 <- 'r' 
        OPCODE_LLI,     0x90, 0x00, 0x00, // [0x1f0] r9 <- 'r' 
        OPCODE_PUTCHAR, 0x90, 0x00, 0x00, // [0x1f4] putchar(r9)
    //     print 'o'
        OPCODE_LUI,     0x90,  'o', 0x00, // [0x1f8] r9 <- 'o' 
        OPCODE_LLI,     0x90, 0x00, 0x00, // [0x1fc] r9 <- 'o' 
        OPCODE_PUTCHAR, 0x90, 0x00, 0x00, // [0x200] putchar(r9)
    //     println 'r'
        OPCODE_LUI,     0x90,  'r', 0x00, // [0x204] r9 <- 'r' 
        OPCODE_LLI,     0x90, 0x00, 0x00, // [0x208] r9 <- 'r' 
        OPCODE_PUTCHAR, 0x90, 0x00, 0x00, // [0x20c] putchar(r9)
        OPCODE_LUI,     0x90, '\n', 0x00, // [0x210] r9 <- '\n' 
        OPCODE_LLI,     0x90, 0x00, 0x00, // [0x214] r9 <- '\n' 
        OPCODE_PUTCHAR, 0x90, 0x00, 0x00, // [0x218] putchar(r9)
    //     println string[i]
    //     halt 
        OPCODE_HLT,     0x90, 0x00, 0x00, // [0x21c] exit program
    // continue:
    //     add i i 1
        OPCODE_ADDI,    0x44, 0x01, 0x00, // [0x220] r4 <- r4 + 1 - ++i
    //     jump while00
        OPCODE_LUI,     0x80, 0x54, 0x00, // [0x224] r8 <- 0x0054 - while00
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x228] r8 <- 0x0000 - while00
        OPCODE_JMP,     0x80, 0x00, 0x00, // [0x22c] jump while00
    // endwhile00:
    //     return val 
        OPCODE_ADDI,    0xd3, 0x00, 0x00, // [0x230] ra <- r3 + 0
        // function epilogue 
        OPCODE_POP,     0x90, 0x00, 0x00, // [0x234] pop r9 - restore caller's r9
        OPCODE_POP,     0x80, 0x00, 0x00, // [0x238] pop r8 - restore caller's r8
        OPCODE_POP,     0x70, 0x00, 0x00, // [0x23c] pop r7 - restore caller's r7
        OPCODE_POP,     0x60, 0x00, 0x00, // [0x240] pop r6 - restore caller's r6
        OPCODE_POP,     0x50, 0x00, 0x00, // [0x244] pop r5 - restore caller's r5
        OPCODE_POP,     0x40, 0x00, 0x00, // [0x248] pop r4 - restore caller's r4
        OPCODE_POP,     0x30, 0x00, 0x00, // [0x24c] pop r3 - restore caller's r3
        OPCODE_POP,     0x20, 0x00, 0x00, // [0x250] pop r2 - restore caller's r2
        OPCODE_POP,     0x10, 0x00, 0x00, // [0x254] pop r1 - restore caller's r1
        OPCODE_POP,     0x00, 0x00, 0x00, // [0x258] pop r0 - restore caller's r0 
        OPCODE_ADDI,    0xfe, 0x00, 0x00, // [0x25c] sp <- bp - remove local vars 
        OPCODE_POP,     0xe0, 0x00, 0x00, // [0x260] bp <- [sp] - restore caller bp
        OPCODE_RET,     0x00, 0x00, 0x00, // [0x264] return from function
    // endstringToInt
        // 0x00,           0x00, 0x00, 0x00, // [0x228] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x22c] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x230] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x234] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x238] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x23c] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x240] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x244] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x248] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x24c] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x250] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x254] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x258] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x25c] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x260] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x264] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x268] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x26c] fluff bytes 

    // //========================================================================
    // // returns the larger of the given two parameters 
    // int max(int a, int b);
    // max: 
        // function prologue 
        OPCODE_PUSH,    0xe0, 0x00, 0x00, // [0x270] push bp - save caller's bp 
        OPCODE_ADDI,    0xef, 0x00, 0x00, // [0x274] bp <- sp + 0
        OPCODE_PUSH,    0x00, 0x00, 0x00, // [0x278] push r0 - save caller's r0
        OPCODE_PUSH,    0x10, 0x00, 0x00, // [0x27c] push r1 - save caller's r1 
        OPCODE_PUSH,    0x80, 0x00, 0x00, // [0x280] push r8 - save caller's r8 
    //     stackget a 0
        OPCODE_LW,      0x0e, 0x08, 0x00, // [0x284] r0 <- [bp+8] - arg a
    //     stackget b 1
        OPCODE_LW,      0x1e, 0x0c, 0x00, // [0x288] r1 <- [bp+12] - arg b
    //     cmp a b
    //     jge greater
        OPCODE_LUI,     0x80, 0xa8, 0x02, // [0x28c] r8 <- 0x02a8 - greater
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x290] r8 <- 0x0000 - greater
        OPCODE_BGT,     0x01, 0x80, 0x00, // [0x294] if r0 > r1 then pc <- r8
    //     return b
        OPCODE_ADDI,    0xd1, 0x00, 0x00, // [0x298] ra <- r1 + 0
        OPCODE_LUI,     0x80, 0xb8, 0x02, // [0x29c] r8 <- 0x02b8 - epilogue
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x2a0] r8 <- 0x0000 - epilogue
        OPCODE_JMP,     0x80, 0x00, 0x00, // [0x2a4] pc <- r8
    // greater:
    //     return a
        OPCODE_ADDI,    0xd0, 0x00, 0x00, // [0x2a8] ra <- r0 + 0
        OPCODE_LUI,     0x80, 0xb8, 0x02, // [0x2ac] r8 <- 0x02b8 - epilogue
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x2b0] r8 <- 0x0000 - epilogue
        OPCODE_JMP,     0x80, 0x00, 0x00, // [0x2b4] pc <- r8
    // epilogue:
        // function epilogue 
        OPCODE_POP,     0x80, 0x00, 0x00, // [0x2b8] pop r8 - restore caller's r8
        OPCODE_POP,     0x10, 0x00, 0x00, // [0x2bc] pop r1 - restore caller's r1
        OPCODE_POP,     0x00, 0x00, 0x00, // [0x2c0] pop r0 - restore caller's r0 
        OPCODE_ADDI,    0xfe, 0x00, 0x00, // [0x2c4] sp <- bp - remove local vars 
        OPCODE_POP,     0xe0, 0x00, 0x00, // [0x2c8] bp <- [sp] - restore caller bp
        OPCODE_RET,     0x00, 0x00, 0x00, // [0x2cc] return from function
    // endmax
        0x00,           0x00, 0x00, 0x00, // [0x2d0] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x2d4] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x2d8] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x2dc] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x2e0] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x2e4] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x2e8] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x2ec] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x2f0] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x2f4] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x2f8] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x2fc] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x300] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x304] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x308] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x30c] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x310] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x314] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x318] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x31c] fluff bytes 

    // //========================================================================

    // reads until newline [or EOF - not implemented]
    // void getline (char buf[]);
    // getline:
        // function prologue 
        OPCODE_PUSH,    0xe0, 0x00, 0x00, // [0x320] push bp - save caller's bp 
        OPCODE_ADDI,    0xef, 0x00, 0x00, // [0x324] bp <- sp + 0
        OPCODE_PUSH,    0x00, 0x00, 0x00, // [0x328] push r0 - save caller's r0
        OPCODE_PUSH,    0x10, 0x00, 0x00, // [0x32c] push r1 - save caller's r1 
        OPCODE_PUSH,    0x20, 0x00, 0x00, // [0x330] push r2 - save caller's r2
        OPCODE_PUSH,    0x60, 0x00, 0x00, // [0x334] push r6 - save caller's r6
        OPCODE_PUSH,    0x70, 0x00, 0x00, // [0x338] push r7 - save caller's r7
        OPCODE_PUSH,    0x80, 0x00, 0x00, // [0x33c] push r8 - save caller's r8 
        // function body
    // char buf[80]; 
        // buffer array is passed as param
        OPCODE_LW,      0x7e, 0x08, 0x00, // [0x340] r7 <- [bp+8] - arg buf
    // int i = 0; 
        OPCODE_LUI,     0x00, 0x00, 0x00, // [0x344] r0 <- 0x0000 - i
        OPCODE_LLI,     0x00, 0x00, 0x00, // [0x348] r0 <- 0x0000 - i
    // char c = getchar();
        OPCODE_GETCHAR, 0x10, 0x00, 0x00, // [0x34c] r1 <- getchar()
    // getline_while (c != '\n')
    // {
        OPCODE_LUI,     0x20, '\n', 0x00, // [0x350] r2 <- '\n'
        OPCODE_LLI,     0x20, 0x00, 0x00, // [0x354] r2 <- '\n'
        OPCODE_LUI,     0x80, 0x80, 0x03, // [0x358] r8 <- 0x0380 - getline_endwhile
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x35c] r8 <- 0x0000 - getline_endwhile
        OPCODE_BEQ,     0x12, 0x80, 0x00, // [0x360] if r1 == r2 then pc <- r8
    //     buf[i] = c;
        OPCODE_ADD,     0x67, 0x00, 0x00, // [0x364] r6 <- r7 + r0 -  buf+i
        OPCODE_SB,      0x61, 0x00, 0x00, // [0x368] [r6+0] <- c 
    //     i += 1;
        OPCODE_ADDI,    0x00, 0x01, 0x00, // [0x36c] r0 <- r0 + 1
    //     c = getchar();
        OPCODE_GETCHAR, 0x10, 0x00, 0x00, // [0x370] r1 <- getchar()
    // }
        OPCODE_LUI,     0x80, 0x50, 0x03, // [0x374] r8 <- 0x0350 - getline_while
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x378] r8 <- 0x0000 - getline_while
        OPCODE_JMP,     0x80, 0x00, 0x00, // [0x37c] pc <- r8
    // getline_endwhile
        // no need to return, buf has line
        // should end in \0
        OPCODE_LUI,     0x10, '\0', 0x00, // [0x380] r1 <- '\0'    - 
        OPCODE_LLI,     0x10, 0x00, 0x00, // [0x384] r1 <- 0x0000  - 
        OPCODE_ADD,     0x67, 0x00, 0x00, // [0x388] r6 <- r7 + r0 - buf+i
        OPCODE_SB,      0x61, 0x00, 0x00, // [0x38c] [r6+0] <- r1  - buf[i] = '\0'

        // function epilogue 
        OPCODE_POP,     0x80, 0x00, 0x00, // [0x390] pop r8 - restore caller's r8
        OPCODE_POP,     0x70, 0x00, 0x00, // [0x394] pop r7 - restore caller's r7
        OPCODE_POP,     0x60, 0x00, 0x00, // [0x398] pop r6 - restore caller's r6
        OPCODE_POP,     0x20, 0x00, 0x00, // [0x39c] pop r2 - restore caller's r2
        OPCODE_POP,     0x10, 0x00, 0x00, // [0x3a0] pop r1 - restore caller's r1
        OPCODE_POP,     0x00, 0x00, 0x00, // [0x3a4] pop r0 - restore caller's r0 
        OPCODE_ADDI,    0xfe, 0x00, 0x00, // [0x3a8] sp <- bp - remove local vars 
        OPCODE_POP,     0xe0, 0x00, 0x00, // [0x3ac] bp <- [sp] - restore caller bp
        OPCODE_RET,     0x00, 0x00, 0x00, // [0x3b0] return from function
    // endgetline
        // 0x00,           0x00, 0x00, 0x00, // [0x3a4] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x3a8] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x3ac] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x3b0] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x3b4] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x3b8] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x3bc] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x3c0] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x3c4] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x3c8] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x3cc] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x3d0] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x3d4] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x3d8] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x3dc] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x3e0] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x3e4] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x3e8] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x3ec] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x3f0] fluff bytes 

    // //========================================================================

    // main:
        // function prologue 
        OPCODE_PUSH,    0xe0, 0x00, 0x00, // [0x3f4] push bp - save caller's bp 
        OPCODE_ADDI,    0xef, 0x00, 0x00, // [0x3f8] bp <- sp + 0
        OPCODE_SUBI,    0xff, 0x0c, 0x00, // [0x3fc] sp <- sp - 3*4 allocate local vars
        // [bp-4]  : n 
        // [bp-8]  : h 
        // [bp-12] : v  
        OPCODE_PUSH,    0x00, 0x00, 0x00, // [0x400] push r0 - save caller's r0
        OPCODE_PUSH,    0x10, 0x00, 0x00, // [0x404] push r1 - save caller's r1 
        OPCODE_PUSH,    0x20, 0x00, 0x00, // [0x408] push r2 - save caller's r2
        OPCODE_PUSH,    0x60, 0x00, 0x00, // [0x40c] push r6 - save caller's r6
        OPCODE_PUSH,    0x70, 0x00, 0x00, // [0x410] push r7 - save caller's r7
        OPCODE_PUSH,    0x80, 0x00, 0x00, // [0x414] push r8 - save caller's r8 

    //     char buf[80]; - on stack 
        OPCODE_SUBI,    0xff, 0x50, 0x00, // [0x418] sp <- sp - 80
        OPCODE_ADDI,    0x0f, 0x00, 0x00, // [0x41c] r0 <- sp + 0  - r0 is buf pointer
    //     call getline (buf)
        OPCODE_LUI,     0x80, 0x20, 0x03, // [0x420] r8 <- 0x0320 - getline addr
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x424] r8 <- 0x0000 - getline addr
        OPCODE_PUSH,    0x00, 0x00, 0x00, // [0x428] push r0 - push buf (arg0) 
        OPCODE_CALL,    0x80, 0x00, 0x00, // [0x42c] call r8 - call getline 
        OPCODE_POP,     0x00, 0x00, 0x00, // [0x430] pop r0  - pop arg0 



    //     // break up line into the three nums
    //     assign begin1 0
        OPCODE_LUI,     0x10, 0x00, 0x00, // [0x434] r1 <- 0x0000 - begin1
        OPCODE_LLI,     0x10, 0x00, 0x00, // [0x438] r1 <- 0x0000 - begin1
    //     assign end1 0
        OPCODE_LUI,     0x20, 0x00, 0x00, // [0x43c] r2 <- 0x0000 - end1
        OPCODE_LLI,     0x20, 0x00, 0x00, // [0x440] r2 <- 0x0000 - end1
    // while01:
    //     cmp line[end1] ' '
    //     jeq endwhile01
        OPCODE_ADD,     0x30, 0x20, 0x00, // [0x444] r3 <- r0 + r2 - line + end1
        OPCODE_LB,      0x43, 0x00, 0x00, // [0x448] r4 <- [r3 + 0] - mem[line + end1]
        OPCODE_LUI,     0x50,  ' ', 0x00, // [0x44c] r5 <- ' '  
        OPCODE_LLI,     0x50, 0x00, 0x00, // [0x450] r5 <- ' ' 
        OPCODE_LUI,     0x80, 0x70, 0x04, // [0x454] r8 <- 0x0470 - endwhile01
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x458] r8 <- 0x0000 - endwhile01
        OPCODE_BEQ,     0x45, 0x80, 0x00, // [0x45c] if r4 == r5 then pc <- r8

    //     add end1 end1 1 
        OPCODE_ADDI,    0x22, 0x01, 0x00, // [0x460] r2 <- r2 + 1 - ++end1
        // repeat
    //     jump while01
        OPCODE_LUI,     0x80, 0x44, 0x04, // [0x464] r8 <- 0x0444 - while01
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x468] r8 <- 0x0000 - while01
        OPCODE_JMP,     0x80, 0x00, 0x00, // [0x46c] pc <- r8
    // endwhile01: 

    //     add begin2 end1 1
        OPCODE_ADDI,    0x32, 0x01, 0x00, // [0x470] r3 <- r2 + 1 - begin2 = end1+1
    //     assign end2 begin2
        OPCODE_ADDI,    0x43, 0x00, 0x00, // [0x474] r4 <- r3 + 0 - end2 = begin2
    // while02:
    //     cmp line[end2] ' '
    //     jeq endwhile02
        OPCODE_ADD,     0x50, 0x40, 0x00, // [0x478] r5 <- r0 + r4 - line + end2
        OPCODE_LB,      0x65, 0x00, 0x00, // [0x47c] r6 <- [r5 + 0] - mem[line + end2]
        OPCODE_LUI,     0x70,  ' ', 0x00, // [0x480] r7 <- ' '  
        OPCODE_LLI,     0x70, 0x00, 0x00, // [0x484] r7 <- ' ' 
        OPCODE_LUI,     0x80, 0xa4, 0x04, // [0x488] r8 <- 0x04a4 - endwhile02
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x48c] r8 <- 0x0000 - endwhile02
        OPCODE_BEQ,     0x67, 0x80, 0x00, // [0x490] if r6 == r7 then pc <- r8

    //     add end2 end2 1 
        OPCODE_ADDI,    0x44, 0x01, 0x00, // [0x494] r4 <- r4 + 1 - ++end2
        // repeat
    //     jump while02
        OPCODE_LUI,     0x80, 0x78, 0x04, // [0x498] r8 <- 0x0478 - while02
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x49c] r8 <- 0x0000 - while02
        OPCODE_JMP,     0x80, 0x00, 0x00, // [0x4a0] pc <- r8
    // endwhile02: 

    //     add begin3 end2 1
        OPCODE_ADDI,    0x54, 0x01, 0x00, // [0x4a4] r5 <- r4 + 1 - begin3 = end2+1
    //     sizeof end3 line
        OPCODE_ADDI,    0x65, 0x00, 0x00, // [0x4a8] r6 <- r5 + 0 - end3 = begin3
    // while03:
    //     cmp line[end3] '\0'
    //     jeq endwhile03
        OPCODE_ADD,     0x70, 0x60, 0x00, // [0x4ac] r7 <- r0 + r6 - line + end3
        OPCODE_LB,      0x77, 0x00, 0x00, // [0x4b0] r7 <- [r7 + 0] - mem[line + end3]
        OPCODE_LUI,     0x90, '\0', 0x00, // [0x4b4] r9 <- '\0'  
        OPCODE_LLI,     0x90, 0x00, 0x00, // [0x4b8] r9 <- '\0' 
        OPCODE_LUI,     0x80, 0xd8, 0x04, // [0x4bc] r8 <- 0x04d8 - endwhile03
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x4c0] r8 <- 0x0000 - endwhile03
        OPCODE_BEQ,     0x79, 0x80, 0x00, // [0x4c4] if r7 == r9 then pc <- r8

    //     add end3 end3 1 
        OPCODE_ADDI,    0x66, 0x01, 0x00, // [0x4c8] r6 <- r6 + 1 - ++end3
        // repeat
    //     jump while03
        OPCODE_LUI,     0x80, 0xac, 0x04, // [0x4cc] r8 <- 0x04ac - while03
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x4d0] r8 <- 0x0000 - while03
        OPCODE_JMP,     0x80, 0x00, 0x00, // [0x4d4] pc <- r8
    // endwhile03: 

    //     push end1
        OPCODE_PUSH,    0x20, 0x00, 0x00, // [0x4d8] push r2 - end1 
    //     push begin1
        OPCODE_PUSH,    0x10, 0x00, 0x00, // [0x4dc] push r1 - begin1 
    //     push line
        OPCODE_PUSH,    0x00, 0x00, 0x00, // [0x4e0] push r0 - line 
    //     call stringToInt
        OPCODE_LUI,     0x80, 0x0c, 0x00, // [0x4e4] r8 <- 0x000c - stringToInt
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x4e8] r8 <- 0x0000 - stringToInt
        OPCODE_CALL,    0x80, 0x00, 0x00, // [0x4ec] call r8
    //     response n
        OPCODE_SW,      0xed, 0xfc, 0xff, // [0x4f0] [bp - 4] <- ra  0xfffc
    //     pop null 
        OPCODE_POP,     0xa0, 0x00, 0x00, // [0x4f4] pop r10 - line 
    //     pop null
        OPCODE_POP,     0xa0, 0x00, 0x00, // [0x4f8] pop r10 - begin1  
    //     pop null
        OPCODE_POP,     0xa0, 0x00, 0x00, // [0x4fc] pop r10 - end1 

    //     push end2
        OPCODE_PUSH,    0x40, 0x00, 0x00, // [0x500] push r4 - end2
    //     push begin2
        OPCODE_PUSH,    0x30, 0x00, 0x00, // [0x504] push r3 - begin2
    //     push line
        OPCODE_PUSH,    0x00, 0x00, 0x00, // [0x508] push r0 - line 
    //     call stringToInt
        OPCODE_LUI,     0x80, 0x0c, 0x00, // [0x50c] r8 <- 0x000c - stringToInt
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x510] r8 <- 0x0000 - stringToInt
        OPCODE_CALL,    0x80, 0x00, 0x00, // [0x514] call r8
    //     response h
        OPCODE_SW,      0xed, 0xf8, 0xff, // [0x518] [bp - 8] <- ra   0xfff8
    //     pop null 
        OPCODE_POP,     0xa0, 0x00, 0x00, // [0x51c] pop r10 - line 
    //     pop null
        OPCODE_POP,     0xa0, 0x00, 0x00, // [0x520] pop r10 - begin2
    //     pop null
        OPCODE_POP,     0xa0, 0x00, 0x00, // [0x524] pop r10 - end2

    //     push end3
        OPCODE_PUSH,    0x60, 0x00, 0x00, // [0x528] push r6 - end3
    //     push begin3
        OPCODE_PUSH,    0x50, 0x00, 0x00, // [0x52c] push r5 - begin3
    //     push line
        OPCODE_PUSH,    0x00, 0x00, 0x00, // [0x530] push r0 - line 
    //     call stringToInt
        OPCODE_LUI,     0x80, 0x0c, 0x00, // [0x534] r8 <- 0x000c - stringToInt
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x538] r8 <- 0x0000 - stringToInt
        OPCODE_CALL,    0x80, 0x00, 0x00, // [0x53c] call r8
    //     response v
        OPCODE_SW,      0xed, 0xf4, 0xff, // [0x540] [bp - 12] <- ra  0xfff4
    //     pop null 
        OPCODE_POP,     0xa0, 0x00, 0x00, // [0x544] pop r10 - line 
    //     pop null
        OPCODE_POP,     0xa0, 0x00, 0x00, // [0x548] pop r10 - begin3
    //     pop null
        OPCODE_POP,     0xa0, 0x00, 0x00, // [0x54c] pop r10 - end3

    //     subtract nh n h
        OPCODE_LW,      0x0e, 0xfc, 0xff, // [0x550] r0 <- [bp - 4] - n
        OPCODE_LW,      0x1e, 0xf8, 0xff, // [0x554] r1 <- [bp - 8] - h
        OPCODE_SUB,     0x20, 0x10, 0x00, // [0x558] r2 <- r0 - r1  - nh
    //     subtract nv n v
        OPCODE_LW,      0x3e, 0xf4, 0xff, // [0x55c] r3 <- [bp - 12] - v
        OPCODE_SUB,     0x40, 0x30, 0x00, // [0x560] r4 <- r0 - r3  - nv

    //     push h
        OPCODE_PUSH,    0x10, 0x00, 0x00, // [0x564] push r1 - h
    //     push nh
        OPCODE_PUSH,    0x20, 0x00, 0x00, // [0x568] push r2 - nh
    //     call max
        OPCODE_LUI,     0x80, 0x70, 0x02, // [0x56c] r8 <- 0x0270 - max
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x570] r8 <- 0x0000 - max
        OPCODE_CALL,    0x80, 0x00, 0x00, // [0x574] call r8
    //     response lhs
        OPCODE_ADDI,    0x5d, 0x00, 0x00, // [0x578] r5 <- ra + 0 - lhs 
    //     pop null
        OPCODE_POP,     0xa0, 0x00, 0x00, // [0x57c] pop r10 - nh
    //     pop null
        OPCODE_POP,     0xa0, 0x00, 0x00, // [0x580] pop r10 - h

    //     push v
        OPCODE_PUSH,    0x30, 0x00, 0x00, // [0x584] push r3 - v
    //     push nv
        OPCODE_PUSH,    0x40, 0x00, 0x00, // [0x588] push r4 - nv
    //     call max 
        OPCODE_LUI,     0x80, 0x70, 0x02, // [0x58c] r8 <- 0x0270 - max
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x590] r8 <- 0x0000 - max
        OPCODE_CALL,    0x80, 0x00, 0x00, // [0x594] call r8
    //     response rhs
        OPCODE_ADDI,    0x6d, 0x00, 0x00, // [0x598] r6 <- ra + 0 - rhs 
    //     pop null
        OPCODE_POP,     0xa0, 0x00, 0x00, // [0x59c] pop r10 - nv
    //     pop null
        OPCODE_POP,     0xa0, 0x00, 0x00, // [0x5a0] pop r10 - v

    //     multiply res lhs rhs
        OPCODE_MUL,     0x05, 0x60, 0x00, // [0x5a4] r0 <- r5 * r6 - res = lhs*rhs
    //     multiply res res 4
        OPCODE_MULI,    0x00, 0x04, 0x00, // [0x5a8] r0 <- r0 * 4  - res *= 4

    //     println res
        OPCODE_PUSH,    0x00, 0x00, 0x00, // [0x5ac] push r0 - arg0
        OPCODE_LUI,     0x80, 0x44, 0x06, // [0x5b0] r8 <- 0x0644 - print_int
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x5b4] r8 <- 0x0000 - print_int
        OPCODE_CALL,    0x80, 0x00, 0x00, // [0x5b8] call r8
        OPCODE_POP,     0x00, 0x00, 0x00, // [0x5bc] pop r0 - arg0

        // function epilogue 
        OPCODE_POP,     0x80, 0x00, 0x00, // [0x5c0] pop r8 - restore caller's r8
        OPCODE_POP,     0x70, 0x00, 0x00, // [0x5c4] pop r7 - restore caller's r7
        OPCODE_POP,     0x60, 0x00, 0x00, // [0x5c8] pop r6 - restore caller's r6
        OPCODE_POP,     0x20, 0x00, 0x00, // [0x5cc] pop r2 - restore caller's r2
        OPCODE_POP,     0x10, 0x00, 0x00, // [0x5d0] pop r1 - restore caller's r1
        OPCODE_POP,     0x00, 0x00, 0x00, // [0x5d4] pop r0 - restore caller's r0 
        OPCODE_ADDI,    0xfe, 0x00, 0x00, // [0x5d8] sp <- bp - remove local vars 
        OPCODE_POP,     0xe0, 0x00, 0x00, // [0x5dc] bp <- [sp] - restore caller bp
        OPCODE_HLT,     0x00, 0x00, 0x00, // [0x5e0] end of program
    // endmain
        // 0x00,           0x00, 0x00, 0x00, // [0x5d0] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x5d4] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x5d8] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x5dc] fluff bytes 
        // 0x00,           0x00, 0x00, 0x00, // [0x5e0] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x5e4] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x5e8] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x5ec] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x5f0] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x5f4] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x5f8] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x5fc] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x600] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x604] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x608] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x60c] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x610] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x614] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x618] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x61c] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x620] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x624] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x628] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x62c] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x630] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x634] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x638] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x63c] fluff bytes 
        0x00,           0x00, 0x00, 0x00, // [0x640] fluff bytes 

    // //========================================================================

    // void pr_int(int n) {
    // if (n < 0) {
    //     putchar('-');
    //     n = -n;
    // }
    // if (n / 10 != 0)
    //     pr_int(n / 10);
    // putchar((n % 10) + '0');
    // }
    // print_int: 
    // function prologue
        OPCODE_PUSH,    0xe0, 0x00, 0x00, // [0x644] push bp - save caller's bp 
        OPCODE_ADDI,    0xef, 0x00, 0x00, // [0x648] bp <- sp + 0
        // no local vars 
        OPCODE_PUSH,    0x00, 0x00, 0x00, // [0x64c] push r0 - save caller's r0
        OPCODE_PUSH,    0x10, 0x00, 0x00, // [0x650] push r1 - save caller's r1 
        OPCODE_PUSH,    0x20, 0x00, 0x00, // [0x654] push r2 - save caller's r2
        OPCODE_PUSH,    0x60, 0x00, 0x00, // [0x658] push r6 - save caller's r6
        OPCODE_PUSH,    0x70, 0x00, 0x00, // [0x65c] push r7 - save caller's r7
        OPCODE_PUSH,    0x80, 0x00, 0x00, // [0x660] push r8 - save caller's r8 

    // function body 
        // stackget n 0
        OPCODE_LW,      0x0e, 0x08, 0x00, // [0x664] r0 <- [bp+8] - arg n
        // cmp n 0
        // jge endif0 
        OPCODE_LUI,     0x10, 0x00, 0x00, // [0x668] r1 <- 0x0000  
        OPCODE_LLI,     0x10, 0x00, 0x00, // [0x66c] r1 <- 0x0000 
        OPCODE_LUI,     0x80, 0x8c, 0x06, // [0x670] r8 <- 0x068c - endif0
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x674] r8 <- 0x0000 - endif0
        OPCODE_BGE,     0x01, 0x80, 0x00, // [0x678] if r0 >= r1 then pc <- r8

        // printchar '-'
        OPCODE_LUI,     0x10,  '-', 0x00, // [0x67c] r1 <- '-'  
        OPCODE_LLI,     0x10, 0x00, 0x00, // [0x680] r1 <- 0x0000 
        OPCODE_PUTCHAR, 0x10, 0x00, 0x00, // [0x684] PUTCHAR(r1) 

        // assign n -n
        OPCODE_MULI,    0x00, 0xff, 0xff, // [0x688] r0 <- r0 * -1

    // endif0:

        // assign temp n 
        OPCODE_ADDI,    0x10, 0x00, 0x00, // [0x68c] r1 <- r0 + 0
        // div temp 10
        OPCODE_DIVI,    0x11, 0x0a, 0x00, // [0x690] r1 <- r1 / 10
        // cmp temp 0 
        // jeq endif1
        OPCODE_LUI,     0x20, 0x00, 0x00, // [0x694] r2 <- 0x0000  
        OPCODE_LLI,     0x20, 0x00, 0x00, // [0x698] r2 <- 0x0000 
        OPCODE_LUI,     0x80, 0xbc, 0x06, // [0x69c] r8 <- 0x06bc - endif1
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x6a0] r8 <- 0x0000 - endif1
        OPCODE_BEQ,     0x12, 0x80, 0x00, // [0x6a4] if r0 >= r1 then pc <- r8

        // push temp
        OPCODE_PUSH,    0x10, 0x00, 0x00, // [0x6a8] push r1 - arg0
        // call pr_int
        OPCODE_LUI,     0x80, 0x44, 0x06, // [0x6ac] r8 <- 0x0644 - print_int
        OPCODE_LLI,     0x80, 0x00, 0x00, // [0x6b0] r8 <- 0x0000 - print_int
        OPCODE_CALL,    0x80, 0x00, 0x00, // [0x6b4] call r8
        // pop temp 
        OPCODE_POP,     0x10, 0x00, 0x00, // [0x6b8] pop r1 - arg0

    // endif1

        // assign temp n 
        OPCODE_ADDI,    0x10, 0x00, 0x00, // [0x6bc] r1 <- r0 + 0
        // mod temp temp 10
        OPCODE_MODI,    0x11, 0x0a, 0x00, // [0x6c0] modi r1 r1 10
        // add temp temp '0'
        OPCODE_ADDI,    0x11,  '0', 0x00, // [0x6c4] r1 <- r1 + '0'

        // printchar temp
        OPCODE_PUTCHAR, 0x10, 0x00, 0x00, // [0x6c8] PUTCHAR(r1) 

    // function epilogue 
        OPCODE_POP,     0x80, 0x00, 0x00, // [0x6cc] pop r8 - restore caller's r8
        OPCODE_POP,     0x70, 0x00, 0x00, // [0x6d0] pop r7 - restore caller's r7
        OPCODE_POP,     0x60, 0x00, 0x00, // [0x6d4] pop r6 - restore caller's r6
        OPCODE_POP,     0x20, 0x00, 0x00, // [0x6d8] pop r2 - restore caller's r2
        OPCODE_POP,     0x10, 0x00, 0x00, // [0x6dc] pop r1 - restore caller's r1
        OPCODE_POP,     0x00, 0x00, 0x00, // [0x6e0] pop r0 - restore caller's r0 
        OPCODE_ADDI,    0xfe, 0x00, 0x00, // [0x6e4] sp <- bp - remove local vars 
        OPCODE_POP,     0xe0, 0x00, 0x00, // [0x6e8] bp <- [sp] - restore caller bp
        OPCODE_RET,     0x00, 0x00, 0x00, // [0x6ec] end of function

    // endprint_int:


    };

    // move instructions into memory 
    std::memcpy (memory, instructions, sizeof(instructions));

    // print bytes 
    if (DEBUG)
    {
        printMemory (memory, MEMORY_SIZE_BYTES);
    }

    // execute instructions 
    if (DEBUG) printf ("Running Program\n");

    unsigned int currentInstructionAddress = 0x00;  // 4 byte (32-bit) instruction register
    // 2^4 32-bit (4-byte) registers
    byte* registers = (byte*) malloc (16 * 4);
    // r0-r12  - general purpose registers (Callee Saved - saved on stack)
    // r13    0xd - return value  (ra)
    byte ra = 13; 
    // r14    0xe - base pointer  (bp)
    byte bp = 14;
    // r15    0xf - stack pointer (sp)
    byte sp = 15; 

    // bp and sp start at the end of memory 
    *(int*)&registers[bp*4] = MEMORY_SIZE_BYTES - (MEMORY_SIZE_BYTES % 4); 
    *(int*)&registers[sp*4] = MEMORY_SIZE_BYTES - (MEMORY_SIZE_BYTES % 4); 

    while (currentInstructionAddress < MEMORY_SIZE_BYTES)
    {
        // we have to pack the instruction into the int using big endian 
        unsigned int instruction = memory[currentInstructionAddress];
        instruction = instruction << 8; 
        instruction |= memory[currentInstructionAddress+1];
        instruction = instruction << 8; 
        instruction |= memory[currentInstructionAddress+2];
        instruction = instruction << 8; 
        instruction |= memory[currentInstructionAddress+3];
        byte opcode = (0b11111111000000000000000000000000 & instruction) >> 24;

        if (DEBUG)
        {
            // print address
            printf (
                "0x%x%x%x%x%x%x%x%x | ", 
                (0b11110000000000000000000000000000 & currentInstructionAddress) >> 28,
                (0b00001111000000000000000000000000 & currentInstructionAddress) >> 24,
                (0b00000000111100000000000000000000 & currentInstructionAddress) >> 20,
                (0b00000000000011110000000000000000 & currentInstructionAddress) >> 16,
                (0b00000000000000001111000000000000 & currentInstructionAddress) >> 12,
                (0b00000000000000000000111100000000 & currentInstructionAddress) >>  8,
                (0b00000000000000000000000011110000 & currentInstructionAddress) >>  4,
                (0b00000000000000000000000000001111 & currentInstructionAddress) >>  0
            );
            // print instruction 
            printf (
                "%x%x %x%x %x%x %x%x\n", 
                (0b11110000000000000000000000000000 & instruction) >> 28,
                (0b00001111000000000000000000000000 & instruction) >> 24,
                (0b00000000111100000000000000000000 & instruction) >> 20,
                (0b00000000000011110000000000000000 & instruction) >> 16,
                (0b00000000000000001111000000000000 & instruction) >> 12,
                (0b00000000000000000000111100000000 & instruction) >>  8,
                (0b00000000000000000000000011110000 & instruction) >>  4,
                (0b00000000000000000000000000001111 & instruction) >>  0
            );
        }


        // LUI dest, imm        - loads upper immediate 16 bits into given register
        // XXXXXXXX dddd0000 iiiiiiii iiiiiiii
        if (opcode == OPCODE_LUI)
        {
            byte dest = (0b00000000111100000000000000000000 & instruction) >> 20;
            // imm acts as the upper 16 bits of the register 
            registers[dest*4+0] = (0b00000000000000001111111100000000 & instruction) >> 8; 
            registers[dest*4+1] = (0b00000000000000000000000011111111 & instruction) >> 0; 
        }
        // LLI dest, imm        - loads lower immediate 16 bits into given register
        // XXXXXXXX dddd0000 iiiiiiii iiiiiiii
        else if (opcode == OPCODE_LLI)
        {
            byte dest = (0b00000000111100000000000000000000 & instruction) >> 20;
            // imm acts as the lower 16 bits of the register 
            registers[dest*4+2] = (0b00000000000000001111111100000000 & instruction) >> 8; 
            registers[dest*4+3] = (0b00000000000000000000000011111111 & instruction) >> 0; 
        }
        // LB dest, offset(src) - load byte 
        // XXXXXXXX ddddssss oooooooo oooooooo
        // offset should be specified in little endian (least -> most significant byte)
        else if (opcode == OPCODE_LB)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int address = *(int*)&registers[src1*4];
            // read offset in little endian
            int offset = *(int16_t*)&memory[currentInstructionAddress+2];
            // clear register bytes
            *(int*)&(registers[dest*4]) = 0; 
            // read in byte 
            *(int*)&(registers[dest*4]) = (unsigned int)memory[address+offset];
        }
        // LH dest, offset(src) - load half (2 bytes)
        // XXXXXXXX ddddssss oooooooo oooooooo
        else if (opcode == OPCODE_LH)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int address = *(int*)&registers[src1*4];
            // read offset in little endian
            int offset = *(int16_t*)&memory[currentInstructionAddress+2];
            // clear register bytes
            *(int*)&(registers[dest*4]) = 0; 
            // read in half word (2 bytes) 
            *(int*)&(registers[dest*4]) = (unsigned int)*(short*)&memory[address+offset];
        }
        // LW dest, offset(src) - load word (4 bytes)
        // XXXXXXXX ddddssss oooooooo oooooooo
        else if (opcode == OPCODE_LW)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int address = *(int*)&registers[src1*4];
            // read offset in little endian
            int offset = *(int16_t*)&memory[currentInstructionAddress+2];
            // clear register bytes
            *(int*)&(registers[dest*4]) = 0; 
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = (unsigned int)*(int*)&memory[address+offset];
        }
        // SB offset(dest), src - store byte
        // XXXXXXXX ddddssss oooooooo oooooooo
        else if (opcode == OPCODE_SB)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int address = *(int*)&registers[dest*4];
            // read offset in little endian
            int offset = *(int16_t*)&memory[currentInstructionAddress+2];
            // store byte 
            *(byte*)&(memory[address+offset]) = *(byte*)&(registers[src1*4]);
        }
        // SH offset(dest), src - store half (2 bytes)
        // XXXXXXXX ddddssss oooooooo oooooooo
        else if (opcode == OPCODE_SH)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int address = *(int*)&registers[dest*4];
            // read offset in little endian
            int offset = *(int16_t*)&memory[currentInstructionAddress+2];
            // store half word (2 bytes)
            *(int16_t*)&(memory[address+offset]) = *(int16_t*)&(registers[src1*4]);
        }
        // SW offset(dest), src - store word (4 bytes)
        // XXXXXXXX ddddssss oooooooo oooooooo
        else if (opcode == OPCODE_SW)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int address = *(int*)&registers[dest*4];
            // read offset in little endian
            int offset = *(int16_t*)&memory[currentInstructionAddress+2];
            // store half word (2 bytes)
            *(int*)&(memory[address+offset]) = *(int*)&(registers[src1*4]);
        }

        // arithmetic instructions
        // ADD dest, src1, src2 - integer addition
        // XXXXXXXX ddddssss ssss0000 00000000
        else if (opcode == OPCODE_ADD)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            byte src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] + *(int*)&registers[src2*4];
        }
        // SUB dest, src1, src2 - integer subtraction
        // XXXXXXXX ddddssss ssss0000 00000000
        else if (opcode == OPCODE_SUB)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            byte src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] - *(int*)&registers[src2*4];
        }
        // MUL dest, src1, src2 - integer multiplication
        // XXXXXXXX ddddssss ssss0000 00000000
        else if (opcode == OPCODE_MUL)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            byte src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] * *(int*)&registers[src2*4];
        }
        // DIV dest, src1, src2 - integer division
        // XXXXXXXX ddddssss ssss0000 00000000
        else if (opcode == OPCODE_DIV)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            byte src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] / *(int*)&registers[src2*4];
        }
        // MOD dest, src1, src2 - integer division remainder
        // XXXXXXXX ddddssss ssss0000 00000000
        else if (opcode == OPCODE_MOD)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            byte src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] % *(int*)&registers[src2*4];
        }
        // SLL dest, src1, src2 - shift left logical
        // XXXXXXXX ddddssss ssss0000 00000000
        else if (opcode == OPCODE_SLL)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            byte src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] << *(int*)&registers[src2*4];
        }
        // SRL dest, src1, src2 - shift right logical
        // XXXXXXXX ddddssss ssss0000 00000000
        else if (opcode == OPCODE_SRL)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            byte src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(unsigned int*)&registers[src1*4] >> *(unsigned int*)&registers[src2*4];
        }
        // SRA dest, src1, src2 - shift right arithmetic
        // XXXXXXXX ddddssss ssss0000 00000000
        else if (opcode == OPCODE_SRA)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            byte src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] >> *(int*)&registers[src2*4];
        }
        // OR  dest, src1, src2 - bitwise or
        // XXXXXXXX ddddssss ssss0000 00000000
        else if (opcode == OPCODE_OR)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            byte src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] | *(int*)&registers[src2*4];
        }
        // AND dest, src1, src2 - bitwise and
        // XXXXXXXX ddddssss ssss0000 00000000
        else if (opcode == OPCODE_AND)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            byte src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] & *(int*)&registers[src2*4];
        }
        // XOR dest, src1, src2 - bitwise xor 
        // XXXXXXXX ddddssss ssss0000 00000000
        else if (opcode == OPCODE_XOR)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            byte src2   = (0b00000000000000001111000000000000 & instruction) >> 12;
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] ^ *(int*)&registers[src2*4];
        }

        // immediate arithmetic instructions
        // immediate values are 14-bit signed
        // ADDI dest, src1, imm - integer addition with immediate
        // - can be used to load immediate into register 
        // - that's why there is no load immediate 
        // - ADDI r0, rzero, 42 : r0 <- 0 + 42
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        else if (opcode == OPCODE_ADDI)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&memory[currentInstructionAddress+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] + imm;
        }
        // SUBI dest, src1, imm - integer subtraction with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        else if (opcode == OPCODE_SUBI)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&memory[currentInstructionAddress+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] - imm;
        }
        // MULI dest, src1, src2 - integer multiplication with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        else if (opcode == OPCODE_MULI)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&memory[currentInstructionAddress+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] * imm;
        }
        // DIVI dest, src1, src2 - integer division with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        else if (opcode == OPCODE_DIVI)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&memory[currentInstructionAddress+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] / imm;
        }
        // MODI dest, src1, src2 - integer division remainder with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        else if (opcode == OPCODE_MODI)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&memory[currentInstructionAddress+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] % imm;
        }
        // SLLI dest, src1, imm - shift left logical with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        else if (opcode == OPCODE_SLLI)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&memory[currentInstructionAddress+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] << imm;
        }
        // SRLI dest, src1, imm - shift right logical with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        else if (opcode == OPCODE_SRLI)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            unsigned int  imm    = *(int16_t*)&memory[currentInstructionAddress+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(unsigned int*)&registers[src1*4] >> imm;
        }
        // SRAI dest, src1, imm - shift right arithmetic with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        else if (opcode == OPCODE_SRAI)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&memory[currentInstructionAddress+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] >> imm;
        }
        // ORI  dest, src1, imm - bitwise or with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        else if (opcode == OPCODE_ORI)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&memory[currentInstructionAddress+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] | imm;
        }
        // ANDI dest, src1, imm - bitwise and with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        else if (opcode == OPCODE_ANDI)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&memory[currentInstructionAddress+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] & imm;
        }
        // XORI dest, src1, imm - bitwise xor  with immediate
        // XXXXXXXX ddddssss ssssiiii iiiiiiii
        else if (opcode == OPCODE_XORI)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src1   = (0b00000000000011110000000000000000 & instruction) >> 16;
            int  imm    = *(int16_t*)&memory[currentInstructionAddress+2];
            // read in word (4 bytes) 
            *(int*)&(registers[dest*4]) = *(int*)&registers[src1*4] ^ imm;
        }

        // branching
        // BEQ src1, src2, addr - if src1 == src2 then pc <- addr
        // XXXXXXXX ssssssss aaaa0000 00000000
        else if (opcode == OPCODE_BEQ)
        {
            byte src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src2   = (0b00000000000011110000000000000000 & instruction) >> 16;
            byte addr   = (0b00000000000000001111000000000000 & instruction) >> 12;
            if (*(int*)&registers[src1*4] == *(int*)&registers[src2*4])
                currentInstructionAddress = (*(int*)&registers[addr*4])-4;
        }
        // BNE src1, src2, addr - if src1 != src2 then pc <- addr
        // XXXXXXXX ssssssss aaaa0000 00000000
        else if (opcode == OPCODE_BNE)
        {
            byte src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src2   = (0b00000000000011110000000000000000 & instruction) >> 16;
            byte addr   = (0b00000000000000001111000000000000 & instruction) >> 12;
            if (*(int*)&registers[src1*4] != *(int*)&registers[src2*4])
                currentInstructionAddress = (*(int*)&registers[addr*4])-4;
        }
        // BLT src1, src2, addr - if src1 <  src2 then pc <- addr
        // XXXXXXXX ssssssss aaaa0000 00000000
        else if (opcode == OPCODE_BLT)
        {
            byte src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src2   = (0b00000000000011110000000000000000 & instruction) >> 16;
            byte addr   = (0b00000000000000001111000000000000 & instruction) >> 12;
            if (*(int*)&registers[src1*4] < *(int*)&registers[src2*4])
                currentInstructionAddress = (*(int*)&registers[addr*4])-4;
        }
        // BLE src1, src2, addr - if src1 <= src2 then pc <- addr
        // XXXXXXXX ssssssss aaaa0000 00000000
        else if (opcode == OPCODE_BLE)
        {
            byte src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src2   = (0b00000000000011110000000000000000 & instruction) >> 16;
            byte addr   = (0b00000000000000001111000000000000 & instruction) >> 12;
            if (*(int*)&registers[src1*4] <= *(int*)&registers[src2*4])
                currentInstructionAddress = (*(int*)&registers[addr*4])-4;
        }
        // BGT src1, src2, addr - if src1 >  src2 then pc <- addr
        // XXXXXXXX ssssssss aaaa0000 00000000
        else if (opcode == OPCODE_BGT)
        {
            byte src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src2   = (0b00000000000011110000000000000000 & instruction) >> 16;
            byte addr   = (0b00000000000000001111000000000000 & instruction) >> 12;
            if (*(int*)&registers[src1*4] > *(int*)&registers[src2*4])
                currentInstructionAddress = (*(int*)&registers[addr*4])-4;
        }
        // BGE src1, src2, addr - if src1 >= src2 then pc <- addr
        // XXXXXXXX ssssssss aaaa0000 00000000
        else if (opcode == OPCODE_BGE)
        {
            byte src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            byte src2   = (0b00000000000011110000000000000000 & instruction) >> 16;
            byte addr   = (0b00000000000000001111000000000000 & instruction) >> 12;
            if (*(int*)&registers[src1*4] >= *(int*)&registers[src2*4])
                currentInstructionAddress = (*(int*)&registers[addr*4])-4;
        }
        // JMP addr - pc <- addr
        // XXXXXXXX aaaa0000 00000000 00000000
        else if (opcode == OPCODE_JMP)
        {
            byte addr   = (0b00000000111100000000000000000000 & instruction) >> 20;
            currentInstructionAddress = (*(int*)&registers[addr*4])-4;
        }

        // function instructions 
        // CALL addr
        // 1. pushes return address on to the stack
        // 2. changes pc to addr
        // base pointer should be pushed on the stack by the callee
        // push bp
        // mov bp, sp
        // Caller's actions
        // 1. push caller saved registers
        // 2. push args in reverse order
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
        else if (opcode == OPCODE_CALL)
        {
            byte addr   = (0b00000000111100000000000000000000 & instruction) >> 20;
            // push return address onto stack 
            *(int*)&registers[sp*4] -= 4; // stack grows towards 0
            *(unsigned int*)&memory[*(int*)&registers[sp*4]] = currentInstructionAddress;
            // change program counter to addr 
            currentInstructionAddress = (*(int*)&registers[addr*4])-4;
        }
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
        else if (opcode == OPCODE_RET)
        {
            // pop return address from stack into 
            currentInstructionAddress = *(unsigned int*)&memory[*(int*)&registers[sp*4]];
            *(int*)&registers[sp*4] += 4; // stack shrinks towards MEM_SIZE
        }
        // PUSH src - sp -= 4 ; [sp] <- src
        // 1. decrements sp by 4 (bytes)
        // 2. places src onto stack at [sp]
        // XXXXXXXX ssss0000 00000000 00000000
        else if (opcode == OPCODE_PUSH)
        {
            byte src    = (0b00000000111100000000000000000000 & instruction) >> 20;
            *(int*)&registers[sp*4] -= 4; // stack grows towards 0
            *(int*)&memory[*(int*)&registers[sp*4]] = *(int*)&registers[src*4];
        }
        // POP dest - dest <- [sp] ; sp += 4
        // 1. moves [sp] into dest 
        // 2. increments sp by 4 (bytes)
        // XXXXXXXX dddd0000 00000000 00000000
        else if (opcode == OPCODE_POP)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            *(int*)&registers[dest*4] = *(int*)&memory[*(int*)&registers[sp*4]]; 
            *(int*)&registers[sp*4] += 4; // stack shrinks towards MEM_SIZE
        }

        // NOP - no operation
        // XXXXXXXX 000000000 00000000 00000000
        else if (opcode == OPCODE_NOP)
        {
            
        }
        // other instructions
        // HLT - halts the computer
        // XXXXXXXX 000000000 00000000 00000000
        else if (opcode == OPCODE_HLT)
        {
            break; 
        }
        // GETCHAR - reads (from stdin) a char (1-byte) and stores it in the 
        // given register
        // XXXXXXXX dddd00000 00000000 00000000
        else if (opcode == OPCODE_GETCHAR)
        {
            byte dest   = (0b00000000111100000000000000000000 & instruction) >> 20;
            *(int*)&registers[dest*4] = getchar();
        }
        // PUTCHAR - outputs (to stdout) a char (1-byte) from the given register
        // XXXXXXXX ssss00000 00000000 00000000
        else if (opcode == OPCODE_PUTCHAR)
        {
            byte src1   = (0b00000000111100000000000000000000 & instruction) >> 20;
            if (DEBUG) printf ("Output = '");
            putchar(*(int*)&registers[src1*4]);
            if (DEBUG) printf ("'\n");
        }
        // unknown instruction
        else
        {
            printf ("Invalid opcode %x%x\n", 
                (0b11110000 & opcode) >> 4,
                (0b00001111 & opcode) >> 0
            );
            break; 
        }




        // go to next instruction 
        // each instruction is 4 bytes; 
        currentInstructionAddress += 4; 

        // print register file
        if (DEBUG)
        {
            printf("registers:\n");
            for (int i = 0; i < 16*4; i+=4)
            {
                printf(
                    "   r%2d: %x%x %x%x %x%x %x%x ",
                    i/4,
                    (0b11110000 & registers[i+0]) >> 4,
                    (0b00001111 & registers[i+0]) >> 0,
                    (0b11110000 & registers[i+1]) >> 4,
                    (0b00001111 & registers[i+1]) >> 0,
                    (0b11110000 & registers[i+2]) >> 4,
                    (0b00001111 & registers[i+2]) >> 0,
                    (0b11110000 & registers[i+3]) >> 4,
                    (0b00001111 & registers[i+3]) >> 0
                );
                // special registers
                if (i/4 == ra) printf ("(ra)");
                if (i/4 == bp) printf ("(bp)");
                if (i/4 == sp) printf ("(sp)");
                printf("\n");
            }
        }

    }

    if (DEBUG) printf ("Program Finished\n");

    // print bytes 
    if (DEBUG)
    {
        printMemory (memory, MEMORY_SIZE_BYTES);
    }

}

//========================================================================