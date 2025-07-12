# CeruleanASM: AST Print Visitor
# By Amy Burnett
# ========================================================================

from abc import ABC, abstractmethod
from sys import exit

from .visitor import ASTVisitor

# ========================================================================

class PrintVisitor (ASTVisitor):

    def __init__(self):
        self.level = 0
        self.outputstrings = []

    def print (self, ast):
        ast.accept (self)
        return "".join (self.outputstrings)

    def printSpaces (self, level):
        while level > 0:
            self.outputstrings += ["|   "]
            level -= 1

    def visitProgramNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += ["Program:\n"]
        self.level += 1
        for codeunit in node.codeunits:
            if codeunit != None:
                codeunit.accept (self)
        self.level -= 1

    def visitLabelNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"Label(\"{node.id}\")\n"]

    def visitInstructionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"Instruction: \"{node.id}\"\n"]
        self.level += 1
        for argument in node.args:
            argument.accept (self)
        self.level -= 1

    def visitRegisterExpressionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"Register(\"{node.id}\")\n"]

    def visitLabelExpressionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"Label(\"{node.id}\")\n"]

    def visitIntLiteralExpressionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"IntLiteral({node.value})\n"]

    def visitFloatLiteralExpressionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"FloatLiteral({node.value})\n"]

    def visitCharLiteralExpressionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"CharLiteral('{node.value}')\n"]

    def visitStringLiteralExpressionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"StringLiteral(\"{node.value}\")\n"]

    def visitNullExpressionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"NullLiteral()\n"]
