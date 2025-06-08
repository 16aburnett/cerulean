# Cerulean IR Compiler - AST Visitors
# By Amy Burnett
# April 24 2021
# ========================================================================

# for abstract classes 
from abc import ABC, abstractmethod
from sys import exit

# ========================================================================

class ASTVisitor (ABC):

    @abstractmethod
    def visitProgramNode (self, node):
        pass

    @abstractmethod
    def visitTypeSpecifierNode (self, node):
        pass

    @abstractmethod
    def visitParameterNode (self, node):
        pass

    @abstractmethod
    def visitGlobalVariableDeclarationNode (self, node):
        pass

    @abstractmethod
    def visitVariableDeclarationNode (self, node):
        pass

    @abstractmethod
    def visitFunctionNode (self, node):
        pass

    @abstractmethod
    def visitBasicBlockNode (self, node):
        pass

    @abstractmethod
    def visitInstructionNode (self, node):
        pass

    @abstractmethod
    def visitCallInstructionNode (self, node):
        pass

    @abstractmethod
    def visitArgumentExpressionNode (self, node):
        pass

    @abstractmethod
    def visitExpressionNode (self, node):
        pass

    @abstractmethod
    def visitGlobalVariableExpressionNode (self, node):
        pass

    @abstractmethod
    def visitLocalVariableExpressionNode (self, node):
        pass

    @abstractmethod
    def visitBasicBlockExpressionNode (self, node):
        pass

    @abstractmethod
    def visitIntLiteralExpressionNode (self, node):
        pass

    @abstractmethod
    def visitFloatLiteralExpressionNode (self, node):
        pass

    @abstractmethod
    def visitCharLiteralExpressionNode (self, node):
        pass

    @abstractmethod
    def visitStringLiteralExpressionNode (self, node):
        pass
