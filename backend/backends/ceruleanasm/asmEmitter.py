# CeruleanIR Compiler - ASM Code Emitter
# By Amy Burnett
# =================================================================================================
# Final pass: Converts the Virtual CeruleanASM AST (with register allocation and frame info)
# into textual assembly code.
# =================================================================================================

import os

from . import ceruleanASMAST as ASM_AST
from .ceruleanASMASTVisitor import ASMASTVisitor

# =================================================================================================

LIB_FILENAME = os.path.dirname(__file__) + "/CeruleanIR_BuiltinLib.ceruleanasm"

# =================================================================================================

class ASMEmitter:
    """
    Emits textual assembly code from the Virtual CeruleanASM AST.
    Uses register allocation and frame information computed by previous passes.
    """
    
    def __init__(self, shouldPrintDebug=False):
        self.shouldPrintDebug = shouldPrintDebug
        self.code = []
        self.dataSection = []
        self.nextStringIndex = 0
        
    def emit(self, finalASM):
        """
        Emit assembly code from the final ASM AST.
        
        Args:
            finalASM: Virtual CeruleanASM AST with register allocation and frame info
            
        Returns:
            String containing the complete assembly code
        """
        self.debugPrint("Emitting assembly code...")
        
        visitor = EmitterVisitor(self)
        visitor.visit(finalASM)
        
        # Combine code and data sections
        codeSection = "".join(self.code)
        dataSectionHeader = "\n// data section\n"
        dataSection = "".join(self.dataSection)
        
        return codeSection + dataSectionHeader + dataSection
    
    def debugPrint(self, *args, **kwargs):
        if self.shouldPrintDebug:
            print("[debug] [asm-emitter]", *args, **kwargs)

# =================================================================================================

class EmitterVisitor(ASMASTVisitor):
    """
    Visitor that traverses the ASM AST and generates text.
    """
    
    def __init__(self, emitter):
        self.emitter = emitter
        self.indentation = 0
        self.currentFunction = None
        
    def visit(self, node):
        """Entry point for visiting the AST."""
        return node.accept(self)
    
    # === HELPER FUNCTIONS =======================================================================
    
    def emit(self, text):
        """Emit text to the code section."""
        self.emitter.code.append(text)
    
    def emitLine(self, line):
        """Emit a line of code with proper indentation."""
        self.emitIndent()
        self.emit(f"{line}\n")
    
    def emitIndent(self):
        """Emit indentation spaces."""
        self.emit("   " * self.indentation)
    
    def emitLabel(self, label):
        """Emit a label (no indentation)."""
        self.emit(f"{label}:\n")
    
    def emitComment(self, comment):
        """Emit a comment."""
        self.emitIndent()
        self.emit(f"// {comment}\n")
    
    def emitData(self, directive, label=None):
        """Emit a data directive."""
        if label:
            self.emitter.dataSection.append(f"{label}:\n")
        self.emitter.dataSection.append(f"   {directive}\n")
    
    def getNewStringLabel(self):
        """Get a new unique string label."""
        label = f"str_{self.emitter.nextStringIndex}"
        self.emitter.nextStringIndex += 1
        return label
    
    # === VISITOR METHODS ========================================================================
    
    def visitProgramNode(self, node):
        """Visit the program node - emit all functions."""
        self.emitComment("CeruleanASM code compiled from CeruleanIR")
        self.emit("// " + "=" * 75 + "\n\n")
        
        # Add built-in library
        self.emit("// " + "=" * 75 + "\n")
        self.emit("//### BUILT-IN LIBRARY CODE " + "#" * 46 + "\n")
        self.emit("// " + "=" * 75 + "\n\n")
        
        try:
            with open(LIB_FILENAME, "r") as file:
                for line in file.readlines():
                    self.emit(line)
        except FileNotFoundError:
            self.emitComment(f"Warning: Could not find library file: {LIB_FILENAME}")
        
        self.emit("\n// " + "=" * 75 + "\n")
        self.emit("//### COMPILED CODE " + "#" * 55 + "\n")
        self.emit("// " + "=" * 75 + "\n\n")
        
        # Emit each function
        for codeunit in node.codeunits:
            if isinstance(codeunit, ASM_AST.FunctionNode):
                self.visit(codeunit)
        
        self.emit("\n// " + "=" * 75 + "\n")
        self.emit("//### END OF CODE " + "#" * 57 + "\n")
        self.emit("// " + "=" * 75 + "\n\n")
        
        # Emit startup code
        self.emitLabel("__start")
        self.indentation += 1
        self.emitComment("Start with main function")
        # Look for main function - should be the last one compiled
        mainFuncLabel = "main"  # default
        for codeunit in node.codeunits:
            if isinstance(codeunit, ASM_AST.FunctionNode):
                if codeunit.id == "main":
                    mainFuncLabel = "main"
                    break
        self.emitLine(f"loada r0, {mainFuncLabel}")
        self.emitLine("call r0")
        self.emitLine("halt")
        self.indentation -= 1
        self.emit("\n")
    
    def visitFunctionNode(self, node):
        """Visit a function node - emit function code."""
        self.currentFunction = node
        
        # Get register allocation info from the node (set by register allocator)
        registerAllocation = getattr(node, 'registerAllocation', {})
        spillSlots = getattr(node, 'spillSlots', {})
        stackFrameSize = getattr(node, 'stackFrameSize', 0)
        
        self.emitter.debugPrint(f"Emitting function: {node.id}")
        self.emitter.debugPrint(f"  Stack frame: {stackFrameSize} bytes")
        self.emitter.debugPrint(f"  Allocations: {len(registerAllocation)} variables")
        
        # Function header
        self.emit("// " + "-" * 75 + "\n")
        self.emitComment(f"Function: {node.id}")
        
        # Emit stack frame layout comments
        if registerAllocation:
            self.emitComment("Stack layout:")
            # Separate parameters and locals
            params = []
            locals = []
            for var, allocation in sorted(registerAllocation.items()):
                kind = allocation.get('kind')
                offset = allocation.get('value')
                if kind == 'param':
                    params.append((var, offset))
                elif kind == 'spill':
                    locals.append((var, offset))
            
            # Sort and emit parameters (positive offsets, descending order)
            for var, offset in sorted(params, key=lambda x: x[1], reverse=True):
                self.emitComment(f"  [bp + {offset}]: {var}")
            
            # Emit fixed stack slots
            self.emitComment(f"  [bp + 8]: return address")
            self.emitComment(f"  [bp + 0]: saved bp")
            
            # Sort and emit locals (negative offsets)
            for var, offset in sorted(locals, key=lambda x: x[1]):
                self.emitComment(f"  [bp - {offset}]: {var}")
        
        self.emitLabel(node.id)
        
        self.indentation += 1
        
        # Function prologue
        self.emitComment("Prologue: Setup stack frame")
        self.emitLine("push bp")
        self.emitLine("mv64 bp, sp")
        if stackFrameSize > 0:
            self.emitLine(f"sub64i sp, sp, {stackFrameSize} // allocate {stackFrameSize} bytes")
        
        # Emit instructions
        self.emitComment("Function body")
        for instr in node.instructions:
            self.visit(instr)
        
        # Function epilogue
        epilogueLabel = f"__epilogue__{node.id}"
        self.emitComment("Epilogue")
        self.emitLabel(epilogueLabel)
        self.emitLine("mv64 sp, bp // restore stack pointer")
        self.emitLine("pop bp")
        self.emitLine("ret")
        
        self.indentation -= 1
        
        # End label
        self.emitLabel(f"__end__{node.id}")
        self.emit("\n")
        
        self.currentFunction = None
    
    def visitInstructionNode(self, node):
        """Visit an instruction node - emit the instruction with proper spill handling."""
        # Emit any labels attached to this instruction
        if hasattr(node, 'labels') and node.labels:
            for label in node.labels:
                self.emitLabel(label)
        
        # Check for special handling of certain instructions
        command = node.command
        
        # Handle alloca pseudo-instruction
        if command == "alloca":
            # Replace with stack address computation
            # Get the destination register
            if node.arguments and len(node.arguments) > 0:
                destOperand = node.arguments[0]
                
                # Get the offset from function's alloca map
                if self.currentFunction and hasattr(self.currentFunction, 'allocaOffsets'):
                    allocaOffsets = self.currentFunction.allocaOffsets
                    regName = destOperand.id if hasattr(destOperand, 'id') else str(destOperand)
                    
                    if regName in allocaOffsets:
                        offset = allocaOffsets[regName]
                        # Compute address into scratch register
                        self.emitLine(f"mv64 r8, bp // alloca: compute stack address")
                        if offset > 0:
                            self.emitLine(f"sub64i r8, r8, {offset}")
                        # Store result to destination (may be spilled)
                        self._emitStore(destOperand, "r8")
                        return
            # Fallback if we couldn't find the offset
            self.emitComment("Warning: alloca offset not found")
            return
        
        # Handle return statements with epilogue jump
        if command == "return" or (command == "jmp" and len(node.arguments) > 0):
            # Check if this is a jump to function epilogue placeholder
            if len(node.arguments) > 0:
                arg = node.arguments[0]
                if isinstance(arg, ASM_AST.LabelNode) and "epilogue" in str(arg.id).lower():
                    # Replace with actual epilogue label
                    if self.currentFunction:
                        epilogueLabel = f"__epilogue__{self.currentFunction.id}"
                        self.emitLine(f"loada r8, {epilogueLabel}")
                        self.emitLine(f"jmp r8")
                        return
        
        # Standard instruction emission with spill handling
        self._emitInstructionWithSpills(node)
    
    def visitCallInstructionNode(self, node):
        """Visit a call instruction node with proper spill handling."""
        # Emit any labels attached to this instruction
        if node.labels:
            for label in node.labels:
                self.emitLabel(label)
        
        # Strip @ prefix from function name if present
        funcName = node.functionName
        if isinstance(funcName, str) and funcName.startswith('@'):
            funcName = funcName[1:]
        
        # Push arguments in reverse order, loading spilled args first
        scratchRegs = ["r9", "r10", "r11"]
        for i in range(len(node.arguments) - 1, -1, -1):
            arg = node.arguments[i]
            
            # Handle spilled arguments
            if self._isSpilled(arg):
                scratch = scratchRegs[i % len(scratchRegs)]
                self._emitLoad(arg, scratch)
                self.emitLine(f"push {scratch}")
            else:
                # Handle normal arguments (physical registers or literals)
                argValue = self.visit(arg)
                self.emitLine(f"push {argValue}")
        
        # Call function
        self.emitLine(f"loada r8, {funcName}")
        self.emitLine(f"call r8")
        
        # Pop arguments
        for _ in node.arguments:
            self.emitLine("pop r8")
    
    def visitRegisterNode(self, node):
        """Visit a register node - return the register name."""
        return node.id
    
    def visitVirtualRegisterNode(self, node):
        """Visit a virtual register node - look up physical register or return spill info."""
        # Virtual registers should have been allocated to physical registers
        # by the register allocator pass
        if self.currentFunction:
            registerAllocation = getattr(self.currentFunction, 'registerAllocation', {})
            if node.id in registerAllocation:
                allocation = registerAllocation[node.id]
                if isinstance(allocation, str):
                    return allocation  # Physical register name like "r0"
                elif isinstance(allocation, dict):
                    if allocation.get('kind') == 'reg':
                        return allocation['value']
                    elif allocation.get('kind') == 'spill':
                        # Return spill location info (to be handled by caller)
                        return allocation
        
        # Fallback: return the virtual register name as-is
        return node.id
    
    def _isSpilled(self, operand):
        """Check if an operand is a spilled virtual register or a parameter."""
        if isinstance(operand, (ASM_AST.VirtualRegisterNode, ASM_AST.VirtualTempRegisterNode)):
            if self.currentFunction:
                registerAllocation = getattr(self.currentFunction, 'registerAllocation', {})
                if operand.id in registerAllocation:
                    allocation = registerAllocation[operand.id]
                    if isinstance(allocation, dict):
                        kind = allocation.get('kind')
                        return kind in ('spill', 'param')
        return False
    
    def _getSpillOffset(self, operand):
        """Get the stack offset for a spilled operand or parameter.
        Returns (offset, kind) where kind is 'param' or 'spill'.
        Returns (None, None) if not found.
        """
        if isinstance(operand, (ASM_AST.VirtualRegisterNode, ASM_AST.VirtualTempRegisterNode)):
            if self.currentFunction:
                registerAllocation = getattr(self.currentFunction, 'registerAllocation', {})
                if operand.id in registerAllocation:
                    allocation = registerAllocation[operand.id]
                    if isinstance(allocation, dict):
                        kind = allocation.get('kind')
                        if kind in ('spill', 'param'):
                            return allocation['value'], kind
        return None, None
    
    def _emitLoad(self, operand, scratchReg):
        """Emit code to load a spilled operand or parameter into a scratch register."""
        offset, kind = self._getSpillOffset(operand)
        if offset is not None:
            if kind == 'param':
                # Parameters are at positive offsets: [bp + offset]
                self.emitLine(f"load64 {scratchReg}, bp, {offset} // load parameter {operand.id}")
            elif kind == 'spill':
                # Spilled locals are at negative offsets: [bp - offset]
                self.emitLine(f"load64 {scratchReg}, bp, -{offset} // load spilled {operand.id}")
        else:
            self.emitComment(f"ERROR: Cannot load operand {operand.id}")
    
    def _emitStore(self, operand, scratchReg):
        """Emit code to store from a scratch register to a spilled operand."""
        offset, kind = self._getSpillOffset(operand)
        if offset is not None:
            if kind == 'param':
                # Parameters shouldn't be stored to (they're read-only in this context)
                # But if needed: [bp + offset]
                self.emitLine(f"store64 bp, {scratchReg}, {offset} // store to parameter {operand.id}")
            elif kind == 'spill':
                # Spilled locals are at negative offsets: [bp - offset]
                self.emitLine(f"store64 bp, {scratchReg}, -{offset} // store to spilled {operand.id}")
        else:
            self.emitComment(f"ERROR: Cannot store to operand {operand.id}")
    
    def _emitInstructionWithSpills(self, node):
        """
        Emit an instruction, handling spilled operands by loading/storing with scratch registers.
        
        Strategy:
        1. Load all spilled source operands into scratch registers (r9, r10, r11)
        2. Emit instruction using physical/scratch registers
        3. Store result from scratch register to spilled destination if needed
        """
        command = node.command
        args = node.arguments if node.arguments else []
        
        # Available scratch registers for spill handling
        # r8 is reserved for other uses, use r9, r10, r11 for spills
        scratchRegs = ["r9", "r10", "r11"]
        scratchIdx = 0
        
        # Track which operands are spilled and their scratch registers
        operandMapping = []  # List of (original_operand, scratch_or_physical_reg)
        
        for arg in args:
            if self._isSpilled(arg):
                # Allocate a scratch register for this spilled operand
                scratch = scratchRegs[scratchIdx % len(scratchRegs)]
                scratchIdx += 1
                operandMapping.append((arg, scratch))
            else:
                # Use the operand directly (physical register or literal)
                resolved = self.visit(arg)
                operandMapping.append((arg, resolved))
        
        # Determine instruction type to understand operand semantics
        # Store instructions: store<size> <base_addr>, <value>, <offset>
        #   - base_addr is source (read), value is source (read)
        #   - No destination register
        # Load instructions: load<size> <dest>, <base_addr>, <offset>
        #   - dest is destination (written), base_addr is source (read)
        # Branch instructions: bge, blt, beq, bne, jmp, call, etc.
        #   - ALL operands are sources (read), no destination
        # Most other instructions: <dest>, <src1>, <src2>, ...
        #   - First operand is destination (written), rest are sources (read)
        
        isStoreInst = command.startswith("store")
        isLoadInst = command.startswith("load")
        isBranchInst = command in ["bge", "blt", "ble", "bgt", "beq", "bne", "jmp", "call", "ret"]
        
        if isStoreInst:
            # For store: all operands are sources, load them all
            for i, (original, mapped) in enumerate(operandMapping):
                if self._isSpilled(original):
                    self._emitLoad(original, mapped)
            destIdx = -1  # No destination
        elif isBranchInst:
            # For branches: all operands are sources, load them all
            for i, (original, mapped) in enumerate(operandMapping):
                if self._isSpilled(original):
                    self._emitLoad(original, mapped)
            destIdx = -1  # No destination
        elif isLoadInst:
            # For load: first operand is dest, rest are sources
            destIdx = 0
            for i, (original, mapped) in enumerate(operandMapping):
                if i != destIdx and self._isSpilled(original):
                    self._emitLoad(original, mapped)
        else:
            # Default: first operand is destination
            destIdx = 0 if len(args) > 0 else -1
            # Load spilled source operands (skip destination)
            for i, (original, mapped) in enumerate(operandMapping):
                if i != destIdx and self._isSpilled(original):
                    self._emitLoad(original, mapped)
        
        # Emit the actual instruction with mapped operands
        mappedArgs = [mapped for (_, mapped) in operandMapping]
        
        if mappedArgs:
            argStr = ", ".join(str(arg) for arg in mappedArgs)
            self.emitLine(f"{command} {argStr}")
        else:
            self.emitLine(f"{command}")
        
        # Store result to spilled destination if needed
        if destIdx >= 0 and destIdx < len(operandMapping):
            original, mapped = operandMapping[destIdx]
            if self._isSpilled(original):
                self._emitStore(original, mapped)
    
    def visitVirtualTempRegisterNode(self, node):
        """Visit a virtual temp register node."""
        return self.visitVirtualRegisterNode(node)
    
    def visitPhysicalRegisterNode(self, node):
        """Visit a physical register node."""
        return node.id
    
    def visitLabelNode(self, node):
        """Visit a label node - handle placeholders and emit actual labels."""
        labelId = node.id
        
        # Replace placeholder labels with actual function epilogue labels
        if "epilogue_placeholder" in labelId and self.currentFunction:
            return f"__epilogue__{self.currentFunction.id}"
        
        return labelId
        return labelId
    
    def visitIntLiteralNode(self, node):
        """Visit an integer literal node."""
        return str(node.value)
    
    def visitFloatLiteralNode(self, node):
        """Visit a float literal node."""
        return str(node.value)
    
    def visitCharLiteralNode(self, node):
        """Visit a char literal node."""
        return f"'{node.value}'"
    
    def visitStringLiteralNode(self, node):
        """Visit a string literal node - add to data section."""
        label = self.getNewStringLabel()
        self.emitData(f'.ascii {node.value}', label)
        return label

# =================================================================================================
