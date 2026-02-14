import unittest
from ceruleanasm.assembler import *

class TestHelloWorld (unittest.TestCase):
    def testHelloWorld1 (self):
        asmCode = """
    lli       r0, 'H'
    putchar   r0
    lli       r0, 'e'
    putchar   r0
    lli       r0, 'l'
    putchar   r0
    lli       r0, 'l'
    putchar   r0
    lli       r0, 'o'
    putchar   r0
    lli       r0, ','
    putchar   r0
    lli       r0, ' '
    putchar   r0
    lli       r0, 'W'
    putchar   r0
    lli       r0, 'o'
    putchar   r0
    lli       r0, 'r'
    putchar   r0
    lli       r0, 'l'
    putchar   r0
    lli       r0, 'd'
    putchar   r0
    lli       r0, '!'
    putchar   r0
    lli       r0, '\\n'
    putchar   r0
    halt
        """
        expectedBytes = [2, 0, 72, 0, 147, 0, 0, 0, 2, 0, 101, 0, 147, 0, 0, 0, 2, 0, 108, 0, 147, 0, 0, 0, 2, 0, 108, 0, 147, 0, 0, 0, 2, 0, 111, 0, 147, 0, 0, 0, 2, 0, 44, 0, 147, 0, 0, 0, 2, 0, 32, 0, 147, 0, 0, 0, 2, 0, 87, 0, 147, 0, 0, 0, 2, 0, 111, 0, 147, 0, 0, 0, 2, 0, 114, 0, 147, 0, 0, 0, 2, 0, 108, 0, 147, 0, 0, 0, 2, 0, 100, 0, 147, 0, 0, 0, 2, 0, 33, 0, 147, 0, 0, 0, 2, 0, 10, 0, 147, 0, 0, 0, 145, 0, 0, 0]
        assembler = CeruleanAssembler ()
        objectCode = assembler.assemble (asmCode, None)
        self.assertEqual(objectCode["bytecode"], expectedBytes)

    def testHelloWorld2 (self):
        asmCode = """
// Simple Hello World with data directives
letsgoooo:
_start:
    lui       r0, %hi(main) // 0x0000000012340000
    lli       r0, %mh(main) // 0x0000000012345678
    sll64i    r0, r0, 16    // 0x0000123456780000
    lli       r0, %ml(main) // 0x0000123456789abc
    sll64i    r0, r0, 16    // 0x123456789abc0000
    lli       r0, %lo(main) // 0x123456789abcdef0
    call      r0
    halt

string_addr:
    .ascii "Hello, World!\n"
    .float32 3.1415
    .int64 1337
    .addr main
    .int8 16

// This should be correctly aligned, despite above not ending at a 32bit alignment
main:
    // Load string_addr into r0
    // Currently this takes 6 instructions
    lui       r0, %hi(string_addr)
    lli       r0, %mh(string_addr)
    sll64i    r0, r0, 16
    lli       r0, %ml(string_addr)
    sll64i    r0, r0, 16
    lli       r0, %lo(string_addr)

    load8     r1, r0, 0
    putchar   r1
    add64i    r0, r0, 1
    load8     r1, r0, 0
    putchar   r1
    add64i    r0, r0, 1
    load8     r1, r0, 0
    putchar   r1
    add64i    r0, r0, 1
    load8     r1, r0, 0
    putchar   r1
    add64i    r0, r0, 1
    load8     r1, r0, 0
    putchar   r1
    add64i    r0, r0, 1
    load8     r1, r0, 0
    putchar   r1
    add64i    r0, r0, 1
    load8     r1, r0, 0
    putchar   r1
    add64i    r0, r0, 1
    load8     r1, r0, 0
    putchar   r1
    add64i    r0, r0, 1
    load8     r1, r0, 0
    putchar   r1
    add64i    r0, r0, 1
    load8     r1, r0, 0
    putchar   r1
    add64i    r0, r0, 1
    load8     r1, r0, 0
    putchar   r1
    add64i    r0, r0, 1
    load8     r1, r0, 0
    putchar   r1
    add64i    r0, r0, 1
    load8     r1, r0, 0
    putchar   r1
    add64i    r0, r0, 1
    load8     r1, r0, 0
    putchar   r1
    ret
        """
        
        expectedBytes = [1, 0, 0, 0, 2, 0, 0, 0, 97, 0, 16, 0, 2, 0, 0, 0, 97, 0, 16, 0, 2, 0, 0, 0, 128, 0, 0, 0, 145, 0, 0, 0, 72, 101, 108, 108, 111, 44, 32, 87, 111, 114, 108, 100, 33, 10, 0, 0, 86, 14, 73, 64, 0, 0, 0, 0, 57, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 97, 0, 16, 0, 2, 0, 0, 0, 97, 0, 16, 0, 2, 0, 0, 0, 3, 16, 0, 0, 147, 16, 0, 0, 33, 0, 1, 0, 3, 16, 0, 0, 147, 16, 0, 0, 33, 0, 1, 0, 3, 16, 0, 0, 147, 16, 0, 0, 33, 0, 1, 0, 3, 16, 0, 0, 147, 16, 0, 0, 33, 0, 1, 0, 3, 16, 0, 0, 147, 16, 0, 0, 33, 0, 1, 0, 3, 16, 0, 0, 147, 16, 0, 0, 33, 0, 1, 0, 3, 16, 0, 0, 147, 16, 0, 0, 33, 0, 1, 0, 3, 16, 0, 0, 147, 16, 0, 0, 33, 0, 1, 0, 3, 16, 0, 0, 147, 16, 0, 0, 33, 0, 1, 0, 3, 16, 0, 0, 147, 16, 0, 0, 33, 0, 1, 0, 3, 16, 0, 0, 147, 16, 0, 0, 33, 0, 1, 0, 3, 16, 0, 0, 147, 16, 0, 0, 33, 0, 1, 0, 3, 16, 0, 0, 147, 16, 0, 0, 33, 0, 1, 0, 3, 16, 0, 0, 147, 16, 0, 0, 130, 0, 0, 0]
        assembler = CeruleanAssembler ()
        objectCode = assembler.assemble (asmCode, None)
        self.assertEqual(objectCode["bytecode"], expectedBytes)

    def testLoadStoreInstructions (self):
        """Test that all load/store instructions assemble with correct opcodes"""
        asmCode = """
    // Test signed loads
    load8     r1, r2, 10
    load16    r3, r4, 20
    load32    r5, r6, 30
    load64    r7, r8, 40
    
    // Test unsigned loads
    loadu8    r1, r2, -10
    loadu16   r3, r4, -20
    loadu32   r5, r6, -30
    
    // Test stores
    store8    r9, r10, 50
    store16   r11, r12, 60
    store32   ra, bp, 70
    store64   sp, r0, 80
    
    halt
        """
        
        assembler = CeruleanAssembler ()
        objectCode = assembler.assemble (asmCode, None)
        bytecode = objectCode["bytecode"]
        
        # Check opcodes are correct
        self.assertEqual(bytecode[0], 0x03)  # LOAD8
        self.assertEqual(bytecode[4], 0x05)  # LOAD16
        self.assertEqual(bytecode[8], 0x07)  # LOAD32
        self.assertEqual(bytecode[12], 0x09) # LOAD64
        
        self.assertEqual(bytecode[16], 0x04) # LOADU8
        self.assertEqual(bytecode[20], 0x06) # LOADU16
        self.assertEqual(bytecode[24], 0x08) # LOADU32
        
        self.assertEqual(bytecode[28], 0x0a) # STORE8
        self.assertEqual(bytecode[32], 0x0b) # STORE16
        self.assertEqual(bytecode[36], 0x0c) # STORE32
        self.assertEqual(bytecode[40], 0x0d) # STORE64

    def testBranchInstructions (self):
        """Test that all branch instructions assemble with correct opcodes"""
        asmCode = """
    // Setup some registers for branch targets
    lli       r0, 16
    lli       r1, 32
    lli       r2, 64
    
    // Test all branch instructions
    beq       r0, r1, r2
    bne       r0, r1, r2
    blt       r0, r1, r2
    bge       r0, r1, r2
    bltu      r0, r1, r2
    bgeu      r0, r1, r2
    jmp       r2
    
    halt
        """
        
        assembler = CeruleanAssembler ()
        objectCode = assembler.assemble (asmCode, None)
        bytecode = objectCode["bytecode"]
        
        # Check opcodes are correct
        self.assertEqual(bytecode[12], 0x70) # BEQ
        self.assertEqual(bytecode[16], 0x71) # BNE
        self.assertEqual(bytecode[20], 0x72) # BLT
        self.assertEqual(bytecode[24], 0x73) # BGE
        self.assertEqual(bytecode[28], 0x74) # BLTU
        self.assertEqual(bytecode[32], 0x75) # BGEU
        self.assertEqual(bytecode[36], 0x76) # JMP
