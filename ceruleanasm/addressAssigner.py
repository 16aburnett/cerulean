# CeruleanASM: AST Address Assigner Visitor
# Assigns addresses to each of the instructions and adds label definitions
# to the SymbolTable
# By Amy Burnett
# ========================================================================

from abc import ABC, abstractmethod
from sys import exit

from .visitor import ASTVisitor

# ========================================================================

class AddressAssignerVisitor (ASTVisitor):

    def __init__(self, symbolTable):
        self.currentAddress = 0
        self.symbolTable = symbolTable

    def visitProgramNode (self, node):
        for codeunit in node.codeunits:
            if codeunit != None:
                codeunit.accept (self)

    def visitLabelNode (self, node):
        self.symbolTable[node.id] = self.currentAddress

    def visitInstructionNode (self, node):
        for argument in node.args:
            argument.accept (self)
        node.address = self.currentAddress
        self.currentAddress += node.size

    def visitRegisterExpressionNode (self, node):
        pass

    def visitLabelExpressionNode (self, node):
        pass

    def visitIntLiteralExpressionNode (self, node):
        pass

    def visitFloatLiteralExpressionNode (self, node):
        pass

    def visitCharLiteralExpressionNode (self, node):
        pass

    def visitStringLiteralExpressionNode (self, node):
        pass

    def visitNullExpressionNode (self, node):
        pass
