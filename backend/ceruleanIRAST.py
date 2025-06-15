# Cerulean IR Compiler - Abstract Syntax Tree
# By Amy Burnett
# April 24 2021
# ========================================================================

# for abstract classes 
from abc import ABC, abstractmethod
from enum import Enum
from sys import exit

from .visitor import *

# ========================================================================

class Type(Enum):
    BYTE     = 1
    CHAR     = 2
    INT32    = 3
    INT64    = 4
    FLOAT32  = 5
    FLOAT64  = 6
    VOID     = 7
    BLOCK    = 8
    TYPE     = 9
    PTR      = 10
    UNKNOWN  = 11
    USERTYPE = 12 # SHOULD NOT BE USED - YET

# ========================================================================

class Node (ABC):
    @abstractmethod
    def accept (self, visitor):
        pass

    @abstractmethod
    def copy (self):
        pass

# ========================================================================
# type - Type
# id - string

class TypeSpecifierNode (Node):
    
    def __init__(self, type:Type, id, token, arrayDimensions=0):
        self.type = type 
        self.id = id
        self.token = token
        self.arrayDimensions = arrayDimensions

        self.decl = None

        self.isGeneric = False

        self.lineNumber = 0
        self.columnNumber = 0

    def __str__(self):
        # <type>{*}
        s = [self.id]
        for i in range(self.arrayDimensions):
            s += ["*"]
        return "".join(s)

    def accept (self, visitor):
        return visitor.visitTypeSpecifierNode (self)

    def copy (self):
        node = TypeSpecifierNode (self.type, self.id, self.token)
        node.arrayDimensions = self.arrayDimensions
        node.decl = self.decl
        node.isGeneric = self.isGeneric
        return node

# ========================================================================
# ProgramNode: the top-most level node for defining a complete program

class ProgramNode (Node):

    def __init__(self, codeunits):
        self.codeunits = codeunits

        self.lineNumber = 0
        self.columnNumber = 0

        self.localVariables = []
        self.floatLiterals = []
        self.stringLiterals = []

    def accept (self, visitor):
        return visitor.visitProgramNode (self)

    def copy (self):
        node = ProgramNode (None)
        for codeunit in self.codeunits:
            node.codeunits += [codeunit.copy ()]
        node.localVariables = [n.copy() for n in self.localVariables]
        return node

# ========================================================================
# Default declaration node - should not be used
# instead use VariableDeclarationNode or GlobalVariableDeclarationNode

class DeclarationNode (Node):

    def __init__(self, id, token):
        # self.type = type
        self.id = id
        self.token = token

        self.scopeName = "<unset-scope-name>"

        self.wasAssigned = False

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitDeclarationNode (self)

    def copy (self):
        node = DeclarationNode (self.type.copy(), self.id, self.token)
        node.scopeName = self.scopeName
        return node

# ========================================================================

class VariableDeclarationNode (DeclarationNode):

    def __init__(self, id, token):
        super().__init__ (id, token)

        self.lineNumber = 0
        self.columnNumber = 0

        # x86 fields
        self.stackOffset = 0

    def accept (self, visitor):
        return visitor.visitVariableDeclarationNode (self)

    def copy (self):
        node = VariableDeclarationNode (self.id, self.token)
        node.stackOffset = self.stackOffset
        return node

# ========================================================================

class GlobalVariableDeclarationNode (DeclarationNode):
    
    def __init__(self, id, token, command, arguments):
        super().__init__ (id, token)
        self.command = command
        self.arguments = arguments

        self.wasAssigned = True

    def accept (self, visitor):
        return visitor.visitGlobalVariableDeclarationNode (self)

    def copy (self):
        return GlobalVariableDeclarationNode (self.id.copy (), self.command.copy (), [argument.copy () for argument in self.arguments])

# ========================================================================

class ParameterNode (DeclarationNode):

    def __init__(self, type:TypeSpecifierNode, id, token):
        super().__init__(id, token)
        self.type = type

        self.lineNumber = 0
        self.columnNumber = 0

        # parameters are always assigned
        self.wasAssigned = True

        # x86 fields
        self.stackOffset = 0

    def accept (self, visitor):
        return visitor.visitParameterNode (self)

    def copy (self):
        node = ParameterNode (self.type.copy(), self.id, self.token)
        node.stackOffset = self.stackOffset
        return node

# ========================================================================
# id - string
# params - List(ParameterNode)
# body - CodeBlockNode

class FunctionNode (Node):
    
    def __init__(self, type:TypeSpecifierNode, id, token, params, basicBlocks):
        self.type = type 
        self.id = id
        self.token = token
        self.params = params
        self.basicBlocks = basicBlocks

        self.signature = ""

        self.scopeName = ""
        self.label = ""
        self.endLabel = ""

        self.templateParams = []

        self.lineNumber = 0
        self.columnNumber = 0

        self.localVariables = []

    def accept (self, visitor):
        return visitor.visitFunctionNode (self)

    def copy (self):
        node = FunctionNode (self.type.copy(), self.id, self.token, [param.copy() for param in self.params], [block.copy() for block in self.basicBlocks])
        node.signature = self.signature
        node.scopeName = self.scopeName
        node.label = self.label
        node.endLabel = self.endLabel
        node.localVariables = [n.copy() for n in self.localVariables]
        return node

# ========================================================================
# basic block - represents a group of instructions

class BasicBlockNode (Node):
    
    def __init__(self, name, instructions, token=None):
        self.name = name
        self.instructions = instructions
        self.token = token
        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitBasicBlockNode (self)

    def copy (self):
        return BasicBlockNode (self.name, [instruction.copy () for instruction in self.instructions])

# ========================================================================

class InstructionNode (Node):
    
    def __init__(self, lhsVariable, command, arguments=[]):
        self.hasAssignment = lhsVariable != None
        self.lhsVariable = lhsVariable
        self.command = command
        self.arguments = arguments
        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitInstructionNode (self)

    def copy (self):
        return InstructionNode (self.lhsVariable.copy (), self.command.copy (), [argument.copy () for argument in self.arguments])

# ========================================================================

class CallInstructionNode (Node):
    
    def __init__(self, lhsVariable, function_name, token, arguments=[]):
        self.hasAssignment = lhsVariable != None
        self.lhsVariable = lhsVariable
        self.function_name = function_name
        self.token = token
        self.arguments = arguments
        self.decl = None
        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitCallInstructionNode (self)

    def copy (self):
        return CallInstructionNode (self.lhsVariable.copy (), self.function_name.copy (), self.token.copy (), [argument.copy () for argument in self.arguments])

# ========================================================================
# An argument expression looks like the following
# <type> '(' <expr> ')'
# This represents an argument to be passed to an instruction or function.

class ArgumentExpressionNode (Node):

    def __init__(self, type:TypeSpecifierNode, expression):
        self.type = type
        self.expression = expression

        self.lineNumber = 0
        self.columnNumber = 0

        # x86 fields
        self.stackOffset = 0

    def accept (self, visitor):
        return visitor.visitArgumentExpressionNode (self)

    def copy (self):
        node = ArgumentExpressionNode (self.type.copy(), self.expression.copy ())
        node.stackOffset = self.stackOffset
        return node

# ========================================================================

class ExpressionNode (Node):

    def __init__(self):
        # this field is used for compiling to python
        # so that we can regenerate parentheses
        self.hasParentheses = False

    def accept (self, visitor):
        return visitor.visitExpressionNode (self)

    def copy (self):
        return ExpressionNode()

# ========================================================================
# id - string

class GlobalVariableExpressionNode (ExpressionNode):

    def __init__(self, id, token, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.id = id
        self.token = token

        self.decl = None
        self.wasAssigned = False

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitGlobalVariableExpressionNode (self)

    def copy (self):
        return GlobalVariableExpressionNode(self.id, self.token, self.lineNumber, self.columnNumber)

# ========================================================================
# id - string

class LocalVariableExpressionNode (ExpressionNode):

    def __init__(self, id, token, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.id = id
        self.token = token

        self.decl = None
        self.wasAssigned = False

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitLocalVariableExpressionNode (self)

    def copy (self):
        return LocalVariableExpressionNode (self.id, self.token, self.lineNumber, self.columnNumber)

# ========================================================================
# id - string

class BasicBlockExpressionNode (ExpressionNode):

    def __init__(self, id, token, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.id = id
        self.token = token

        self.decl = None
        self.wasAssigned = False

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitBasicBlockExpressionNode (self)

    def copy (self):
        return BasicBlockExpressionNode(self.id, self.token, self.lineNumber, self.columnNumber)

# ========================================================================
# value - int

class IntLiteralExpressionNode (ExpressionNode):

    def __init__(self, value:int):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.INT32, "int32", None)
        self.value = value

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitIntLiteralExpressionNode (self)

    def copy (self):
        return IntLiteralExpressionNode(self.value)

# ========================================================================
# value - float

class FloatLiteralExpressionNode (ExpressionNode):

    def __init__(self, value:float):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.FLOAT32, "float32", None)
        self.value = value

        self.lineNumber = 0
        self.columnNumber = 0
        
        # x86
        self.label = "<ERROR:LABEL NOT SET>"

    def accept (self, visitor):
        return visitor.visitFloatLiteralExpressionNode (self)

    def copy (self):
        return FloatLiteralExpressionNode(self.value)

# ========================================================================
# value - char

class CharLiteralExpressionNode (ExpressionNode):

    def __init__(self, value:chr):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.BYTE, "byte", None)
        self.value = value

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitCharLiteralExpressionNode (self)

    def copy (self):
        return CharLiteralExpressionNode(self.value)

# ========================================================================
# value - string

class StringLiteralExpressionNode (ExpressionNode):

    def __init__(self, value:str):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.PTR, "ptr", None, 0)
        self.value = value

        self.lineNumber = 0
        self.columnNumber = 0

        # x86
        self.label = "<ERROR:LABEL NOT SET>"

    def accept (self, visitor):
        return visitor.visitStringLiteralExpressionNode (self)

    def copy (self):
        return StringLiteralExpressionNode(self.value)

# ========================================================================

class NullExpressionNode (ExpressionNode):

    def __init__(self):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.PTR, "ptr", None, 0)
        self.value = None

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitNullExpressionNode (self)

    def copy (self):
        return NullExpressionNode(self.lineNumber, self.columnNumber)

# ========================================================================
