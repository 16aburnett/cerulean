# CeruleanASM: AST Lowering visitor for lowering high level structures to low level
# By Amy Burnett
# =================================================================================================

from abc import ABC, abstractmethod
from sys import exit

from .visitor import ASTVisitor
from .pseudoInstructions import *

# =================================================================================================

class LoweringVisitor (ASTVisitor):

    def __init__(self):
        pass

    def lower (self, ast):
        ast.accept (self)

    # ---------------------------------------------------------------------------------------------

    def visitProgramNode (self, node):
        newCodeunits = []
        for codeunit in node.codeunits:
            if codeunit != None:
                expandedCodeunits = codeunit.accept (self)
                newCodeunits.extend (expandedCodeunits)
        node.codeunits = newCodeunits

    def visitLabelNode (self, node):
        pass

    def visitDataDirectiveNode (self, node):
        # for label in node.labels:
        #     label.accept (self)
        # for argument in node.args:
        #     argument.accept (self)
        return [node]

    def visitInstructionNode (self, node):
        # for label in node.labels:
        #     label.accept (self)
        # for argument in node.args:
        #     argument.accept (self)
        # Ensure pseudo-instructions are expanded into their real instructions
        if node.id in PSEUDO_INSTRUCTIONS:
            return PSEUDO_INSTRUCTIONS[node.id].expander (node)
        return [node]

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
