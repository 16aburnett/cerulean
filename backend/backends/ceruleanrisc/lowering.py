# CeruleanIR Compiler - Lowering step
# 
# By Amy Burnett
# =================================================================================================

from sys import exit

from ...ceruleanIRAST import *
from ...visitor import ASTVisitor
from ...typeUtils import getTypeSize
from . import ceruleanVirtualRISCAST as ASM_AST

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
    
    def emitLoadImmediate64(self, destReg, value):
        """
        Generate instructions to load a 64-bit immediate value into a register.
        
        Since lli/lui only modify 16 bits at a time, we need to generate
        a full sequence to properly initialize the entire register:
        1. lui - load upper 16 bits (bits 48-63)
        2. lli - load next 16 bits (bits 32-47)
        3. sll64i - shift left 16 bits
        4. lli - load next 16 bits (bits 16-31)
        5. sll64i - shift left 16 bits  
        6. lli - load lower 16 bits (bits 0-15)
        
        Args:
            destReg: The destination register (AST node)
            value: The integer value to load (or IntLiteralNode/CharLiteralNode)
            
        Returns:
            List of instruction nodes
        """
        # For character literals, zero out register then load character
        if isinstance(value, ASM_AST.CharLiteralNode):
            # XOR register with itself to zero it, then load the char into lower bits
            return [
                ASM_AST.InstructionNode("xor64", [destReg, destReg, destReg]),  # Zero out register
                ASM_AST.InstructionNode("lli", [destReg, value])  # Load char literal
            ]
        
        # Extract the integer value if it's wrapped in a node
        if isinstance(value, ASM_AST.IntLiteralNode):
            val = value.value
        else:
            val = value
        
        # Split 64-bit value into 4 x 16-bit chunks
        # Handle negative numbers with two's complement
        val = val & 0xFFFFFFFFFFFFFFFF  # Ensure 64-bit value
        
        lo = val & 0xFFFF
        ml = (val >> 16) & 0xFFFF
        mh = (val >> 32) & 0xFFFF
        hi = (val >> 48) & 0xFFFF
        
        return [
            ASM_AST.InstructionNode("lui", [destReg, ASM_AST.IntLiteralNode(hi)]),
            ASM_AST.InstructionNode("lli", [destReg, ASM_AST.IntLiteralNode(mh)]),
            ASM_AST.InstructionNode("sll64i", [destReg, destReg, ASM_AST.IntLiteralNode(16)]),
            ASM_AST.InstructionNode("lli", [destReg, ASM_AST.IntLiteralNode(ml)]),
            ASM_AST.InstructionNode("sll64i", [destReg, destReg, ASM_AST.IntLiteralNode(16)]),
            ASM_AST.InstructionNode("lli", [destReg, ASM_AST.IntLiteralNode(lo)])
        ]

    # === VISITOR FUNCTIONS =======================================================================

    def visitProgramNode (self, node):
        codeunits = []
        externSymbols = []
        globalVars = []  # Track global variable declarations
        
        self.debugPrint(f"Processing program with {len(node.codeunits)} codeunits")
        
        for codeunit in node.codeunits:
            if codeunit != None:
                self.debugPrint(f"  Codeunit type: {type(codeunit).__name__}, id: {getattr(codeunit, 'id', 'N/A')}")
                
                # Check if this is a global variable declaration
                if isinstance(codeunit, GlobalVariableDeclarationNode):
                    globalVar = codeunit.accept(self)
                    if globalVar:
                        globalVars.append(globalVar)
                    self.debugPrint(f"Found global variable: {codeunit.id}")
                # Check if this is an extern function before lowering
                elif isinstance(codeunit, FunctionNode) and codeunit.isExtern:
                    # Strip @ prefix if present
                    funcName = codeunit.id[1:] if codeunit.id.startswith('@') else codeunit.id
                    externSymbols.append(funcName)
                    self.debugPrint(f"Found extern function: {funcName}")
                    # Skip lowering extern functions
                else:
                    newCodeunit = codeunit.accept (self)
                    if newCodeunit:
                        codeunits += [newCodeunit]
        
        self.debugPrint(f"Total extern symbols: {externSymbols}")
        self.debugPrint(f"Total global variables: {len(globalVars)}")
        return ASM_AST.ProgramNode (codeunits, externSymbols, globalVars)

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
        # Global variables go in the data section, not as virtual registers
        # Structure: global @name = command (type(value))
        # Example: global @length = value (int32(14))
        # Example: global @greeting = value (ptr("Hello"))
        
        # Strip @ prefix from global variable name if present
        globalId = node.id[1:] if node.id.startswith('@') else node.id
        # Sanitize label name - replace periods and other invalid characters with underscores
        globalId = globalId.replace('.', '_')
        
        # Extract type from the first argument (if available)
        typeStr = "int64"  # default
        initialValueNode = None  # Will be AST node (literal or string)
        
        if hasattr(node, 'arguments') and len(node.arguments) > 0:
            arg = node.arguments[0]
            
            # Get type from argument
            if hasattr(arg, 'type') and arg.type:
                typeStr = arg.type.accept(self) if hasattr(arg.type, 'accept') else str(arg.type)
            
            # Get initial value from argument expression
            # We need to lower it to get the proper ASM node
            if hasattr(arg, 'expression') and arg.expression:
                initialValueNode = arg.expression.accept(self)
        
        # Get size in bytes
        size = getTypeSize(typeStr)
        
        # Create global variable node for data section
        # Emitter will place this in the data section with appropriate directive
        # initialValueNode can be IntLiteralNode, StringLiteralNode, etc.
        self.debugPrint(f"Creating global variable '{globalId}' of type '{typeStr}' (size={size} bytes)")
        globalVar = ASM_AST.GlobalVariableNode(globalId, size=size, initialValue=initialValueNode)
        return globalVar

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
            # CeruleanRISC: add <dest>, <src0>, <src1>
            if isinstance (asmArguments[1], ASM_AST.RegisterNode):
                asmInstruction = ASM_AST.InstructionNode ("add64", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
            # Usage 2: Reg, Imm
            # CeruleanIR : <dest> = add (<src0>, <imm>)
            # CeruleanRISC: addi <dest>, <src0>, <imm>
            else: # assuming imm is the only other option
                asmInstruction = ASM_AST.InstructionNode ("add64i", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
        elif commandName == "sub":
            lhsReg = node.lhsVariable.accept (self)
            # Usage 1: Reg, Reg
            # CeruleanIR : <dest> = sub (<src0>, <src1>)
            # CeruleanRISC: sub <dest>, <src0>, <src1>
            if isinstance (asmArguments[1], ASM_AST.RegisterNode):
                asmInstruction = ASM_AST.InstructionNode ("sub64", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
            # Usage 2: Reg, Imm
            # CeruleanIR : <dest> = sub (<src0>, <imm>)
            # CeruleanRISC: subi <dest>, <src0>, <imm>
            else: # assuming imm is the only other option
                asmInstruction = ASM_AST.InstructionNode ("sub64i", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
        elif commandName == "mul":
            lhsReg = node.lhsVariable.accept (self)
            # Usage 1: Reg, Reg
            # CeruleanIR : <dest> = mul (<src0>, <src1>)
            # CeruleanRISC: mul<size> <dest>, <src0>, <src1>
            if isinstance (asmArguments[1], ASM_AST.RegisterNode):
                asmInstruction = ASM_AST.InstructionNode ("mul64", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
            # Usage 2: Reg, Imm
            # CeruleanIR : <dest> = mul (<src0>, <imm>)
            # CeruleanRISC: mul<size>i <dest>, <src0>, <imm>
            else: # assuming imm is the only other option
                asmInstruction = ASM_AST.InstructionNode ("mul64i", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
        elif commandName == "div":
            lhsReg = node.lhsVariable.accept (self)
            # Usage 1: Reg, Reg
            # CeruleanIR : <dest> = div (<src0>, <src1>)
            # CeruleanRISC: divi<size> <dest>, <src0>, <src1>
            # NOTE: Currently only using ints
            if isinstance (asmArguments[1], ASM_AST.RegisterNode):
                asmInstruction = ASM_AST.InstructionNode ("divi64", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
            # Usage 2: Reg, Imm
            # CeruleanIR : <dest> = div (<src0>, <imm>)
            # CeruleanRISC: divi<size>i <dest>, <src0>, <imm>
            # NOTE: Currently only using ints
            else: # assuming imm is the only other option
                asmInstruction = ASM_AST.InstructionNode ("divi64i", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
        elif commandName == "mod":
            lhsReg = node.lhsVariable.accept (self)
            # Usage 1: Reg, Reg
            # CeruleanIR : <dest> = mod (<src0>, <src1>)
            # CeruleanRISC: modi<size> <dest>, <src0>, <src1>
            # NOTE: Currently only using ints
            if isinstance (asmArguments[1], ASM_AST.RegisterNode):
                asmInstruction = ASM_AST.InstructionNode ("divi64", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
            # Usage 2: Reg, Imm
            # CeruleanIR : <dest> = mod (<src0>, <imm>)
            # CeruleanRISC: modi<size>i <dest>, <src0>, <imm>
            # NOTE: Currently only using ints
            else: # assuming imm is the only other option
                asmInstruction = ASM_AST.InstructionNode ("modi64i", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
        elif commandName == "lnot":
            lhsReg = node.lhsVariable.accept (self)
            # Usage 1: Reg
            # CeruleanIR : <dest> = lnot (<src0>)
            # CeruleanRISC: not64 <dest>, <src0>
            asmInstruction = ASM_AST.InstructionNode ("not64", [lhsReg, *asmArguments])
            asmInstructions += [asmInstruction]
        elif commandName == "value":
            lhsReg = node.lhsVariable.accept (self)
            # Usage 1: Reg
            # CeruleanIR : <dest> = value (<arg0>)
            # CeruleanRISC: mv64 <dest>, <arg0>
            if isinstance (asmArguments[0], ASM_AST.RegisterNode):
                asmInstruction = ASM_AST.InstructionNode ("mv64", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
            # Usage 2: Global Variable or String Literal (needs loada for address)
            # CeruleanIR : <dest> = value (global_var) OR <dest> = value (ptr("string"))
            # CeruleanRISC: loada <dest>, <label>
            # Both global variables and string literals are represented as LabelNode or StringLiteralNode
            elif isinstance (asmArguments[0], ASM_AST.LabelNode):
                # Global variable reference - load its address
                asmInstruction = ASM_AST.InstructionNode ("loada", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
            elif isinstance (asmArguments[0], ASM_AST.StringLiteralNode):
                # String literals are handled by the emitter (creates data section)
                # For now, keep the string literal and let emitter handle it
                # But we need loada instead of lli
                asmInstruction = ASM_AST.InstructionNode ("loada", [lhsReg, *asmArguments])
                asmInstructions += [asmInstruction]
            # Usage 3: Imm
            # CeruleanIR : <dest> = value (<imm>)
            # CeruleanRISC: Full 64-bit load sequence
            else: # assuming imm is the only other option
                asmInstructions += self.emitLoadImmediate64(lhsReg, asmArguments[0])
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
            
            # Handle case where base address is a label (global variable)
            # Need to load address into a register first
            baseReg = asmArguments[1]
            if isinstance (baseReg, ASM_AST.LabelNode):
                # CeruleanIR : <dest> = load (<type>, <global_label>, <offset>)
                # CeruleanRISC: loada r<temp>, <global_label>
                #              load<size> r<dest>, r<temp>, imm<offset>
                tempReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += [ASM_AST.InstructionNode ("loada", [tempReg, baseReg])]
                baseReg = tempReg
            
            # Usage 1: reg offset
            # CeruleanIR : <dest> = load (<type>, <pointer>, <offset>)
            # CeruleanRISC: add64 r<temp>, r<ptr>, r<offset>
            #              load<size> r<dest>, r<temp>, imm<offset>
            if isinstance (asmArguments[2], ASM_AST.RegisterNode):
                self.debugPrint (f">>> lowering load(R,R) to add(R,R,R) and {loadOp}(R,R,I)")
                tempReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += [
                    ASM_AST.InstructionNode ("add64", [tempReg, baseReg, asmArguments[2]]),
                    ASM_AST.InstructionNode (loadOp, [lhsReg, tempReg, ASM_AST.IntLiteralNode (0)])
                ]
            # Usage 2: imm offset
            # CeruleanIR : <dest> = load (<type>, <pointer>, <offset>)
            # CeruleanRISC: load<size> r<dest>, r<ptr>, imm<offset>
            elif isinstance (asmArguments[2], ASM_AST.LiteralNode):
                asmInstructions += [ASM_AST.InstructionNode (loadOp, [lhsReg, baseReg, asmArguments[2]])]
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
            
            # Handle case where base address is a label (global variable)
            # Need to load address into a register first
            baseReg = asmArguments[0]
            if isinstance (baseReg, ASM_AST.LabelNode):
                # CeruleanIR : store (<global_label>, <offset>, <value>)
                # CeruleanRISC: loada r<temp>, <global_label>
                #              store<size> r<temp>, r<value>, imm<offset>
                tempReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += [ASM_AST.InstructionNode ("loada", [tempReg, baseReg])]
                baseReg = tempReg
            
            # Usage 1: reg offset, reg value
            # CeruleanIR : store (<pointer>, <offset_reg>, <value>)
            # CeruleanRISC: add64 r<temp>, r<ptr>, r<offset>
            #              store<size> r<temp>, r<value>, imm<0>
            if isinstance (asmArguments[1], ASM_AST.RegisterNode):
                self.debugPrint (f">>> lowering store(R,R,R) to add(R,R,R) and {storeOp}(R,R,I)")
                tempReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += [
                    ASM_AST.InstructionNode ("add64", [tempReg, baseReg, asmArguments[1]]),
                    ASM_AST.InstructionNode (storeOp, [tempReg, asmArguments[2], ASM_AST.IntLiteralNode (0)])
                ]
            # Usage 2: imm offset, reg value
            # CeruleanIR : store (<pointer>, <offset_imm>, <value>)
            # CeruleanRISC: store<size> r<ptr>, r<value>, imm<offset>
            elif isinstance (asmArguments[1], ASM_AST.LiteralNode):
                # Check if value is reg or imm
                if isinstance (asmArguments[2], ASM_AST.RegisterNode):
                    asmInstructions += [ASM_AST.InstructionNode (storeOp, [baseReg, asmArguments[2], asmArguments[1]])]
                # Usage 3: imm offset, imm value
                # CeruleanIR : store (<pointer>, <offset_imm>, <imm_value>)
                # CeruleanRISC: Full 64-bit load sequence to temp register
                #              store<size> r<ptr>, r<temp>, imm<offset>
                else:
                    tempReg = ASM_AST.VirtualTempRegisterNode()
                    asmInstructions += self.emitLoadImmediate64(tempReg, asmArguments[2])
                    asmInstructions += [
                        ASM_AST.InstructionNode (storeOp, [baseReg, tempReg, asmArguments[1]])
                    ]
            else:
                print (f"Lowering Error: Unexpected argument type for store offset: {asmArguments[1]}")
                exit (1)
        elif commandName == "clt":
            # CeruleanIR: <dest> = clt(<a>, <b>)
            # Returns 1 if a < b, 0 otherwise (signed)
            # CeruleanRISC: lt <dest>, <a>, <b>
            lhsReg = node.lhsVariable.accept(self)
            a = asmArguments[0]
            b = asmArguments[1]
            if isinstance(a, ASM_AST.LiteralNode):
                tempA = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(tempA, a)
                a = tempA
            if isinstance(b, ASM_AST.LiteralNode):
                tempB = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(tempB, b)
                b = tempB
            asmInstructions += [ASM_AST.InstructionNode("lt", [lhsReg, a, b])]
        elif commandName == "cle":
            # CeruleanIR: <dest> = cle(<a>, <b>)
            # Returns 1 if a <= b, 0 otherwise (signed)
            # Strategy: a <= b is !(a > b) = !(b < a)
            # CeruleanRISC: lt <dest>, <b>, <a>
            #              xor64i <dest>, <dest>, 1
            lhsReg = node.lhsVariable.accept(self)
            a = asmArguments[0]
            b = asmArguments[1]
            if isinstance(a, ASM_AST.LiteralNode):
                tempA = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(tempA, a)
                a = tempA
            if isinstance(b, ASM_AST.LiteralNode):
                tempB = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(tempB, b)
                b = tempB
            asmInstructions += [
                ASM_AST.InstructionNode("lt", [lhsReg, b, a]),
                ASM_AST.InstructionNode("xor64i", [lhsReg, lhsReg, ASM_AST.IntLiteralNode(1)])
            ]
        elif commandName == "cgt":
            # CeruleanIR: <dest> = cgt(<a>, <b>)
            # Returns 1 if a > b, 0 otherwise (signed)
            # Strategy: a > b is b < a (swap operands)
            # CeruleanRISC: lt <dest>, <b>, <a>
            lhsReg = node.lhsVariable.accept(self)
            a = asmArguments[0]
            b = asmArguments[1]
            if isinstance(a, ASM_AST.LiteralNode):
                tempA = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(tempA, a)
                a = tempA
            if isinstance(b, ASM_AST.LiteralNode):
                tempB = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(tempB, b)
                b = tempB
            asmInstructions += [ASM_AST.InstructionNode("lt", [lhsReg, b, a])]
        elif commandName == "cge":
            # CeruleanIR: <dest> = cge(<a>, <b>)
            # Returns 1 if a >= b, 0 otherwise (signed)
            # Strategy: a >= b is !(a < b)
            # CeruleanRISC: lt <dest>, <a>, <b>
            #              xor64i <dest>, <dest>, 1
            lhsReg = node.lhsVariable.accept(self)
            a = asmArguments[0]
            b = asmArguments[1]
            if isinstance(a, ASM_AST.LiteralNode):
                tempA = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(tempA, a)
                a = tempA
            if isinstance(b, ASM_AST.LiteralNode):
                tempB = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(tempB, b)
                b = tempB
            asmInstructions += [
                ASM_AST.InstructionNode("lt", [lhsReg, a, b]),
                ASM_AST.InstructionNode("xor64i", [lhsReg, lhsReg, ASM_AST.IntLiteralNode(1)])
            ]
        elif commandName == "ceq":
            # CeruleanIR: <dest> = ceq(<a>, <b>)
            # Returns 1 if a == b, 0 otherwise
            # CeruleanRISC: eq <dest>, <a>, <b>
            lhsReg = node.lhsVariable.accept(self)
            a = asmArguments[0]
            b = asmArguments[1]
            if isinstance(a, ASM_AST.LiteralNode):
                tempA = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(tempA, a)
                a = tempA
            if isinstance(b, ASM_AST.LiteralNode):
                tempB = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(tempB, b)
                b = tempB
            asmInstructions += [ASM_AST.InstructionNode("eq", [lhsReg, a, b])]
        elif commandName == "cne":
            # CeruleanIR: <dest> = cne(<a>, <b>)
            # Returns 1 if a != b, 0 otherwise
            # Strategy: a != b is equivalent to !(a == b)
            # CeruleanRISC: eq <dest>, <a>, <b>
            #              xor64i <dest>, <dest>, 1
            lhsReg = node.lhsVariable.accept(self)
            a = asmArguments[0]
            b = asmArguments[1]
            if isinstance(a, ASM_AST.LiteralNode):
                tempA = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(tempA, a)
                a = tempA
            if isinstance(b, ASM_AST.LiteralNode):
                tempB = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(tempB, b)
                b = tempB
            asmInstructions += [
                ASM_AST.InstructionNode("eq", [lhsReg, a, b]),
                ASM_AST.InstructionNode("xor64i", [lhsReg, lhsReg, ASM_AST.IntLiteralNode(1)])
            ]
        elif commandName == "jmp":
            # CeruleanIR: jmp (block(label))
            # Unconditional jump to a label
            # CeruleanRISC: loada r<temp>, <label>
            #              jmp r<temp>
            tempReg = ASM_AST.VirtualTempRegisterNode()
            asmInstructions += [
                ASM_AST.InstructionNode("loada", [tempReg, asmArguments[0]]),
                ASM_AST.InstructionNode("jmp", [tempReg])
            ]
        elif commandName == "jcmp":
            # CeruleanIR: jcmp(<cond>, block(label_true), block(label_false))
            # Jump to label_true if cond is non-zero, otherwise jump to label_false
            # CeruleanRISC: lli r<tempZero>, 0
            #              loada r<tempFalse>, <label_false>
            #              beq r<cond>, r<tempZero>, r<tempFalse>  // if cond == 0, jump to false
            #              loada r<tempTrue>, <label_true>
            #              jmp r<tempTrue>                          // otherwise jump to true
            tempZero = ASM_AST.VirtualTempRegisterNode()
            tempFalse = ASM_AST.VirtualTempRegisterNode()
            tempTrue = ASM_AST.VirtualTempRegisterNode()
            cond = asmArguments[0]
            labelTrue = asmArguments[1]
            labelFalse = asmArguments[2]
            
            # Handle immediate condition
            if isinstance(cond, ASM_AST.LiteralNode):
                condReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(condReg, cond)
                cond = condReg
            
            asmInstructions += self.emitLoadImmediate64(tempZero, 0)
            asmInstructions += [
                ASM_AST.InstructionNode("loada", [tempFalse, labelFalse]),
                ASM_AST.InstructionNode("beq", [cond, tempZero, tempFalse]),
                ASM_AST.InstructionNode("loada", [tempTrue, labelTrue]),
                ASM_AST.InstructionNode("jmp", [tempTrue])
            ]
        elif commandName == "jg":
            # CeruleanIR: jg(<a>, <b>, block(label))
            # Jump to label if a > b (signed)
            # Strategy: a > b is b < a (swap operands for BLT)
            # CeruleanRISC: loada r<temp>, <label>
            #              blt r<b>, r<a>, r<temp>
            tempReg = ASM_AST.VirtualTempRegisterNode()
            a = asmArguments[0]
            b = asmArguments[1]
            if isinstance(a, ASM_AST.LiteralNode):
                aReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(aReg, a)
                a = aReg
            if isinstance(b, ASM_AST.LiteralNode):
                bReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(bReg, b)
                b = bReg
            asmInstructions += [
                ASM_AST.InstructionNode("loada", [tempReg, asmArguments[2]]),
                ASM_AST.InstructionNode("blt", [b, a, tempReg])
            ]
        elif commandName == "jge":
            # CeruleanIR: jge (int32(lhs), int32(rhs), block(label))
            # Jump to label if lhs >= rhs
            # CeruleanRISC: loada r<temp>, <label>
            #              bge r<lhs>, r<rhs>, r<temp>
            tempReg = ASM_AST.VirtualTempRegisterNode()
            
            # Handle immediate operands - load into temp registers
            lhs = asmArguments[0]
            rhs = asmArguments[1]
            
            # If lhs is immediate, load into temp
            if isinstance(lhs, ASM_AST.LiteralNode):
                lhsReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(lhsReg, lhs)
                lhs = lhsReg
            
            # If rhs is immediate, load into temp
            if isinstance(rhs, ASM_AST.LiteralNode):
                rhsReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(rhsReg, rhs)
                rhs = rhsReg
            
            asmInstructions += [
                ASM_AST.InstructionNode("loada", [tempReg, asmArguments[2]]),
                ASM_AST.InstructionNode("bge", [lhs, rhs, tempReg])
            ]
        elif commandName == "jl":
            # CeruleanIR: jl(<a>, <b>, block(label))
            # Jump to label if a < b (signed)
            # CeruleanRISC: loada r<temp>, <label>
            #              blt r<a>, r<b>, r<temp>
            tempReg = ASM_AST.VirtualTempRegisterNode()
            a = asmArguments[0]
            b = asmArguments[1]
            # Handle immediate operands
            if isinstance(a, ASM_AST.LiteralNode):
                aReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(aReg, a)
                a = aReg
            if isinstance(b, ASM_AST.LiteralNode):
                bReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(bReg, b)
                b = bReg
            asmInstructions += [
                ASM_AST.InstructionNode("loada", [tempReg, asmArguments[2]]),
                ASM_AST.InstructionNode("blt", [a, b, tempReg])
            ]
        elif commandName == "jle":
            # CeruleanIR: jle(<a>, <b>, block(label))
            # Jump to label if a <= b (signed)
            # Strategy: a <= b is b >= a (swap operands for BGE)
            # CeruleanRISC: loada r<temp>, <label>
            #              bge r<b>, r<a>, r<temp>
            tempReg = ASM_AST.VirtualTempRegisterNode()
            a = asmArguments[0]
            b = asmArguments[1]
            if isinstance(a, ASM_AST.LiteralNode):
                aReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(aReg, a)
                a = aReg
            if isinstance(b, ASM_AST.LiteralNode):
                bReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(bReg, b)
                b = bReg
            asmInstructions += [
                ASM_AST.InstructionNode("loada", [tempReg, asmArguments[2]]),
                ASM_AST.InstructionNode("bge", [b, a, tempReg])
            ]
        elif commandName == "jne":
            # CeruleanIR: jne(<a>, <b>, block(label))
            # Jump to label if a != b
            # CeruleanRISC: loada r<temp>, <label>
            #              bne r<a>, r<b>, r<temp>
            tempReg = ASM_AST.VirtualTempRegisterNode()
            a = asmArguments[0]
            b = asmArguments[1]
            # Handle immediate operands
            if isinstance(a, ASM_AST.LiteralNode):
                aReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(aReg, a)
                a = aReg
            if isinstance(b, ASM_AST.LiteralNode):
                bReg = ASM_AST.VirtualTempRegisterNode()
                asmInstructions += self.emitLoadImmediate64(bReg, b)
                b = bReg
            asmInstructions += [
                ASM_AST.InstructionNode("loada", [tempReg, asmArguments[2]]),
                ASM_AST.InstructionNode("bne", [a, b, tempReg])
            ]
        elif commandName == "return":
            # Usage 1: no return value
            # CeruleanIR : return ()
            # CeruleanRISC: loada r<temp> <functionEpilogueLabel>
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
            # CeruleanRISC: mv64 ra, r<src>
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
            # CeruleanRISC: load immediate into ra
            #              loada r<temp> <functionEpilogueLabel>
            #              jmp r<temp>
            elif isinstance (asmArguments[0], ASM_AST.LiteralNode):
                returnReg = ASM_AST.PhysicalRegisterNode ("ra")
                tempReg = ASM_AST.VirtualTempRegisterNode ()
                functionEpilogueLabel = ASM_AST.LabelNode ("<function_epilogue_placeholder>")
                asmInstructions += self.emitLoadImmediate64(returnReg, asmArguments[0])
                asmInstructions += [
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
        # Global variables are accessed via their label (address in data section)
        # Return a label node so it works with loada instruction
        # This is similar to how string literals work
        # Strip @ prefix from global variable name if present
        globalId = node.id[1:] if node.id.startswith('@') else node.id
        # Sanitize label name - replace periods and other invalid characters with underscores
        globalId = globalId.replace('.', '_')
        return ASM_AST.LabelNode (globalId)

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
