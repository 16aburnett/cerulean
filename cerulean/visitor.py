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
    def visitTypeSpecifierNode (self, node):
        pass

    @abstractmethod
    def visitParameterNode (self, node):
        pass

    @abstractmethod
    def visitCodeUnitNode (self, node):
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
    def visitClassDeclarationNode (self, node):
        pass

    @abstractmethod
    def visitFieldDeclarationNode (self, node):
        pass

    @abstractmethod
    def visitMethodDeclarationNode (self, node):
        pass

    @abstractmethod
    def visitConstructorDeclarationNode (self, node):
        pass

    @abstractmethod
    def visitEnumDeclarationNode (self, node):
        pass

    @abstractmethod
    def visitStatementNode (self, node):
        pass

    @abstractmethod
    def visitIfStatementNode (self, node):
        pass

    @abstractmethod
    def visitElifStatementNode (self, node):
        pass

    @abstractmethod
    def visitElseStatementNode (self, node):
        pass

    @abstractmethod
    def visitForStatementNode (self, node):
        pass

    @abstractmethod
    def visitWhileStatementNode (self, node):
        pass

    @abstractmethod
    def visitExpressionStatementNode (self, node):
        pass

    @abstractmethod
    def visitReturnStatementNode (self, node):
        pass

    @abstractmethod
    def visitContinueStatementNode (self, node):
        pass

    @abstractmethod
    def visitBreakStatementNode (self, node):
        pass

    @abstractmethod
    def visitCodeBlockNode (self, node):
        pass

    @abstractmethod
    def visitExpressionNode (self, node):
        pass

    @abstractmethod
    def visitTupleExpressionNode (self, node):
        pass

    @abstractmethod
    def visitAssignExpressionNode (self, node):
        pass

    @abstractmethod
    def visitLogicalOrExpressionNode (self, node):
        pass

    @abstractmethod
    def visitLogicalAndExpressionNode (self, node):
        pass

    @abstractmethod
    def visitEqualityExpressionNode (self, node):
        pass

    @abstractmethod
    def visitInequalityExpressionNode (self, node):
        pass

    @abstractmethod
    def visitAdditiveExpressionNode (self, node):
        pass

    @abstractmethod
    def visitMultiplicativeExpressionNode (self, node):
        pass

    @abstractmethod
    def visitPreIncrementExpressionNode (self, node):
        pass

    @abstractmethod
    def visitPreDecrementExpressionNode (self, node):
        pass

    @abstractmethod
    def visitNegativeExpressionNode (self, node):
        pass

    @abstractmethod
    def visitLogicalNotExpressionNode (self, node):
        pass

    @abstractmethod
    def visitBitwiseNegatationExpressionNode (self, node):
        pass

    @abstractmethod
    def visitPostIncrementExpressionNode (self, node):
        pass

    @abstractmethod
    def visitPostDecrementExpressionNode (self, node):
        pass

    @abstractmethod
    def visitSubscriptExpressionNode (self, node):
        pass

    @abstractmethod
    def visitFunctionCallExpressionNode (self, node):
        pass

    @abstractmethod
    def visitMemberAccessorExpressionNode (self, node):
        pass

    @abstractmethod
    def visitFieldAccessorExpressionNode (self, node):
        pass

    @abstractmethod
    def visitMethodAccessorExpressionNode (self, node):
        pass

    @abstractmethod
    def visitThisExpressionNode (self, node):
        pass

    @abstractmethod
    def visitIdentifierExpressionNode (self, node):
        pass

    @abstractmethod
    def visitArrayAllocatorExpressionNode (self, node):
        pass

    @abstractmethod
    def visitConstructorCallExpressionNode (self, node):
        pass

    @abstractmethod
    def visitSizeofExpressionNode (self, node):
        pass

    @abstractmethod
    def visitFreeExpressionNode (self, node):
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
    def visitListConstructorExpressionNode (self, node):
        pass

    @abstractmethod
    def visitNullExpressionNode (self, node):
        pass
