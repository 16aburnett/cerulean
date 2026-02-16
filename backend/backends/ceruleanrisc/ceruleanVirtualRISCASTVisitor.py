# Cerulean IR Compiler - AST Visitors
# By Amy Burnett
# April 24 2021
# ========================================================================

# for abstract classes 
from abc import ABC, abstractmethod
from sys import exit

# ========================================================================

class ASMASTVisitor (ABC):

    @abstractmethod
    def visitProgramNode (self, node):
        pass

    @abstractmethod
    def visitFunctionNode (self, node):
        pass

    @abstractmethod
    def visitInstructionNode (self, node):
        pass

    @abstractmethod
    def visitCallInstructionNode (self, node):
        pass

    @abstractmethod
    def visitRegisterNode (self, node):
        pass

    @abstractmethod
    def visitVirtualRegisterNode (self, node):
        pass

    @abstractmethod
    def visitVirtualTempRegisterNode (self, node):
        pass

    @abstractmethod
    def visitPhysicalRegisterNode (self, node):
        pass

    @abstractmethod
    def visitLabelNode (self, node):
        pass

    @abstractmethod
    def visitIntLiteralNode (self, node):
        pass

    @abstractmethod
    def visitFloatLiteralNode (self, node):
        pass

    @abstractmethod
    def visitCharLiteralNode (self, node):
        pass

    @abstractmethod
    def visitStringLiteralNode (self, node):
        pass
