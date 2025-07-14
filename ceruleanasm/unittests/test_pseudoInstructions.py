import unittest
from ceruleanasm.assembler import *
from ceruleanasm.AST import *
from ceruleanasm.pseudoInstructions import *

class TestPseudoInstructions (unittest.TestCase):
    def testLoadaExpansion (self):
        # main:
        # loada r0, main
        pseudoInstruction = InstructionNode (None, "loada",
            [RegisterExpressionNode (None, "r0"), LabelExpressionNode (None, "main")],
            [LabelNode (None, "main")]
        )

        label = LabelNode (None, "main")
        reg = RegisterExpressionNode (None, "r0")
        imm16 = IntLiteralExpressionNode (None, 16)
        expectedInstructions = [
            InstructionNode (None, 'lui'   , args=[reg, LabelExpressionNode (None, "main", modifier="hi")], labels=[label]),
            InstructionNode (None, 'lli'   , args=[reg, LabelExpressionNode (None, "main", modifier="mh")]),
            InstructionNode (None, 'sll64i', args=[reg, reg, imm16]),
            InstructionNode (None, 'lli'   , args=[reg, LabelExpressionNode (None, "main", modifier="ml")]),
            InstructionNode (None, 'sll64i', args=[reg, reg, imm16]),
            InstructionNode (None, 'lli'   , args=[reg, LabelExpressionNode (None, "main", modifier="lo")]),
        ]

        # Ensure it is a valid pseudo instruction
        self.assertTrue (pseudoInstruction.id in PSEUDO_INSTRUCTIONS)

        # Expand instruction
        expanderFunc = PSEUDO_INSTRUCTIONS[pseudoInstruction.id].expander
        expandedInstructions = expanderFunc (pseudoInstruction)

        self.assertEqual (expandedInstructions, expectedInstructions)

    def testMv32Expansion (self):
        # mv32 r1, r0
        regDest = RegisterExpressionNode (None, "r1")
        regSrc  = RegisterExpressionNode (None, "r0")
        pseudoInstruction = InstructionNode (None, "mv32", [regDest, regSrc])

        imm0 = IntLiteralExpressionNode (None, 0)
        expectedInstructions = [
            InstructionNode (None, 'add32i', args=[regDest, regSrc, imm0], labels=[])
        ]

        # Ensure it is a valid pseudo instruction
        self.assertTrue (pseudoInstruction.id in PSEUDO_INSTRUCTIONS)

        # Expand instruction
        expanderFunc = PSEUDO_INSTRUCTIONS[pseudoInstruction.id].expander
        expandedInstructions = expanderFunc (pseudoInstruction)

        self.assertEqual (expandedInstructions, expectedInstructions)

    def testMv64Expansion (self):
        # mv32 r1, r0
        regDest = RegisterExpressionNode (None, "r1")
        regSrc  = RegisterExpressionNode (None, "r0")
        pseudoInstruction = InstructionNode (None, "mv64", [regDest, regSrc])

        imm0 = IntLiteralExpressionNode (None, 0)
        expectedInstructions = [
            InstructionNode (None, 'add64i', args=[regDest, regSrc, imm0], labels=[])
        ]

        # Ensure it is a valid pseudo instruction
        self.assertTrue (pseudoInstruction.id in PSEUDO_INSTRUCTIONS)

        # Expand instruction
        expanderFunc = PSEUDO_INSTRUCTIONS[pseudoInstruction.id].expander
        expandedInstructions = expanderFunc (pseudoInstruction)

        self.assertEqual (expandedInstructions, expectedInstructions)
