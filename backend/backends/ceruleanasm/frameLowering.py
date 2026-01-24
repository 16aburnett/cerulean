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
        
        return ASM_AST.ProgramNode(processedFunctions)
    
    def visitFunctionNode(self, node):
        """
        Add stack frame information to the function.
        """
        self.frameLowering.debugPrint(f"\nProcessing frame for function: {node.id}")
        
        # Calculate total stack frame size
        # This includes: spilled variables + local variables + alignment
        stackFrameSize = getattr(node, 'stackFrameSize', 0)
        
        # Ensure 16-byte alignment (common requirement on many architectures)
        if stackFrameSize % 16 != 0:
            stackFrameSize = ((stackFrameSize // 16) + 1) * 16
        
        # Store frame info on the node
        node.stackFrameSize = stackFrameSize
        
        self.frameLowering.debugPrint(f"  Final stack frame size: {stackFrameSize} bytes (aligned)")
        
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
