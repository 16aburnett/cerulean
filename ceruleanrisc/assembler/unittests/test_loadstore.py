import unittest
from ceruleanrisc.assembler.assembler import *

class TestLoadStore (unittest.TestCase):
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
