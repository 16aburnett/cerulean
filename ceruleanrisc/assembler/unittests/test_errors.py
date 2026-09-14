import unittest
from ceruleanrisc.assembler.assembler import CeruleanAssembler
from ceruleanrisc.assembler.exceptions import AssemblerError

class TestAssemblerErrors (unittest.TestCase):
    def testParseError (self):
        """Test that parse errors raise AssemblerError instead of exiting"""
        invalidAsm = """
    add32 r0, r1, // missing argument
        """
        assembler = CeruleanAssembler ()
        with self.assertRaises (AssemblerError):
            assembler.assemble (invalidAsm, "<test>")

    def testSemanticError (self):
        """Test that undefined label errors raise AssemblerError instead of exiting"""
        invalidAsm = """
    jmp undefined_label
        """
        assembler = CeruleanAssembler ()
        with self.assertRaises (AssemblerError):
            assembler.assemble (invalidAsm, "<test>")
