import unittest
from ceruleanrisc.assembler.assembler import *

class TestConversions (unittest.TestCase):
    def testConversionInstructions (self):
        """Test that all type conversion instructions assemble with correct opcodes"""
        asmCode = """
    // Setup registers
    lli       r0, 100
    lli       r1, 200
    
    // Sign extension instructions
    sext8     r2, r0
    sext16    r2, r0
    sext32    r2, r0
    
    // Zero extension instructions
    zext8     r3, r0
    zext16    r3, r0
    zext32    r3, r0
    
    // Integer to float conversions
    cvti32f32 r4, r0
    cvti64f64 r4, r0
    
    // Float to integer conversions
    cvtf32i32 r5, r4
    cvtf64i64 r5, r4
    
    // Float precision conversions
    cvtf64f32 r6, r4
    cvtf32f64 r6, r4
    
    halt
        """
        
        assembler = CeruleanAssembler ()
        objectCode = assembler.assemble (asmCode, None)
        bytecode = objectCode["bytecode"]
        
        # Check opcodes are correct
        self.assertEqual(bytecode[8], 0x40)  # SEXT8
        self.assertEqual(bytecode[12], 0x41) # SEXT16
        self.assertEqual(bytecode[16], 0x42) # SEXT32
        self.assertEqual(bytecode[20], 0x43) # ZEXT8
        self.assertEqual(bytecode[24], 0x44) # ZEXT16
        self.assertEqual(bytecode[28], 0x45) # ZEXT32
        self.assertEqual(bytecode[32], 0x46) # CVTI32F32
        self.assertEqual(bytecode[36], 0x47) # CVTI64F64
        self.assertEqual(bytecode[40], 0x48) # CVTF32I32
        self.assertEqual(bytecode[44], 0x49) # CVTF64I64
        self.assertEqual(bytecode[48], 0x4a) # CVTF64F32
        self.assertEqual(bytecode[52], 0x4b) # CVTF32F64
