# CeruleanASM: Abstract Syntax Tree
# By Amy Burnett
# ========================================================================

# for abstract classes 
from abc import ABC, abstractmethod
from enum import Enum
from sys import exit

from .visitor import *

# ========================================================================

class Type (Enum):
    BOOL     = 1
    BYTE     = 2
    CHAR     = 3
    INT32    = 4
    INT64    = 5
    FLOAT32  = 6
    FLOAT64  = 7
    VOID     = 8
    USERTYPE = 9
    NULL     = 10
    UNKNOWN  = 11

# ========================================================================

class Node (ABC):
    @abstractmethod
    def accept (self, visitor):
        pass

    @abstractmethod
    def copy (self):
        pass

# ========================================================================

class ProgramNode (Node):

    def __init__ (self, codeunits):
        self.codeunits = codeunits
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

class LabelNode (Node):

    def __init__ (self, token, id):
        self.token = token
        self.id = id

    def accept (self, visitor):
        return visitor.visitLabelNode (self)

    def copy (self):
        return LabelNode (self.token, self.id)

# ========================================================================

class InstructionNode (Node):

    def __init__(self, token, id, args):
        self.token = token
        self.id = id
        self.args = args
        self.address = None
        # Size of the instruction in bytes
        # Currently all instructions are 4 bytes, but in the future
        # we might want to support larger instructions
        self.size = 4

    def accept (self, visitor):
        return visitor.visitInstructionNode (self)

    def copy (self):
        return InstructionNode (self.token, self.id, self.args.copy())

# ========================================================================

class RegisterExpressionNode (Node):

    def __init__ (self, token, id):
        self.token = token
        self.id = id

    def accept (self, visitor):
        return visitor.visitRegisterExpressionNode (self)

    def copy (self):
        return RegisterExpressionNode (self.token, self.id)

# ========================================================================

class LabelExpressionNode (Node):

    def __init__ (self, token, id):
        self.token = token
        self.id = id
        self.address = None

    def accept (self, visitor):
        return visitor.visitLabelExpressionNode (self)

    def copy (self):
        return LabelExpressionNode (self.token, self.id)

# ========================================================================

class IntLiteralExpressionNode (Node):

    def __init__ (self, token, value:int):
        self.token = token
        self.value = value

    def accept (self, visitor):
        return visitor.visitIntLiteralExpressionNode (self)

    def copy (self):
        return IntLiteralExpressionNode (self.token, self.value)

# ========================================================================

class FloatLiteralExpressionNode (Node):

    def __init__ (self, token, value:float):
        self.token = token
        self.value = value

    def accept (self, visitor):
        return visitor.visitFloatLiteralExpressionNode (self)

    def copy (self):
        return FloatLiteralExpressionNode (self.token, self.value)

# ========================================================================

class CharLiteralExpressionNode (Node):

    def __init__ (self, token, value:chr):
        self.token = token
        self.value = value

    def accept (self, visitor):
        return visitor.visitCharLiteralExpressionNode (self)

    def copy (self):
        return CharLiteralExpressionNode (self.token, self.value)

# ========================================================================

class StringLiteralExpressionNode (Node):

    def __init__ (self, token, value:str):
        self.token = token
        self.value = value

    def accept (self, visitor):
        return visitor.visitStringLiteralExpressionNode (self)

    def copy (self):
        return StringLiteralExpressionNode (self.token, self.value)

# ========================================================================

class NullExpressionNode (Node):

    def __init__ (self, token):
        self.token = token
        self.value = 0

    def accept (self, visitor):
        return visitor.visitNullExpressionNode (self)

    def copy (self):
        return NullExpressionNode (self.token)
