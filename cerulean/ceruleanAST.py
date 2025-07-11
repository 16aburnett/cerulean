# Cerulean Compiler - Abstract Syntax Tree
# By Amy Burnett
# April 24 2021
# ========================================================================

# for abstract classes 
from abc import ABC, abstractmethod
from enum import Enum
from sys import exit

if __name__ == "ceruleanAST":
    from visitor import *
else:
    from .visitor import *

# ========================================================================

class Type(Enum):
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

class Security (Enum):
    PUBLIC = 1
    PRIVATE = 2

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
    
    def __init__(self, type:Type, id, token, templateParams=[], arrayDimensions=0):
        self.type = type 
        self.id = id
        self.token = token
        self.arrayDimensions = arrayDimensions

        self.templateParams = templateParams

        self.decl = None

        self.isGeneric = False

        self.lineNumber = 0
        self.columnNumber = 0

    def __str__(self):
        s = [self.id]
        if len(self.templateParams) > 0:
            s += ["<:", self.templateParams[0].__str__()]
            for i in range(1, len(self.templateParams)):
                s += [f", {self.templateParams[i].__str__()}"]
            s += [":>"]
        for i in range(self.arrayDimensions):
            s += ["[]"]
        return "".join(s)

    def accept (self, visitor):
        return visitor.visitTypeSpecifierNode (self)

    def copy (self):
        node = TypeSpecifierNode (self.type, self.id, self.token)
        node.arrayDimensions = self.arrayDimensions
        node.decl = self.decl
        node.isGeneric = self.isGeneric
        node.templateParams = [t.copy() for t in self.templateParams]
        return node

# ========================================================================
# codeunits - List(CodeUnitNode)

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

class DeclarationNode (Node):

    def __init__(self, type:TypeSpecifierNode, id, token):
        self.type = type
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

class GlobalVariableDeclarationNode (DeclarationNode):

    def __init__(self, type:TypeSpecifierNode, id, token, rhs):
        super().__init__(type, id, token)
        self.rhs = rhs
        self.wasAssigned = False
        # For determining whether to use alloca or reg
        self.assignCount = 0

        self.lineNumber = 0
        self.columnNumber = 0

        # x86 fields
        self.stackOffset = 0

    def accept (self, visitor):
        return visitor.visitGlobalVariableDeclarationNode (self)

    def copy (self):
        node = GlobalVariableDeclarationNode (self.type.copy(), self.id, self.token, self.rhs.copy())
        node.stackOffset = self.stackOffset
        return node

# ========================================================================

class VariableDeclarationNode (DeclarationNode):

    def __init__(self, type:TypeSpecifierNode, id, token):
        super().__init__(type, id, token)
        self.wasAssigned = False
        # For determining whether to use alloca or reg
        self.assignCount = 0

        self.lineNumber = 0
        self.columnNumber = 0

        # x86 fields
        self.stackOffset = 0

    def accept (self, visitor):
        return visitor.visitVariableDeclarationNode (self)

    def copy (self):
        node = VariableDeclarationNode (self.type.copy(), self.id, self.token)
        node.stackOffset = self.stackOffset
        return node

# ========================================================================

class ParameterNode (DeclarationNode):

    def __init__(self, type:TypeSpecifierNode, id, token):
        super().__init__(type, id, token)
        # Parameters are always assigned
        self.wasAssigned = True
        # Parameter nodes are allocated on the stack
        # Added this here for completion
        self.assignCount = 1

        self.lineNumber = 0
        self.columnNumber = 0

        # x86 fields
        self.stackOffset = 0

    def accept (self, visitor):
        return visitor.visitParameterNode (self)

    def copy (self):
        node = ParameterNode (self.type.copy(), self.id, self.token)
        node.stackOffset = self.stackOffset
        return node

# ========================================================================

class GenericDeclarationNode (DeclarationNode):

    def __init__(self, type:TypeSpecifierNode, id, token):
        super().__init__(type, id, token)

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitGenericDeclarationNode (self)

    def copy (self):
        node = GenericDeclarationNode (self.type.copy(), self.id, self.token)
        return node

# ========================================================================

class CodeUnitNode (Node):
    
    def __init__(self):
        pass

    def accept (self, visitor):
        return visitor.visitCodeUnitNode (self)

    def copy (self):
        node = CodeUnitNode ()
        return node

# ========================================================================
# id - string
# params - List(ParameterNode)
# body - CodeBlockNode

class FunctionNode (CodeUnitNode):
    
    def __init__(self, type:TypeSpecifierNode, id, token, params, body):
        self.type = type 
        self.id = id
        self.token = token
        self.params = params
        self.body = body

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
        node = FunctionNode (self.type.copy(), self.id, self.token, [param.copy() for param in self.params], self.body.copy())
        node.signature = self.signature
        node.scopeName = self.scopeName
        node.label = self.label
        node.endLabel = self.endLabel
        node.localVariables = [n.copy() for n in self.localVariables]
        return node

# ========================================================================
# id - string
# body - CodeBlockNode

class ClassDeclarationNode (CodeUnitNode):
    
    def __init__(self, type, id, token, parent, pToken, constructors, fields, virtualMethods, methods):
        self.type = type
        self.type.decl = self 
        self.id = id
        self.token = token
        self.parent = parent 
        self.pToken = pToken
        self.pDecl = None 
        self.constructors = constructors
        self.fields = fields 
        self.methods = methods 

        self.templateParams = []

        self.children = []

        self.virtualMethods = [] 
        self.functionPointerList = [] 

        self.scopeName = ""
        self.dtableScopeName = ""

        self.signature = ""
        self.signatureNoScope = ""

        self.isForwardDeclaration = False 

        # x86 dispatch table offset
        self.stackOffset = 0

        # x86 this keyword offset
        self.thisStackOffset = 0

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitClassDeclarationNode (self)

    def copy (self):
        node = ClassDeclarationNode (self.type.copy(), self.id, self.token, self.parent, self.pToken, [c.copy() for c in self.constructors], [f.copy() for f in self.fields], [v.copy() for v in self.virtualMethods], [m.copy() for m in self.methods])
        node.children = [child.copy () for child in self.children]
        node.functionPointerList = [fptr.copy() for fptr in self.functionPointerList]
        node.scopeName = self.scopeName
        node.dtableScopeName = self.dtableScopeName
        node.isForwardDeclaration = self.isForwardDeclaration
        return node

# ========================================================================
# id - string

class FieldDeclarationNode (DeclarationNode):
    
    def __init__(self, security, type, id, token):
        self.security = security
        super().__init__(type, id, token)
        self.parentClass = None
        self.index = 0

        self.scopeName = ""
        self.signature = ""
        self.signatureNoScope = ""

        self.isInherited = False
        self.originalInheritedField = None

        # x86 fields
        self.stackOffset = 0

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitFieldDeclarationNode (self)

    def copy (self):
        node = FieldDeclarationNode (self.security, self.type.copy(), self.id, self.token)
        if self.parentClass != None:
            node.parentClass = self.parentClass.copy ()
        node.index = self.index 
        node.isInherited = self.isInherited
        return node

# ========================================================================
# id - string

class MethodDeclarationNode (DeclarationNode):
    
    def __init__(self, security, type, id, token, params, body, isVirtual=False):
        self.security = security
        super().__init__(type, id, token)
        self.params = params
        self.body = body 
        self.parentClass = None

        self.scopeName = ""

        self.signature = ""
        self.signatureNoScope = ""

        self.isVirtual = isVirtual
        self.isInherited = False 
        self.inheritedMethod = None
        self.isOverride = False 

        self.lineNumber = 0
        self.columnNumber = 0

        self.localVariables = []

    def accept (self, visitor):
        return visitor.visitMethodDeclarationNode (self)

    def copy (self):
        node = MethodDeclarationNode (self.security, self.type.copy(), self.id, self.token, [p.copy() for p in self.params], self.body.copy (), self.isVirtual)
        
        if self.parentClass != None:
            node.parentClass = self.parentClass.copy ()

        node.scopeName = self.scopeName

        node.signature = self.signature
        node.signatureNoScope = self.signatureNoScope

        node.isVirtual = self.isVirtual
        node.isInherited = self.isInherited 
        if self.inheritedMethod != None:
            node.inheritedMethod = self.inheritedMethod.copy()
        node.isOverride = self.isOverride 
        return node

# ========================================================================
# id - string

class ConstructorDeclarationNode (DeclarationNode):
    
    def __init__(self, token, params, body):
        self.type = None
        self.id = ""
        self.token = token
        self.params = params
        self.body = body 
        self.parentClass = None

        self.scopeName = ""

        self.lineNumber = 0
        self.columnNumber = 0

        self.localVariables = []

    def accept (self, visitor):
        return visitor.visitConstructorDeclarationNode (self)

    def copy (self):
        node = ConstructorDeclarationNode (self.token, [p.copy() for p in self.params], self.body.copy ())
        
        if self.parentClass != None:
            node.parentClass = self.parentClass.copy ()

        node.scopeName = self.scopeName

        return node

# ========================================================================

class EnumDeclarationNode (CodeUnitNode):
    
    def __init__(self, type, id, token, fields):
        self.type = type
        self.type.decl = self 
        self.id = id
        self.token = token
        self.fields = fields 
        
        self.parent = "Enum"
        self.pDecl = None 

        self.scopeName = ""
        self.dtableScopeName = ""

        self.isForwardDeclaration = False 

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitEnumDeclarationNode (self)

    def copy (self):
        node = EnumDeclarationNode (self.type.copy(), self.id, self.token, [field.copy() for field in self.fields])
        return node

# ========================================================================

class FunctionTemplateDeclarationNode (CodeUnitNode):
    
    def __init__(self, type, id, token, types, function):
        self.type = type
        self.id = id
        self.token = token

        # template parameter names 
        self.types = types 

        # function declaration for the template 
        self.function = function

        # map of (string(templateParams), functionDeclaration)
        self.instantiations = {}

        self.scopeName = ""
        self.dtableScopeName = ""

        self.isForwardDeclaration = False 

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitFunctionTemplateNode (self)

    def copy (self):
        node = FunctionTemplateDeclarationNode (self.type.copy(), self.id, self.token, [type for type in self.types], self.function.copy())
        return node

# ========================================================================

class ClassTemplateDeclarationNode (CodeUnitNode):
    
    def __init__(self, type, id, token, templateParams, _class):
        self.type = type
        self.id = id
        self.token = token

        # template parameter names 
        self.templateParams = templateParams 

        # class declaration for the template 
        self._class = _class

        # map of (string(templateParams), classDeclarationNodes)
        self.instantiations = {}

        self.scopeName = ""
        self.dtableScopeName = ""

        self.isForwardDeclaration = False 

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitClassTemplateDeclarationNode (self)

    def copy (self):
        return ClassTemplateDeclarationNode (self.type.copy(), self.id, self.token, [type for type in self.templateParams], self._class.copy())

# ========================================================================

class StatementNode (CodeUnitNode):
    
    def __init__(self):
        pass

    def accept (self, visitor):
        return visitor.visitStatementNode (self)

    def copy (self):
        return StatementNode ()

# ========================================================================
# cond - ExpressionNode
# body - StatementNode
# elifs - List(ElifStatementNode)
# elseStmt - ElseStatementNode

class IfStatementNode (StatementNode):
    
    def __init__(self, cond, body, elifs=[], elseStmt=None):
        self.cond = cond
        self.body = body
        self.elifs = elifs
        self.elseStmt = elseStmt 

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitIfStatementNode (self)

    def copy (self):
        return IfStatementNode (self.cond.copy(), self.body.copy(), [e.copy() for e in self.elifs], None if self.elseStmt == None else self.elseStmt.copy())

# ========================================================================
# cond - ExpressionNode
# body - StatementNode

class ElifStatementNode (StatementNode):
    
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitElifStatementNode (self)

    def copy (self):
        return ElifStatementNode (self.cond.copy(), self.body.copy())

# ========================================================================
# body - StatementNode

class ElseStatementNode (StatementNode):
    
    def __init__(self, body):
        self.body = body

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitElseStatementNode (self)

    def copy (self):
        return ElseStatementNode (self.body.copy())

# ========================================================================
# init - ExpressionNode
# cond - ExpressionNode
# update - ExpressionNode
# body - CodeUnitNode

class ForStatementNode (StatementNode):
    
    def __init__(self, init, cond, update, body, elseStmt):
        self.init = init
        self.cond = cond
        self.update = update
        self.body = body 
        self.elseStmt = elseStmt
        self.startLabel = None
        self.continueLabel = None
        self.breakLabel = None
        self.endLabel = None

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitForStatementNode (self)

    def copy (self):
        return ForStatementNode (self.init.copy(), self.cond.copy(), self.update.copy(), self.body.copy(), self.elseStmt.copy() if self.elseStmt else None)

# ========================================================================
# cond - ExpressionNode
# body - CodeUnitNode

class WhileStatementNode (StatementNode):
    
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body 
        self.startLabel = None
        self.continueLabel = None
        self.breakLabel = None
        self.endLabel = None

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitWhileStatementNode (self)

    def copy (self):
        return WhileStatementNode (self.cond.copy(), self.body.copy())

# ========================================================================
# expr - ExpressionNode

class ExpressionStatementNode (StatementNode):
    
    def __init__(self, expr=None):
        self.expr = expr  

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitExpressionStatementNode (self)

    def copy (self):
        return ExpressionStatementNode (self.expr.copy() if self.expr != None else None)

# ========================================================================
# expr - ExpressionNode

class ReturnStatementNode (StatementNode):
    
    def __init__(self, token, expr):
        self.token = token
        self.expr = expr 

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitReturnStatementNode (self)

    def copy (self):
        return ReturnStatementNode (self.token, self.expr.copy() if self.expr != None else None)

# ========================================================================

class ContinueStatementNode (StatementNode):
    
    def __init__(self, token):
        self.token = token

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitContinueStatementNode (self)

    def copy (self):
        return ContinueStatementNode (self.token)

# ========================================================================

class BreakStatementNode (StatementNode):
    
    def __init__(self, token):
        self.token = token

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitBreakStatementNode (self)

    def copy (self):
        return BreakStatementNode (self.token)

# ========================================================================
# statements - List(StatementNode)

class CodeBlockNode (StatementNode):
    
    def __init__(self, statements):
        self.statements = statements

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitCodeBlockNode (self)

    def copy (self):
        return CodeBlockNode ([statement.copy() for statement in self.statements])

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
# lhs - ExpressionNode 
# rhs - ExpressionNode

class TupleExpressionNode (ExpressionNode):

    def __init__(self, lhs, rhs, line, column):
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.lhs = lhs
        self.rhs = rhs 

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitTupleExpressionNode (self)

    def copy (self):
        return TupleExpressionNode(self.lhs.copy(), self.rhs.copy(), self.lineNumber, self.columnNumber)

# ========================================================================
# lhs - ExpressionNode
# op  - AssignOp 
# rhs - ExpressionNode

class AssignExpressionNode (ExpressionNode):

    def __init__(self, token, lhs, rhs, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.lhs = lhs
        self.rhs = rhs 

        self.overloadedFunctionCall = None

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitAssignExpressionNode (self)

    def copy (self):
        return AssignExpressionNode(self.token, self.lhs.copy(), self.rhs.copy(), self.lineNumber, self.columnNumber)

# ========================================================================
# lhs - ExpressionNode
# rhs - ExpressionNode

class LogicalOrExpressionNode (ExpressionNode):

    def __init__(self, token, lhs, rhs, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.lhs = lhs
        self.rhs = rhs 

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitLogicalOrExpressionNode (self)

    def copy (self):
        return LogicalOrExpressionNode(self.token, self.lhs.copy(), self.rhs, self.lineNumber, self.columnNumber)

# ========================================================================
# lhs - ExpressionNode
# rhs - ExpressionNode

class LogicalAndExpressionNode (ExpressionNode):

    def __init__(self, token, lhs, rhs, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.lhs = lhs
        self.rhs = rhs 

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitLogicalAndExpressionNode (self)

    def copy (self):
        return LogicalAndExpressionNode(self.token, self.lhs.copy(), self.rhs.copy(), self.lineNumber, self.columnNumber)

# ========================================================================
# lhs - ExpressionNode
# op  - equality op  
# rhs - ExpressionNode

class EqualityExpressionNode (ExpressionNode):

    def __init__(self, token, lhs, rhs, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.lhs = lhs
        self.rhs = rhs 

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitEqualityExpressionNode (self)

    def copy (self):
        return EqualityExpressionNode (self.token, self.lhs.copy(), self.rhs.copy(), self.lineNumber, self.columnNumber)

# ========================================================================
# lhs - ExpressionNode
# op  - inequality op  
# rhs - ExpressionNode

class InequalityExpressionNode (ExpressionNode):

    def __init__(self, token, lhs, rhs, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.lhs = lhs
        self.rhs = rhs 

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitInequalityExpressionNode (self)

    def copy (self):
        return InequalityExpressionNode(self.token, self.lhs.copy(), self.rhs.copy(), self.lineNumber, self.columnNumber)

# ========================================================================
# lhs - ExpressionNode
# op  - additive op  
# rhs - ExpressionNode

class AdditiveExpressionNode (ExpressionNode):

    def __init__(self, token, lhs, rhs, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.lhs = lhs
        self.rhs = rhs 

        self.overloadedFunctionCall = None

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitAdditiveExpressionNode (self)

    def copy (self):
        return AdditiveExpressionNode (self.token, self.lhs.copy(), self.rhs.copy(), self.lineNumber, self.columnNumber)

# ========================================================================
# lhs - ExpressionNode
# op  - multiplicative op  
# rhs - ExpressionNode

class MultiplicativeExpressionNode (ExpressionNode):

    def __init__(self, token, lhs, rhs, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.lhs = lhs
        self.rhs = rhs 

        self.overloadedFunctionCall = None

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitMultiplicativeExpressionNode (self)

    def copy (self):
        return MultiplicativeExpressionNode (self.token, self.lhs.copy(), self.rhs.copy(), self.lineNumber, self.columnNumber)

# ========================================================================
# ++<rhs>
# op  - pre-increment op token
# rhs - ExpressionNode

class PreIncrementExpressionNode (ExpressionNode):

    def __init__(self, token, rhs, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.rhs = rhs 

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitPreIncrementExpressionNode (self)

    def copy (self):
        return PreIncrementExpressionNode(self.token, self.rhs.copy(), self.lineNumber, self.columnNumber)

# ========================================================================
# --<rhs>
# op - pre-decrement op token
# rhs - ExpressionNode

class PreDecrementExpressionNode (ExpressionNode):

    def __init__(self, token, rhs, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.rhs = rhs 

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitPreDecrementExpressionNode (self)

    def copy (self):
        return PreDecrementExpressionNode(self.token, self.rhs.copy(), self.lineNumber, self.columnNumber)

# ========================================================================
# -<rhs>
# op - negative op token
# rhs - ExpressionNode

class NegativeExpressionNode (ExpressionNode):

    def __init__(self, token, rhs, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.rhs = rhs 

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitNegativeExpressionNode (self)

    def copy (self):
        return NegativeExpressionNode(self.token, self.rhs.copy(), self.lineNumber, self.columnNumber)

# ========================================================================
# !<rhs>
# op - logical not op token
# rhs - ExpressionNode

class LogicalNotExpressionNode (ExpressionNode):

    def __init__(self, token, rhs, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.rhs = rhs 

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitLogicalNotExpressionNode (self)

    def copy (self):
        return LogicalNotExpressionNode(self.token, self.rhs.copy(), self.lineNumber, self.columnNumber)

# ========================================================================
# ~<rhs>
# op - bitwise negation op token
# rhs - ExpressionNode

class BitwiseNegatationExpressionNode (ExpressionNode):

    def __init__(self, token, rhs, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.rhs = rhs 

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitBitwiseNegatationExpressionNode (self)

    def copy (self):
        return BitwiseNegatationExpressionNode(self.token, self.rhs.copy(), self.lineNumber, self.columnNumber)

# ========================================================================
# lhs - ExpressionNode

class PostIncrementExpressionNode (ExpressionNode):

    def __init__(self, token, lhs, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.lhs = lhs 

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitPostIncrementExpressionNode (self)

    def copy (self):
        return PostIncrementExpressionNode(self.token, self.lhs.copy(), self.lineNumber, self.columnNumber)

# ========================================================================
# lhs - ExpressionNode

class PostDecrementExpressionNode (ExpressionNode):

    def __init__(self, token, lhs, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.lhs = lhs 
        self.token = token

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitPostDecrementExpressionNode (self)

    def copy (self):
        return PostDecrementExpressionNode(self.token, self.lhs.copy(), self.lineNumber, self.columnNumber)

# ========================================================================
# lhs - ExpressionNode
# offset - ExpressionNode

class SubscriptExpressionNode (ExpressionNode):

    def __init__(self, token, lhs, offset, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.lhs = lhs
        self.offset = offset

        self.overloadedFunctionCall = None
        self.overloadedMethodCall = None

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitSubscriptExpressionNode (self)

    def copy (self):
        return SubscriptExpressionNode(self.token, self.lhs.copy(), self.offset.copy(), self.lineNumber, self.columnNumber)

# ========================================================================
# function - ExpressionNode
# args - list[ExpressionNode]

class FunctionCallExpressionNode (ExpressionNode):

    def __init__(self, token, function, args, templateParams, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.function = function
        self.args = args 

        self.templateParams = templateParams 

        self.decl = None

        # this is ad hoc for default ctors
        self.is_ctor = False

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitFunctionCallExpressionNode (self)

    def copy (self):
        return FunctionCallExpressionNode(self.token, self.function.copy(), [arg.copy() for arg in self.args], [tempParam.copy() for tempParam in self.templateParams], self.lineNumber, self.columnNumber)

# ========================================================================
# lhs - ExpressionNode - must be class type 
# rhs - ExpressionNode  - must be a valid member  

class MemberAccessorExpressionNode (ExpressionNode):

    def __init__(self, token, lhs, rhs, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.lhs = lhs
        self.rhs = rhs
        # id is the assembly representation of the function 
        # for class method calls 
        self.id = ""

        self.isstatic = False

        self.decl = None

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitMemberAccessorExpressionNode (self)

    def copy (self):
        return MemberAccessorExpressionNode(self.token, self.lhs.copy(), self.rhs.copy(), self.lineNumber, self.columnNumber)

# ========================================================================
# lhs - ExpressionNode - must be class type 
# rhs - ExpressionNode  - must be a valid member  

class FieldAccessorExpressionNode (ExpressionNode):

    def __init__(self, token, lhs, rhs, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.lhs = lhs
        self.rhs = rhs

        self.decl = None

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitFieldAccessorExpressionNode (self)

    def copy (self):
        return FieldAccessorExpressionNode(self.token, self.lhs.copy(), self.rhs.copy(), self.lineNumber, self.columnNumber)

# ========================================================================
# lhs - ExpressionNode - must be class type 
# rhs - ExpressionNode  - must be a valid member  

class MethodAccessorExpressionNode (ExpressionNode):

    def __init__(self, token, lhs, rhs, args, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.lhs = lhs
        self.rhs = rhs
        self.args = args

        self.decl = None

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitMethodAccessorExpressionNode (self)

    def copy (self):
        return MethodAccessorExpressionNode(self.token, self.lhs.copy(), self.rhs.copy(), [arg.copy() for arg in self.args], self.lineNumber, self.columnNumber)

# ========================================================================

class ThisExpressionNode (ExpressionNode):

    def __init__(self, token, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token

        self.decl = None

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitThisExpressionNode (self)

    def copy (self):
        return ThisExpressionNode(self.token, self.lineNumber, self.columnNumber)

# ========================================================================
# id - string

class IdentifierExpressionNode (ExpressionNode):

    def __init__(self, token, id, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.id = id

        self.decl = None
        self.wasAssigned = False

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitIdentifierExpressionNode (self)

    def copy (self):
        return IdentifierExpressionNode(self.token, self.id, self.lineNumber, self.columnNumber)

# ========================================================================

class ArrayAllocatorExpressionNode (ExpressionNode):

    def __init__(self, token, elementType, sizeExpr, templateParams, line, column):
        super ().__init__ ()
        self.token = token
        self.type = elementType.copy ()
        # the allocator returns a pointer so turn type into a pointer
        self.type.arrayDimensions += 1
        self.elementType = elementType
        self.sizeExpr = sizeExpr

        self.templateParams = templateParams

        self.decl = None

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitArrayAllocatorExpressionNode (self)

    def copy (self):
        return ArrayAllocatorExpressionNode(self.token, self.type.copy(), [d.copy() for d in self.dimensions], [t.copy() for t in self.templateParams], self.lineNumber, self.columnNumber)

# ========================================================================

class ConstructorCallExpressionNode (ExpressionNode):

    def __init__(self, token, type, id, args, templateParams, line, column):
        super ().__init__ ()
        self.token = token
        self.type = type
        self.id = id
        self.args = args

        self.templateParams = templateParams

        self.decl = None

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitConstructorCallExpressionNode (self)

    def copy (self):
        return ConstructorCallExpressionNode(self.token, self.type.copy(), self.id, [a.copy() for a in self.args], [t.copy() for t in self.templateParams], self.lineNumber, self.columnNumber)

# ========================================================================

class SizeofExpressionNode (ExpressionNode):

    def __init__(self, token, type, rhs, line, column):
        super ().__init__ ()
        self.type = type
        self.token = token
        self.rhs = rhs

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitSizeofExpressionNode (self)

    def copy (self):
        return SizeofExpressionNode(self.token, self.type.copy(), self.rhs.copy(), self.lineNumber, self.columnNumber)

# ========================================================================

class FreeExpressionNode (ExpressionNode):

    def __init__(self, token, type, rhs, line, column):
        super ().__init__ ()
        self.type = type
        self.token = token
        self.rhs = rhs

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitFreeExpressionNode (self)

    def copy (self):
        return FreeExpressionNode(self.token, self.type.copy(), self.rhs.copy(), self.lineNumber, self.columnNumber)

# ========================================================================
# value - int

class IntLiteralExpressionNode (ExpressionNode):

    def __init__(self, token, value:int):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.INT32, "int32", None)
        self.token = token
        self.value = value

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitIntLiteralExpressionNode (self)

    def copy (self):
        return IntLiteralExpressionNode(self.token, self.value)

# ========================================================================
# value - float

class FloatLiteralExpressionNode (ExpressionNode):

    def __init__(self, token, value:float):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.FLOAT32, "float32", None)
        self.token = token
        self.value = value

        self.lineNumber = 0
        self.columnNumber = 0
        
        # x86
        self.label = "<ERROR:LABEL NOT SET>"

    def accept (self, visitor):
        return visitor.visitFloatLiteralExpressionNode (self)

    def copy (self):
        return FloatLiteralExpressionNode(self.token, self.value)

# ========================================================================
# value - char

class CharLiteralExpressionNode (ExpressionNode):

    def __init__(self, token, value:chr):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.CHAR, "char", None)
        self.token = token
        self.value = value

        self.lineNumber = 0
        self.columnNumber = 0

    def accept (self, visitor):
        return visitor.visitCharLiteralExpressionNode (self)

    def copy (self):
        return CharLiteralExpressionNode(self.token, self.value)

# ========================================================================
# value - string

class StringLiteralExpressionNode (ExpressionNode):

    def __init__(self, token, value:str):
        super ().__init__ ()
        # char[] instead of string
        self.type = TypeSpecifierNode (Type.CHAR, "char", None, arrayDimensions=1)
        self.token = token
        self.value = value

        self.lineNumber = 0
        self.columnNumber = 0

        # x86
        self.label = "<ERROR:LABEL NOT SET>"

    def accept (self, visitor):
        return visitor.visitStringLiteralExpressionNode (self)

    def copy (self):
        return StringLiteralExpressionNode(self.token, self.value)

# ========================================================================
# elems - list[ExpressionNode]

class ListConstructorExpressionNode (ExpressionNode):

    def __init__(self, token, elems:list, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.UNKNOWN, "", None)
        self.token = token
        self.elems = elems

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitListConstructorExpressionNode (self)

    def copy (self):
        return ListConstructorExpressionNode(self.token, [e.copy() for e in self.elems], self.lineNumber, self.columnNumber)

# ========================================================================

class NullExpressionNode (ExpressionNode):

    def __init__(self, token, line, column):
        super ().__init__ ()
        self.type = TypeSpecifierNode (Type.NULL, "null", None)
        self.token = token
        self.value = 0

        self.lineNumber = line
        self.columnNumber = column

    def accept (self, visitor):
        return visitor.visitNullExpressionNode (self)

    def copy (self):
        return NullExpressionNode(self.token, self.lineNumber, self.columnNumber)

# ========================================================================