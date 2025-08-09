# CeruleanIR Compiler - Semantic analysis
# By Amy Burnett
# June 19 2024
# ========================================================================

from sys import exit

from .tokenizer import printToken
from .ceruleanIRAST import *
from .visitor import ASTVisitor
from .symbolTable import *

# ========================================================================

class SemanticAnalysisVisitor (ASTVisitor):

    def __init__ (self, lines, debug=False):
        self.debug = debug
        self.table = SymbolTable (self.debug)

        self.parameters = []
        self.isFunctionBody = False

        self.lines = lines
        self.table.lines = self.lines

        self.wasSuccessful = True
        self.checkDeclaration = True
        # CeruleanIR only allows one containing function
        self.containingFunction = []

        # keeps track of the root node
        self.programNode = None

        self.insertFunc = True

    # ====================================================================

    def analyze (self, ast):
        ast.accept (self)
        return self.wasSuccessful

    # ====================================================================

    def visitProgramNode (self, node):
        # keep track of the root node 
        self.programNode = node

        for codeunit in node.codeunits:
            if codeunit != None:
                codeunit.accept (self)

    # ====================================================================

    def visitTypeSpecifierNode (self, node):
        # print (f"[typespec] {node}")
        # if type spec is not primitive
        # if (node.type == Type.USERTYPE):
        #     # first save any template parameters
        #     # this is useful for the following case
        #     # where Vector:<char:> needs to be known
        #     # before the outer vector
        #     # Ex: Vector<:Vector<:char:>:>
        #     for tparam in node.templateParams:
        #         tparam.accept (self)
        #     # make sure type exists 
        #     # and save with the type spec for later lookup 
        #     node.decl = self.table.lookup (node.id, Kind.TYPE, [], node.templateParams, self)
        #     # variable has no declaration
        #     if (node.decl == None):
        #         print (f"Semantic Error: '{node}' does not name a type")
        #         if node.token != None:
        #             printToken (node.token)
        #         print ()
        #         self.wasSuccessful = False
        #         node.type = Type.UNKNOWN
        pass

    # ====================================================================

    def visitParameterNode (self, node):
        node.type.accept (self)
        wasSuccessful = self.table.insert (node, node.id, Kind.VAR)

        # if (not wasSuccessful):
        #     varname = node.id 
        #     originalDec = self.table.lookup (varname, Kind.VAR)
        #     print (f"Semantic Error: Redeclaration of Param '{varname}'")
        #     print (f"   Original:")
        #     printToken (originalDec.token, "      ")
        #     print (f"   Redeclaration:")
        #     printToken (node.token, "      ")
        #     print ()
        #     self.wasSuccessful = False
        
        # **CeruleanIR has no concept of variable declarations
        # so we dont have to worry about redeclared variables.

    # ====================================================================

    def visitGlobalVariableDeclarationNode (self, node):
        # node.type.accept (self)
        wasSuccessful = self.table.insert (node, node.id, Kind.VAR)
        if (not wasSuccessful):
            varname = node.id 
            originalDec = self.table.lookup (varname, Kind.VAR)
            print (f"Semantic Error: Redeclaration of global variable '{varname}'")
            print (f"   Original:")
            printToken (originalDec.token, "      ")
            print (f"   Redeclaration:")
            printToken (node.token, "      ")
            print ()
            self.wasSuccessful = False

    # ====================================================================

    def visitVariableDeclarationNode (self, node):
        # node.type.accept (self)
        wasSuccessful = self.table.insert (node, node.id, Kind.VAR)
        if (not wasSuccessful):
            varname = node.id 
            originalDec = self.table.lookup (varname, Kind.VAR)
            print (f"Semantic Error: Reassignment of SSA variable '{varname}'")
            print (f"   Original:")
            printToken (originalDec.token, "      ")
            print (f"   Reassignment:")
            printToken (node.token, "      ")
            print ()
            self.wasSuccessful = False

        # save a reference to this variable for the function header
        if len(self.containingFunction) > 0:
            self.containingFunction[-1].localVariables += [node]
        # if global code, save to global localVariables 
        else:
            self.programNode.localVariables += [node]

    # ====================================================================

    def visitFunctionNode (self, node):
        node.type.accept (self)
        # create signature for node
        signature = [f"{node.id}"]
        signature += [f"("]
        if len(node.params) > 0:
            signature += [node.params[0].type.__str__()]
        for i in range(1, len(node.params)):
            signature += [f", {node.params[i].type.__str__()}"]
        signature += [")"]
        signature = "".join(signature)
        node.signature = signature

        # this is for checking template instances 
        if self.insertFunc:
            wasSuccessful = self.table.insert (node, node.id, Kind.FUNC)

            if (not wasSuccessful):
                originalDec = self.table.lookup (node.id, Kind.FUNC, node.params)
                print (f"Semantic Error: Redeclaration of function '{node.signature}'")
                print (f"   Original:")
                printToken (originalDec.token, "      ")
                print (f"   Redeclaration:")
                printToken (node.token, "      ")
                print ()
                self.wasSuccessful = False
        else:
            self.insertFunc = True

        self.table.enterScope (ScopeType.FUNCTION)
        # check parameters
        for p in node.params:
            p.accept (self)
        # containing function keeps track of what function 
        # we're currently in 
        # this is helpful for ensuring RETURN is in a function
        # and for ensuring the value being returned matches the function's return type 
        self.containingFunction += [node]
        for i in range (0, len (node.basicBlocks)):
            basicBlock = node.basicBlocks[i]
            basicBlock.accept (self)
            # Ensure this basic block name is unique
            for j in range (i + 1, len(node.basicBlocks)):
                if node.basicBlocks[i].name == node.basicBlocks[j].name:
                    print (f"Semantic Error: Redeclaration of basic block '{node.basicBlocks[i].name}' in function '{node.signature}'")
                    print (f"   Original:")
                    printToken (node.basicBlocks[i].token, "      ")
                    print (f"   Redeclaration:")
                    printToken (node.basicBlocks[j].token, "      ")
                    print ()
                    self.wasSuccessful = False
        self.containingFunction.pop ()
        self.table.exitScope ()

    # ====================================================================

    def visitBasicBlockNode (self, node):
        # visit each instruction
        for instruction in node.instructions:
            instruction.accept (self)

    # ====================================================================

    def visitInstructionNode (self, node):
        # Check lhs (if exists)
        if node.hasAssignment:
            node.lhsVariable.accept (self)
        # Check arguments
        for argument in node.arguments:
            argument.accept (self)
        # Ensure command exists
        # TODO
        # Ensure arguments agree with command
        # TODO

    # ====================================================================

    def visitCallInstructionNode (self, node):
        # Check lhs (if exists)
        if node.hasAssignment:
            node.lhsVariable.accept (self)
        # Check arguments
        for argument in node.arguments:
            argument.accept (self)

        # search for function
        # create signature for node
        signature = [f"{node.function_name}"]
        signature += ["("]
        if len(node.arguments) > 0:
            signature += [node.arguments[0].type.__str__()]
        for i in range(1, len(node.arguments)):
            signature += [f", {node.arguments[i].type.__str__()}"]
        signature += [")"]
        signature = "".join(signature)

        decl = self.table.lookup (node.function_name, Kind.FUNC, node.arguments, None, self)

        # Save declaration with function call
        node.decl = decl 

        # Ensure the function declaration exists and its a function 
        if (decl == None or not isinstance (decl,(FunctionNode))):
            print (f"Semantic Error: No function matching signature '{signature}'")
            printToken (node.token)
            print ()
            self.wasSuccessful = False
            return 

        node.type = node.decl.type
        # Ensure function exists
        # 
        # Ensure function parameters match
        # TODO

    # ====================================================================

    def visitArgumentExpressionNode (self, node):
        # Check expression
        node.expression.accept (self)
        # Ensure expression matches/agrees-with argument type
        # TODO

    # ====================================================================

    def visitExpressionNode (self, node):
        # dummy node - nothing to do
        pass

    # ====================================================================

    def visitGlobalVariableExpressionNode (self, node):
        if (self.checkDeclaration):
            decl = self.table.lookup (node.id, Kind.VAR)
            # Ensure variable has a declaration
            if (decl == None):
                print (f"Semantic Error: '{node.id}' was not declared in this scope")
                printToken (node.token)
                print ()
                self.wasSuccessful = False
                return
            # variable has declaration
            else:
                # save declaration's type info
                # node.type = decl.type
                # save declaration 
                node.decl = decl 
                # print(f"==> {node.decl.id} : linksFollowed={self.table.linksFollowed}")
            # ensure variable was assigned
            if not node.decl.wasAssigned:
                print (f"Semantic Error: variable '{node.id}' referenced before assignment")
                printToken (node.token)
                print ()
                self.wasSuccessful = False

    # ====================================================================

    def visitLocalVariableExpressionNode (self, node):
        if (self.checkDeclaration):
            decl = self.table.lookup (node.id, Kind.VAR)
            # variable has no declaration
            if (decl == None):
                print (f"Semantic Error: '{node.id}' was not declared in this scope")
                printToken (node.token)
                print ()
                self.wasSuccessful = False
                return
            # variable has declaration
            else:
                # save declaration's type info
                # node.type = decl.type
                # save declaration 
                node.decl = decl 
                # print(f"==> {node.decl.id} : linksFollowed={self.table.linksFollowed}")
            # ensure variable was assigned
            if not node.decl.wasAssigned:
                print (f"Semantic Error: local variable '{node.id}' referenced before assignment")
                printToken (node.token)
                print ()
                self.wasSuccessful = False

    # ====================================================================

    def visitBasicBlockExpressionNode (self, node):
        # if (self.checkDeclaration):
        #     decl = self.table.lookup (node.id, Kind.VAR)
        #     # variable has no declaration
        #     if (decl == None):
        #         print (f"Semantic Error: '{node.id}' was not declared in this scope")
        #         printToken (node.token)
        #         print ()
        #         self.wasSuccessful = False
        #         return
        #     # variable has declaration
        #     else:
        #         # save declaration's type info
        #         # node.type = decl.type
        #         # save declaration 
        #         node.decl = decl 
        #         # print(f"==> {node.decl.id} : linksFollowed={self.table.linksFollowed}")
        #     # ensure variable was assigned
        #     if not node.decl.wasAssigned:
        #         print (f"Semantic Error: variable '{node.id}' referenced before assignment")
        #         printToken (node.token)
        #         print ()
        #         self.wasSuccessful = False
        pass

    # ====================================================================

    def visitIntLiteralExpressionNode (self, node):
        pass

    # ====================================================================

    def visitFloatLiteralExpressionNode (self, node):
        # FOR X86-64
        # save with program node so these can be added to the data section
        self.programNode.floatLiterals += [node]

    # ====================================================================

    def visitCharLiteralExpressionNode (self, node):
        pass

    # ====================================================================

    def visitStringLiteralExpressionNode (self, node):
        # FOR X86-64
        # save with program node so these can be added to the data section
        self.programNode.stringLiterals += [node]

# ========================================================================