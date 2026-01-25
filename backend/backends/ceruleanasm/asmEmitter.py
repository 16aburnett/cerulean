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
        """Visit an instruction node - emit the instruction."""
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
                destReg = self.visit(destOperand)
                
                # Get the offset from function's alloca map
                if self.currentFunction and hasattr(self.currentFunction, 'allocaOffsets'):
                    allocaOffsets = self.currentFunction.allocaOffsets
                    regName = destOperand.id if hasattr(destOperand, 'id') else str(destOperand)
                    
                    if regName in allocaOffsets:
                        offset = allocaOffsets[regName]
                        # Compute address: bp - offset
                        # Since stack grows down, alloca space is below bp
                        self.emitLine(f"mv64 {destReg}, bp // alloca: compute stack address")
                        if offset > 0:
                            self.emitLine(f"sub64i {destReg}, {destReg}, {offset}")
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
        
        # Standard instruction emission
        args = [self.visit(arg) for arg in node.arguments]
        
        if args:
            argStr = ", ".join(str(arg) for arg in args)
            self.emitLine(f"{command} {argStr}")
        else:
            self.emitLine(f"{command}")
    
    def visitCallInstructionNode(self, node):
        """Visit a call instruction node."""
        # Emit any labels attached to this instruction
        if node.labels:
            for label in node.labels:
                self.emitLabel(label)
        
        # Strip @ prefix from function name if present
        funcName = node.functionName
        if isinstance(funcName, str) and funcName.startswith('@'):
            funcName = funcName[1:]
        
        # Push arguments in reverse order
        for i in range(len(node.arguments) - 1, -1, -1):
            arg = self.visit(node.arguments[i])
            self.emitLine(f"push {arg}")
        
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
        """Visit a virtual register node - look up physical register."""
        # Virtual registers should have been allocated to physical registers
        # by the register allocator pass
        if self.currentFunction:
            registerAllocation = getattr(self.currentFunction, 'registerAllocation', {})
            if node.id in registerAllocation:
                # Get the physical register or spill slot
                allocation = registerAllocation[node.id]
                if isinstance(allocation, str):
                    return allocation  # Physical register name like "r0"
                elif isinstance(allocation, dict):
                    if allocation.get('kind') == 'reg':
                        return allocation['value']
                    elif allocation.get('kind') == 'spill':
                        # For spills, we need to emit load/store around uses
                        # For now, just return a comment
                        slot = allocation['value']
                        return f"[bp-{slot*8}]"  # Stack location
        
        # Fallback: return the virtual register name as-is
        return node.id
    
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
