# Cerulean IR Compiler - Abstract Syntax Tree For CeruleanASM
# By Amy Burnett
# ========================================================================

# for abstract classes 
from abc import ABC, abstractmethod
from enum import Enum
from sys import exit

# from .visitor import *

# ========================================================================

class Type (Enum):
    BOOL     = 0
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
# ProgramNode: the top-most level node for defining a complete program

class ProgramNode (Node):

    def __init__ (self, codeunits):
        self.codeunits = codeunits

    def accept (self, visitor):
        return visitor.visitProgramNode (self)

    def copy (self):
        node = ProgramNode (None)
        for codeunit in self.codeunits:
            node.codeunits += [codeunit.copy ()]
        return node

    def __repr__ (self):
        return f"Program({repr (self.codeunits)})"

    def __str__ (self):
        return "\n".join ([str (codeunit) for codeunit in self.codeunits])

# ========================================================================

class FunctionNode (Node):
    
    def __init__ (self, id, token, params, instructions):
        self.id = id
        self.token = token
        self.params = params
        self.instructions = instructions

        self.signature = ""

        self.scopeName = ""
        self.label = ""
        self.endLabel = ""

        self.templateParams = []

        self.localVariables = []

    def accept (self, visitor):
        return visitor.visitFunctionNode (self)

    def copy (self):
        node = FunctionNode (self.type, self.id, self.token, [param.copy() for param in self.params])
        node.signature = self.signature
        node.scopeName = self.scopeName
        node.label = self.label
        node.endLabel = self.endLabel
        node.localVariables = [n.copy() for n in self.localVariables]
        return node

    def __repr__ (self):
        return f"Function(id={repr (self.id)}, params={repr (self.params)}, instructions={repr (self.instructions)})"

    def __str__ (self):
        return "\n".join ([
            f"{self.id}:",
            *[f"   // {str(param)}" for param in self.params],
            # NOTE: This does not account for Labels!!
            *[f"   {str(instr)}" for instr in self.instructions]
            ])

# ========================================================================

class InstructionNode (Node):
    
    def __init__ (self, command, arguments, labels=None):
        self.command = command
        self.arguments = arguments
        self.labels = []

    def accept (self, visitor):
        return visitor.visitInstructionNode (self)

    def copy (self):
        return InstructionNode (self.command.copy (), [argument.copy () for argument in self.arguments])

    def __repr__ (self):
        return f"Instruction({repr (self.command)}, args={repr (self.arguments)}, labels={repr (self.labels)})"

    def __str__ (self):
        return f"{self.command} " + ', '.join (str (arg) for arg in self.arguments)

# ========================================================================

class CallInstructionNode (Node):
    
    def __init__ (self, functionName, token, arguments, labels=None):
        self.functionName = functionName
        self.token = token
        self.arguments = arguments
        self.labels = labels if labels is not None else []
        self.decl = None

    def accept (self, visitor):
        return visitor.visitCallInstructionNode (self)

    def copy (self):
        return CallInstructionNode (self.functionName.copy (), self.token.copy (), [argument.copy () for argument in self.arguments])

    def __repr__ (self):
        return f"Call({repr (self.functionName)}, args={repr (self.arguments)}, labels={repr (self.labels)})"

    def __str__ (self):
        # NOTE: Call only accepts a register
        return f"call {self.functionName} " + ', '.join (str (arg) for arg in self.arguments)

# ========================================================================

class RegisterNode (Node):

    def __init__ (self, id, token=None):
        super ().__init__ ()
        self.id = id
        self.token = token

    def accept (self, visitor):
        return visitor.visitRegisterNode (self)

    def copy (self):
        return RegisterNode (self.id, self.token)

    def __repr__ (self):
        return f"Reg({repr (self.id)})"

    def __str__ (self):
        return str (self.id)

# ========================================================================

class VirtualRegisterNode (RegisterNode):

    def __init__ (self, id, token=None):
        super ().__init__ (id, token)
        self.id = id
        self.token = token

    def accept (self, visitor):
        return visitor.visitVirtualRegisterNode (self)

    def copy (self):
        return VirtualRegisterNode (self.id, self.token)

    def __repr__ (self):
        return f"VReg({repr (self.id)})"

    def __str__ (self):
        return str (self.id)

# ========================================================================

class VirtualTempRegisterNode (RegisterNode):
    # For creating unique register names
    _counter = 0

    def __init__ (self, token=None):
        super ().__init__ ("", token)
        self.id = f"tmp{VirtualTempRegisterNode._counter}"
        VirtualTempRegisterNode._counter += 1
        self.token = token

    def accept (self, visitor):
        return visitor.visitVirtualTempRegisterNode (self)

    def copy (self):
        return VirtualTempRegisterNode (self.id, self.token)

    def __repr__ (self):
        return f"TReg({repr (self.id)})"

    def __str__ (self):
        return str (self.id)

# ========================================================================

class PhysicalRegisterNode (RegisterNode):

    def __init__ (self, id, token=None):
        super ().__init__ (id, token)
        self.id = id
        self.token = token

    def accept (self, visitor):
        return visitor.visitPhysicalRegisterNode (self)

    def copy (self):
        return PhysicalRegisterNode (self.id, self.token)

    def __repr__ (self):
        return f"Reg({repr (self.id)})"

    def __str__ (self):
        return str (self.id)

# ========================================================================

class LabelNode (Node):

    def __init__ (self, id, token=None):
        super ().__init__ ()
        self.id = id
        self.token = token

    def accept (self, visitor):
        return visitor.visitLabelNode (self)

    def copy (self):
        return LabelNode (self.id, self.token)

    def __repr__ (self):
        return f"Label({repr (self.id)})"

    def __str__ (self):
        return str (self.id)

# ========================================================================

class LiteralNode (Node):

    def __init__ (self, value):
        super ().__init__ ()
        self.type = Type.INT32
        self.value = value

    def accept (self, visitor):
        return visitor.visitLiteralNode (self)

    def copy (self):
        return LiteralNode (self.value)

    def __repr__ (self):
        return f"Literal({repr (self.value)})"

    def __str__ (self):
        return str (self.value)

# ========================================================================

class IntLiteralNode (LiteralNode):

    def __init__ (self, value:int):
        super ().__init__ (value)
        self.type = Type.INT32
        self.value = value

    def accept (self, visitor):
        return visitor.visitIntLiteralNode (self)

    def copy (self):
        return IntLiteralNode (self.value)

    def __repr__ (self):
        return f"Int({repr (self.value)})"

    def __str__ (self):
        return str (self.value)

# ========================================================================

class FloatLiteralNode (LiteralNode):

    def __init__ (self, value:float):
        super ().__init__ (value)
        self.type = Type.FLOAT32
        self.value = value

    def accept (self, visitor):
        return visitor.visitFloatLiteralNode (self)

    def copy (self):
        return FloatLiteralNode (self.value)

    def __repr__ (self):
        return f"Float({repr (self.value)})"

    def __str__ (self):
        return str (self.value)

# ========================================================================

class CharLiteralNode (LiteralNode):

    def __init__ (self, value:chr):
        super ().__init__ (value)
        self.type = Type.BYTE
        self.value = value

    def accept (self, visitor):
        return visitor.visitCharLiteralNode (self)

    def copy (self):
        return CharLiteralNode (self.value)

    def __repr__ (self):
        return f"Char({repr (self.value)})"

    def __str__ (self):
        return f"'{str(self.value)}'"

# ========================================================================

class StringLiteralNode (LiteralNode):

    def __init__ (self, value:str):
        super ().__init__ (value)
        self.type = Type.PTR
        self.value = value

    def accept (self, visitor):
        return visitor.visitStringLiteralNode (self)

    def copy (self):
        return StringLiteralNode (self.value)

    def __repr__ (self):
        return f"String({repr (self.value)})"

    def __str__ (self):
        return str (self.value)
