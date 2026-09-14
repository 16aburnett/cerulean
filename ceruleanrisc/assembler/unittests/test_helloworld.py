import unittest
from ceruleanrisc.assembler.assembler import *

class TestHelloWorld (unittest.TestCase):
    def testHelloWorld1 (self):
        asmCode = """
    lli       r1, 'H'
    putchar   r1
    lli       r1, 'e'
    putchar   r1
    lli       r1, 'l'
    putchar   r1
    lli       r1, 'l'
    putchar   r1
    lli       r1, 'o'
    putchar   r1
    lli       r1, ','
    putchar   r1
    lli       r1, ' '
    putchar   r1
    lli       r1, 'W'
    putchar   r1
    lli       r1, 'o'
    putchar   r1
    lli       r1, 'r'
    putchar   r1
    lli       r1, 'l'
    putchar   r1
    lli       r1, 'd'
    putchar   r1
    lli       r1, '!'
    putchar   r1
    lli       r1, '\\n'
    putchar   r1
    halt
        """
        assembler = CeruleanAssembler ()
        objectCode = assembler.assemble (asmCode, None)
        self.assertEqual(len(objectCode["bytecode"]), 29 * 4)

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
    .f32 3.1415
    .i64 1337
    .addr main
    .i8 16

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
    add64i    r1, r1, 1
    load8     r2, r1, 0
    putchar   r2
    ret
        """
        
        assembler = CeruleanAssembler ()
        objectCode = assembler.assemble (asmCode, None)
        self.assertTrue(len(objectCode["bytecode"]) > 0)
