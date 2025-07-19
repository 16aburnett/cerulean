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

    def __init__ (self, codeunits, visibilityDirectives=[]):
        self.codeunits = codeunits
        self.visibilityDirectives = visibilityDirectives
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

    def __repr__ (self):
        return f"Program({repr (self.codeunits)})"

    def __str__ (self):
        return "\n".join ([repr (codeunit) for codeunit in self.codeunits])

    def __eq__ (self, other):
        if not isinstance (other, ProgramNode):
            return False
        if len (self.codeunits) != len (other.codeunits):
            return False
        for i in range (0, len (self.codeunits)):
            if self.codeunits[i] != other.codeunits[i]:
                return False
        return True

# ========================================================================

class LabelNode (Node):

    def __init__ (self, token, id, visibility=None):
        self.token = token
        self.id = id
        self.visibility = visibility
        # Needs to be assigned
        self.address = 0

    def accept (self, visitor):
        return visitor.visitLabelNode (self)

    def copy (self):
        return LabelNode (self.token, self.id, self.visibility)

    def __repr__ (self):
        return f"Label('{self.id}')"

    def __str__ (self):
        return f"{self.id}:"

    def __eq__ (self, other):
        if not isinstance (other, LabelNode):
            return False
        return self.id == other.id

# ========================================================================

class VisibilityDirectiveNode (Node):

    def __init__ (self, token, id, label):
        self.token = token
        self.id = id
        self.label = label

    def accept (self, visitor):
        return visitor.visitVisibilityDirectiveNode (self)

    def copy (self):
        return VisibilityDirectiveNode (self.token, self.id, self.label)

    def __repr__ (self):
        return f"VisibilityDirective('{self.id}', label='{self.label}')"

    def __str__ (self):
        return f"@{self.id} {self.label}"

    def __eq__ (self, other):
        return isinstance (other, VisibilityDirectiveNode) and \
            self.id == other.id and \
            self.label == other.label

# ========================================================================

class DataDirectiveNode (Node):

    def __init__ (self, token, id, args, labels):
        self.token = token
        self.id = id
        self.args = args
        self.labels = labels
        self.address = None
        # Size of the data in bytes
        # To be filled in later
        self.size = None

    def accept (self, visitor):
        return visitor.visitDataDirectiveNode (self)

    def copy (self):
        return DataDirectiveNode (self.token, self.id, self.args.copy (), self.labels.copy ())

    def __repr__ (self):
        return f"DataDirective('{self.id}', args={repr (self.args)})"

    def __str__ (self):
        return f".{self.id} " + ', '.join (str (arg) for arg in self.args)

    def __eq__ (self, other):
        return isinstance (other, DataDirectiveNode) and \
            self.id == other.id and \
            self.args == other.args and \
            self.labels == other.labels

# ========================================================================

class InstructionNode (Node):

    def __init__ (self, token, id, args, labels=[]):
        self.token = token
        self.id = id
        self.args = args
        self.labels = labels
        self.address = None
        # Size of the instruction in bytes
        # Currently all instructions are 4 bytes, but in the future
        # we might want to support larger instructions
        self.size = 4

    def accept (self, visitor):
        return visitor.visitInstructionNode (self)

    def copy (self):
        return InstructionNode (self.token, self.id, self.args.copy (), self.labels.copy ())

    def __repr__ (self):
        return f"Instruction('{self.id}', args={repr (self.args)}, labels={repr (self.labels)})"

    def __str__ (self):
        return f"{self.id} " + ', '.join (str (arg) for arg in self.args)

    def __eq__ (self, other):
        return isinstance (other, InstructionNode) and \
            self.id == other.id and \
            self.args == other.args and \
            self.labels == other.labels

# ========================================================================

class RegisterExpressionNode (Node):

    def __init__ (self, token, id):
        self.token = token
        self.id = id
        self.value = None

    def accept (self, visitor):
        return visitor.visitRegisterExpressionNode (self)

    def copy (self):
        return RegisterExpressionNode (self.token, self.id)

    def __repr__ (self):
        return f"Reg('{self.id}')"

    def __str__ (self):
        return self.id

    def __eq__ (self, other):
        return isinstance (other, RegisterExpressionNode) and \
            self.id == other.id

# ========================================================================

class LabelExpressionNode (Node):

    def __init__ (self, token, id, modifierToken=None, modifier=None, decl=None):
        self.token = token
        self.id = id
        self.modifierToken = modifierToken
        if self.modifierToken:
            self.modifier = self.modifierToken.lexeme[1:]
        else:
            self.modifier = modifier
        self.address = None
        self.value = None
        self.decl = decl

    def accept (self, visitor):
        return visitor.visitLabelExpressionNode (self)

    def copy (self):
        return LabelExpressionNode (self.token, self.id, self.modifierToken, self.modifier)

    def __repr__ (self):
        return f"Label('{self.id}', modifier={repr (self.modifier)})"

    def __str__ (self):
        if self.modifier:
            return f"%{self.modifier}({self.id})"
        return self.id

    def __eq__ (self, other):
        return isinstance (other, LabelExpressionNode) and \
            self.id == other.id and \
            self.modifier == other.modifier

# ========================================================================

class IntLiteralExpressionNode (Node):

    def __init__ (self, token, value:int):
        self.token = token
        self.value = value

    def accept (self, visitor):
        return visitor.visitIntLiteralExpressionNode (self)

    def copy (self):
        return IntLiteralExpressionNode (self.token, self.value)

    def __repr__ (self):
        return repr (self.value)

    def __str__ (self):
        return str (self.value)

    def __eq__ (self, other):
        return isinstance (other, IntLiteralExpressionNode) and \
            self.value == other.value

# ========================================================================

class FloatLiteralExpressionNode (Node):

    def __init__ (self, token, value:float):
        self.token = token
        self.value = value

    def accept (self, visitor):
        return visitor.visitFloatLiteralExpressionNode (self)

    def copy (self):
        return FloatLiteralExpressionNode (self.token, self.value)

    def __repr__ (self):
        return repr (self.value)

    def __str__ (self):
        return str (self.value)

    def __eq__ (self, other):
        return isinstance (other, FloatLiteralExpressionNode) and \
            self.value == other.value

# ========================================================================

class CharLiteralExpressionNode (Node):

    def __init__ (self, token, value:chr):
        self.token = token
        self.value = value

    def accept (self, visitor):
        return visitor.visitCharLiteralExpressionNode (self)

    def copy (self):
        return CharLiteralExpressionNode (self.token, self.value)

    def __repr__ (self):
        return repr (self.value)

    def __str__ (self):
        return f"'{self.value}'"

    def __eq__ (self, other):
        return isinstance (other, CharLiteralExpressionNode) and \
            self.value == other.value

# ========================================================================

class StringLiteralExpressionNode (Node):

    def __init__ (self, token, value:str):
        self.token = token
        self.value = value

    def accept (self, visitor):
        return visitor.visitStringLiteralExpressionNode (self)

    def copy (self):
        return StringLiteralExpressionNode (self.token, self.value)

    def __repr__ (self):
        return repr (self.value)

    def __str__ (self):
        return self.value

    def __eq__ (self, other):
        return isinstance (other, StringLiteralExpressionNode) and \
            self.value == other.value

# ========================================================================

class NullExpressionNode (Node):

    def __init__ (self, token):
        self.token = token
        self.value = 0

    def accept (self, visitor):
        return visitor.visitNullExpressionNode (self)

    def copy (self):
        return NullExpressionNode (self.token)

    def __repr__ (self):
        return repr (self.value)

    def __str__ (self):
        return self.value

    def __eq__ (self, other):
        return isinstance (other, NullExpressionNode) and \
            self.value == other.value
