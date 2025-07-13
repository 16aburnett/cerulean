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
from .dataDirectives import *

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

    def visitDataDirectiveNode (self, node):
        # Assuming only a single argument - this might need to change to support multiple values
        argValue = node.args[0].accept (self)
        encodedDataDirectiveBytes = encodeDataDirective (node.id, argValue)
        # Add padding bytes for alignment if needed
        while len (self.bytecode) < node.address:
            self.bytecode.extend ([0x00])
            # print (f"Adding padding byte for '{node.id}'")
        self.bytecode.extend (encodedDataDirectiveBytes)

    def visitInstructionNode (self, node):
        instructionData = INSTRUCTION_MAPPING[node.id.upper ()]
        opcode = instructionData["opcode"]
        format = instructionData["format"]
        encoder = FORMAT_ENCODERS[format]
        encodedArgs = [arg.accept (self) for arg in node.args]
        encodedInstructionBytes = encoder (opcode, *encodedArgs)
        # Add padding bytes for alignment if needed
        while len (self.bytecode) < node.address:
            self.bytecode.extend ([0x00])
            # print (f"Adding padding byte for '{node.id}'")
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
        decodedString = codecs.decode (node.value.strip ('"'), 'unicode_escape')
        return bytearray (ord (c) for c in decodedString)

    def visitNullExpressionNode (self, node):
        return node.value
