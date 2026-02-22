# Cerulean IR Compiler - Abstract Syntax Tree
# By Amy Burnett
# ========================================================================

# for abstract classes 
from abc import ABC, abstractmethod
from enum import Enum
from sys import exit

from .visitor import *
from .irTypes import Type

# ========================================================================

TAB_SPACE = "    "

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

    def accept (self, visitor):
        return visitor.visitTypeSpecifierNode (self)

    def copy (self):
        node = TypeSpecifierNode (self.type, self.id, self.token)
        node.arrayDimensions = self.arrayDimensions
        node.decl = self.decl
        node.isGeneric = self.isGeneric
        return node

    def __repr__ (self):
        return f"TypeSpecifierNode(type={self.type}, id='{self.id}', arrayDimensions={self.arrayDimensions})"

    def __str__(self):
        # <type>{*}
        s = [self.id]
        for i in range(self.arrayDimensions):
            s += ["*"]
        return "".join(s)

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

    def __repr__ (self):
        codeunits_repr = f",\n{TAB_SPACE}".join(repr(cu) for cu in self.codeunits)
        return f"ProgramNode(codeunits=[\n{TAB_SPACE}{codeunits_repr}\n], localVariables={repr(self.localVariables)}, floatLiterals={repr(self.floatLiterals)}, stringLiterals={repr(self.stringLiterals)})"

    def __str__(self):
        s = []
        for codeunit in self.codeunits:
            s += [str(codeunit)]
        return "\n".join(s)

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

    def __repr__ (self):
        return f"DeclarationNode(id='{self.id}', scopeName='{self.scopeName}')"

    def __str__ (self):
        return self.id

# ========================================================================

class VariableDeclarationNode (DeclarationNode):

    def __init__(self, id, token):
        super().__init__ (id, token)
        self.wasAssigned = True
        self.references = []

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

    def __repr__ (self):
        return f"VariableDeclarationNode(id='{self.id}', stackOffset={self.stackOffset})"

    def __str__ (self):
        return self.id

# ========================================================================

class GlobalVariableDeclarationNode (DeclarationNode):
    
    def __init__(self, id, token, command, arguments):
        super().__init__ (id, token)
        self.command = command
        self.arguments = arguments
        self.wasAssigned = True
        self.references = []

    def accept (self, visitor):
        return visitor.visitGlobalVariableDeclarationNode (self)

    def copy (self):
        return GlobalVariableDeclarationNode (self.id.copy (), self.command.copy (), [argument.copy () for argument in self.arguments])

    def __repr__ (self):
        args_repr = ', '.join(repr(arg) for arg in self.arguments)
        return f"GlobalVariableDeclarationNode(id='{self.id}', command='{self.command}', arguments=[{args_repr}])"

    def __str__ (self):
        args_str = ', '.join(str(arg) for arg in self.arguments)
        return f"global {self.id} = {self.command} ({args_str})"

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

    def __repr__ (self):
        return f"ParameterNode(type={repr(self.type)}, id='{self.id}')"

    def __str__ (self):
        return f"{self.type}({self.id})"

# ========================================================================
# FunctionNode - represents both function definitions and extern declarations
# id - string
# params - List(ParameterNode)
# basicBlocks - List(BasicBlockNode) or None for extern functions
# isExtern - bool indicating if this is an extern declaration

class FunctionNode (Node):
    
    def __init__(self, type:TypeSpecifierNode, id, token, params, basicBlocks, isExtern=False):
        self.type = type 
        self.id = id
        self.token = token
        self.params = params
        self.basicBlocks = basicBlocks  # None or [] for extern functions
        self.isExtern = isExtern  # True for extern declarations

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
        node = FunctionNode (
            self.type.copy(), 
            self.id, 
            self.token, 
            [param.copy() for param in self.params], 
            [block.copy() for block in self.basicBlocks] if self.basicBlocks else None,
            self.isExtern
        )
        node.signature = self.signature
        node.scopeName = self.scopeName
        node.label = self.label
        node.endLabel = self.endLabel
        node.localVariables = [n.copy() for n in self.localVariables]
        return node

    def __repr__ (self):
        basicblocks_repr = f',\n{TAB_SPACE}{TAB_SPACE}'.join(repr(bb) for bb in self.basicBlocks) if self.basicBlocks else "None"
        params_repr = ', '.join(repr(p) for p in self.params)
        return f"FunctionNode(type={repr(self.type)}, id='{self.id}', params=[{params_repr}], basicBlocks=[\n{TAB_SPACE}{TAB_SPACE}{basicblocks_repr}\n{TAB_SPACE}], isExtern={self.isExtern})"

    def __str__ (self):
        params_str = ', '.join(str(p) for p in self.params)
        extern_prefix = "extern " if self.isExtern else ""
        return f"{extern_prefix}function {self.type} {self.id} ({params_str})"

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

    def __repr__ (self):
        instructions_repr = f',\n{TAB_SPACE}{TAB_SPACE}{TAB_SPACE}'.join(repr(instr) for instr in self.instructions)
        return f"BasicBlockNode(name='{self.name}', instructions=[\n{TAB_SPACE}{TAB_SPACE}{TAB_SPACE}{instructions_repr}\n{TAB_SPACE}{TAB_SPACE}], token={repr(self.token)})"

    def __str__ (self):
        instr_str = '\n        '.join(str(i) for i in self.instructions)
        return f"    block {self.name} {{\n        {instr_str}\n    }}"

# ========================================================================

class InstructionNode (Node):
    
    def __init__(self, lhsVariable, command, arguments=None):
        self.hasAssignment = lhsVariable != None
        self.lhsVariable = lhsVariable
        self.command = command
        self.arguments = arguments if arguments is not None else []
        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitInstructionNode (self)

    def copy (self):
        return InstructionNode (self.lhsVariable.copy (), self.command.copy (), [argument.copy () for argument in self.arguments])

    def __repr__ (self):
        args_repr = ', '.join(repr(arg) for arg in self.arguments)
        lhs_repr = repr(self.lhsVariable) if self.hasAssignment else "None"
        return f"InstructionNode(lhs={lhs_repr}, command='{self.command}', arguments=[{args_repr}])"

    def __str__ (self):
        args_str = ', '.join(str(arg) for arg in self.arguments)
        lhs_str = f"{self.lhsVariable} = " if self.hasAssignment else ""
        return f"{lhs_str}{self.command} ({args_str})"

# ========================================================================

class CallInstructionNode (Node):
    
    def __init__(self, lhsVariable, function_name, token, arguments=None):
        self.hasAssignment = lhsVariable != None
        self.lhsVariable = lhsVariable
        self.function_name = function_name
        self.token = token
        self.arguments = arguments if arguments is not None else []
        self.decl = None
        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitCallInstructionNode (self)

    def copy (self):
        return CallInstructionNode (self.lhsVariable.copy (), self.function_name.copy (), self.token.copy (), [argument.copy () for argument in self.arguments])

    def __repr__ (self):
        args_repr = ', '.join(repr(arg) for arg in self.arguments)
        lhs_repr = repr(self.lhsVariable) if self.hasAssignment else "None"
        return f"CallInstructionNode(lhs={lhs_repr}, function='{self.function_name}', arguments=[{args_repr}])"

    def __str__ (self):
        args_str = ', '.join(str(arg) for arg in self.arguments)
        lhs_str = f"{self.lhsVariable} = " if self.hasAssignment else ""
        return f"{lhs_str}call {self.function_name} ({args_str})"

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

    def __repr__ (self):
        return f"ArgumentExpressionNode(type={repr(self.type)}, expression={repr(self.expression)})"

    def __str__ (self):
        return f"{self.type}({self.expression})"

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

    def __repr__ (self):
        return "ExpressionNode()"

    def __str__ (self):
        return "<expr>"

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

    def __repr__ (self):
        return f"GlobalVariableExpressionNode(id='{self.id}')"

    def __str__ (self):
        return self.id

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

    def __repr__ (self):
        return f"LocalVariableExpressionNode(id='{self.id}')"

    def __str__ (self):
        return self.id

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

    def __repr__ (self):
        return f"BasicBlockExpressionNode(id='{self.id}')"

    def __str__ (self):
        return f"block({self.id})"

# ========================================================================
# value - int

class IntLiteralExpressionNode (ExpressionNode):

    def __init__(self, value:int):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.I32, "i32", None)
        self.value = value

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitIntLiteralExpressionNode (self)

    def copy (self):
        return IntLiteralExpressionNode(self.value)

    def __repr__ (self):
        return f"IntLiteralExpressionNode({self.value})"

    def __str__ (self):
        return str(self.value)

# ========================================================================
# value - float

class FloatLiteralExpressionNode (ExpressionNode):

    def __init__(self, value:float):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.F32, "f32", None)
        self.value = value

        self.lineNumber = 0
        self.columnNumber = 0
        
        # x86
        self.label = "<ERROR:LABEL NOT SET>"

    def accept (self, visitor):
        return visitor.visitFloatLiteralExpressionNode (self)

    def copy (self):
        return FloatLiteralExpressionNode(self.value)

    def __repr__ (self):
        return f"FloatLiteralExpressionNode({self.value})"

    def __str__ (self):
        return str(self.value)

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

    def __repr__ (self):
        return f"CharLiteralExpressionNode('{self.value}')"

    def __str__ (self):
        return f"'{self.value}'"

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

    def __repr__ (self):
        return f"StringLiteralExpressionNode({repr(self.value)})"

    def __str__ (self):
        return f'"{self.value}"'

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

    def __repr__ (self):
        return "NullExpressionNode()"

    def __str__ (self):
        return "null"

# ========================================================================
