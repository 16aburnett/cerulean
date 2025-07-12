# CeruleanASM: AST Semantic Analysis Checker Visitor
# By Amy Burnett
# ========================================================================

from abc import ABC, abstractmethod
from sys import exit

from .visitor import ASTVisitor
from .modifiers import MODIFIERS
from .tokenizer import printToken, Token

# ========================================================================

class SemanticAnalysisVisitor (ASTVisitor):

    def __init__(self):
        # Assume semantics pass initially and try to break this assumption
        self.wasSuccessful = True

    def error (self, msg, debugToken:Token):
        print ("Semantic Analysis ERROR:", msg)
        if debugToken:
            printToken (debugToken)
        self.wasSuccessful = False

    def visitProgramNode (self, node):
        for codeunit in node.codeunits:
            if codeunit != None:
                codeunit.accept (self)

    def visitLabelNode (self, node):
        pass

    def visitInstructionNode (self, node):
        for argument in node.args:
            argument.accept (self)

    def visitRegisterExpressionNode (self, node):
        pass

    def visitLabelExpressionNode (self, node):
        # Ensure the modifier is correct if it has one
        if node.modifier != None and node.modifier not in MODIFIERS:
            self.error (f"'{node.modifier}' is not a valid modifier", node.modifierToken)

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
