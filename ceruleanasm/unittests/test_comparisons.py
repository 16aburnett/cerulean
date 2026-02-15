import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from opcodes import INSTRUCTION_MAPPING
from ceruleanasm.assembler import *

class TestComparisonOpcodes(unittest.TestCase):
    
    def testComparisonInstructions(self):
        """Test that all comparison instructions assemble with correct opcodes"""
        asmCode = """
    // Setup some registers
    lli       r0, 10
    lli       r1, 20
    lli       r2, 30
    
    // Test integer comparisons
    eq        r3, r0, r1
    lt        r3, r0, r1
    ltu       r3, r0, r1
    
    // Convert to floats for float comparisons
    cvti32f32 r4, r0
    cvti32f32 r5, r1
    cvti64f64 r6, r0
    cvti64f64 r7, r1
    
    // Test float32 comparisons
    eqf32     r3, r4, r5
    ltf32     r3, r4, r5
    lef32     r3, r4, r5
    
    // Test float64 comparisons
    eqf64     r3, r6, r7
    ltf64     r3, r6, r7
    lef64     r3, r6, r7
    
    halt
        """
        
        assembler = CeruleanAssembler()
        objectCode = assembler.assemble(asmCode, None)
        bytecode = objectCode["bytecode"]
        
        # Find comparison instruction opcodes in bytecode
        # Skip header and setup instructions
        eq_idx = None
        lt_idx = None
        ltu_idx = None
        eqf32_idx = None
        ltf32_idx = None
        lef32_idx = None
        eqf64_idx = None
        ltf64_idx = None
        lef64_idx = None
        
        for i in range(0, len(bytecode), 4):
            opcode = bytecode[i]
            if opcode == 0x77 and eq_idx is None:
                eq_idx = i
            elif opcode == 0x78 and lt_idx is None:
                lt_idx = i
            elif opcode == 0x79 and ltu_idx is None:
                ltu_idx = i
            elif opcode == 0x7a and eqf32_idx is None:
                eqf32_idx = i
            elif opcode == 0x7c and ltf32_idx is None:
                ltf32_idx = i
            elif opcode == 0x7e and lef32_idx is None:
                lef32_idx = i
            elif opcode == 0x7b and eqf64_idx is None:
                eqf64_idx = i
            elif opcode == 0x7d and ltf64_idx is None:
                ltf64_idx = i
            elif opcode == 0x7f and lef64_idx is None:
                lef64_idx = i
        
        # Verify all comparison instructions were found
        self.assertIsNotNone(eq_idx, "EQ instruction not found")
        self.assertIsNotNone(lt_idx, "LT instruction not found")
        self.assertIsNotNone(ltu_idx, "LTU instruction not found")
        self.assertIsNotNone(eqf32_idx, "EQF32 instruction not found")
        self.assertIsNotNone(ltf32_idx, "LTF32 instruction not found")
        self.assertIsNotNone(lef32_idx, "LEF32 instruction not found")
        self.assertIsNotNone(eqf64_idx, "EQF64 instruction not found")
        self.assertIsNotNone(ltf64_idx, "LTF64 instruction not found")
        self.assertIsNotNone(lef64_idx, "LEF64 instruction not found")

if __name__ == '__main__':
    unittest.main()
