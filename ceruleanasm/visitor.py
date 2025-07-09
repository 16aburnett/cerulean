# Cerulean Compiler - AST Visitors
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
    def visitLabelNode (self, node):
        pass

    @abstractmethod
    def visitInstructionNode (self, node):
        pass

    @abstractmethod
    def visitRegisterExpressionNode (self, node):
        pass

    @abstractmethod
    def visitLabelExpressionNode (self, node):
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

    @abstractmethod
    def visitNullExpressionNode (self, node):
        pass
