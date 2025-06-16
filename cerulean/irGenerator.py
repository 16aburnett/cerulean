# Cerulean Compiler - x86 backend 
# By Amy Burnett
# April 11 2021
# ========================================================================

import os 
from sys import exit

if __name__ == "irGenerator":
    from ceruleanAST import *
    from visitor import ASTVisitor
    from symbolTable import SymbolTable
    from tokenizer import printToken
    import backend.ceruleanIRAST as irast
else:
    from .ceruleanAST import *
    from .visitor import ASTVisitor
    from .symbolTable import SymbolTable
    from .tokenizer import printToken
    import backend.ceruleanIRAST as irast

# ========================================================================

DIVIDER_LENGTH = 75 
INITIAL_INDENT_LENGTH = 9
TAB_LENGTH = 3

LIB_FILENAME = os.path.dirname(__file__) + "/AmyScriptBuiltinLib_x86.asm"

# ========================================================================

class IRGeneratorVisitor (ASTVisitor):

    def __init__(self, lines):
        self.parameters = []
        self.lines = lines 
        self.indentation = 0
        self.ast = None
        self.containingIRFunction = None
        self.containingBasicBlock = None
        self.newLocalRegIndex = 0

        self.lhs = "null"
        self.jumpIndex = 0
        self.shouldComment = True
        # stack implementation
        # keeps track of containing loop
        # for break and continue statements 
        self.parentLoops = []
        self.pushParent = False
        self.scopeNames = []
        self.indent = "".join ([' ' for i in range(INITIAL_INDENT_LENGTH)])

        self.floatNegOneLabel = ".floatNegOne"
        self.floatZeroLabel = ".floatZero"
        self.floatOneLabel = ".floatOne"

    # === HELPER FUNCTIONS ===============================================

    def enterScope (self, name):
        self.scopeNames += [f"__{name}"]

    def exitScope (self):
        self.scopeNames.pop ()

    # Returns a new unique local register
    def newLocalReg (self):
        reg = irast.LocalVariableExpressionNode (f"%{self.newLocalRegIndex}", None, None, None)
        self.newLocalRegIndex += 1
        return reg

    # === VISITOR FUNCTIONS ==============================================

    def visitProgramNode (self, node):
        self.ast = irast.ProgramNode ([])
        # add library code
        # file = open (LIB_FILENAME, "r")
        # for line in file.readlines ():
        #     self.code += [line]

        # predetermine string literal labels 
        # this needs to be done before processing the code
        # so that we know the label of the string to lookup
        # * this really should go in a pre-codegen step
        # * can be optimized to include only unique labels
        # for i in range(len(node.stringLiterals)):
        #     node.stringLiterals[i].label = f".str{i}"
        # for i in range(len(node.floatLiterals)):
        #     node.floatLiterals[i].label = f".float{i}"

        for codeunit in node.codeunits:
            if codeunit != None:
                codeunit.accept (self)

        # Global data
        # Add all of the string literals to the global section
        # for i in range(len(node.stringLiterals)):

        #     # This routine splits the string to separate chars
        #     # because '\n' isn't automatically interpreted as a newline
        #     # so this finds escaped chars and replaces it with its ascii value
        #     # * this can be changed to compress adjacent chars into a string
        #     # like the following examples
        #     # Current:  db 'H', 'e', 'l', 'l', 'o', 10, 0
        #     # Expected: db "Hello", 10, 0

        #     # print (node.stringLiterals[i].value)
        #     import ast
        #     asciiString = (ast.literal_eval(node.stringLiterals[i].value))
        #     # print (asciiString)

        #     line = [f"{node.stringLiterals[i].label}: db "]

        #     if len(asciiString) > 0:
        #         # if it is an escape character - '\n'
        #         if len(repr(asciiString[0])) > 3:  
        #             line += [f"{ord(asciiString[0])}"]  
        #             # print (ord(asciiString[0]))
        #         # if it is an apostrophe 
        #         # an apostrophe would become '''
        #         # which is causes problems
        #         elif asciiString[0] == '\'':
        #             line += [f"{ord(asciiString[0])}"]
        #         # normal character
        #         else:
        #             line += [f"'{asciiString[0]}'"]
        #     for j in range(1, len(asciiString)):
        #         # print (repr(asciiString[j])) 
        #         # if it is an escape character - '\n'
        #         if len(repr(asciiString[j])) > 3:  
        #             line += [f", {ord(asciiString[j])}"]  
        #             # print (ord(asciiString[j]))
        #         # if it is an apostrophe 
        #         # an apostrophe would become '''
        #         # which is causes problems
        #         elif asciiString[j] == '\'':
        #             line += [f", {ord(asciiString[j])}"]
        #         # normal character
        #         else:
        #             line += [f", '{asciiString[j]}'"]
        #     # string needs to end in null \0
        #     line += [", 0"]

        #     self.printLabel ("".join(line))
        # # print all float literals 
        # for i in range(len(node.floatLiterals)):
        #     self.printLabel (f"{node.floatLiterals[i].label}: dq {node.floatLiterals[i].value}")

        # predefined floats
        # self.printLabel (f"{self.floatNegOneLabel}: dq -1.0")
        # self.printLabel (f"{self.floatZeroLabel}: dq 0.0")
        # self.printLabel (f"{self.floatOneLabel}: dq 1.0")

    def visitTypeSpecifierNode (self, node):
        # Convert Cerulean type to CeruleanIR type
        # opaque points lose some type info
        if   node.arrayDimensions > 0  : [type, name] = [irast.Type.PTR, "ptr"]
        elif node.type == Type.BOOL    : [type, name] = [irast.Type.BOOL, "bool"]
        elif node.type == Type.BYTE    : [type, name] = [irast.Type.BYTE, "byte"]
        elif node.type == Type.CHAR    : [type, name] = [irast.Type.CHAR, "char"]
        elif node.type == Type.INT32   : [type, name] = [irast.Type.INT32, "int32"]
        elif node.type == Type.INT64   : [type, name] = [irast.Type.INT64, "int64"]
        elif node.type == Type.FLOAT32 : [type, name] = [irast.Type.FLOAT32, "float32"]
        elif node.type == Type.FLOAT64 : [type, name] = [irast.Type.FLOAT64, "float64"]
        elif node.type == Type.VOID    : [type, name] = [irast.Type.VOID, "void"]
        elif node.type == Type.NULL    : [type, name] = [irast.Type.PTR, "ptr"]
        else                           : [type, name] = [irast.Type.UNKNOWN, "<unkown>"]
        return irast.TypeSpecifierNode (type, name, None)

    def visitParameterNode (self, node):
        irType = node.type.accept (self)
        node.scopeName = "".join (self.scopeNames) + "__" + node.id
        param = irast.ParameterNode (irType, f"%{node.id}", None)
        self.containingIRFunction.params += [param]

        reg = irast.LocalVariableExpressionNode (f"%{node.id}", None, None, None)
        # Use alloca to store on the stack to support reassignment
        ptrReg = irast.LocalVariableExpressionNode (f"%{node.id}.ptr", None, None, None)
        arg0 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.TYPE, "type", None), irType)
        arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), irast.IntLiteralExpressionNode (1))
        instruction = irast.InstructionNode (ptrReg, "alloca", [arg0, arg1])
        self.containingBasicBlock.instructions += [instruction]
        # Store param's value to the stack
        offset = irast.IntLiteralExpressionNode (0)
        arg0 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.PTR, "ptr", None), ptrReg)
        arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), offset)
        arg2 = irast.ArgumentExpressionNode (irType, reg)
        instruction = irast.InstructionNode (None, "store", [arg0, arg1, arg2])
        self.containingBasicBlock.instructions += [instruction]
        return reg

    def visitCodeUnitNode (self, node):
        pass

    def visitGlobalVariableDeclarationNode (self, node):
        node.type.accept (self)
        # variable names are modified by its scope 
        scopeName = "".join (self.scopeNames) + "__" + node.id
        node.scopeName = scopeName
        command="value"
        if node.rhs:
            literal = node.rhs.accept (self)
        else:
            # If global wasnt assigned, default to 0
            literal = IntLiteralExpressionNode (0)
        arg0 = irast.ArgumentExpressionNode (literal.type, literal)
        irNode = irast.GlobalVariableDeclarationNode (f"@{node.id}.ptr", None, command, [arg0])
        self.ast.codeunits += [irNode]

    def visitVariableDeclarationNode (self, node):
        varIRType = node.type.accept (self)
        # variable names are modified by its scope 
        scopeName = "".join (self.scopeNames) + "__" + node.id
        node.scopeName = scopeName
        # Reassigned variable
        if (node.assignCount > 1):
            reg = irast.LocalVariableExpressionNode (f"%{node.id}.ptr", None, None, None)
            # Use alloca to store on the stack to support reassignment
            arg0 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.TYPE, "type", None), varIRType)
            arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), irast.IntLiteralExpressionNode (1))
            instruction = irast.InstructionNode (reg, "alloca", [arg0, arg1])
            self.containingBasicBlock.instructions += [instruction]
            return reg
        # Single assign variable
        else:
            # NOTE: this should probably be scopename
            return irast.LocalVariableExpressionNode (f"%{node.id}", None, None, None)

    def visitFunctionNode (self, node):

        # function names are mangled by its scope and argument types
        # scopeName = ["".join (self.scopeNames), "____", node.id]
        # functions should be top-level so no prepend
        scopeName = [node.id]
        # add signature to scopeName for overloaded functions
        if len(node.params) > 0:
            scopeName += [f"__{node.params[0].type.id}"]
            # param template types
            if len(node.params[0].type.templateParams) > 0:
                 scopeName += [f"__tparam{0}__{node.params[0].type.templateParams[0].id}"]
            for i in range(1, len(node.params[0].type.templateParams)):
                 scopeName += [f"__tparam{i}__{node.params[0].type.templateParams[i].id}"]
            # add array dimensions
            if node.params[0].type.arrayDimensions > 0:
                scopeName += [f"__{node.params[0].type.arrayDimensions}"]
            for i in range(1, len(node.params)):
                scopeName += [f"__{node.params[i].type.id}"]
                # param template types
                if len(node.params[i].type.templateParams) > 0:
                    scopeName += [f"__tparam{0}__{node.params[i].type.templateParams[0].id}"]
                for j in range(1, len(node.params[i].type.templateParams)):
                    scopeName += [f"__tparam{j}__{node.params[i].type.templateParams[j].id}"]
                # add array dimensions
                if node.params[i].type.arrayDimensions > 0:
                    scopeName += [f"__{node.params[i].type.arrayDimensions}"]
        node.scopeName = "".join(scopeName)

        # AD HOC CENTRAL!!
        # fill in prereferences with scopename 
        # for i in range(len(self.code)):
        #     if f"${node.signature}" in self.code[i]:
        #         self.code[i] = self.code[i].replace(f"${node.signature}", node.scopeName)

        # create new scope level 
        self.scopeNames += [f"__{node.id}"]

        irReturnType = node.type.accept (self)
        irFunction = irast.FunctionNode (irReturnType, f"@{node.scopeName}", None, [], [])
        # Add function to program
        self.ast.codeunits += [irFunction]
        self.containingIRFunction = irFunction
        self.newLocalRegIndex = 0

        # Create entry basic block
        basicBlock = irast.BasicBlockNode ("entry", [])
        self.containingIRFunction.basicBlocks += [basicBlock]
        self.containingBasicBlock = basicBlock
        # load parameters - this will setup the parameters for the function
        for i in range(len(node.params)):
            node.params[i].accept (self)
        # Body
        node.body.accept (self)

        self.scopeNames.pop ()

    def visitClassDeclarationNode(self, node):
        print("ERROR: ClassDeclarationNode not implemented")
        printToken (node.token)
        exit(1)

    def visitFieldDeclarationNode (self, node):
        print("ERROR: FieldDeclarationNode not implemented")
        printToken (node.token)
        exit(1)

    def visitMethodDeclarationNode (self, node):
        print("ERROR: MethodDeclarationNode not implemented")
        printToken (node.token)
        exit(1)

    def visitConstructorDeclarationNode (self, node):
        print("ERROR: ConstructorDeclarationNode not implemented")
        printToken (node.token)
        exit(1)

    def visitEnumDeclarationNode (self, node):
        print("ERROR: EnumDeclarationNode not implemented")
        printToken (node.token)
        exit(1)

    def visitFunctionTemplateNode (self, node):
        print("ERROR: FunctionTemplateNode not implemented")
        printToken (node.token)
        exit(1)

    def visitClassTemplateDeclarationNode (self, node):
        print("ERROR: ClassTemplateDeclarationNode not implemented")
        printToken (node.token)
        exit(1)

    def visitStatementNode (self, node):
        pass

    def visitIfStatementNode (self, node):
        # unique codes for jump labels 
        ifIndex = self.jumpIndex
        self.jumpIndex += 1
        elifIndex = 0

        # start with . because they are local to 
        # the function that they are contained in
        # * might be able to use this in more cases
        ifBodyLabel = f"if_body{ifIndex}"
        firstElifLabel = f"elif_cond{ifIndex}x{elifIndex}"
        elseBodyLabel = f"else_body{ifIndex}"
        ifEndLabel = f"if_end{ifIndex}"

        # create new scope level 
        self.scopeNames += [ifBodyLabel]

        # if-statement Condition
        # NOTE: No need to contain first if condition in a block
        # just add to current block
        condReg = node.cond.accept (self)
        condRegType = irast.TypeSpecifierNode (irast.Type.INT32, "int32", None)
        # jump to next elif if there is one 
        if (len(node.elifs) > 0):
            falseBlockExpr = irast.BasicBlockExpressionNode (firstElifLabel, None, None, None)
        # no elifs so jump to else if there is one
        elif node.elseStmt != None:
            falseBlockExpr = irast.BasicBlockExpressionNode (elseBodyLabel, None, None, None)
        # no elif or else, jump to end of if-chain
        else:
            falseBlockExpr = irast.BasicBlockExpressionNode (ifEndLabel, None, None, None)
        # jcmp (int32(%cmp), block(if_body), block(<falseBlock>))
        condRegType = irast.TypeSpecifierNode (irast.Type.INT32, "int32", None)
        bodyBlockExprType = irast.TypeSpecifierNode (irast.Type.BLOCK, "block", None)
        bodyBlockExpr = irast.BasicBlockExpressionNode (ifBodyLabel, None, None, None)
        falseBlockExprType = irast.TypeSpecifierNode (irast.Type.BLOCK, "block", None)
        arg0 = irast.ArgumentExpressionNode (condRegType, condReg)
        arg1 = irast.ArgumentExpressionNode (bodyBlockExprType, bodyBlockExpr)
        arg2 = irast.ArgumentExpressionNode (falseBlockExprType, falseBlockExpr)
        instruction = irast.InstructionNode (None, "jcmp", [arg0, arg1, arg2])
        self.containingBasicBlock.instructions += [instruction]

        # print the body of if 
        bodyBlock = irast.BasicBlockNode (ifBodyLabel, [])
        self.containingIRFunction.basicBlocks += [bodyBlock]
        self.containingBasicBlock = bodyBlock
        node.body.accept (self)
        # Unconditionally jump to the end of the if
        # jmp (block(if_end))
        ifEndBlockExprType = irast.TypeSpecifierNode (irast.Type.BLOCK, "block", None)
        ifEndBlockExpr = irast.BasicBlockExpressionNode (ifEndLabel, None, None, None)
        arg0 = irast.ArgumentExpressionNode (ifEndBlockExprType, ifEndBlockExpr)
        instruction = irast.InstructionNode (None, "jmp", [arg0])
        self.containingBasicBlock.instructions += [instruction]

        # exit if scope
        self.scopeNames.pop ()

        # print elifs
        for i in range(len(node.elifs)):
            elifNode = node.elifs[i]

            elifCondLabel = f"elif_cond{ifIndex}x{elifIndex}"
            elifBodyLabel = f"elif_body{ifIndex}x{elifIndex}"
            # create new scope level 
            self.scopeNames += [f"__elif__{ifIndex}x{elifIndex}"]

            # Elif condition
            condBlock = irast.BasicBlockNode (elifCondLabel, [])
            self.containingIRFunction.basicBlocks += [condBlock]
            self.containingBasicBlock = condBlock
            condReg = elifNode.cond.accept (self)
            condRegType = irast.TypeSpecifierNode (irast.Type.INT32, "int32", None)
            # jump to next elif if there is one 
            if (i+1 < len(node.elifs)):
                nextElifLabel = f"elif_cond{ifIndex}x{elifIndex+1}"
                falseBlockExpr = irast.BasicBlockExpressionNode (nextElifLabel, None, None, None)
            # no elifs so jump to else if there is one
            elif node.elseStmt != None:
                falseBlockExpr = irast.BasicBlockExpressionNode (elseBodyLabel, None, None, None)
            # no elif or else, jump to end of if-chain
            else:
                falseBlockExpr = irast.BasicBlockExpressionNode (ifEndLabel, None, None, None)
            # jcmp (int32(%cmp), block(elif_body), block(<falseBlock>))
            condRegType = irast.TypeSpecifierNode (irast.Type.INT32, "int32", None)
            bodyBlockExprType = irast.TypeSpecifierNode (irast.Type.BLOCK, "block", None)
            bodyBlockExpr = irast.BasicBlockExpressionNode (elifBodyLabel, None, None, None)
            falseBlockExprType = irast.TypeSpecifierNode (irast.Type.BLOCK, "block", None)
            arg0 = irast.ArgumentExpressionNode (condRegType, condReg)
            arg1 = irast.ArgumentExpressionNode (bodyBlockExprType, bodyBlockExpr)
            arg2 = irast.ArgumentExpressionNode (falseBlockExprType, falseBlockExpr)
            instruction = irast.InstructionNode (None, "jcmp", [arg0, arg1, arg2])
            self.containingBasicBlock.instructions += [instruction]

            # Body of elif
            bodyBlock = irast.BasicBlockNode (elifBodyLabel, [])
            self.containingIRFunction.basicBlocks += [bodyBlock]
            self.containingBasicBlock = bodyBlock
            elifNode.body.accept (self)
            # Unconditionally jump to the end of the if
            # jmp (block(if_end))
            ifEndBlockExprType = irast.TypeSpecifierNode (irast.Type.BLOCK, "block", None)
            ifEndBlockExpr = irast.BasicBlockExpressionNode (ifEndLabel, None, None, None)
            arg0 = irast.ArgumentExpressionNode (ifEndBlockExprType, ifEndBlockExpr)
            instruction = irast.InstructionNode (None, "jmp", [arg0])
            self.containingBasicBlock.instructions += [instruction]

            # exit scope
            self.scopeNames.pop ()

            # move to next elif
            elifIndex += 1

        # print else if there is one
        if node.elseStmt != None:
            # create new scope level
            self.scopeNames += [elseBodyLabel]

            # Body of else
            bodyBlock = irast.BasicBlockNode (elseBodyLabel, [])
            self.containingIRFunction.basicBlocks += [bodyBlock]
            self.containingBasicBlock = bodyBlock
            node.elseStmt.body.accept (self)
            # Unconditionally jump to the end of the if
            # jmp (block(if_end))
            ifEndBlockExprType = irast.TypeSpecifierNode (irast.Type.BLOCK, "block", None)
            ifEndBlockExpr = irast.BasicBlockExpressionNode (ifEndLabel, None, None, None)
            arg0 = irast.ArgumentExpressionNode (ifEndBlockExprType, ifEndBlockExpr)
            instruction = irast.InstructionNode (None, "jmp", [arg0])
            self.containingBasicBlock.instructions += [instruction]

            # exit scope
            self.scopeNames.pop ()

        # End of if
        endBlock = irast.BasicBlockNode (ifEndLabel, [])
        self.containingIRFunction.basicBlocks += [endBlock]
        self.containingBasicBlock = endBlock

    def visitElifStatementNode (self, node):
        self.printComment ("*** Compiler Error: Elif node should not be used ")

    def visitElseStatementNode (self, node):
        self.printComment ("*** Compiler Error: Else node should not be used ")

    def visitForStatementNode (self, node):
        # unique codes for jump labels 
        forIndex = self.jumpIndex
        self.jumpIndex += 1
        forLabel    = f"for{forIndex}"
        condLabel   = f"for_cond{forIndex}"
        bodyLabel   = f"for_body{forIndex}"
        updateLabel = f"for_update{forIndex}"
        endLabel    = f"for_end{forIndex}"

        # create new scope level 
        self.scopeNames += [forLabel]

        # save loop info for break and continue statements
        node.startLabel = condLabel
        node.continueLabel = updateLabel
        node.breakLabel = endLabel
        node.endLabel = endLabel
        self.parentLoops += [node]

        # Init
        # No need to create a block, just add code to current block
        node.init.accept (self)
        # unconditionally jump to for condition
        condBlockExprType = irast.TypeSpecifierNode (irast.Type.BLOCK, "block", None)
        condBlockExpr = irast.BasicBlockExpressionNode (condLabel, None, None, None)
        arg0 = irast.ArgumentExpressionNode (condBlockExprType, condBlockExpr)
        instruction = irast.InstructionNode (None, "jmp", [arg0])
        self.containingBasicBlock.instructions += [instruction]

        # Condition
        condBlock = irast.BasicBlockNode (condLabel, [])
        self.containingIRFunction.basicBlocks += [condBlock]
        self.containingBasicBlock = condBlock
        condReg = node.cond.accept (self)
        # jump to body or end based on loop condition
        condRegType = irast.TypeSpecifierNode (irast.Type.INT32, "int32", None)
        bodyBlockExprType = irast.TypeSpecifierNode (irast.Type.BLOCK, "block", None)
        bodyBlockExpr = irast.BasicBlockExpressionNode (bodyLabel, None, None, None)
        endBlockExprType = irast.TypeSpecifierNode (irast.Type.BLOCK, "block", None)
        endBlockExpr = irast.BasicBlockExpressionNode (endLabel, None, None, None)
        arg0 = irast.ArgumentExpressionNode (condRegType, condReg)
        arg1 = irast.ArgumentExpressionNode (bodyBlockExprType, bodyBlockExpr)
        arg2 = irast.ArgumentExpressionNode (endBlockExprType, endBlockExpr)
        instruction = irast.InstructionNode (None, "jcmp", [arg0, arg1, arg2])
        self.containingBasicBlock.instructions += [instruction]

        # Body
        bodyBlock = irast.BasicBlockNode (bodyLabel, [])
        self.containingIRFunction.basicBlocks += [bodyBlock]
        self.containingBasicBlock = bodyBlock
        node.body.accept (self)
        # unconditionally jump to update
        updateBlockExprType = irast.TypeSpecifierNode (irast.Type.BLOCK, "block", None)
        updateBlockExpr = irast.BasicBlockExpressionNode (updateLabel, None, None, None)
        arg0 = irast.ArgumentExpressionNode (updateBlockExprType, updateBlockExpr)
        instruction = irast.InstructionNode (None, "jmp", [arg0])
        self.containingBasicBlock.instructions += [instruction]

        # Update
        updateBlock = irast.BasicBlockNode (updateLabel, [])
        self.containingIRFunction.basicBlocks += [updateBlock]
        self.containingBasicBlock = updateBlock
        node.update.accept (self)
        # Unconditionally jump back to the condition
        condBlockExprType = irast.TypeSpecifierNode (irast.Type.BLOCK, "block", None)
        condBlockExpr = irast.BasicBlockExpressionNode (condLabel, None, None, None)
        arg0 = irast.ArgumentExpressionNode (condBlockExprType, condBlockExpr)
        instruction = irast.InstructionNode (None, "jmp", [arg0])
        self.containingBasicBlock.instructions += [instruction]

        # End of for
        endBlock = irast.BasicBlockNode (endLabel, [])
        self.containingIRFunction.basicBlocks += [endBlock]
        self.containingBasicBlock = endBlock

        # exit scope
        self.parentLoops.pop ()
        self.scopeNames.pop ()

    def visitWhileStatementNode (self, node):
        # Unique codes for jump labels
        whileIndex = self.jumpIndex
        self.jumpIndex += 1
        whileLabel = f"while{whileIndex}"
        condLabel  = f"while_cond{whileIndex}"
        bodyLabel  = f"while_body{whileIndex}"
        endLabel   = f"while_end{whileIndex}"

        # create new scope level
        # This will encasulate the variables in the condition and body
        self.scopeNames += [whileLabel]

        # save loop info for break and continue statements
        node.startLabel = condLabel
        node.continueLabel = condLabel
        node.breakLabel = endLabel
        node.endLabel = endLabel
        self.parentLoops += [node]

        # Condition
        condBlock = irast.BasicBlockNode (condLabel, [])
        self.containingIRFunction.basicBlocks += [condBlock]
        self.containingBasicBlock = condBlock
        condReg = node.cond.accept (self)
        condRegType = irast.TypeSpecifierNode (irast.Type.INT32, "int32", None)
        # jump to body or end based on loop condition
        # jcmp (int32(%cond), block(while_body), block(while_end))
        bodyBlockExprType = irast.TypeSpecifierNode (irast.Type.BLOCK, "block", None)
        bodyBlockExpr = irast.BasicBlockExpressionNode (bodyLabel, None, None, None)
        endBlockExprType = irast.TypeSpecifierNode (irast.Type.BLOCK, "block", None)
        endBlockExpr = irast.BasicBlockExpressionNode (endLabel, None, None, None)
        arg0 = irast.ArgumentExpressionNode (condRegType, condReg)
        arg1 = irast.ArgumentExpressionNode (bodyBlockExprType, bodyBlockExpr)
        arg2 = irast.ArgumentExpressionNode (endBlockExprType, endBlockExpr)
        instruction = irast.InstructionNode (None, "jcmp", [arg0, arg1, arg2])
        self.containingBasicBlock.instructions += [instruction]

        # Body
        bodyBlock = irast.BasicBlockNode (bodyLabel, [])
        self.containingIRFunction.basicBlocks += [bodyBlock]
        self.containingBasicBlock = bodyBlock
        node.body.accept (self)
        # unconditionally jump to cond
        # jmp (block(while_cond))
        condBlockExprType = irast.TypeSpecifierNode (irast.Type.BLOCK, "block", None)
        condBlockExpr = irast.BasicBlockExpressionNode (condLabel, None, None, None)
        arg0 = irast.ArgumentExpressionNode (condBlockExprType, condBlockExpr)
        instruction = irast.InstructionNode (None, "jmp", [arg0])
        self.containingBasicBlock.instructions += [instruction]

        # End of while
        endBlock = irast.BasicBlockNode (endLabel, [])
        self.containingIRFunction.basicBlocks += [endBlock]
        self.containingBasicBlock = endBlock

        # Leave scope
        self.parentLoops.pop ()
        self.scopeNames.pop ()

    def visitExpressionStatementNode (self, node):
        # ignore variable decl
        # int x; should not translate to anything
        if node.expr != None and not isinstance(node.expr, VariableDeclarationNode):
            node.expr.accept (self)

    def visitReturnStatementNode (self, node):
        # if there is a value provided 
        if node.expr != None:
            retValReg = node.expr.accept (self)
            retValType = node.expr.type.accept (self)
            arg0 = irast.ArgumentExpressionNode (retValType, retValReg)
            instruction = irast.InstructionNode (None, "return", [arg0])
            self.containingBasicBlock.instructions += [instruction]
        # no value provided 
        else:
            instruction = irast.InstructionNode (None, "return", [])
            self.containingBasicBlock.instructions += [instruction]

    def visitContinueStatementNode (self, node):
        continueLabel = self.parentLoops[-1].continueLabel
        # jmp (block(<loop_continue>))
        continueBlockExprType = irast.TypeSpecifierNode (irast.Type.BLOCK, "block", None)
        continueBlockExpr = irast.BasicBlockExpressionNode (continueLabel, None, None, None)
        arg0 = irast.ArgumentExpressionNode (continueBlockExprType, continueBlockExpr)
        instruction = irast.InstructionNode (None, "jmp", [arg0])
        self.containingBasicBlock.instructions += [instruction]

    def visitBreakStatementNode (self, node):
        breakLabel = self.parentLoops[-1].breakLabel
        # jmp (block(<loop_end>))
        breakBlockExprType = irast.TypeSpecifierNode (irast.Type.BLOCK, "block", None)
        breakBlockExpr = irast.BasicBlockExpressionNode (breakLabel, None, None, None)
        arg0 = irast.ArgumentExpressionNode (breakBlockExprType, breakBlockExpr)
        instruction = irast.InstructionNode (None, "jmp", [arg0])
        self.containingBasicBlock.instructions += [instruction]

    def visitCodeBlockNode (self, node):
        # create new scope level 
        self.scopeNames += [f"__block__{self.jumpIndex}"]
        self.jumpIndex += 1
        # if this is a function body
        # then add the parameters to this scope
        # for p in self.parameters:
        #     p.accept (self)
        # self.parameters.clear ()
        # visit each statement
        for statement in node.statements:
            statement.accept (self)
        # exit scope
        self.scopeNames.pop ()

    def visitExpressionNode (self, node):
        pass

    def visitTupleExpressionNode (self, node):
        node.lhs.accept (self)
        node.rhs.accept (self)

    def visitAssignExpressionNode (self, node):
        rhsReg = node.rhs.accept (self)
        irType = node.type.accept (self)
        lhsReg = None
        offsetReg = None
        isMem = False
        if isinstance(node.lhs, VariableDeclarationNode):
            # alloca
            if node.lhs.assignCount > 1:
                isMem = True
                # Vardec should add the alloca instruction so we need to visit
                lhsReg = node.lhs.accept (self)
                offsetReg = irast.IntLiteralExpressionNode (0)
            # register
            else:
                lhsReg = node.lhs.accept (self)
        elif isinstance(node.lhs, IdentifierExpressionNode):            
            # global var
            if isinstance(node.lhs.decl, GlobalVariableDeclarationNode):
                isMem = True
                # we dont want to visit lhs bc we dont want to load it from mem
                # So just use the pointer as the register
                lhsReg = irast.LocalVariableExpressionNode (f"@{node.lhs.id}.ptr", None, None, None)
                offsetReg = irast.IntLiteralExpressionNode (0)
            # alloca
            elif node.lhs.decl.assignCount > 1:
                isMem = True
                # we dont want to visit lhs bc we dont want to load it from mem
                # So just use the pointer as the register
                lhsReg = irast.LocalVariableExpressionNode (f"%{node.lhs.id}.ptr", None, None, None)
                offsetReg = irast.IntLiteralExpressionNode (0)
            # register
            else:
                lhsReg = node.lhs.accept (self)
        elif isinstance(node.lhs, SubscriptExpressionNode):
            isMem = True
            lhsReg = node.lhs.lhs.accept (self)
            offsetReg = node.lhs.offset.accept (self)
            # NOTE: we should probably use getelementptr here
        elif isinstance (node.lhs, MemberAccessorExpressionNode):
            print("ERROR: Assigning to MemberAccessorExpressionNode not implemented")
            printToken (node.lhs.op)
            exit(1)

        # Read lhs if we need it
        if (node.op.type != "ASSIGN"):
            if isMem:
                # %lhsValue = load (type(<type>), ptr(<lhs>), int32(<offset>))
                lhsValueReg = self.newLocalReg ()
                arg0 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.TYPE, "type", None), irType)
                arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.PTR, "ptr", None), lhsReg)
                arg2 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), offsetReg)
                instruction = irast.InstructionNode (lhsValueReg, "load", [arg0, arg1, arg2])
                self.containingBasicBlock.instructions += [instruction]
            else:
                lhsValueReg = lhsReg

        # perform extra operation
        # =
        if node.op.type == "ASSIGN":
            resultReg = rhsReg
        # +=
        elif node.op.type == "ASSIGN_ADD":
            resultReg = self.newLocalReg ()
            arg0 = irast.ArgumentExpressionNode (irType, lhsValueReg)
            arg1 = irast.ArgumentExpressionNode (irType, rhsReg)
            instruction = irast.InstructionNode (resultReg, "add", [arg0, arg1])
            self.containingBasicBlock.instructions += [instruction]
        # -=
        elif node.op.type == "ASSIGN_SUB":
            resultReg = self.newLocalReg ()
            arg0 = irast.ArgumentExpressionNode (irType, lhsValueReg)
            arg1 = irast.ArgumentExpressionNode (irType, rhsReg)
            instruction = irast.InstructionNode (resultReg, "sub", [arg0, arg1])
            self.containingBasicBlock.instructions += [instruction]
        # *=
        elif node.op.type == "ASSIGN_MUL":
            resultReg = self.newLocalReg ()
            arg0 = irast.ArgumentExpressionNode (irType, lhsValueReg)
            arg1 = irast.ArgumentExpressionNode (irType, rhsReg)
            instruction = irast.InstructionNode (resultReg, "mul", [arg0, arg1])
            self.containingBasicBlock.instructions += [instruction]
        # /=
        elif node.op.type == "ASSIGN_DIV":
            resultReg = self.newLocalReg ()
            arg0 = irast.ArgumentExpressionNode (irType, lhsValueReg)
            arg1 = irast.ArgumentExpressionNode (irType, rhsReg)
            instruction = irast.InstructionNode (resultReg, "div", [arg0, arg1])
            self.containingBasicBlock.instructions += [instruction]
        # %=
        elif node.op.type == "ASSIGN_MOD":
            resultReg = self.newLocalReg ()
            arg0 = irast.ArgumentExpressionNode (irType, lhsValueReg)
            arg1 = irast.ArgumentExpressionNode (irType, rhsReg)
            instruction = irast.InstructionNode (resultReg, "mod", [arg0, arg1])
            self.containingBasicBlock.instructions += [instruction]

        # Perform assign
        if isMem:
            arg0 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.PTR, "ptr", None), lhsReg)
            arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), offsetReg)
            arg2 = irast.ArgumentExpressionNode (irType, resultReg)
            instruction = irast.InstructionNode (None, "store", [arg0, arg1, arg2])
            self.containingBasicBlock.instructions += [instruction]
        else:
            arg0 = irast.ArgumentExpressionNode (irType, resultReg)
            instruction = irast.InstructionNode (lhsReg, "value", [arg0])
            self.containingBasicBlock.instructions += [instruction]
        
        return resultReg

    def visitLogicalOrExpressionNode (self, node):
        print("ERROR: LogicalOrExpressionNode not implemented")
        printToken (node.token)
        exit(1)
        self.printComment ("OR")

        self.indentation += 1

        # calc lhs 
        self.printComment ("Eval LHS")
        self.indentation += 1
        node.lhs.accept (self)
        self.indentation -= 1

        # generate unique labels
        # this is done after eval LHS so the jumpIndexes increase top-down
        short_circuit_state_label = f".OR_SHORT_CIRCUIT{self.jumpIndex}"
        false_label = f".OR_FALSE{self.jumpIndex}"
        end_label = f".OR_END{self.jumpIndex}"
        self.jumpIndex += 1

        # short-circuit if true 
        self.printComment ("Check if we need to short-circuit")
        self.indentation += 1
        self.printCode ("pop rax ; __lhs")
        self.printCode ("test rax, rax")
        self.printCode (f"jne {short_circuit_state_label}")
        self.indentation -= 1

        # calc rhs 
        self.printComment ("Eval RHS")
        self.indentation += 1
        node.rhs.accept (self)
        self.indentation -= 1

        # short-circuit if false 
        self.printComment ("Check rhs")
        self.indentation += 1
        self.printCode ("pop rax ; __rhs")
        self.printCode ("test rax, rax")
        self.printCode (f"je {false_label} ; skip true state if false (rax == 0)")
        self.indentation -= 1

        # short cicuit state
        self.printLabel (f"{short_circuit_state_label}:")
        self.printCode ("mov rax, 1 ; result = True")
        self.printCode (f"jmp {end_label} ; skip false state")

        # false state
        self.printComment ("False state")
        self.printLabel (f"{false_label}:")
        self.printCode ("mov rax, 0 ; result = False")

        # end state
        self.printLabel (f"{end_label}:")
        self.printCode ("movzx eax, al")
        self.printCode ("push rax ; result")

        self.indentation -= 1

    def visitLogicalAndExpressionNode (self, node):
        print("ERROR: LogicalAndExpressionNode not implemented")
        printToken (node.token)
        exit(1)
        self.printComment ("AND")

        self.indentation += 1

        # calc lhs 
        self.printComment ("Eval LHS")
        self.indentation += 1
        node.lhs.accept (self)
        self.indentation -= 1

        # generate unique labels
        # this is done after eval LHS so the jumpIndexes increase top-down
        short_circuit_state_label = f".AND_SHORT_CIRCUIT{self.jumpIndex}"
        end_label = f".AND_END{self.jumpIndex}"
        self.jumpIndex += 1

        # short-circuit if false 
        self.printComment ("Check if we need to short-circuit")
        self.indentation += 1
        self.printCode ("pop rax ; __lhs")
        self.printCode ("test rax, rax")
        self.printCode (f"je {short_circuit_state_label}")
        self.indentation -= 1

        # calc rhs 
        self.printComment ("Eval RHS")
        self.indentation += 1
        node.rhs.accept (self)
        self.indentation -= 1

        # short-circuit if false 
        self.printComment ("Check RHS")
        self.indentation += 1
        self.printCode ("pop rax ; __rhs")
        self.printCode ("test rax, rax")
        self.printCode (f"je {short_circuit_state_label}")
        self.indentation -= 1

        # success state
        self.printComment ("Success state")
        self.printCode ("mov rax, 1 ; result = True")
        self.printCode (f"jmp {end_label}")

        # short cicuit state
        self.printLabel (f"{short_circuit_state_label}:")
        self.printCode ("mov rax, 0 ; result = False")

        # end state
        self.printLabel (f"{end_label}:")
        self.printCode ("movzx eax, al")
        self.printCode ("push rax ; result")

        self.indentation -= 1

    def visitEqualityExpressionNode (self, node):
        lhsReg = node.lhs.accept (self)
        rhsReg = node.rhs.accept (self)
        destReg = self.newLocalReg ()
        if node.op.lexeme == "==":
            command = "ceq"
        else: # node.op.lexeme == "!=":
            command = "cne"
        lhsIRType = node.lhs.type.accept (self)
        arg0 = irast.ArgumentExpressionNode (lhsIRType, lhsReg)
        rhsIRType = node.rhs.type.accept (self)
        arg1 = irast.ArgumentExpressionNode (rhsIRType, rhsReg)
        instruction = irast.InstructionNode (destReg, command, [arg0, arg1])
        self.containingBasicBlock.instructions += [instruction]
        return destReg

    def visitInequalityExpressionNode (self, node):
        lhsReg = node.lhs.accept (self)
        rhsReg = node.rhs.accept (self)
        destReg = self.newLocalReg ()
        if node.op.lexeme == "<":
            command = "clt"
        elif node.op.lexeme == "<=":
            command = "cle"
        elif node.op.lexeme == ">":
            command = "cgt"
        else: # node.op.lexeme == ">=":
            command = "cge"
        lhsIRType = node.lhs.type.accept (self)
        arg0 = irast.ArgumentExpressionNode (lhsIRType, lhsReg)
        rhsIRType = node.rhs.type.accept (self)
        arg1 = irast.ArgumentExpressionNode (rhsIRType, rhsReg)
        instruction = irast.InstructionNode (destReg, command, [arg0, arg1])
        self.containingBasicBlock.instructions += [instruction]
        return destReg

    def visitAdditiveExpressionNode (self, node):
        lhsReg = node.lhs.accept (self)
        rhsReg = node.rhs.accept (self)
        destReg = self.newLocalReg ()
        if node.op.lexeme == '+':
            command = "add"
        else: # node.op.lexeme == '-':
            command = "sub"
        lhsIRType = node.lhs.type.accept (self)
        arg0 = irast.ArgumentExpressionNode (lhsIRType, lhsReg)
        rhsIRType = node.rhs.type.accept (self)
        arg1 = irast.ArgumentExpressionNode (rhsIRType, rhsReg)
        instruction = irast.InstructionNode (destReg, command, [arg0, arg1])
        self.containingBasicBlock.instructions += [instruction]
        return destReg

    def visitMultiplicativeExpressionNode (self, node):
        lhsReg = node.lhs.accept (self)
        rhsReg = node.rhs.accept (self)
        destReg = self.newLocalReg ()
        if node.op.lexeme == '*':
            command = "mul"
        elif node.op.lexeme == '/':
            command = "div"
        else: # node.op.lexeme == '%':
            command = "mod"
        lhsIRType = node.lhs.type.accept (self)
        arg0 = irast.ArgumentExpressionNode (lhsIRType, lhsReg)
        rhsIRType = node.rhs.type.accept (self)
        arg1 = irast.ArgumentExpressionNode (rhsIRType, rhsReg)
        instruction = irast.InstructionNode (destReg, command, [arg0, arg1])
        self.containingBasicBlock.instructions += [instruction]
        return destReg

    def visitPreIncrementExpressionNode(self, node):
        # Cerulean  : ++<rhs>
        # CeruleanIR: %rhsValue = load (type(int32), ptr(<rhs>), int32(0))
        #             %result = add (int32(%rhsValue), int32(1))
        #             store (ptr(<rhs>), int32(0), int32(%result))
        #             // return %result
        # NOTE: Considering that preincrement means reassignment and reassigned variables are
        # allocated on the stack, we can assume that rhs is a mem lookup
        irType = node.type.accept (self)
        rhsReg = None
        offsetReg = None
        isMem = False
        if isinstance(node.rhs, VariableDeclarationNode):
            # alloca
            if node.rhs.assignCount > 1:
                isMem = True
                # Vardec should add the alloca instruction so we need to visit
                rhsReg = node.rhs.accept (self)
                offsetReg = irast.IntLiteralExpressionNode (0)
            # register
            else:
                rhsReg = node.rhs.accept (self)
        elif isinstance(node.rhs, IdentifierExpressionNode):            
            # global var
            if isinstance(node.rhs.decl, GlobalVariableDeclarationNode):
                isMem = True
                # we dont want to visit rhs bc we dont want to load it from mem
                # So just use the pointer as the register
                rhsReg = irast.LocalVariableExpressionNode (f"@{node.rhs.id}.ptr", None, None, None)
                offsetReg = irast.IntLiteralExpressionNode (0)
            # alloca
            elif node.rhs.decl.assignCount > 1:
                isMem = True
                # we dont want to visit rhs bc we dont want to load it from mem
                # So just use the pointer as the register
                rhsReg = irast.LocalVariableExpressionNode (f"%{node.rhs.id}.ptr", None, None, None)
                offsetReg = irast.IntLiteralExpressionNode (0)
            # register
            else:
                rhsReg = node.rhs.accept (self)
        elif isinstance(node.rhs, SubscriptExpressionNode):
            isMem = True
            rhsReg = node.rhs.lhs.accept (self)
            offsetReg = node.rhs.offset.accept (self)
            # NOTE: we should probably use getelementptr here
        elif isinstance (node.rhs, MemberAccessorExpressionNode):
            print("ERROR: pre-increment to MemberAccessorExpressionNode not implemented")
            printToken (node.rhs.op)
            exit(1)
        else:
            print("ERROR: Invalid rhs to pre-increment")
            printToken (node.rhs.op)
            exit(1)

        # Read rhs value
        if isMem:
            # %lhsValue = load (type(<type>), ptr(<lhs>), int32(<offset>))
            rhsValueReg = self.newLocalReg ()
            arg0 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.TYPE, "type", None), irType)
            arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.PTR, "ptr", None), rhsReg)
            arg2 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), offsetReg)
            instruction = irast.InstructionNode (rhsValueReg, "load", [arg0, arg1, arg2])
            self.containingBasicBlock.instructions += [instruction]
        else:
            rhsValueReg = rhsReg

        # Perform increment
        resultReg = self.newLocalReg ()
        arg0 = irast.ArgumentExpressionNode (irType, rhsValueReg)
        arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), irast.IntLiteralExpressionNode (1))
        instruction = irast.InstructionNode (resultReg, "add", [arg0, arg1])
        self.containingBasicBlock.instructions += [instruction]

        # Write back value
        if isMem:
            arg0 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.PTR, "ptr", None), rhsReg)
            arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), offsetReg)
            arg2 = irast.ArgumentExpressionNode (irType, resultReg)
            instruction = irast.InstructionNode (None, "store", [arg0, arg1, arg2])
            self.containingBasicBlock.instructions += [instruction]
        else:
            arg0 = irast.ArgumentExpressionNode (irType, resultReg)
            instruction = irast.InstructionNode (rhsReg, "value", [arg0])
            self.containingBasicBlock.instructions += [instruction]

        return resultReg

    # NOTE: I hate how much duplicated code there is between this and pre
    def visitPreDecrementExpressionNode(self, node):
        # Cerulean  : --<rhs>
        # CeruleanIR: %rhsValue = load (type(int32), ptr(<rhs>), int32(0))
        #             %result = sub (int32(%rhsValue), int32(1))
        #             store (ptr(<rhs>), int32(0), int32(%result))
        #             // return %result
        # NOTE: Considering that predecrement means reassignment and reassigned variables are
        # allocated on the stack, we can assume that rhs is a mem lookup
        irType = node.type.accept (self)
        rhsReg = None
        offsetReg = None
        isMem = False
        if isinstance(node.rhs, VariableDeclarationNode):
            # alloca
            if node.rhs.assignCount > 1:
                isMem = True
                # Vardec should add the alloca instruction so we need to visit
                rhsReg = node.rhs.accept (self)
                offsetReg = irast.IntLiteralExpressionNode (0)
            # register
            else:
                rhsReg = node.rhs.accept (self)
        elif isinstance(node.rhs, IdentifierExpressionNode):            
            # global var
            if isinstance(node.rhs.decl, GlobalVariableDeclarationNode):
                isMem = True
                # we dont want to visit rhs bc we dont want to load it from mem
                # So just use the pointer as the register
                rhsReg = irast.LocalVariableExpressionNode (f"@{node.rhs.id}.ptr", None, None, None)
                offsetReg = irast.IntLiteralExpressionNode (0)
            # alloca
            elif node.rhs.decl.assignCount > 1:
                isMem = True
                # we dont want to visit rhs bc we dont want to load it from mem
                # So just use the pointer as the register
                rhsReg = irast.LocalVariableExpressionNode (f"%{node.rhs.id}.ptr", None, None, None)
                offsetReg = irast.IntLiteralExpressionNode (0)
            # register
            else:
                rhsReg = node.rhs.accept (self)
        elif isinstance(node.rhs, SubscriptExpressionNode):
            isMem = True
            rhsReg = node.rhs.lhs.accept (self)
            offsetReg = node.rhs.offset.accept (self)
            # NOTE: we should probably use getelementptr here
        elif isinstance (node.rhs, MemberAccessorExpressionNode):
            print("ERROR: pre-decrement to MemberAccessorExpressionNode not implemented")
            printToken (node.rhs.op)
            exit(1)
        else:
            print("ERROR: Invalid rhs to pre-decrement")
            printToken (node.rhs.op)
            exit(1)

        # Read rhs value
        if isMem:
            # %lhsValue = load (type(<type>), ptr(<lhs>), int32(<offset>))
            rhsValueReg = self.newLocalReg ()
            arg0 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.TYPE, "type", None), irType)
            arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.PTR, "ptr", None), rhsReg)
            arg2 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), offsetReg)
            instruction = irast.InstructionNode (rhsValueReg, "load", [arg0, arg1, arg2])
            self.containingBasicBlock.instructions += [instruction]
        else:
            rhsValueReg = rhsReg

        # Perform decrement
        resultReg = self.newLocalReg ()
        arg0 = irast.ArgumentExpressionNode (irType, rhsValueReg)
        arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), irast.IntLiteralExpressionNode (1))
        instruction = irast.InstructionNode (resultReg, "sub", [arg0, arg1])
        self.containingBasicBlock.instructions += [instruction]

        # Write back value
        if isMem:
            arg0 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.PTR, "ptr", None), rhsReg)
            arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), offsetReg)
            arg2 = irast.ArgumentExpressionNode (irType, resultReg)
            instruction = irast.InstructionNode (None, "store", [arg0, arg1, arg2])
            self.containingBasicBlock.instructions += [instruction]
        else:
            arg0 = irast.ArgumentExpressionNode (irType, resultReg)
            instruction = irast.InstructionNode (rhsReg, "value", [arg0])
            self.containingBasicBlock.instructions += [instruction]

        return resultReg

    def visitNegativeExpressionNode(self, node):
        # Cerulean  : -<rhs>
        # CeruleanIR: %negatedValue = sub (<type>(0), <type>(<rhs>))
        #             // return %negatedValue from expression
        rhsReg = node.rhs.accept (self)
        rhsIRType = node.rhs.type.accept (self)
        resultReg = self.newLocalReg ()
        arg0 = irast.ArgumentExpressionNode (rhsIRType, irast.IntLiteralExpressionNode(0))
        arg1 = irast.ArgumentExpressionNode (rhsIRType, rhsReg)
        instruction = irast.InstructionNode (resultReg, "sub", [arg0, arg1])
        self.containingBasicBlock.instructions += [instruction]
        return resultReg

    def visitLogicalNotExpressionNode(self, node):
        # Cerulean  : !<rhs>
        # CeruleanIR: %negatedValue = lnot (bool(<rhs>))
        #             // This might need a zext as well
        #             // return %negatedValue from expression
        rhsReg = node.rhs.accept (self)
        rhsIRType = node.rhs.type.accept (self)
        resultReg = self.newLocalReg ()
        arg0 = irast.ArgumentExpressionNode (rhsIRType, rhsReg)
        instruction = irast.InstructionNode (resultReg, "lnot", [arg0])
        self.containingBasicBlock.instructions += [instruction]
        return resultReg

    def visitBitwiseNegatationExpressionNode(self, node):
        print("ERROR: BitwiseNegatationExpressionNode not implemented")
        printToken (node.op)
        exit(1)

    def visitPostIncrementExpressionNode(self, node):
        # Cerulean  : <lhs>++
        # CeruleanIR: %lhsValue = load (type(int32), ptr(<lhs>), int32(0))
        #             %result = add (int32(%lhsValue), int32(1))
        #             store (ptr(<lhs>), int32(0), int32(%result))
        #             // return %lhsValue
        # NOTE: Considering that postincrement means reassignment and reassigned variables are
        # allocated on the stack, we can assume that lhs is a mem lookup
        irType = node.type.accept (self)
        lhsReg = None
        offsetReg = None
        isMem = False
        if isinstance(node.lhs, VariableDeclarationNode):
            # alloca
            if node.lhs.assignCount > 1:
                isMem = True
                # Vardec should add the alloca instruction so we need to visit
                lhsReg = node.lhs.accept (self)
                offsetReg = irast.IntLiteralExpressionNode (0)
            # register
            else:
                lhsReg = node.lhs.accept (self)
        elif isinstance(node.lhs, IdentifierExpressionNode):            
            # global var
            if isinstance(node.lhs.decl, GlobalVariableDeclarationNode):
                isMem = True
                # we dont want to visit lhs bc we dont want to load it from mem
                # So just use the pointer as the register
                lhsReg = irast.LocalVariableExpressionNode (f"@{node.lhs.id}.ptr", None, None, None)
                offsetReg = irast.IntLiteralExpressionNode (0)
            # alloca
            elif node.lhs.decl.assignCount > 1:
                isMem = True
                # we dont want to visit lhs bc we dont want to load it from mem
                # So just use the pointer as the register
                lhsReg = irast.LocalVariableExpressionNode (f"%{node.lhs.id}.ptr", None, None, None)
                offsetReg = irast.IntLiteralExpressionNode (0)
            # register
            else:
                lhsReg = node.lhs.accept (self)
        elif isinstance(node.lhs, SubscriptExpressionNode):
            isMem = True
            lhsReg = node.lhs.lhs.accept (self)
            offsetReg = node.lhs.offset.accept (self)
            # NOTE: we should probably use getelementptr here
        elif isinstance (node.lhs, MemberAccessorExpressionNode):
            print("ERROR: post-increment to MemberAccessorExpressionNode not implemented")
            printToken (node.lhs.op)
            exit(1)
        else:
            print("ERROR: Invalid lhs to post-increment")
            printToken (node.lhs.op)
            exit(1)

        # Read lhs value
        if isMem:
            # %lhsValue = load (type(<type>), ptr(<lhs>), int32(<offset>))
            lhsValueReg = self.newLocalReg ()
            arg0 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.TYPE, "type", None), irType)
            arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.PTR, "ptr", None), lhsReg)
            arg2 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), offsetReg)
            instruction = irast.InstructionNode (lhsValueReg, "load", [arg0, arg1, arg2])
            self.containingBasicBlock.instructions += [instruction]
        else:
            lhsValueReg = lhsReg

        # Perform increment
        resultReg = self.newLocalReg ()
        arg0 = irast.ArgumentExpressionNode (irType, lhsValueReg)
        arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), irast.IntLiteralExpressionNode (1))
        instruction = irast.InstructionNode (resultReg, "add", [arg0, arg1])
        self.containingBasicBlock.instructions += [instruction]

        # Write back value
        if isMem:
            arg0 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.PTR, "ptr", None), lhsReg)
            arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), offsetReg)
            arg2 = irast.ArgumentExpressionNode (irType, resultReg)
            instruction = irast.InstructionNode (None, "store", [arg0, arg1, arg2])
            self.containingBasicBlock.instructions += [instruction]
        else:
            arg0 = irast.ArgumentExpressionNode (irType, resultReg)
            instruction = irast.InstructionNode (lhsReg, "value", [arg0])
            self.containingBasicBlock.instructions += [instruction]

        # Return the register that has the previous value of lhs
        return lhsValueReg

    def visitPostDecrementExpressionNode (self, node):
        # Cerulean  : <lhs>++
        # CeruleanIR: %lhsValue = load (type(int32), ptr(<lhs>), int32(0))
        #             %result = sub (int32(%lhsValue), int32(1))
        #             store (ptr(<lhs>), int32(0), int32(%result))
        #             // return %lhsValue
        # NOTE: Considering that postdecrement means reassignment and reassigned variables are
        # allocated on the stack, we can assume that lhs is a mem lookup
        irType = node.type.accept (self)
        lhsReg = None
        offsetReg = None
        isMem = False
        if isinstance(node.lhs, VariableDeclarationNode):
            # alloca
            if node.lhs.assignCount > 1:
                isMem = True
                # Vardec should add the alloca instruction so we need to visit
                lhsReg = node.lhs.accept (self)
                offsetReg = irast.IntLiteralExpressionNode (0)
            # register
            else:
                lhsReg = node.lhs.accept (self)
        elif isinstance(node.lhs, IdentifierExpressionNode):            
            # global var
            if isinstance(node.lhs.decl, GlobalVariableDeclarationNode):
                isMem = True
                # we dont want to visit lhs bc we dont want to load it from mem
                # So just use the pointer as the register
                lhsReg = irast.LocalVariableExpressionNode (f"@{node.lhs.id}.ptr", None, None, None)
                offsetReg = irast.IntLiteralExpressionNode (0)
            # alloca
            elif node.lhs.decl.assignCount > 1:
                isMem = True
                # we dont want to visit lhs bc we dont want to load it from mem
                # So just use the pointer as the register
                lhsReg = irast.LocalVariableExpressionNode (f"%{node.lhs.id}.ptr", None, None, None)
                offsetReg = irast.IntLiteralExpressionNode (0)
            # register
            else:
                lhsReg = node.lhs.accept (self)
        elif isinstance(node.lhs, SubscriptExpressionNode):
            isMem = True
            lhsReg = node.lhs.lhs.accept (self)
            offsetReg = node.lhs.offset.accept (self)
            # NOTE: we should probably use getelementptr here
        elif isinstance (node.lhs, MemberAccessorExpressionNode):
            print("ERROR: post-decrement to MemberAccessorExpressionNode not implemented")
            printToken (node.lhs.op)
            exit(1)
        else:
            print("ERROR: Invalid lhs to post-decrement")
            printToken (node.lhs.op)
            exit(1)

        # Read lhs value
        if isMem:
            # %lhsValue = load (type(<type>), ptr(<lhs>), int32(<offset>))
            lhsValueReg = self.newLocalReg ()
            arg0 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.TYPE, "type", None), irType)
            arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.PTR, "ptr", None), lhsReg)
            arg2 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), offsetReg)
            instruction = irast.InstructionNode (lhsValueReg, "load", [arg0, arg1, arg2])
            self.containingBasicBlock.instructions += [instruction]
        else:
            lhsValueReg = lhsReg

        # Perform decrement
        resultReg = self.newLocalReg ()
        arg0 = irast.ArgumentExpressionNode (irType, lhsValueReg)
        arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), irast.IntLiteralExpressionNode (1))
        instruction = irast.InstructionNode (resultReg, "sub", [arg0, arg1])
        self.containingBasicBlock.instructions += [instruction]

        # Write back value
        if isMem:
            arg0 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.PTR, "ptr", None), lhsReg)
            arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), offsetReg)
            arg2 = irast.ArgumentExpressionNode (irType, resultReg)
            instruction = irast.InstructionNode (None, "store", [arg0, arg1, arg2])
            self.containingBasicBlock.instructions += [instruction]
        else:
            arg0 = irast.ArgumentExpressionNode (irType, resultReg)
            instruction = irast.InstructionNode (lhsReg, "value", [arg0])
            self.containingBasicBlock.instructions += [instruction]

        # Return the register that has the previous value of lhs
        return lhsValueReg

    def visitSubscriptExpressionNode (self, node):
        irType = node.type.accept (self)
        ptrReg = node.lhs.accept (self)
        offsetReg = node.offset.accept (self)
        arg0 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.TYPE , "type", None), irType)
        arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.PTR  , "ptr", None), ptrReg)
        arg2 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), offsetReg)
        resultReg = self.newLocalReg ()
        instruction = irast.InstructionNode (resultReg, "load", [arg0, arg1, arg2])
        self.containingBasicBlock.instructions += [instruction]
        return resultReg

    def visitFunctionCallExpressionNode (self, node):
        arguments = []
        for i in range(len(node.args)):
            argReg = node.args[i].accept (self)
            argType = node.args[i].type.accept (self)
            arguments += [irast.ArgumentExpressionNode (argType, argReg)]
        retReg = self.newLocalReg ()
        instruction = irast.CallInstructionNode (retReg, f"@{node.decl.scopeName}", None, arguments)
        self.containingBasicBlock.instructions += [instruction]
        return retReg

    def visitMemberAccessorExpressionNode (self, node):
        print("ERROR: MemberAccessorExpressionNode not implemented")
        printToken (node.op)
        exit(1)

        # static calls 
        # lhs is not an identifier 
        if node.isstatic:
            # enum 
            self.printComment (f"Enum Member Accessor - {node.lhs.id}.{node.rhs.id}")
            self.indentation += 1
            self.printCode (f"PUSH {node.decl.scopeName}")
            self.indentation -= 1
            return 

        self.printComment ("Member Accessor")

        self.indentation += 1

        self.printComment ("LHS")
        self.indentation += 1
        node.lhs.accept (self)
        self.indentation -= 1

        self.printComment ("RHS")
        self.indentation += 1
        if node.decl.scopeName == "":
            x = sum([1 if '\n' in s else 0 for s in self.code])
            print (f"[code-gen] [member-accessor] Error: no scope name for '{node.decl.id}' on line {node.lineNumber}")
            print (f"   this could have happened due to a cyclic reference/composition with template classes")
            print (f"   cyclic references are not yet supported")
            exit (1)
        self.printCode (f"push qword [{node.decl.scopeName}] ; stored index associated with field that is being accessed")
        self.indentation -= 1

        self.printCode ("pop rdx ; rhs")
        self.printCode ("pop rax ; lhs")
        self.printCode ("push qword [rax + 8*rdx] ; lhs.rhs")

        self.indentation -= 1

    def visitFieldAccessorExpressionNode (self, node):
        print("ERROR: FieldAccessorExpressionNode not implemented")
        printToken (node.op)
        exit(1)
        self.printComment ("Field Accessor")

        self.indentation += 1

        self.printComment ("LHS")
        self.indentation += 1
        node.lhs.accept (self)
        self.indentation -= 1

        self.printComment ("RHS")
        self.indentation += 1
        # construct field index var 
        self.printCode (f"PUSH {node.decl.scopeName}")
        self.indentation -= 1

        self.printCode ("POP __child")
        self.printCode ("POP __parent")
        self.printCode ("PUSH __parent[__child]")

        self.indentation -= 1

    def visitMethodAccessorExpressionNode (self, node):
        print("ERROR: MethodAccessorExpressionNode not implemented")
        printToken (node.op)
        exit(1)
        if node.decl.isVirtual:
            self.printComment (f"Virtual Method Call - {node.decl.signatureNoScope} -> {node.decl.type}")
        else:
            self.printComment (f"Method Call - {node.decl.signature} -> {node.decl.type}")

        self.indentation += 1

        # must be allocated before object param
        self.printComment (f"Make space for {len(node.args)} arg(s) and object parameter")
        self.printCode (f"sub rsp, {(len(node.args)+1)*8}")

        self.printComment ("LHS")
        self.indentation += 1
        node.lhs.accept (self)
        self.printCode ("pop rax ; object parameter")
        self.printCode (f"mov qword [rsp + 0], rax ; place as first parameter")
        self.indentation -= 1

        self.printComment ("RHS")
        self.indentation += 1
        # *** nothing atm
        self.indentation -= 1

        self.printComment ("Arguments")
        self.indentation += 1
        # calc arguments first
        # an argument could be another function call
        # to avoid conflicts with variables, 
        # we will have a separate loop to pop the values
        for i in range(len(node.args)):
            self.printComment (f"Eval arg{i}")
            self.indentation += 1
            node.args[i].accept (self)
            self.indentation -= 1
            
            # move arg result to proper place in stack
            self.printComment (f"Move arg{i}'s result to reverse order position on stack")
            self.printCode ("pop rax")
            offset = (i+1) * 8
            self.printCode (f"mov qword [rsp + {offset}], rax")
        
        self.indentation -= 1 # end args
        

        # if virtual function
        if node.decl.isVirtual:
            # call the appropriate function 
            self.printComment (f"Virtual Function Dispatch")
            # find dispatch table index 
            # by locating the matching virtual function 
            index = 0 
            for i in range(len(node.decl.parentClass.virtualMethods)):
                if node.decl.signatureNoScope == node.decl.parentClass.virtualMethods[i].signatureNoScope:
                    # found index 
                    index = i 
                    break 
            else:
                print (f"Error: Dispatch Function not found")
            # call proper dispatch function 
            self.printCode (f"mov rdx, qword [rsp + 0] ;  rdx = object")
            self.printCode (f"mov rdi, qword [rdx + 0] ;  rdi = object[0] ; dtable")
            self.printCode (f"call qword [rdi + {8*index}] ; dtable[{index}] ; {node.decl.scopeName}")

        # otherwise, call function normally
        else:
            self.printCode (f"call .{node.decl.scopeName}")

        # remove arguments from stack
        self.printComment ("Remove args")
        self.printCode (f"add rsp, {(len(node.args)+1)*8}")
        
        # put function's return val on the stack
        # float values are stored in xmm0
        self.printComment ("Push return value")
        if node.decl.type.__str__() == "float":
            # move from fancy reg to normal reg
            self.printCode ("movq rax, xmm0")
            self.printCode ("push rax")
        # all other types of return values
        else:
            self.printCode ("push rax")

        # restore indentation
        self.indentation -= 1

    def visitThisExpressionNode (self, node):
        print("ERROR: ThisExpressionNode not implemented")
        printToken (node.op)
        exit(1)
        self.printComment (f"This keyword")
        self.indentation += 1
        # push [rbp - 8] ; this 
        # this is a pointer so we only need to worry about qword
        self.printCode (f"push qword [rbp - {node.decl.thisStackOffset}] ; __this")
        self.indentation -= 1

    def visitIdentifierExpressionNode (self, node):
        # Var is on the stack
        # Global variables and Parameters are stored on the stack
        if node.decl.assignCount > 1 or isinstance(node.decl, (GlobalVariableDeclarationNode, ParameterNode)):
            irType = node.type.accept (self)
            if isinstance(node.decl, GlobalVariableDeclarationNode):
                ptr = irast.LocalVariableExpressionNode (f"@{node.id}.ptr", None, None, None)
            else:
                ptr = irast.LocalVariableExpressionNode (f"%{node.id}.ptr", None, None, None)
            offset = irast.IntLiteralExpressionNode (0)
            arg0 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.TYPE , "type", None), irType)
            arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.PTR  , "ptr", None), ptr)
            arg2 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), offset)
            resultReg = self.newLocalReg ()
            instruction = irast.InstructionNode (resultReg, "load", [arg0, arg1, arg2])
            self.containingBasicBlock.instructions += [instruction]
            return resultReg
        # Var is in a reg
        return irast.LocalVariableExpressionNode (f"%{node.id}", None, None, None)

    def visitArrayAllocatorExpressionNode (self, node):
        elementType = node.elementType.accept (self)
        sizeReg = node.sizeExpr.accept (self)
        arg0 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.TYPE , "type", None), elementType)
        arg1 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.INT32, "int32", None), sizeReg)
        resultReg = self.newLocalReg ()
        instruction = irast.InstructionNode (resultReg, "malloc", [arg0, arg1])
        self.containingBasicBlock.instructions += [instruction]
        return resultReg

    def visitConstructorCallExpressionNode (self, node):
        print("ERROR: ConstructorCallExpressionNode not implemented")
        printToken (node.token)
        exit(1)
        self.printComment (f"Constructor Call - {node.decl.signature} -> {node.decl.parentClass.type}")

        self.indentation += 1

        self.printComment (f"Make space for {len(node.args)} arg(s)")
        self.printCode (f"sub rsp, {len(node.args)*8}")

        self.printComment ("Arguments")
        self.indentation += 1
        # calc arguments first
        # an argument could be another function call
        # to avoid conflicts with variables, 
        # we will have a separate loop to pop the values
        for i in range(len(node.args)):
            self.printComment (f"Eval arg{i}")
            self.indentation += 1
            node.args[i].accept (self)
            self.indentation -= 1
            
            # move arg result to proper place in stack
            self.printComment (f"Move arg{i}'s result to reverse order position on stack")
            self.printCode ("pop rax")
            offset = i * 8
            self.printCode (f"mov qword [rsp + {offset}], rax")
        
        self.indentation -= 1 # end args

        # call function
        self.printComment (f"Call {node.decl.signature}")
        if node.decl.scopeName == "":
            # x = sum([1 if '\n' in s else 0 for s in self.code])
            # print (f"[code-gen] Error: no scope name for {node.function.id} {[t.type.__str__() for t in node.args]} {node.lineNumber} {x}")
            # print (f"   this could have happened due to a template using a class that was defined after the template")
            # print (f"   temporary fix: move the class declaration to above the template class that uses it")
            # solution! extremely ad hoc 
            self.printCode (f"call ${node.decl.signature}")
            # exit (1)
        else:
            self.printCode (f"call .{node.decl.scopeName}")

        # remove arguments from stack
        self.printComment ("Remove args")
        self.printCode (f"add rsp, {len(node.args)*8}")
        
        # put function's return val on the stack
        # float values are stored in xmm0
        self.printComment ("Push return value")
        if node.decl.type.__str__() == "float":
            # move from fancy reg to normal reg
            self.printCode ("movq rax, xmm0")
            self.printCode ("push rax")
        # all other types of return values
        else:
            self.printCode ("push rax")

        # restore indentation
        self.indentation -= 1
    
    def visitSizeofExpressionNode(self, node):
        print("ERROR: SizeofExpressionNode not implemented")
        printToken (node.token)
        exit(1)
        self.printComment ("Sizeof Operator")
        self.indentation += 1

        # calc rhs
        self.printComment ("RHS")
        self.indentation += 1
        node.rhs.accept (self)
        self.indentation -= 1

        print (f"[codegen] Error: sizeof keyword not implemented for x86")
        exit (1)

        self.printComment ("Calculate array size")
        self.printCode ("POP __array")
        self.printCode ("SIZEOF __size __array")
        self.printCode ("PUSH __size")

        self.indentation -= 1
    
    def visitFreeExpressionNode (self, node):
        ptrReg = node.rhs.accept (self)
        arg0 = irast.ArgumentExpressionNode (irast.TypeSpecifierNode (irast.Type.PTR , "ptr", None), ptrReg)
        instruction = irast.InstructionNode (None, "free", [arg0])
        self.containingBasicBlock.instructions += [instruction]
        return None

    def visitIntLiteralExpressionNode (self, node):
        return irast.IntLiteralExpressionNode (node.value)

    def visitFloatLiteralExpressionNode (self, node):
        return irast.FloatLiteralExpressionNode (node.value)

    def visitCharLiteralExpressionNode (self, node):
        return irast.CharLiteralExpressionNode (node.value)

    def visitStringLiteralExpressionNode (self, node):
        return irast.StringLiteralExpressionNode (node.value)

    def visitNullExpressionNode (self, node):
        return irast.NullExpressionNode ()

    def visitListConstructorExpressionNode (self, node):
        print("ERROR: ListConstructorExpressionNode not implemented")
        printToken (node.token)
        exit(1)
        self.printComment ("Array Constructor")

        self.indentation += 1

        # evaluate each element
        # elements could be list constructors 
        #  so we don't want to pop values into variables yet
        self.printComment ("Elements")
        for elem in node.elems:
            elem.accept (self)
            
        # allocate space for array
        # ** right now this is only on heap
        # but after evaluating the arguments, we already have the array on the stack lmao - usable?

        # determine element size in bytes
        # char - 1 byte
        # int, float, pointer - 8 bytes
        if node.type.__str__() == "char[]":
            self.printCode (f"mov edi, {len(node.elems)} ; number of bytes to allocate (nArgs * 1byte (char))")
        else:
            self.printCode (f"mov edi, {len(node.elems)*8} ; number of bytes to allocate (nArgs * 8bytes)")
        
        self.printCode (f"call malloc ; allocates edi bytes on heap and stores pointer in rax")

        # add elements to list in correct order
        self.printComment ("Populate array values")
        for i in range(len(node.elems)-1, -1, -1):
            self.printCode (f"pop rdx ; get array element {i}")
            # determine element size in bytes
            # char - 1 byte
            if node.type.__str__() == "char[]":
                self.printCode (f"mov byte [rax + {i}], dl ; arr[{i}] = rdx")
            # int, float, pointer - 8 bytes
            else:
                self.printCode (f"mov qword [rax + {i*8}], rdx ; arr[{i}] = rdx")

        # push array onto stack
        self.printCode ("push rax")

        self.indentation -= 1

# ========================================================================
