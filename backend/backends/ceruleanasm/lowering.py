# CeruleanIR Compiler - Lowering step
# 
# By Amy Burnett
# =================================================================================================

from sys import exit

from ...ceruleanIRAST import *
from ...visitor import ASTVisitor
from ...typeUtils import getTypeSize
from . import ceruleanASMAST as ASM_AST

# =================================================================================================

class LoweringVisitor (ASTVisitor):

    def __init__(self, shouldPrintDebug=False):
        self.shouldPrintDebug = shouldPrintDebug
        self.currentFunctionName = None  # Track current function for label scoping
        self.functionIndex = 0  # Global function counter for unique labels
        self.currentFunctionIndex = 0  # Index of current function
        self.blockIndex = 0  # Block counter within current function
        self.blockNameToIndex = {}  # Map block name -> index for current function

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
        externSymbols = []
        for codeunit in node.codeunits:
            if codeunit != None:
                # Check if this is an extern function before lowering
                if isinstance(codeunit, FunctionNode) and codeunit.isExtern:
                    # Strip @ prefix if present
                    funcName = codeunit.id[1:] if codeunit.id.startswith('@') else codeunit.id
                    externSymbols.append(funcName)
                    self.debugPrint(f"Found extern function: {funcName}")
                    continue  # Skip lowering extern functions
                newCodeunit = codeunit.accept (self)
                if newCodeunit:
                    codeunits += [newCodeunit]
        self.debugPrint(f"Total extern symbols: {externSymbols}")
        return ASM_AST.ProgramNode (codeunits, externSymbols)

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
        # Skip extern functions - they have no body to lower
        if node.isExtern:
            return None
        
        params = []
        # Collect parameter IDs before lowering
        paramIds = []
        for i in range(len(node.params)):
            param = node.params[i]
            if param is not None and hasattr(param, 'id'):
                paramIds.append(param.id)
            params += [param.accept(self) if param else None]
        # Strip @ prefix from function name if present
        funcId = node.id[1:] if node.id.startswith('@') else node.id
        # Track current function name and assign unique index for label scoping
        self.currentFunctionName = funcId
        self.currentFunctionIndex = self.functionIndex
        self.functionIndex += 1
        self.blockIndex = 0  # Reset block counter for new function
        
        # First pass: build block name -> index mapping
        self.blockNameToIndex = {}
        for basicBlock in node.basicBlocks:
            self.blockNameToIndex[basicBlock.name] = self.blockIndex
            self.blockIndex += 1
        
        # Second pass: lower instructions with proper label references
        self.blockIndex = 0  # Reset for actual lowering
        asmInstructions = []
        for basicBlock in node.basicBlocks:
            asmInstructions += basicBlock.accept (self)
        funcNode = ASM_AST.FunctionNode (funcId, node.token, params, asmInstructions)
        # Preserve scope name if it exists
        if hasattr(node, 'scopeName'):
            funcNode.scopeName = node.scopeName
        # Store parameter IDs for allocator
        funcNode.parameterIds = paramIds
        return funcNode

    # =============================================================================================

    def visitBasicBlockNode (self, node):
        asmInstructions = []

        for instruction in node.instructions:
            # Each instruction may expand to multiple asm instructions when lowered
            asmInstructions += instruction.accept (self)

        # Attach the basic block label to the first instruction
        # Format: functionName_blockName_fN_bM (guaranteed unique via indices)
        # e.g., println_entry_f0_b0, println_for_cond_f0_b1, main_entry_f1_b0
        if len(asmInstructions) > 0:
            scopedLabel = f"{self.currentFunctionName}_{node.name}_f{self.currentFunctionIndex}_b{self.blockIndex}"
            self.blockIndex += 1  # Increment for next block in this function
            self.debugPrint(f"Attaching label '{scopedLabel}' (was '{node.name}') to instruction: {asmInstructions[0].command if hasattr(asmInstructions[0], 'command') else type(asmInstructions[0]).__name__}")
            self.debugPrint(f"  Block has {len(asmInstructions)} instructions")
            asmInstructions[0].labels.append(scopedLabel)
        
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
            # Strategy: Create a pseudo-instruction with metadata
            # Frame lowering will calculate actual stack space and offsets
            # Code emission will replace this with address computation
            lhsReg = node.lhsVariable.accept (self)
            typeArg = node.arguments[0].accept (self)
            countNode = node.arguments[1]
            
            # Calculate size in bytes using centralized type utilities
            elementSize = getTypeSize(typeArg)
            
            # Get count value
            if hasattr(countNode, 'value'):
                count = countNode.value
            elif hasattr(countNode, 'expression') and hasattr(countNode.expression, 'value'):
                count = countNode.expression.value
            else:
                count = 1  # Fallback
            
            totalBytes = elementSize * count
            
            # Create pseudo-instruction with metadata
            asmInstruction = ASM_AST.InstructionNode("alloca", [lhsReg])
            asmInstruction.allocaSize = totalBytes  # Attach size metadata
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
            
            # Map type to load instruction
            typeToLoadOp = {
                "char": "load8",
                "int8": "load8",
                "int16": "load16",
                "int32": "load32",
                "int64": "load64",
                "float32": "load32",
                "float64": "load64",
                "ptr": "load64"
            }
            loadOp = typeToLoadOp.get(typeArg, "load64")  # Default to 64-bit
            
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
            # CeruleanIR: store(<pointer>, <offset>, <value>)
            # Stores <value> at memory location <pointer> + <offset>
            # Extract type from the value argument (3rd argument in IR)
            valueNode = node.arguments[2]
            valueType = None
            if hasattr(valueNode, 'type'):
                valueType = valueNode.type.id if hasattr(valueNode.type, 'id') else str(valueNode.type)
            
            # Map type to store instruction
            typeToStoreOp = {
                "char": "store8",
                "int8": "store8",
                "int16": "store16",
                "int32": "store32",
                "int64": "store64",
                "float32": "store32",
                "float64": "store64",
                "ptr": "store64"
            }
            storeOp = typeToStoreOp.get(valueType, "store64")  # Default to 64-bit
            
            # Usage 1: reg offset, reg value
            # CeruleanIR : store (<pointer>, <offset_reg>, <value>)
            # CeruleanASM: add64 r<temp>, r<ptr>, r<offset>
            #              store<size> r<temp>, r<value>, imm<0>
            if isinstance (asmArguments[1], ASM_AST.RegisterNode):
                self.debugPrint (f">>> lowering store(R,R,R) to add(R,R,R) and {storeOp}(R,R,I)")
                tempReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += [
                    ASM_AST.InstructionNode ("add64", [tempReg, asmArguments[0], asmArguments[1]]),
                    ASM_AST.InstructionNode (storeOp, [tempReg, asmArguments[2], ASM_AST.IntLiteralNode (0)])
                ]
            # Usage 2: imm offset, reg value
            # CeruleanIR : store (<pointer>, <offset_imm>, <value>)
            # CeruleanASM: store<size> r<ptr>, r<value>, imm<offset>
            elif isinstance (asmArguments[1], ASM_AST.LiteralNode):
                # Check if value is reg or imm
                if isinstance (asmArguments[2], ASM_AST.RegisterNode):
                    asmInstructions += [ASM_AST.InstructionNode (storeOp, [asmArguments[0], asmArguments[2], asmArguments[1]])]
                # Usage 3: imm offset, imm value
                # CeruleanIR : store (<pointer>, <offset_imm>, <imm_value>)
                # CeruleanASM: lli r<temp>, imm<value>
                #              store<size> r<ptr>, r<temp>, imm<offset>
                else:
                    tempReg = ASM_AST.VirtualTempRegisterNode()
                    asmInstructions += [
                        ASM_AST.InstructionNode ("lli", [tempReg, asmArguments[2]]),
                        ASM_AST.InstructionNode (storeOp, [asmArguments[0], tempReg, asmArguments[1]])
                    ]
            else:
                print (f"Lowering Error: Unexpected argument type for store offset: {asmArguments[1]}")
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
            # CeruleanIR: jmp (block(label))
            # Unconditional jump to a label
            # CeruleanASM: loada r<temp>, <label>
            #              jmp r<temp>
            tempReg = ASM_AST.VirtualTempRegisterNode()
            asmInstructions += [
                ASM_AST.InstructionNode("loada", [tempReg, asmArguments[0]]),
                ASM_AST.InstructionNode("jmp", [tempReg])
            ]
        elif commandName == "jcmp":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "jg":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "jge":
            # CeruleanIR: jge (int32(lhs), int32(rhs), block(label))
            # Jump to label if lhs >= rhs
            # CeruleanASM: loada r<temp>, <label>
            #              bge r<lhs>, r<rhs>, r<temp>
            tempReg = ASM_AST.VirtualTempRegisterNode()
            
            # Handle immediate operands - load into temp registers
            lhs = asmArguments[0]
            rhs = asmArguments[1]
            
            # If lhs is immediate, load into temp
            if isinstance(lhs, ASM_AST.LiteralNode):
                lhsReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += [ASM_AST.InstructionNode("lli", [lhsReg, lhs])]
                lhs = lhsReg
            
            # If rhs is immediate, load into temp
            if isinstance(rhs, ASM_AST.LiteralNode):
                rhsReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += [ASM_AST.InstructionNode("lli", [rhsReg, rhs])]
                rhs = rhsReg
            
            asmInstructions += [
                ASM_AST.InstructionNode("loada", [tempReg, asmArguments[2]]),
                ASM_AST.InstructionNode("bge", [lhs, rhs, tempReg])
            ]
        elif commandName == "jl":
            print (f"Lowering ERROR: {commandName} not implemented")
            exit (1)
        elif commandName == "jle":
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
        # Look up the block index from pre-built mapping
        blockIdx = self.blockNameToIndex.get(node.id, 0)
        # Scope label to current function with unique suffix
        # Format: functionName_blockName_fN_bM
        scopedLabel = f"{self.currentFunctionName}_{node.id}_f{self.currentFunctionIndex}_b{blockIdx}"
        return ASM_AST.LabelNode (scopedLabel)

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
