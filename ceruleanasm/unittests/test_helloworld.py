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
        expectedBytes = b'\x02\x00H\x00\x93\x00\x00\x00\x02\x00e\x00\x93\x00\x00\x00\x02\x00l\x00\x93\x00\x00\x00\x02\x00l\x00\x93\x00\x00\x00\x02\x00o\x00\x93\x00\x00\x00\x02\x00,\x00\x93\x00\x00\x00\x02\x00 \x00\x93\x00\x00\x00\x02\x00W\x00\x93\x00\x00\x00\x02\x00o\x00\x93\x00\x00\x00\x02\x00r\x00\x93\x00\x00\x00\x02\x00l\x00\x93\x00\x00\x00\x02\x00d\x00\x93\x00\x00\x00\x02\x00!\x00\x93\x00\x00\x00\x02\x00\n\x00\x93\x00\x00\x00\x91\x00\x00\x00'
        assembler = CeruleanAssembler ()
        bytecode = assembler.assemble (asmCode, None)
        self.assertEqual(bytecode, expectedBytes)

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
        expectedBytes = b'\x01\x00\x00\x00\x02\x00\x00\x00a\x00\x10\x00\x02\x00\x00\x00a\x00\x10\x00\x02\x00L\x00\x80\x00\x00\x00\x91\x00\x00\x00Hello, World!\n\x00\x00V\x0eI@\x00\x00\x00\x009\x05\x00\x00\x00\x00\x00\x00L\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00a\x00\x10\x00\x02\x00\x00\x00a\x00\x10\x00\x02\x00 \x00\x03\x10\x00\x00\x93\x10\x00\x00!\x00\x01\x00\x03\x10\x00\x00\x93\x10\x00\x00!\x00\x01\x00\x03\x10\x00\x00\x93\x10\x00\x00!\x00\x01\x00\x03\x10\x00\x00\x93\x10\x00\x00!\x00\x01\x00\x03\x10\x00\x00\x93\x10\x00\x00!\x00\x01\x00\x03\x10\x00\x00\x93\x10\x00\x00!\x00\x01\x00\x03\x10\x00\x00\x93\x10\x00\x00!\x00\x01\x00\x03\x10\x00\x00\x93\x10\x00\x00!\x00\x01\x00\x03\x10\x00\x00\x93\x10\x00\x00!\x00\x01\x00\x03\x10\x00\x00\x93\x10\x00\x00!\x00\x01\x00\x03\x10\x00\x00\x93\x10\x00\x00!\x00\x01\x00\x03\x10\x00\x00\x93\x10\x00\x00!\x00\x01\x00\x03\x10\x00\x00\x93\x10\x00\x00!\x00\x01\x00\x03\x10\x00\x00\x93\x10\x00\x00\x82\x00\x00\x00'
        assembler = CeruleanAssembler ()
        bytecode = assembler.assemble (asmCode, None)
        self.assertEqual(bytecode, expectedBytes)
