# CeruleanASM: AST Reference/Label Resolution Visitor
# By Amy Burnett
# ========================================================================

from abc import ABC, abstractmethod
from sys import exit

from .AST import *
from .visitor import ASTVisitor

# ========================================================================

class ReferenceResolverVisitor (ASTVisitor):

    def __init__(self, symbolTable):
        self.symbolTable = symbolTable
        self.relocationTable = []

    def visitProgramNode (self, node):
        for codeunit in node.codeunits:
            if codeunit != None:
                codeunit.accept (self)

    def visitLabelNode (self, node):
        pass

    def visitInstructionNode (self, node):
        for i, arg in enumerate (node.args):
            # Ensure we are only looking at label expressions
            # Ideally we would have wanted the visitor pattern to resolve this
            # But we need extra context than is stored with the label expresision node
            if not isinstance (arg, LabelExpressionNode):
                continue
            # Local (in file) symbols
            if arg.id in self.symbolTable:
                arg.address = self.symbolTable[arg.id]
            # Exteral (outside of file) symbols
            else:
                # Just use 0 as a placeholder
                # Linker will need to resolve this
                arg.address = 0
                self.relocationTable.append ({
                    "location": node.address,
                    "symbol": arg.id,
                    "type": "absolute",
                    "arg_index": i
                })

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
