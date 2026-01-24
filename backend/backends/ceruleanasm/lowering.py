# CeruleanIR Compiler - Lowering step
# 
# By Amy Burnett
# =================================================================================================

from sys import exit

from ...ceruleanIRAST import *
from ...visitor import ASTVisitor
from . import ceruleanASMAST as ASM_AST

# =================================================================================================

class LoweringVisitor (ASTVisitor):

    def __init__(self, shouldPrintDebug=False):
        self.shouldPrintDebug = shouldPrintDebug

    def lower (self, ast):
        asm_ast = ast.accept (self)
        return asm_ast

    # === HELPER FUNCTIONS ========================================================================
    
    def debugPrint (self, *args, **kwargs):
        if (self.shouldPrintDebug):
            print ("[debug] [lowering]", *args, **kwargs)

    # === VISITOR FUNCTIONS =======================================================================

    def visitProgramNode (self, node):
        codeunits = []
        for codeunit in node.codeunits:
            if codeunit != None:
                newCodeunit = codeunit.accept (self)
                if newCodeunit:
                    codeunits += [newCodeunit]
        return ASM_AST.ProgramNode (codeunits)

    # =============================================================================================

    def visitTypeSpecifierNode (self, node):
        return node.id

    # =============================================================================================

    def visitParameterNode (self, node):
        # Parameters don't need special handling in Virtual ASM
        # Just return the node itself or None
        return None

    # =============================================================================================

    def visitGlobalVariableDeclarationNode (self, node):
        return ASM_AST.VirtualRegisterNode (node.id)

    # =============================================================================================

    def visitVariableDeclarationNode (self, node):
        return ASM_AST.VirtualRegisterNode (node.id)

    # =============================================================================================

    def visitFunctionNode (self, node):
        params = []
        for i in range(len(node.params)):
            params += [node.params[i].accept (self)]
        asmInstructions = []
        for basicBlock in node.basicBlocks:
            asmInstructions += basicBlock.accept (self)
        # Strip @ prefix from function name if present
        funcId = node.id[1:] if node.id.startswith('@') else node.id
        funcNode = ASM_AST.FunctionNode (funcId, node.token, params, asmInstructions)
        # Preserve scope name if it exists
        if hasattr(node, 'scopeName'):
            funcNode.scopeName = node.scopeName
        return funcNode

    # =============================================================================================

    def visitBasicBlockNode (self, node):
        asmInstructions = []
        for instruction in node.instructions:
            # Each instruction may expand to multiple asm instructions when lowered
            asmInstructions += instruction.accept (self)
        return asmInstructions

    # =============================================================================================

    def visitInstructionNode (self, node):
        asmArguments = []
        for arg in node.arguments:
            asmArguments += [arg.accept (self)]
        # can expand to multiple instructions
        asmInstructions = []
        commandName = node.command
        if commandName == "add":
            lhsReg = node.lhsVariable.accept (self)
            # Usage 1: Reg, Reg
            # CeruleanIR : <dest> = add (<src0>, <src1>)
            # CeruleanASM: add <dest>, <src0>, <src1>
            if isinstance (asmArguments[1], ASM_AST.RegisterNode):
                asmInstruction = ASM_AST.InstructionNode ("add64", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
            # Usage 2: Reg, Imm
            # CeruleanIR : <dest> = add (<src0>, <imm>)
            # CeruleanASM: addi <dest>, <src0>, <imm>
            else: # assuming imm is the only other option
                asmInstruction = ASM_AST.InstructionNode ("add64i", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
        elif commandName == "sub":
            lhsReg = node.lhsVariable.accept (self)
            # Usage 1: Reg, Reg
            # CeruleanIR : <dest> = sub (<src0>, <src1>)
            # CeruleanASM: sub <dest>, <src0>, <src1>
            if isinstance (asmArguments[1], ASM_AST.RegisterNode):
                asmInstruction = ASM_AST.InstructionNode ("sub64", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
            # Usage 2: Reg, Imm
            # CeruleanIR : <dest> = sub (<src0>, <imm>)
            # CeruleanASM: subi <dest>, <src0>, <imm>
            else: # assuming imm is the only other option
                asmInstruction = ASM_AST.InstructionNode ("sub64i", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
        elif commandName == "mul":
            lhsReg = node.lhsVariable.accept (self)
            # Usage 1: Reg, Reg
            # CeruleanIR : <dest> = mul (<src0>, <src1>)
            # CeruleanASM: mul<size> <dest>, <src0>, <src1>
            if isinstance (asmArguments[1], ASM_AST.RegisterNode):
                asmInstruction = ASM_AST.InstructionNode ("mul64", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
            # Usage 2: Reg, Imm
            # CeruleanIR : <dest> = mul (<src0>, <imm>)
            # CeruleanASM: mul<size>i <dest>, <src0>, <imm>
            else: # assuming imm is the only other option
                asmInstruction = ASM_AST.InstructionNode ("mul64i", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
        elif commandName == "div":
            lhsReg = node.lhsVariable.accept (self)
            # Usage 1: Reg, Reg
            # CeruleanIR : <dest> = div (<src0>, <src1>)
            # CeruleanASM: divi<size> <dest>, <src0>, <src1>
            # NOTE: Currently only using ints
            if isinstance (asmArguments[1], ASM_AST.RegisterNode):
                asmInstruction = ASM_AST.InstructionNode ("divi64", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
            # Usage 2: Reg, Imm
            # CeruleanIR : <dest> = div (<src0>, <imm>)
            # CeruleanASM: divi<size>i <dest>, <src0>, <imm>
            # NOTE: Currently only using ints
            else: # assuming imm is the only other option
                asmInstruction = ASM_AST.InstructionNode ("divi64i", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
        elif commandName == "mod":
            lhsReg = node.lhsVariable.accept (self)
            # Usage 1: Reg, Reg
            # CeruleanIR : <dest> = mod (<src0>, <src1>)
            # CeruleanASM: modi<size> <dest>, <src0>, <src1>
            # NOTE: Currently only using ints
            if isinstance (asmArguments[1], ASM_AST.RegisterNode):
                asmInstruction = ASM_AST.InstructionNode ("divi64", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
            # Usage 2: Reg, Imm
            # CeruleanIR : <dest> = mod (<src0>, <imm>)
            # CeruleanASM: modi<size>i <dest>, <src0>, <imm>
            # NOTE: Currently only using ints
            else: # assuming imm is the only other option
                asmInstruction = ASM_AST.InstructionNode ("modi64i", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
        elif commandName == "lnot":
            lhsReg = node.lhsVariable.accept (self)
            # Usage 1: Reg
            # CeruleanIR : <dest> = lnot (<src0>)
            # CeruleanASM: not64 <dest>, <src0>
            asmInstruction = ASM_AST.InstructionNode ("not64", [lhsReg, *asmArguments])
            asmInstructions += [asmInstruction]
        elif commandName == "value":
            lhsReg = node.lhsVariable.accept (self)
            # Usage 1: Reg
            # CeruleanIR : <dest> = value (<arg0>)
            # CeruleanASM: mv64 <dest>, <arg0>
            if isinstance (asmArguments[0], ASM_AST.RegisterNode):
                asmInstruction = ASM_AST.InstructionNode ("mv64", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
            # Usage 2: String Literal (needs loada for address)
            # CeruleanIR : <dest> = value (ptr("string"))
            # CeruleanASM: loada <dest>, <label>
            elif isinstance (asmArguments[0], ASM_AST.StringLiteralNode):
                # String literals are handled by the emitter (creates data section)
                # For now, keep the string literal and let emitter handle it
                # But we need loada instead of lli
                asmInstruction = ASM_AST.InstructionNode ("loada", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
            # Usage 3: Imm
            # CeruleanIR : <dest> = value (<imm>)
            # CeruleanASM: lli <dest>, <imm>
            # NOTE: Imm must fit in 16-bits
            else: # assuming imm is the only other option
                asmInstruction = ASM_AST.InstructionNode ("lli", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
        elif commandName == "alloca":
            # CeruleanIR: <ptr> = alloca(<type>, <count>)
            # Allocates <count> elements of <type> on the stack
            # Returns a pointer (address) to the allocated memory
            # 
            # Strategy: Use frame pointer arithmetic
            # The actual stack space will be allocated during frame lowering
            # Here we just need to compute the address
            #
            # For now, treat alloca variables as special stack-allocated registers
            # They'll be handled specially during register allocation
            lhsReg = node.lhsVariable.accept (self)
            typeArg = node.arguments[0].accept (self)
            count = node.arguments[1]
            
            # Create a pseudo-instruction to mark this as an alloca
            # The register allocator will handle this specially
            asmInstruction = ASM_AST.InstructionNode ("alloca", [lhsReg, ASM_AST.IntLiteralNode(str(count.value))])
            asmInstructions += [asmInstruction]
        elif commandName == "malloc":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "free":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "load":
            lhsReg = node.lhsVariable.accept (self)
            # Determine load instruction size based on type
            typeArg = node.arguments[0].accept (self)
            loadOp = "load8" if typeArg == "char" else "load64"
            
            # Usage 1: reg offset
            # CeruleanIR : <dest> = load (<type>, <pointer>, <offset>)
            # CeruleanASM: add64 r<temp>, r<ptr>, r<offset>
            #              load<size> r<dest>, r<temp>, imm<offset>
            if isinstance (asmArguments[2], ASM_AST.RegisterNode):
                self.debugPrint (f">>> lowering load(R,R) to add(R,R,R) and {loadOp}(R,R,I)")
                tempReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += [
                    ASM_AST.InstructionNode ("add64", [tempReg, asmArguments[1], asmArguments[2]]),
                    ASM_AST.InstructionNode (loadOp, [lhsReg, tempReg, ASM_AST.IntLiteralNode (0)])
                ]
            # Usage 2: imm offset
            # CeruleanIR : <dest> = load (<type>, <pointer>, <offset>)
            # CeruleanASM: load<size> r<dest>, r<ptr>, imm<offset>
            elif isinstance (asmArguments[2], ASM_AST.LiteralNode):
                asmInstructions += [ASM_AST.InstructionNode (loadOp, [lhsReg, asmArguments[1], asmArguments[2]])]
            else:
                print (f"Lowering Error: Unexpected argument type {asmArguments[2]}")
                exit (1)
        elif commandName == "store":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "clt":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "cle":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "cgt":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "cge":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "ceq":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "cne":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "jmp":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "jcmp":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "jg":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "jge":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "jl":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "jle":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "jne":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "jne":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "return":
            # Usage 1: no return value
            # CeruleanIR : return ()
            # CeruleanASM: loada r<temp> <functionEpilogueLabel>
            #              jmp r<temp>
            # NOTE: we dont want to just use the ASM ret
            # We want to use the function epilogue to fix the stack and such
            if len(asmArguments) < 1:
                tempReg = ASM_AST.VirtualTempRegisterNode ()
                functionEpilogueLabel = ASM_AST.LabelNode ("<function_epilogue_placeholder>")
                asmInstructions += [
                    ASM_AST.InstructionNode ("loada", [tempReg, functionEpilogueLabel]),
                    ASM_AST.InstructionNode ("jmp", [tempReg])
                ]
            # Usage 2: return reg
            # CeruleanIR : return (reg)
            # CeruleanASM: mv64 ra, r<src>
            #              loada r<temp> <functionEpilogueLabel>
            #              jmp r<temp>
            elif isinstance (asmArguments[0], ASM_AST.RegisterNode):
                returnReg = ASM_AST.PhysicalRegisterNode ("ra")
                tempReg = ASM_AST.VirtualTempRegisterNode ()
                functionEpilogueLabel = ASM_AST.LabelNode ("<function_epilogue_placeholder>")
                asmInstructions += [
                    ASM_AST.InstructionNode ("mv64", [returnReg, asmArguments[0]]),
                    ASM_AST.InstructionNode ("loada", [tempReg, functionEpilogueLabel]),
                    ASM_AST.InstructionNode ("jmp", [tempReg])
                ]
            # Usage 3: return imm
            # CeruleanIR : return (imm)
            # CeruleanASM: lli ra, imm
            #              loada r<temp> <functionEpilogueLabel>
            #              jmp r<temp>
            # NOTE: Imm needs to fit in 16-bit
            elif isinstance (asmArguments[0], ASM_AST.LiteralNode):
                returnReg = ASM_AST.PhysicalRegisterNode ("ra")
                tempReg = ASM_AST.VirtualTempRegisterNode ()
                functionEpilogueLabel = ASM_AST.LabelNode ("<function_epilogue_placeholder>")
                asmInstructions += [
                    ASM_AST.InstructionNode ("lli", [returnReg, asmArguments[0]]),
                    ASM_AST.InstructionNode ("loada", [tempReg, functionEpilogueLabel]),
                    ASM_AST.InstructionNode ("jmp", [tempReg])
                ]
            # Unknown arg
            else:
                print (f"Lowering error: unknown argument '{asmArguments[0]}' for 'return' instruction")
                exit (1)
        else:
            print (f"Lowering error: Unknown instruction '{commandName}'")
            self.wasSuccessful = False
        return asmInstructions

    # =============================================================================================

    def visitCallInstructionNode (self, node):
        astArguments = []
        for arg in node.arguments:
            astArguments += [arg.accept (self)]
        return [ASM_AST.CallInstructionNode (node.function_name, node.token, astArguments)]

    # =============================================================================================

    # writes any code it needs to
    # returns the parsed argument
    def visitArgumentExpressionNode (self, node):
        return node.expression.accept (self)

    # =============================================================================================

    # root node - should not be used
    def visitExpressionNode (self, node):
        pass

    # =============================================================================================

    def visitGlobalVariableExpressionNode (self, node):
        return ASM_AST.VirtualRegisterNode (node.id)

    # =============================================================================================

    def visitLocalVariableExpressionNode (self, node):
        return ASM_AST.VirtualRegisterNode (node.id)

    # =============================================================================================

    def visitBasicBlockExpressionNode (self, node):
        return ASM_AST.LabelNode (node.id)

    # =============================================================================================

    def visitIntLiteralExpressionNode (self, node):
        return ASM_AST.IntLiteralNode (node.value)

    # =============================================================================================

    def visitFloatLiteralExpressionNode (self, node):
        return ASM_AST.FloatLiteralNode (node.value)

    # =============================================================================================

    def visitCharLiteralExpressionNode (self, node):
        return ASM_AST.CharLiteralNode (node.value)

    # =============================================================================================

    def visitStringLiteralExpressionNode (self, node):
        return ASM_AST.StringLiteralNode (node.value)
