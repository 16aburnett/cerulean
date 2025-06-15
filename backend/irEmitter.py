# Cerulean IR Compiler - IR Emitter Visitor
# By Amy Burnett
# June 10, 2025
# ========================================================================

# for abstract classes 
from abc import ABC, abstractmethod
from sys import exit

from .visitor import ASTVisitor
from .ceruleanIRAST import *

# ========================================================================

class IREmitterVisitor (ASTVisitor):

    def __init__(self):
        self.level = 0
        self.code = []

    def getIRCode (self):
        return "".join (self.code)

    # === HELPER FUNCTIONS ===============================================

    def printCode (self, line):
        self.code += [f"{line}\n"]

    # === VISITOR FUNCTIONS ==============================================

    def visitProgramNode (self, node):
        for codeunit in node.codeunits:
            if codeunit != None:
                codeunit.accept (self)

    # ====================================================================

    def visitTypeSpecifierNode (self, node):
        return str (node)

    # ====================================================================

    def visitParameterNode (self, node):
        typeStr = node.type.accept (self)
        return f"{typeStr}({node.id})"

    # ====================================================================

    def visitGlobalVariableDeclarationNode (self, node):
        argumentStrings = []
        for argument in node.arguments:
            argumentString = argument.accept (self)
            argumentStrings += [argumentString]
        argumentListString = ", ".join (argumentStrings)
        self.printCode (f"global {node.id} = {node.command} ({argumentListString})")

    # ====================================================================

    def visitVariableDeclarationNode (self, node):
        return node.id

    # ====================================================================

    def visitFunctionNode (self, node):
        returnTypeString = node.type.accept (self)
        # print parameters
        paramListStrings = []
        for param in node.params:
            paramString = param.accept (self)
            paramListStrings += [paramString]
        paramListString = ", ".join (paramListStrings)

        self.printCode (f"function {returnTypeString} {node.id} ({paramListString}) {{")
        for basicBlock in node.basicBlocks:
            basicBlock.accept (self)
        self.printCode (f"}}\n")

    # ====================================================================

    def visitBasicBlockNode (self, node):
        self.printCode (f"    block {node.name} {{")
        for instruction in node.instructions:
            instruction.accept (self)
        self.printCode (f"    }}")

    # ====================================================================

    def visitInstructionNode (self, node):
        if node.hasAssignment:
            lhsString = f"{node.lhsVariable.id} = "
        else:
            lhsString = f""
        argumentStrings = []
        for argument in node.arguments:
            argumentString = argument.accept (self)
            argumentStrings += [argumentString]
        argumentListString = ", ".join (argumentStrings)
        self.printCode (f"        {lhsString}{node.command} ({argumentListString})")

    # ====================================================================

    def visitCallInstructionNode (self, node):
        if node.hasAssignment:
            lhsString = f"{node.lhsVariable.id} = "
        else:
            lhsString = f""
        argumentStrings = []
        for argument in node.arguments:
            argumentString = argument.accept (self)
            argumentStrings += [argumentString]
        argumentListString = ", ".join (argumentStrings)
        self.printCode (f"        {lhsString}call {node.function_name} ({argumentListString})")

    # ====================================================================

    def visitArgumentExpressionNode (self, node):
        type = node.type.accept (self)
        expr = node.expression.accept (self)
        return f"{type}({expr})"

    # ====================================================================

    def visitExpressionNode (self, node):
        pass

    # ====================================================================

    def visitGlobalVariableExpressionNode (self, node):
        return node.id

    # ====================================================================

    def visitLocalVariableExpressionNode (self, node):
        return node.id

    # ====================================================================

    def visitBasicBlockExpressionNode (self, node):
        return node.id

    # ====================================================================

    def visitIntLiteralExpressionNode (self, node):
        return node.value

    # ====================================================================

    def visitFloatLiteralExpressionNode (self, node):
        return node.value

    # ====================================================================

    def visitCharLiteralExpressionNode (self, node):
        # Single quotes are pruned so add them back
        return f"'{node.value}'"

    # ====================================================================

    def visitStringLiteralExpressionNode (self, node):
        return node.value

# ========================================================================