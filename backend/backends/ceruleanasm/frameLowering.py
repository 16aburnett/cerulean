# CeruleanIR Compiler - Frame Lowering Pass
# By Amy Burnett
# =================================================================================================
# This pass handles stack frame setup/teardown for functions.
# It uses the register allocation information to determine stack sizes.
#
# Input:  Virtual ASM with register allocation info
# Output: Virtual ASM with function prologue/epilogue and resolved stack offsets
# =================================================================================================

from . import ceruleanASMAST as ASM_AST
from .ceruleanASMASTVisitor import ASMASTVisitor

# =================================================================================================

class FrameLowering:
    """
    Handles stack frame setup and teardown.
    """
    
    def __init__(self, shouldPrintDebug=False):
        self.shouldPrintDebug = shouldPrintDebug
    
    def lower(self, allocatedASM):
        """
        Main entry point for frame lowering.
        
        Args:
            allocatedASM: AST with register allocation info
            
        Returns:
            Modified AST with stack frame information
        """
        self.debugPrint("Starting frame lowering...")
        
        lowerer = FrameLoweringVisitor(self)
        finalASM = allocatedASM.accept(lowerer)
        
        self.debugPrint("Frame lowering complete!")
        return finalASM
    
    def debugPrint(self, *args, **kwargs):
        if self.shouldPrintDebug:
            print("[debug] [frame-lowering]", *args, **kwargs)

# =================================================================================================

class FrameLoweringVisitor(ASMASTVisitor):
    """
    Visitor that adds frame information to functions.
    """
    
    def __init__(self, frameLowering):
        self.frameLowering = frameLowering
    
    def visitProgramNode(self, node):
        """Visit each function."""
        processedFunctions = []
        for function in node.codeunits:
            if isinstance(function, ASM_AST.FunctionNode):
                processedFunc = function.accept(self)
                processedFunctions.append(processedFunc)
            else:
                processedFunctions.append(function)
        
        return ASM_AST.ProgramNode(processedFunctions, node.externSymbols)
    
    def visitFunctionNode(self, node):
        """
        Add stack frame information to the function.
        Calculates space needed for spilled registers and alloca'd memory.
        """
        self.frameLowering.debugPrint(f"\nProcessing frame for function: {node.id}")
        
        # Start with spilled variables from register allocation
        spilledSize = getattr(node, 'stackFrameSize', 0)
        
        # Scan instructions for allocas and calculate their offsets
        allocaSize = 0
        allocaOffsets = {}  # Map alloca register -> offset from bp
        currentOffset = spilledSize  # Allocas come after spills
        
        for instr in node.instructions:
            if isinstance(instr, ASM_AST.InstructionNode) and instr.command == "alloca":
                if hasattr(instr, 'allocaSize'):
                    size = instr.allocaSize
                    # Get the destination register
                    destReg = instr.arguments[0].id if instr.arguments else None
                    if destReg:
                        # Align each alloca to 8 bytes for safety
                        if currentOffset % 8 != 0:
                            currentOffset = ((currentOffset // 8) + 1) * 8
                        allocaOffsets[destReg] = currentOffset
                        self.frameLowering.debugPrint(f"  Alloca {destReg}: {size} bytes at offset {currentOffset}")
                        currentOffset += size
                        allocaSize += size
        
        # Total frame = spills + allocas
        totalFrameSize = spilledSize + allocaSize
        
        # Ensure 16-byte alignment for the entire frame
        if totalFrameSize % 16 != 0:
            totalFrameSize = ((totalFrameSize // 16) + 1) * 16
        
        # Store frame info on the node
        node.stackFrameSize = totalFrameSize
        node.allocaOffsets = allocaOffsets  # For use during emission
        
        self.frameLowering.debugPrint(f"  Spilled: {spilledSize} bytes, Allocas: {allocaSize} bytes")
        self.frameLowering.debugPrint(f"  Final stack frame size: {totalFrameSize} bytes (aligned)")
        
        return node
    
    # Default implementations
    def visitTypeSpecifierNode(self, node):
        return node
    
    def visitParameterNode(self, node):
        return node
    
    def visitInstructionNode(self, node):
        return node
    
    def visitCallInstructionNode(self, node):
        return node
    
    def visitRegisterNode(self, node):
        return node
    
    def visitVirtualRegisterNode(self, node):
        return node
    
    def visitVirtualTempRegisterNode(self, node):
        return node
    
    def visitPhysicalRegisterNode(self, node):
        return node
    
    def visitLabelNode(self, node):
        return node
    
    def visitIntLiteralNode(self, node):
        return node
    
    def visitFloatLiteralNode(self, node):
        return node
    
    def visitCharLiteralNode(self, node):
        return node
    
    def visitStringLiteralNode(self, node):
        return node

# =================================================================================================
