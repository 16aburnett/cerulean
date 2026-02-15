import unittest
from ceruleanasm.assembler import *

class TestBranches (unittest.TestCase):
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
