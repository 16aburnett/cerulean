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
