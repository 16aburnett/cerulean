# Cerulean IR Compiler - AST Print Visitor
# By Amy Burnett
# June 19, 2024
# ========================================================================

# for abstract classes 
from abc import ABC, abstractmethod
from sys import exit

from visitor import ASTVisitor

# ========================================================================

class PrintVisitor (ASTVisitor):

    def __init__(self):
        self.level = 0
        self.outputstrings = []

    # ====================================================================

    def visitProgramNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += ["ProgramNode:\n"]

        self.level += 1

        for codeunit in node.codeunits:
            if codeunit != None:
                codeunit.accept (self)

        self.level -= 1

    # ====================================================================

    def visitTypeSpecifierNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"Type: {node.type} {node.id}"]

        for i in range(node.arrayDimensions):
            self.outputstrings += ["*"]
        self.outputstrings += ["\n"]

    # ====================================================================

    def visitParameterNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"Parameter: \n"]

        self.level += 1

        node.type.accept (self)

        self.printSpaces (self.level)
        self.outputstrings += [f"Name: {node.id}\n"]

        self.level -= 1

    # ====================================================================

    def visitLabelNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"Label: {node.id}\n"]

    # ====================================================================

    def visitGlobalVariableDeclarationNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"GlobalVariableDeclaration: \n"]

        self.level += 1

        self.printSpaces (self.level)
        self.outputstrings += [f"Name: {node.id}\n"]

        self.printSpaces (self.level)
        self.outputstrings += [f"Command: {node.command.lexeme}\n"]

        self.printSpaces (self.level)
        self.outputstrings += [f"Arguments:\n"]
        self.level += 1
        for argument in node.arguments:
            argument.accept (self)
        self.level -= 1


        self.level -= 1

    # ====================================================================

    def visitVariableDeclarationNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"VariableDeclaration: \n"]

        self.level += 1

        node.type.accept (self)

        self.printSpaces (self.level)
        self.outputstrings += [f"Name: {node.id}\n"]

        self.level -= 1

    # ====================================================================

    def visitFunctionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"Function: {node.id} "]

        # function signature
        self.outputstrings += [f"("]
        if (len(node.params) == 0):
            self.outputstrings += ["void"]
        else:
            self.outputstrings += [f"{node.params[0].type}"]
            for i in range(1, len(node.params)):
                self.outputstrings += [f",{node.params[i].type}"]
        self.outputstrings += [f")"]
        self.outputstrings += [f"->{node.type}\n"]

        self.level += 1

        self.printSpaces (self.level)
        self.outputstrings += ["ReturnType:\n"]
        self.level += 1
        node.type.accept (self)
        self.level -= 1

        # print parameters 
        for param in node.params:
            param.accept (self)

        self.printSpaces (self.level)
        self.outputstrings += ["Body:\n"]

        self.level += 1
        if node.body != None:
            node.body.accept (self)

        self.level -= 2

    # ====================================================================

    def visitCodeBlockNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"CodeBlock:\n"]

        self.level += 1

        # print each codeunit
        for unit in node.codeunits:
            unit.accept (self)

        self.level -= 1

    # ====================================================================

    def visitInstructionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"Instruction:\n"]

        self.level += 1

        if node.hasAssignment:
            self.printSpaces (self.level)
            self.outputstrings += [f"LHS: {node.lhsVariable}\n"]
        
        self.printSpaces (self.level)
        self.outputstrings += [f"Command: {node.command}\n"]

        self.printSpaces (self.level)
        self.outputstrings += [f"Arguments:\n"]
        self.level += 1
        for arg in node.arguments:
            arg.accept (self)
        self.level -= 1

        self.level -= 1

    # ====================================================================

    def visitCallInstructionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"Call Instruction:\n"]

        self.level += 1

        if node.hasAssignment:
            self.printSpaces (self.level)
            self.outputstrings += [f"LHS: {node.lhsVariable}\n"]
        
        self.printSpaces (self.level)
        self.outputstrings += [f"Called Function: {node.function_name}\n"]

        self.printSpaces (self.level)
        self.outputstrings += [f"Arguments:\n"]
        self.level += 1
        for arg in node.arguments:
            arg.accept (self)
        self.level -= 1

        self.level -= 1

    # ====================================================================

    def visitArgumentExpressionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"Argument: \n"]

        self.level += 1

        node.type.accept (self)

        self.printSpaces (self.level)
        self.outputstrings += [f"Expression:\n"]
        self.level += 1
        node.expression.accept (self)
        self.level -= 1

        self.level -= 1

    # ====================================================================

    def visitExpressionNode (self, node):
        pass

    # ====================================================================

    def visitGlobalVariableExpressionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"Global Variable: {node.id}\n"]

    # ====================================================================

    def visitLocalVariableExpressionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"Local Variable: {node.id}\n"]

    # ====================================================================

    def visitIdentifierExpressionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"Identifier: {node.id}\n"]

    # ====================================================================

    def visitIntLiteralExpressionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"Int Literal: {node.value} {node.type}\n"]

    # ====================================================================

    def visitFloatLiteralExpressionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"Float Literal: {node.value} {node.type}\n"]

    # ====================================================================

    def visitCharLiteralExpressionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"Char Literal: {node.value} {node.type}\n"]

    # ====================================================================

    def visitStringLiteralExpressionNode (self, node):
        self.printSpaces (self.level)
        self.outputstrings += [f"String Literal: {node.value} {node.type}\n"]

    # ====================================================================

    def printSpaces (self, level):
        while level > 0:
            self.outputstrings += ["|   "]
            level -= 1

# ========================================================================