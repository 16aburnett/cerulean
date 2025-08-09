# CeruleanIR Compiler - Code Generation for AmyAssembly
# By Amy Burnett
# June 22 2024
# ========================================================================

import os
from sys import exit

from ...ceruleanIRAST import *
from ...visitor import ASTVisitor
from ...symbolTable import SymbolTable

# ========================================================================

DIVIDER_LENGTH = 75
TAB_LENGTH = 3

LIB_FILENAME = os.path.dirname(__file__) + "/CeruleanIR_BuiltinLib.amyasm"

# ========================================================================

class CodeGenVisitor_AmyAssembly (ASTVisitor):

    def __init__(self, lines):
        self.parameters = []
        self.lines = lines 
        self.indentation = 0
        self.code = []
        self.lhs = "null"
        self.jumpIndex = 0
        self.shouldComment = False
        # stack implementation
        # keeps track of containing loop
        # for break and continue statements 
        self.parentLoops = []
        self.pushParent = False
        self.scopeNames = ["__main"]
        # assume it is successful - generator will set to false
        # if an error is encountered
        self.wasSuccessful = True
        self.cmpIndex = 0

    # === HELPER FUNCTIONS ===============================================

    def printSpaces (self, level):
        if not self.shouldComment:
            level = 1
            
        while level > 0:
            for i in range(TAB_LENGTH):
                self.code += [" "]
            level -= 1

    def printCode (self, line):
        self.printSpaces (self.indentation)
        self.code += [f"{line}\n"]

    def printLabel (self, label):
        # labels do not have indentation
        self.code += [f"{label}:\n"]

    def printComment (self, comment):
        if not self.shouldComment:
            return 
            
        self.printSpaces (self.indentation)
        self.code += ["// ", comment, "\n"]

    def printHeader (self, header):
        if not self.shouldComment:
            return 
            
        self.printSpaces (self.indentation)
        dividerLength = DIVIDER_LENGTH - (self.indentation * TAB_LENGTH) - len (header) - 8
        divider = ["//### "]
        divider += [header, " "]
        for i in range(dividerLength):
            divider += ["#"]
        divider += ["\n"]
        self.code += ["".join(divider)]

    def printDivider (self):
        if not self.shouldComment:
            return 
            
        self.printSpaces (self.indentation)
        dividerLength = DIVIDER_LENGTH - (self.indentation * TAB_LENGTH) - 3
        divider = ["//"]
        for i in range(dividerLength):
            divider += ["="]
        divider += ["\n"]
        self.code += ["".join(divider)]

    def printSubDivider (self):
        if not self.shouldComment:
            return 
            
        self.printSpaces (self.indentation)
        dividerLength = DIVIDER_LENGTH - (self.indentation * TAB_LENGTH) - 3
        divider = ["//"]
        for i in range(dividerLength):
            divider += ["-"]
        divider += ["\n"]
        self.code += ["".join(divider)]

    def printNewline (self):
        if not self.shouldComment:
            return 
        self.code += ["\n"]

    def enterScope (self, name):
        self.scopeNames += [f"__{name}"]

    def exitScope (self):
        self.scopeNames.pop ()

    # === VISITOR FUNCTIONS ==============================================

    def visitProgramNode (self, node):

        self.printComment ("AmyAssembly compiled from CeruleanIR")
        self.printDivider ()
        self.printNewline ()

        self.printDivider ()
        self.printHeader ("BUILT-IN LIBRARY CODE")
        self.printDivider ()
        self.printNewline ()

        # add library code
        file = open (LIB_FILENAME, "r")
        for line in file.readlines ():
            self.code += [line]

        self.printDivider ()
        self.printHeader ("COMPILED CODE")
        self.printDivider ()
        self.printNewline ()

        for codeunit in node.codeunits:
            if codeunit != None:
                codeunit.accept (self)

        self.printDivider ()
        self.printHeader ("END OF CODE")
        self.printDivider ()
        self.printNewline ()

        self.printLabel ("__start")
        self.indentation += 1
        self.printComment ("Start with main function")
        self.printCode ("CALL __main____main")
        self.printCode ("HALT")
        self.indentation -= 1

    #=====================================================================

    def visitTypeSpecifierNode (self, node):
        pass

    #=====================================================================

    def visitParameterNode (self, node):
        node.type.accept (self)
        node.scopeName = "".join (self.scopeNames) + "__" + node.id[1:]

    #=====================================================================

    def visitGlobalVariableDeclarationNode (self, node):
        self.printComment (f"Global Variable Declaration - {node.id}")

        self.indentation += 1

        # variable names are modified by its scope 
        scopeName = "".join (self.scopeNames) + "__" + node.id[1:]

        # get rhs
        rhs_value = node.arguments[0].accept (self)

        # declare the variable with default value
        # Moreso a requirement of CeruleanIR, global variables must be pointers to memory
        self.printCode (f"MALLOC {scopeName.replace(".", "_")} 1")
        self.printCode (f"ASSIGN {scopeName.replace(".", "_")}[0] {rhs_value}")
        self.lhs = node.id
        node.scopeName = scopeName

        self.indentation -= 1

    #=====================================================================

    def visitVariableDeclarationNode (self, node):
        self.printComment (f"Variable Declaration - {node.id}")

        self.indentation += 1

        # variable names are modified by its scope 
        scopeName = "".join (self.scopeNames) + "__" + node.id[1:]

        # dont need to declare variable initially
        # self.printCode (f"ASSIGN {scopeName} 0")
        self.lhs = node.id
        node.scopeName = scopeName

        self.indentation -= 1

    #=====================================================================

    def visitFunctionNode (self, node):

        # variable names are modified by its scope 
        scopeName = ["".join (self.scopeNames), "____", node.id[1:]]
        # add signature to scopeName for overloaded functions
        if len(node.params) > 0:
            scopeName += [f"__{node.params[0].type.id}"]
            # add array dimensions
            if node.params[0].type.arrayDimensions > 0:
                scopeName += [f"__{node.params[0].type.arrayDimensions}"]
            for i in range(1, len(node.params)):
                scopeName += [f"__{node.params[i].type.id}"]
                # add array dimensions
                if node.params[i].type.arrayDimensions > 0:
                    scopeName += [f"__{node.params[i].type.arrayDimensions}"]
        node.scopeName = "".join(scopeName)

        # AD HOC CENTRAL!!
        # fill in prereferences with scopename 
        for i in range(len(self.code)):
            if f"${node.signature}" in self.code[i]:
                self.code[i] = self.code[i].replace(f"${node.signature}", node.scopeName)

        # create new scope level 
        self.scopeNames += [f"__{node.id[1:]}"]

        self.printDivider ()
        self.printComment (f"Function Declaration - {node.signature} -> {node.type}")
        # add jump to skip over function 
        self.printCode (f"JUMP __end__{node.scopeName}")

        # place function jump-point label 
        self.printLabel (node.scopeName)

        self.indentation += 1

        # load parameters 
        self.printComment ("Parameters")
        self.indentation += 1
        for i in range(len(node.params)):
            self.printComment (f"Param: {node.params[i].id}")
            node.params[i].accept (self)
            # keep the same parameter name 
            self.printCode (f"STACKGET {node.params[i].scopeName.replace(".", "_")} {i}")
        self.indentation -= 1

        self.printComment ("Body")
        self.indentation += 1
        for basicBlock in node.basicBlocks:
            basicBlock.accept (self)
        self.indentation -= 1

        # extra return statement for if return is not provided 
        self.printCode ("RETURN 0")

        self.indentation -= 1

        self.printLabel (f"__end__{node.scopeName}")

        self.printComment (f"End Function Declaration - {node.scopeName}")
        self.printDivider ()
        self.printNewline ()

        # remove scope level 
        self.scopeNames.pop ()

    #=====================================================================

    def visitBasicBlockNode (self, node):
        self.printSubDivider ()
        self.printComment ("Basic Block")
        self.indentation += 1

        node.scopeName = "".join (self.scopeNames) + "__" + node.name
        self.printLabel (f"{node.scopeName}")

        for instruction in node.instructions:
            instruction.accept (self)

        self.indentation -= 1
        self.printSubDivider ()

    #=====================================================================

    def visitInstructionNode (self, node):
        self.printComment (f"Instruction - {node.command}")
        self.indentation += 1

        # Convert/map CeruleanIR instructions to AmyAssembly instructions
        # Instructions are slightly different in either language.
        command_name = node.command
        if command_name == "add":
            # CeruleanIR : <dest> = add (<src0>, <src1>)
            # AmyAssembly: add <dest> <src0> <src1>
            # visit variabledecl to establish scopename
            # **lhsvariable should probably return scopename
            node.lhsVariable.accept (self)
            lhs_var = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"ADD {lhs_var} {arg0} {arg1}")
        elif command_name == "sub":
            # CeruleanIR : <dest> = sub (<src0>, <src1>)
            # AmyAssembly: subtract <dest> <src0> <src1>
            # visit variabledecl to establish scopename
            # **lhsvariable should probably return scopename
            node.lhsVariable.accept (self)
            lhs_var = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"SUBTRACT {lhs_var} {arg0} {arg1}")
        elif command_name == "mul":
            # CeruleanIR : <dest> = mul (<src0>, <src1>)
            # AmyAssembly: multiply <dest> <src0> <src1>
            # visit variabledecl to establish scopename
            # **lhsvariable should probably return scopename
            node.lhsVariable.accept (self)
            lhs_var = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"MULTIPLY {lhs_var} {arg0} {arg1}")
        elif command_name == "div":
            # CeruleanIR : <dest> = div (<src0>, <src1>)
            # AmyAssembly: divide <dest> <src0> <src1>
            # visit variabledecl to establish scopename
            # **lhsvariable should probably return scopename
            node.lhsVariable.accept (self)
            lhs_var = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"DIVIDE {lhs_var} {arg0} {arg1}")
        elif command_name == "mod":
            # CeruleanIR : <dest> = mod (<src0>, <src1>)
            # AmyAssembly: mod <dest> <src0> <src1>
            # visit variabledecl to establish scopename
            # **lhsvariable should probably return scopename
            node.lhsVariable.accept (self)
            lhs_var = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"MOD {lhs_var} {arg0} {arg1}")
        elif command_name == "lnot":
            # Logical Negation
            # CeruleanIR : <dest> = lnot (<src0>)
            # AmyAssembly: NOT <dest> <src0>
            # visit variabledecl to establish scopename
            # **lhsvariable should probably return scopename
            node.lhsVariable.accept (self)
            lhs_var = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            self.printCode (f"NOT {lhs_var}, {arg0}")
        elif command_name == "value": # just an assignment
            # CeruleanIR : <dest> = value (<arg0>)
            # AmyAssembly: assign <dest> <arg0>
            # visit variabledecl to establish scopename
            node.lhsVariable.accept (self)
            lhs_var = node.lhsVariable.scopeName.replace(".", "_")
            # visit argument expression to get new argument
            rhs_value = node.arguments[0].accept (self)
            self.printCode (f"ASSIGN {lhs_var} {rhs_value}")
        elif command_name == "alloca":
            # CeruleanIR : <ptr> = alloca (<type>, <size>)
            # AmyAssembly: MALLOC <ptr> <size>
            # NOTE: amyasm probably needs an alloca but mapping to malloc for now
            # visit variabledecl to establish scopename
            # **lhsvariable should probably return scopename
            node.lhsVariable.accept (self)
            lhs_var = node.lhsVariable.scopeName.replace(".", "_")
            type = node.arguments[0].accept (self)
            # AmyAsm allocates in terms of elements not bytes
            # so we can ignore the type
            size = node.arguments[1].accept (self)
            self.printCode (f"MALLOC {lhs_var} {size}")
        elif command_name == "malloc":
            # CeruleanIR : <ptr> = malloc (<type>, <size>)
            # AmyAssembly: MALLOC <ptr> <size>
            # NOTE: LLVMIR uses a call to malloc - not a builtin malloc
            # visit variabledecl to establish scopename
            # **lhsvariable should probably return scopename
            node.lhsVariable.accept (self)
            lhs_var = node.lhsVariable.scopeName.replace(".", "_")
            type = node.arguments[0].accept (self)
            # AmyAsm allocates in terms of elements not bytes
            # so we can ignore the type
            size = node.arguments[1].accept (self)
            self.printCode (f"MALLOC {lhs_var} {size}")
        elif command_name == "free":
            # CeruleanIR : free (<ptr>)
            # AmyAssembly: FREE <ptr>
            ptr = node.arguments[0].accept (self)
            self.printCode (f"FREE {ptr}")
        elif command_name == "load":
            # CeruleanIR : <dest> = load (<type>, <pointer>, <offset>)
            # AmyAssembly: ASSIGN <dest> <pointer>[<offset>]
            # visit variabledecl to establish scopename
            # **lhsvariable should probably return scopename
            node.lhsVariable.accept (self)
            lhs_var = node.lhsVariable.scopeName.replace(".", "_")
            # **NOTE** ignoring type arg
            pointer = node.arguments[1].accept (self)
            offset = node.arguments[2].accept (self)
            self.printCode (f"ASSIGN {lhs_var} {pointer}[{offset}]")
        elif command_name == "store":
            # CeruleanIR : store (<pointer>, <offset>, <value>)
            # AmyAssembly: ASSIGN <pointer>[<offset>] <value>
            # visit variabledecl to establish scopename
            # **lhsvariable should probably return scopename
            pointer = node.arguments[0].accept (self)
            offset = node.arguments[1].accept (self)
            value = node.arguments[2].accept (self)
            self.printCode (f"ASSIGN {pointer}[{offset}] {value}")
        elif command_name == "clt":
            # CeruleanIR : <dest> = clt (<arg0>, <arg1>)
            # AmyAssembly: LT <dest>, <arg0>, <arg1>
            node.lhsVariable.accept (self)
            dest = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"LT {dest}, {arg0}, {arg1}")
        elif command_name == "cle":
            # CeruleanIR : <dest> = cle (<arg0>, <arg1>)
            # AmyAssembly: LE <dest>, <arg0>, <arg1>
            node.lhsVariable.accept (self)
            dest = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"LE {dest}, {arg0}, {arg1}")
        elif command_name == "cgt":
            # CeruleanIR : <dest> = cgt (<arg0>, <arg1>)
            # AmyAssembly: GT <dest>, <arg0>, <arg1>
            node.lhsVariable.accept (self)
            dest = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"GT {dest}, {arg0}, {arg1}")
        elif command_name == "cge":
            # CeruleanIR : <dest> = cge (<arg0>, <arg1>)
            # AmyAssembly: GE <dest>, <arg0>, <arg1>
            node.lhsVariable.accept (self)
            dest = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"GE {dest}, {arg0}, {arg1}")
        elif command_name == "ceq":
            # CeruleanIR : <dest> = ceq (<arg0>, <arg1>)
            # AmyAssembly: EQUAL <dest>, <arg0>, <arg1>
            node.lhsVariable.accept (self)
            dest = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"EQUAL {dest}, {arg0}, {arg1}")
        elif command_name == "cne":
            # CeruleanIR : <dest> = cne (<arg0>, <arg1>)
            # AmyAssembly: NEQUAL <dest>, <arg0>, <arg1>
            node.lhsVariable.accept (self)
            dest = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"NEQUAL {dest}, {arg0}, {arg1}")
        elif command_name == "jmp":
            # CeruleanIR : jmp (<label>)
            # AmyAssembly: jump <label>
            label = node.arguments[0].accept (self)
            self.printCode (f"JUMP {label}")
        elif command_name == "jcmp":
            # CeruleanIR : jcmp (<cmp>, <label_if_true>, <label_if_false>)
            # AmyAssembly: CMP <cmp>, 1
            #              JEQ <label_if_true>
            #              JUMP <label_if_false>
            cmp = node.arguments[0].accept (self)
            label_true = node.arguments[1].accept (self)
            label_false = node.arguments[2].accept (self)
            self.printCode (f"CMP {cmp}, 1 // set flag if cmp is true")
            self.printCode (f"JEQ {label_true} // jump to true block")
            self.printCode (f"JUMP {label_false} // otherwise jump to false block")
        elif command_name == "jg":
            # CeruleanIR : jg (<arg0>, <arg1>, <label>)
            # AmyAssembly: cmp <arg0> <arg1>
            #              jg <label>
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            label = node.arguments[2].accept (self)
            self.printCode (f"CMP {arg0}, {arg1}")
            self.printCode (f"JG {label}")
        elif command_name == "jge":
            # CeruleanIR : jge (<arg0>, <arg1>, <label>)
            # AmyAssembly: cmp <arg0> <arg1>
            #              jge <label>
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            label = node.arguments[2].accept (self)
            self.printCode (f"CMP {arg0}, {arg1}")
            self.printCode (f"JGE {label}")
        elif command_name == "jl":
            # CeruleanIR : jl (<arg0>, <arg1>, <label>)
            # AmyAssembly: cmp <arg0> <arg1>
            #              jl <label>
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            label = node.arguments[2].accept (self)
            self.printCode (f"CMP {arg0}, {arg1}")
            self.printCode (f"JL {label}")
        elif command_name == "jle":
            # CeruleanIR : jle (<arg0>, <arg1>, <label>)
            # AmyAssembly: cmp <arg0> <arg1>
            #              jle <label>
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            label = node.arguments[2].accept (self)
            self.printCode (f"CMP {arg0}, {arg1}")
            self.printCode (f"JLE {label}")
        elif command_name == "jne":
            # CeruleanIR : jne (<arg0>, <arg1>, <label>)
            # AmyAssembly: cmp <arg0> <arg1>
            #              jne <label>
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            label = node.arguments[2].accept (self)
            self.printCode (f"CMP {arg0}, {arg1}")
            self.printCode (f"JEQ {label}")
        elif command_name == "jne":
            # CeruleanIR : jne (<arg0>, <arg1>, <label>)
            # AmyAssembly: cmp <arg0>, <arg1>
            #              jne <label>
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            label = node.arguments[2].accept (self)
            self.printCode (f"CMP {arg0}, {arg1}")
            self.printCode (f"JNE {label}")
        elif command_name == "return":
            # CeruleanIR : return (<return_value>)
            # AmyAssembly: return <return_value>
            if len(node.arguments) > 0:
                return_value = node.arguments[0].accept (self)
            else:
                # AmyAssembly requires a return value even if returning nothing
                return_value = "0"
            self.printCode (f"RETURN {return_value}")
        else:
            print (f"CodeGen error: Unknown instruction '{command_name}'")
            self.wasSuccessful = False

        self.indentation -= 1

    #=====================================================================

    def visitCallInstructionNode (self, node):
        self.printComment (f"Call instruction - {node.function_name}")
        self.indentation += 1
        
        # CeruleanIR : <retVal> = call <function_name> (<arg0>, <arg1>, ... <argN>)
        # AmyAssembly: PUSH <argN>
        #              ...
        #              PUSH <arg1>
        #              PUSH <arg0>
        #              CALL <function_name>
        #              POP <arg0>
        #              POP <arg1>
        #              ...
        #              POP <argN>
        # push arguments in reverse order
        for i in range(len(node.arguments)-1, -1, -1):
            arg = node.arguments[i].accept (self)
            self.printCode (f"PUSH {arg}")
        self.printCode (f"CALL {node.decl.scopeName}")
        # Get return value
        if node.lhsVariable:
            node.lhsVariable.accept (self)
            self.printCode (f"RESPONSE {node.lhsVariable.scopeName}")
        # pop arguments off
        for i in range(len(node.arguments)):
            self.printCode (f"POP _arg{i}")

        self.indentation -= 1

    #=====================================================================

    # writes any code it needs to
    # returns the parsed argument
    def visitArgumentExpressionNode (self, node):
        return node.expression.accept (self)

    #=====================================================================

    # root node - should not be used
    def visitExpressionNode (self, node):
        pass

    #=====================================================================

    def visitGlobalVariableExpressionNode (self, node):
        self.printComment (f"Global variable expression - {node.decl.scopeName}")
        return node.decl.scopeName.replace(".", "_")

    #=====================================================================

    def visitLocalVariableExpressionNode (self, node):
        self.printComment (f"Local Expression - {node.decl.scopeName}")
        return node.decl.scopeName.replace(".", "_")

    #=====================================================================

    def visitBasicBlockExpressionNode (self, node):
        scopeName = "".join (self.scopeNames) + "__" + node.id
        self.printComment (f"Identifier - {scopeName}")
        return scopeName

    #=====================================================================

    def visitIntLiteralExpressionNode (self, node):
        self.printComment (f"Int Literal - {node.value}")
        return node.value

    #=====================================================================

    def visitFloatLiteralExpressionNode (self, node):
        self.printComment (f"Float Literal - {node.value}")
        return node.value

    #=====================================================================

    def visitCharLiteralExpressionNode (self, node):
        self.printComment (f"Float Literal - '{node.value}'")
        return f"'{node.value}'"

    #=====================================================================

    def visitStringLiteralExpressionNode (self, node):
        self.printComment ("String Literal")
        self.indentation += 1
        # this should be allocated statically
        # I REALLY need to fix this stack/heap issue
        # create string on heap as char[]
        node.value = (node.value.replace(f'\n', f'\\n').replace ('\t', '\\t')).replace ("\r", "\\r").replace ("\b", "\\b")
        # node.value = node.value.replace ("\\n", "\n").replace ("\\t", "\t").replace ("\\r", "\r").replace ("\\b", "\b")
        chars = [node.value[i] for i in range(1, len(node.value)-1)]
        for i in range(len(chars)-1):
            if i >= len(chars)-1:
                break
            if chars[i] == "\\": # and \
                # (chars[i+1] == 'n'  \
                # or chars[i+1] == 't'\
                # or chars[i+1] == 'r'\
                # or chars[i+1] == 'b'):
                chars[i] = "\\" + chars[i+1]
                del chars[i+1]
            # add backslash to apostrophe 
            elif chars[i] == '\'':
                chars[i] = '\\\''
        node.value = chars + ['\\0']
        backSlashes = 0
        # for c in node.value:
        #     if c == '\\':
        #         backSlashes += 1
        self.printCode (f"MALLOC __str {len(node.value)-backSlashes}")
        for i in range(len(node.value)-backSlashes):
            self.printCode (f"ASSIGN __str[{i}] '{(node.value[i])}'")
        # self.printCode ("PUSH __str")
        self.indentation -= 1
        return "__str"

# ========================================================================