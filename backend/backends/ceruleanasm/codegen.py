# CeruleanIR Compiler - Code Generation for CeruleanASM
# By Amy Burnett
# =================================================================================================

import os
from sys import exit

from ...ceruleanIRAST import *
from ...visitor import ASTVisitor
from ...symbolTable import SymbolTable
from .livenessAnalyzer import LivenessAnalyzer

# =================================================================================================

DIVIDER_LENGTH = 75
TAB_LENGTH = 3

LIB_FILENAME = os.path.dirname(__file__) + "/CeruleanIR_BuiltinLib.ceruleanasm"

# =================================================================================================

class CodeGenVisitor_CeruleanASM (ASTVisitor):

    def __init__(self, lines, shouldPrintDebug=False):
        self.parameters = []
        self.lines = lines 
        self.shouldPrintDebug = shouldPrintDebug
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

        self.functionEpilogueLabel = "<unknown-function-epilogue-label>"

        # Reg allocation
        # Only use the first 8 registers
        # Reserve the remaining 8 registers for other uses
        self.MAX_AVAILABLE_REGISTERS = 8
        self.availableRegisters = [f"r{i}" for i in range (self.MAX_AVAILABLE_REGISTERS)]
        self.scratchRegisters = ["r8", "r9", "r10"]
        self.virtualToPhysical = {} # Maps SSA var → reg or spill
        self.usedRegisters = set ()
        self.spillSlots = {}        # SSA var → stack slot index
        self.nextSpillSlot = 0

    def generate (self, ast):
        ast.accept (self)
        return "".join (self.code)

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
    
    def debugPrint (self, *args, **kwargs):
        if (self.shouldPrintDebug):
            print ("[debug] [codegen-ceruleanasm]", *args, **kwargs)

    # === REG ALLOCATION =================================================

    def allocate (self, virtualName):
        # If already allocated, return existing assignment
        if virtualName in self.virtualToPhysical:
            return self.virtualToPhysical[virtualName]
        
        # Try to find a free physical register
        for reg in self.availableRegisters:
            if reg not in self.usedRegisters:
                self.usedRegisters.add (reg)
                regObj = {"kind": "reg", "value": reg}
                self.virtualToPhysical[virtualName] = regObj
                return regObj
        
        # Spill: assign a stack slot
        slot = self.nextSpillSlot
        self.nextSpillSlot += 1
        self.spillSlots[virtualName] = slot
        self.virtualToPhysical[virtualName] = {"kind": "spill", "value": slot}
        return self.virtualToPhysical[virtualName]

    # Returns a register corresponding to the given virtual register/variable
    # If register spilling was needed, then this will emit a load instruction
    # to read the value from the stack and return it in a temporary register
    # Given virtual register/variable must have been allocated
    def resolve (self, virtualName):
        regOrSpill = self.virtualToPhysical[virtualName]
        
        if regOrSpill is None:
            raise Exception(f"Unknown virtual register {virtualName}")
        
        if regOrSpill["kind"] == "spill":
            # Emit a LOAD from spill slot into a temp reg
            tempReg = getTempReg ()
            self.printCode (f"load64 {tempReg}, bp, -{regOrSpill['value']}")
            return tempReg
        reg = regOrSpill["value"]
        return reg

    # Frees up the allocated register or stack spill slot so other virtual registers can use it
    def deallocate (self, virtualName):
        regOrSpill = self.virtualToPhysical[virtualName]
        if regOrSpill and regOrSpill["kind"] == "reg" and regOrSpill["value"] in self.usedRegisters:
            self.usedRegisters.remove (regOrSpill["value"])

    # Returns the next available temporary register
    def getTempReg (self):
        for temp in self.scratchRegisters:
            if temp not in self.usedRegisters:
                self.usedRegisters.add (temp)
                return temp
        raise RuntimeError("No scratch registers available")

    def deallocateTempReg (self, reg):
        self.usedRegisters.remove (reg)

    # === VISITOR FUNCTIONS ==============================================

    def visitProgramNode (self, node):

        # TODO: This really shouldnt be inside another visitor
        livenessAnalyzer = LivenessAnalyzer (self.shouldPrintDebug)
        livenessAnalyzer.analyze (node)

        self.printComment ("CeruleanASM code compiled from CeruleanIR")
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

        # This cannot be emitted per file...
        self.printLabel ("__start")
        self.indentation += 1
        self.printComment ("Start with main function")
        self.printCode (f"loada r0, __main____main")
        self.printCode (f"call r0")
        self.printCode (f"halt")
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
        print ("ERROR: visitGlobalVariableDeclarationNode not implemented")
        exit (1)
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

        self.debugPrint (f"Variable declaration '{node.id}'")
        regOrSpill = self.allocate (node.id)
        self.debugPrint (f"Allocating '{regOrSpill}' for variable '{node.id}'")

        self.indentation -= 1

        return regOrSpill

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

        self.functionEpilogueLabel = f"__epilogue__{node.scopeName}"

        # place function jump-point label 
        self.printLabel (node.scopeName)

        self.indentation += 1

        # Setup stack
        self.printComment ("Setup stack frame")
        self.indentation += 1
        self.printCode ("push bp")
        self.printCode ("mv64 bp, sp")
        # Allocate space for local vars
        # Warning! Make sure not to exceed 16-bit imm
        localVariablesBytes = 0
        self.printCode (f"sub64i sp, sp, {localVariablesBytes} // allocate space for local variables")
        self.indentation -= 1
        
        # load parameters 
        self.printComment ("Parameters")
        self.indentation += 1
        for i in range(len(node.params)):
            node.params[i].accept (self)
            # +16 because retaddr (8-bytes) and prev_rbp (8-bytes)
            offset = i * 8 + 16
            self.printComment (f"Param: {node.params[i].id} [bp + {offset}]")
            # * parameter offsets are made negative since they are accessed opposite to localVars
            # could be weird, might want to flip localVars to be negative instead
            node.params[i].stackOffset = -offset
        self.indentation -= 1

        self.printComment ("Body")
        self.indentation += 1
        for basicBlock in node.basicBlocks:
            basicBlock.accept (self)
        self.indentation -= 1

        # FUNCTION EPILOGUE
        self.printComment ("Function Epilogue")
        self.printLabel (self.functionEpilogueLabel)
        self.printCode ("mv64 sp, bp // remove local vars + unpopped pushes")
        self.printCode ("pop bp")
        # extra return statement for if return is not provided 
        self.printCode ("ret")

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

        # Convert/map CeruleanIR instructions to CeruleanASM instructions
        # Instructions are slightly different in either language.
        command_name = node.command
        if command_name == "add":
            # CeruleanIR : <dest> = add (<src0>, <src1>)
            # CeruleanASM: add <dest>, <src0>, <src1>
            regOrSpill = node.lhsVariable.accept (self)
            lhs_var = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            if regOrSpill["kind"] == "spill":
                offset = -regOrSpill["value"] * 8
                tempReg = self.getTempReg ()
                self.printCode (f"add64 {tempReg}, {arg0}, {arg1} // {lhs_var} = add {arg0}, {arg1}")
                self.printCode (f"store64 bp, {tempReg}, {offset} // spill to stack")
                self.deallocateTempReg (tempReg)
            else:
                reg = regOrSpill["value"]
                self.printCode (f"add64 {reg}, {arg0}, {arg1} // {lhs_var} = add {arg0}, {arg1}")
        elif command_name == "sub":
            # CeruleanIR : <dest> = sub (<src0>, <src1>)
            # CeruleanASM: sub64 <dest>, <src0>, <src1>
            # visit variabledecl to establish scopename
            # **lhsvariable should probably return scopename
            node.lhsVariable.accept (self)
            lhs_var = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"sub64 {lhs_var}, {arg0}, {arg1}")
        elif command_name == "mul":
            # CeruleanIR : <dest> = mul (<src0>, <src1>)
            # CeruleanASM: mul64 <dest>, <src0>, <src1>
            # visit variabledecl to establish scopename
            # **lhsvariable should probably return scopename
            node.lhsVariable.accept (self)
            lhs_var = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"mul64 {lhs_var}, {arg0}, {arg1}")
        elif command_name == "div":
            # CeruleanIR : <dest> = div (<src0>, <src1>)
            # CeruleanASM: divi64 <dest>, <src0>, <src1>
            # visit variabledecl to establish scopename
            # **lhsvariable should probably return scopename
            node.lhsVariable.accept (self)
            lhs_var = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"divi64 {lhs_var}, {arg0}, {arg1}")
        elif command_name == "mod":
            # CeruleanIR : <dest> = mod (<src0>, <src1>)
            # CeruleanASM: modi64 <dest>, <src0>, <src1>
            # visit variabledecl to establish scopename
            # **lhsvariable should probably return scopename
            node.lhsVariable.accept (self)
            lhs_var = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"modi64 {lhs_var}, {arg0}, {arg1}")
        elif command_name == "lnot":
            # Logical Negation
            # CeruleanIR : <dest> = lnot (<src0>)
            # CeruleanASM: not64 <dest>, <src0>
            # visit variabledecl to establish scopename
            # **lhsvariable should probably return scopename
            node.lhsVariable.accept (self)
            lhs_var = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            self.printCode (f"not64 {lhs_var}, {arg0}")
        elif command_name == "value": # just an assignment
            # CeruleanIR : <dest> = value (<arg0>)
            # CeruleanASM: mov64 <dest>, <arg0>
            regOrSpill = node.lhsVariable.accept (self)
            lhs_var = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            if isinstance (node.arguments[0].expression, (IntLiteralExpressionNode, FloatLiteralExpressionNode, CharLiteralExpressionNode, StringLiteralExpressionNode)):
                # NOTE: This is problematic if the arg doesnt fit in 16 bits
                op = "lli"
            else:
                op = "mv64"
            if regOrSpill["kind"] == "spill":
                offset = -regOrSpill["value"] * 8
                tempReg = self.getTempReg ()
                self.printCode (f"{op} {tempReg}, {arg0} // {lhs_var} = value {arg0}")
                self.printCode (f"store64 bp, {tempReg}, {offset} // spill to stack")
                self.deallocateTempReg (tempReg)
            else:
                reg = regOrSpill["value"]
                self.printCode (f"{op} {reg}, {arg0} // {lhs_var} = value {arg0}")
        elif command_name == "alloca":
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : <ptr> = alloca (<type>, <size>)
            # CeruleanASM: MALLOC <ptr> <size>
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
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : <ptr> = malloc (<type>, <size>)
            # CeruleanASM: MALLOC <ptr> <size>
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
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : free (<ptr>)
            # CeruleanASM: FREE <ptr>
            ptr = node.arguments[0].accept (self)
            self.printCode (f"FREE {ptr}")
        elif command_name == "load":
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : <dest> = load (<type>, <pointer>, <offset>)
            # CeruleanASM: ASSIGN <dest> <pointer>[<offset>]
            # visit variabledecl to establish scopename
            # **lhsvariable should probably return scopename
            node.lhsVariable.accept (self)
            lhs_var = node.lhsVariable.scopeName.replace(".", "_")
            # **NOTE** ignoring type arg
            pointer = node.arguments[1].accept (self)
            offset = node.arguments[2].accept (self)
            self.printCode (f"ASSIGN {lhs_var} {pointer}[{offset}]")
        elif command_name == "store":
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : store (<pointer>, <offset>, <value>)
            # CeruleanASM: ASSIGN <pointer>[<offset>] <value>
            # visit variabledecl to establish scopename
            # **lhsvariable should probably return scopename
            pointer = node.arguments[0].accept (self)
            offset = node.arguments[1].accept (self)
            value = node.arguments[2].accept (self)
            self.printCode (f"ASSIGN {pointer}[{offset}] {value}")
        elif command_name == "clt":
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : <dest> = clt (<arg0>, <arg1>)
            # CeruleanASM: LT <dest>, <arg0>, <arg1>
            node.lhsVariable.accept (self)
            dest = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"LT {dest}, {arg0}, {arg1}")
        elif command_name == "cle":
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : <dest> = cle (<arg0>, <arg1>)
            # CeruleanASM: LE <dest>, <arg0>, <arg1>
            node.lhsVariable.accept (self)
            dest = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"LE {dest}, {arg0}, {arg1}")
        elif command_name == "cgt":
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : <dest> = cgt (<arg0>, <arg1>)
            # CeruleanASM: GT <dest>, <arg0>, <arg1>
            node.lhsVariable.accept (self)
            dest = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"GT {dest}, {arg0}, {arg1}")
        elif command_name == "cge":
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : <dest> = cge (<arg0>, <arg1>)
            # CeruleanASM: GE <dest>, <arg0>, <arg1>
            node.lhsVariable.accept (self)
            dest = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"GE {dest}, {arg0}, {arg1}")
        elif command_name == "ceq":
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : <dest> = ceq (<arg0>, <arg1>)
            # CeruleanASM: EQUAL <dest>, <arg0>, <arg1>
            node.lhsVariable.accept (self)
            dest = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"EQUAL {dest}, {arg0}, {arg1}")
        elif command_name == "cne":
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : <dest> = cne (<arg0>, <arg1>)
            # CeruleanASM: NEQUAL <dest>, <arg0>, <arg1>
            node.lhsVariable.accept (self)
            dest = node.lhsVariable.scopeName.replace(".", "_")
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            self.printCode (f"NEQUAL {dest}, {arg0}, {arg1}")
        elif command_name == "jmp":
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : jmp (<label>)
            # CeruleanASM: jump <label>
            label = node.arguments[0].accept (self)
            self.printCode (f"JUMP {label}")
        elif command_name == "jcmp":
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : jcmp (<cmp>, <label_if_true>, <label_if_false>)
            # CeruleanASM: CMP <cmp>, 1
            #              JEQ <label_if_true>
            #              JUMP <label_if_false>
            cmp = node.arguments[0].accept (self)
            label_true = node.arguments[1].accept (self)
            label_false = node.arguments[2].accept (self)
            self.printCode (f"CMP {cmp}, 1 // set flag if cmp is true")
            self.printCode (f"JEQ {label_true} // jump to true block")
            self.printCode (f"JUMP {label_false} // otherwise jump to false block")
        elif command_name == "jg":
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : jg (<arg0>, <arg1>, <label>)
            # CeruleanASM: cmp <arg0> <arg1>
            #              jg <label>
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            label = node.arguments[2].accept (self)
            self.printCode (f"CMP {arg0}, {arg1}")
            self.printCode (f"JG {label}")
        elif command_name == "jge":
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : jge (<arg0>, <arg1>, <label>)
            # CeruleanASM: cmp <arg0> <arg1>
            #              jge <label>
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            label = node.arguments[2].accept (self)
            self.printCode (f"CMP {arg0}, {arg1}")
            self.printCode (f"JGE {label}")
        elif command_name == "jl":
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : jl (<arg0>, <arg1>, <label>)
            # CeruleanASM: cmp <arg0> <arg1>
            #              jl <label>
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            label = node.arguments[2].accept (self)
            self.printCode (f"CMP {arg0}, {arg1}")
            self.printCode (f"JL {label}")
        elif command_name == "jle":
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : jle (<arg0>, <arg1>, <label>)
            # CeruleanASM: cmp <arg0> <arg1>
            #              jle <label>
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            label = node.arguments[2].accept (self)
            self.printCode (f"CMP {arg0}, {arg1}")
            self.printCode (f"JLE {label}")
        elif command_name == "jne":
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : jne (<arg0>, <arg1>, <label>)
            # CeruleanASM: cmp <arg0> <arg1>
            #              jne <label>
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            label = node.arguments[2].accept (self)
            self.printCode (f"CMP {arg0}, {arg1}")
            self.printCode (f"JEQ {label}")
        elif command_name == "jne":
            print (f"ERROR: {command_name} not implemented")
            exit (1)
            # CeruleanIR : jne (<arg0>, <arg1>, <label>)
            # CeruleanASM: cmp <arg0>, <arg1>
            #              jne <label>
            arg0 = node.arguments[0].accept (self)
            arg1 = node.arguments[1].accept (self)
            label = node.arguments[2].accept (self)
            self.printCode (f"CMP {arg0}, {arg1}")
            self.printCode (f"JNE {label}")
        elif command_name == "return":
            # CeruleanIR : return (<return_value>)
            # CeruleanASM: mv64 ra, <return_value>
            #              ret
            if len(node.arguments) > 0:
                return_value = node.arguments[0].accept (self)
                if isinstance (node.arguments[0].expression, (IntLiteralExpressionNode, FloatLiteralExpressionNode, CharLiteralExpressionNode, StringLiteralExpressionNode)):
                    # NOTE: This is problematic if the arg doesnt fit in 16 bits
                    op = "lli"
                else: # registers
                    op = "mv64"
                self.printCode (f"{op} ra, {return_value} // return value")
            tempReg = self.getTempReg ()
            self.printCode (f"loada {tempReg}, {self.functionEpilogueLabel}")
            self.printCode (f"jmp {tempReg}")
            self.deallocateTempReg (tempReg)
        else:
            print (f"CodeGen error: Unknown instruction '{command_name}'")
            self.wasSuccessful = False

        self.indentation -= 1

    #=====================================================================

    def visitCallInstructionNode (self, node):
        self.printComment (f"Call instruction - {node.function_name}")
        self.indentation += 1
        
        # CeruleanIR : <retVal> = call <function_name> (<arg0>, <arg1>, ... <argN>)
        # CeruleanASM: push <argN>
        #              ...
        #              push <arg1>
        #              push <arg0>
        #              loada rd, <function_name>
        #              call rd
        #              pop <arg0>
        #              pop <arg1>
        #              ...
        #              pop <argN>
        # push arguments in reverse order
        for i in range(len(node.arguments)-1, -1, -1):
            regOrSpill = node.arguments[i].accept (self)
            if regOrSpill["kind"] == "spill":
                offset = -regOrSpill["value"] * 8
                tempReg = self.getTempReg ()
                self.printCode (f"load64 {tempReg}, bp, {offset} // read spilled value from stack")
                self.printCode (f"push {tempReg}")
                self.deallocateTempReg (tempReg)
            else:
                reg = regOrSpill["value"]
                self.printCode (f"push {reg}")
        # Call the function
        tempReg = self.getTempReg ()
        self.printCode (f"loada {tempReg}, {node.decl.scopeName}")
        self.printCode (f"call {tempReg}")
        self.deallocateTempReg (tempReg)
        # Get return value
        if node.lhsVariable:
            node.lhsVariable.accept (self)
            self.printComment (f"Get return value")
            self.printCode (f"mov64 {node.lhsVariable.scopeName}, ra")
        # pop arguments off
        self.printComment (f"Pop off arguments")
        for i in range(len(node.arguments)):
            self.printCode (f"pop ra")

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
        print ("ERROR: visitGlobalVariableExpressionNode not implemented")
        exit (1)
        self.printComment (f"Global variable expression - {node.decl.scopeName}")
        return node.decl.scopeName.replace(".", "_")

    #=====================================================================

    def visitLocalVariableExpressionNode (self, node):
        self.printComment (f"Local Expression - {node.decl.scopeName}")
        # return node.decl.scopeName.replace(".", "_")
        self.debugPrint (f"Variable expression '{node.id}'")
        regOrSpill = self.allocate (node.id)
        self.debugPrint (f"Allocating '{regOrSpill}' for variable '{node.id}'")
        return regOrSpill

    #=====================================================================

    def visitBasicBlockExpressionNode (self, node):
        print ("ERROR: visitBasicBlockExpressionNode not implemented")
        exit (1)
        scopeName = "".join (self.scopeNames) + "__" + node.id
        self.printComment (f"Identifier - {scopeName}")
        return scopeName

    #=====================================================================

    def visitIntLiteralExpressionNode (self, node):
        self.printComment (f"Int Literal - {node.value}")
        return node.value

    #=====================================================================

    def visitFloatLiteralExpressionNode (self, node):
        print ("ERROR: visitFloatLiteralExpressionNode not implemented")
        exit (1)
        self.printComment (f"Float Literal - {node.value}")
        return node.value

    #=====================================================================

    def visitCharLiteralExpressionNode (self, node):
        self.printComment (f"Char Literal - '{node.value}'")
        return f"'{node.value}'"

    #=====================================================================

    def visitStringLiteralExpressionNode (self, node):
        print ("ERROR: visitStringLiteralExpressionNode not implemented")
        exit (1)
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
