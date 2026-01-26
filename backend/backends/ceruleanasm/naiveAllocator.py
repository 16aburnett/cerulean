# CeruleanIR Compiler - Naive Register Allocator
# By Amy Burnett
# =================================================================================================
# This is a simple "no optimization" allocator that spills all virtual registers to the stack.
# 
# Strategy:
# - Every virtual register gets its own stack slot
# - Physical registers are used only as temporaries for operations
# - Instructions are NOT rewritten - the emitter handles load/store insertion
#
# This allocator always produces correct code (no liveness issues) but is slow.
# It's equivalent to -O0 in other compilers.
# =================================================================================================

from . import ceruleanASMAST as ASM_AST
from .ceruleanASMASTVisitor import ASMASTVisitor

# =================================================================================================

class NaiveAllocator:
    """
    Naive register allocator: spill everything to the stack.
    Use physical registers only as scratch/temporary registers.
    """
    
    def __init__(self, shouldPrintDebug=False):
        self.shouldPrintDebug = shouldPrintDebug
    
    def allocate(self, virtualASM, livenessInfo=None):
        """
        Main entry point for naive register allocation.
        
        Args:
            virtualASM: AST with virtual registers
            livenessInfo: Ignored (not needed for naive allocation)
            
        Returns:
            Modified AST with allocation information (no instruction rewriting)
        """
        self.debugPrint("Starting naive register allocation...")
        self.debugPrint("Strategy: Spill all virtual registers to stack")
        
        # Allocate stack slots for each function
        allocator = NaiveAllocationVisitor(self)
        allocatedASM = virtualASM.accept(allocator)
        
        self.debugPrint("Naive register allocation complete!")
        return allocatedASM
    
    def debugPrint(self, *args, **kwargs):
        if self.shouldPrintDebug:
            print("[debug] [naive-allocator]", *args, **kwargs)

# =================================================================================================

class NaiveAllocationVisitor(ASMASTVisitor):
    """
    Visitor that assigns stack slots to all virtual registers.
    Does NOT rewrite instructions - that's handled by the emitter.
    """
    
    def __init__(self, allocator):
        self.allocator = allocator
    
    def visitProgramNode(self, node):
        """Visit each function and allocate stack slots."""
        allocatedFunctions = []
        for function in node.codeunits:
            if isinstance(function, ASM_AST.FunctionNode):
                allocatedFunc = function.accept(self)
                allocatedFunctions.append(allocatedFunc)
            else:
                allocatedFunctions.append(function)
        
        return ASM_AST.ProgramNode(allocatedFunctions)
    
    def visitFunctionNode(self, node):
        """
        Naive allocation: Spill ALL virtual registers to stack.
        Physical registers are only used as scratch space within instructions.
        """
        self.allocator.debugPrint(f"\nAllocating stack slots for function: {node.id}")
        
        # Collect all unique virtual registers used in this function
        virtualRegs = self._collectVirtualRegisters(node.instructions)
        
        # Assign each virtual register to a stack slot
        # Offsets start at 8 to account for saved BP at bp+0 and return address at bp+8
        # Actually, saved BP is at [bp], so spills start at offset 8 meaning bp-8
        registerAllocation = {}
        stackSlots = {}
        currentOffset = 8  # Start at 8 to skip saved bp
        
        for vreg in sorted(virtualRegs):
            stackSlots[vreg] = currentOffset
            # Mark as spilled with offset
            registerAllocation[vreg] = {"kind": "spill", "value": currentOffset}
            self.allocator.debugPrint(f"  {vreg} -> stack slot at bp-{currentOffset}")
            currentOffset += 8  # 8 bytes per slot (64-bit values)
        
        # Round up to 16-byte alignment
        if currentOffset % 16 != 0:
            currentOffset = ((currentOffset + 15) // 16) * 16
        
        # Store allocation info in the function node
        node.registerAllocation = registerAllocation
        node.spillSlots = stackSlots
        node.stackFrameSize = currentOffset
        
        self.allocator.debugPrint(f"Total stack frame size: {currentOffset} bytes")
        self.allocator.debugPrint(f"Spilled {len(virtualRegs)} virtual registers to stack")
        
        return node
    
    def _collectVirtualRegisters(self, instructions):
        """
        Collect all unique virtual register names from a list of instructions.
        """
        virtualRegs = set()
        
        for instr in instructions:
            # Handle regular instructions
            if isinstance(instr, ASM_AST.InstructionNode):
                for arg in instr.arguments:
                    self._collectFromNode(arg, virtualRegs)
            
            # Handle call instructions
            elif isinstance(instr, ASM_AST.CallInstructionNode):
                for arg in instr.arguments:
                    self._collectFromNode(arg, virtualRegs)
        
        return virtualRegs
    
    def _collectFromNode(self, node, virtualRegs):
        """Recursively collect virtual register names from an AST node."""
        if isinstance(node, (ASM_AST.VirtualRegisterNode, ASM_AST.VirtualTempRegisterNode)):
            virtualRegs.add(node.id)
        elif isinstance(node, ASM_AST.RegisterNode):
            # Check if it's a virtual register by name
            if hasattr(node, 'id') and isinstance(node.id, str) and node.id.startswith('%'):
                virtualRegs.add(node.id)
    
    # Default implementations for other node types
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
