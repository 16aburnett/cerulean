# CeruleanASM: Bytecode generator
# By Amy Burnett
# ========================================================================

from abc import ABC, abstractmethod
from sys import exit
import codecs

from .AST import *
from .visitor import ASTVisitor
from .registers import REGISTER_MAP
from .opcodes import INSTRUCTION_MAPPING
from .encoders import *

# ========================================================================

class BytecodeGeneratorVisitor (ASTVisitor):

    def __init__(self, symbolTable):
        self.bytecode = bytearray ()

    def visitProgramNode (self, node):
        for codeunit in node.codeunits:
            if codeunit != None:
                codeunit.accept (self)

    def visitLabelNode (self, node):
        pass

    def visitInstructionNode (self, node):
        instructionData = INSTRUCTION_MAPPING[node.id.upper ()]
        opcode = instructionData["opcode"]
        format = instructionData["format"]
        encoder = FORMAT_ENCODERS[format]
        encodedArgs = [arg.accept (self) for arg in node.args]
        encodedInstructionBytes = encoder (opcode, *encodedArgs)
        self.bytecode.extend (encodedInstructionBytes)

    def visitRegisterExpressionNode (self, node):
        return REGISTER_MAP.get (node.id)

    def visitLabelExpressionNode (self, node):
        if node.modifier == "hi": return (node.address >> 48) & 0xFFFF
        if node.modifier == "mh": return (node.address >> 32) & 0xFFFF
        if node.modifier == "ml": return (node.address >> 16) & 0xFFFF
        if node.modifier == "lo": return (node.address      ) & 0xFFFF
        return node.address

    def visitIntLiteralExpressionNode (self, node):
        return node.value

    def visitFloatLiteralExpressionNode (self, node):
        return node.value

    def visitCharLiteralExpressionNode (self, node):
        # Using codecs to interpret backslashed chars correctly
        return ord (codecs.decode (node.value, 'unicode_escape'))

    def visitStringLiteralExpressionNode (self, node):
        return node.value

    def visitNullExpressionNode (self, node):
        return node.value
