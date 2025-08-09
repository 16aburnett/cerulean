# CeruleanIR Compiler - Liveness Analysis for CeruleanASM
# By Amy Burnett
# =================================================================================================

import os
from sys import exit

from ...ceruleanIRAST import *
from ...visitor import ASTVisitor
from ...symbolTable import SymbolTable

# =================================================================================================

class LivenessAnalyzer (ASTVisitor):

    def __init__(self, shouldPrintDebug=False):
        self.shouldPrintDebug = shouldPrintDebug
        self.symbolTable = {}

    def analyze (self, ast):
        ast.accept (self)

    # === HELPER FUNCTIONS ===============================================
    
    def debugPrint (self, *args, **kwargs):
        if (self.shouldPrintDebug):
            print ("[debug] [liveness]", *args, **kwargs)

    # === VISITOR FUNCTIONS ==============================================

    def visitProgramNode (self, node):
        for codeunit in node.codeunits:
            if codeunit != None:
                codeunit.accept (self)

    #=====================================================================

    def visitTypeSpecifierNode (self, node):
        pass

    #=====================================================================

    def visitParameterNode (self, node):
        node.type.accept (self)
        node.scopeName = "".join (self.scopeNames) + "__" + node.id[1:]

    #=====================================================================

    def visitGlobalVariableDeclarationNode (self, node):
        pass

    #=====================================================================

    def visitVariableDeclarationNode (self, node):
        pass

    #=====================================================================

    def visitFunctionNode (self, node):
        for i in range(len(node.params)):
            node.params[i].accept (self)

        for basicBlock in node.basicBlocks:
            basicBlock.accept (self)

    #=====================================================================

    def visitBasicBlockNode (self, node):
        for instruction in node.instructions:
            instruction.accept (self)

    #=====================================================================

    def visitInstructionNode (self, node):
        for arg in node.arguments:
            arg.accept (self)

    #=====================================================================

    def visitCallInstructionNode (self, node):
        for arg in node.arguments:
            arg.accept (self)

    #=====================================================================

    # writes any code it needs to
    # returns the parsed argument
    def visitArgumentExpressionNode (self, node):
        return node.expression.accept (self)

    #=====================================================================

    # root node - should not be used
    def visitExpressionNode (self, node):
        pass

    #=====================================================================

    def visitGlobalVariableExpressionNode (self, node):
        # Ensure reference has a decl
        if node.decl == None:
            raise ValueError (f"LivenessAnalyzer: ERROR: Reference does not have a matching declaration - this is an error with the compiler")
        self.debugPrint (f"Counting global reference for '{node.id}'")
        node.decl.references.append (node)

    #=====================================================================

    def visitLocalVariableExpressionNode (self, node):
        # Ensure reference has a decl
        if node.decl == None:
            raise ValueError (f"LivenessAnalyzer: ERROR: Reference does not have a matching declaration - this is an error with the compiler")
        self.debugPrint (f"Counting reference for '{node.id}'")
        node.decl.references.append (node)

    #=====================================================================

    def visitBasicBlockExpressionNode (self, node):
        pass

    #=====================================================================

    def visitIntLiteralExpressionNode (self, node):
        pass

    #=====================================================================

    def visitFloatLiteralExpressionNode (self, node):
        pass

    #=====================================================================

    def visitCharLiteralExpressionNode (self, node):
        pass

    #=====================================================================

    def visitStringLiteralExpressionNode (self, node):
        pass
