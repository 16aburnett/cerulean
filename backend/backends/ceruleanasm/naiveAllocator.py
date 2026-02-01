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
        self.seen = set()  # Track seen virtual registers for deduplication
    
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
        
        IMPORTANT: Parameters are pushed before the call, so they live at positive
        offsets above bp ([bp+16], [bp+24], etc.). Local variables and temporaries
        are allocated at negative offsets below bp ([bp-8], [bp-16], etc.).
        """
        self.allocator.debugPrint(f"\nAllocating stack slots for function: {node.id}")
        
        # Collect all unique virtual registers used in this function
        virtualRegs = self._collectVirtualRegisters(node.instructions)
        
        # Separate parameters from local variables
        # Parameters are stored in node.parameterIds (set during lowering)
        paramNames = set(getattr(node, 'parameterIds', []))
        
        registerAllocation = {}
        stackSlots = {}
        
        # Allocate parameters at POSITIVE offsets (above bp)
        # Stack layout after call and prologue:
        #   [bp + 24] <- second parameter (pushed second, so higher address)
        #   [bp + 16]  <- first parameter (pushed first)
        #   [bp + 8]  <- return address (pushed by call instruction)
        #   [bp + 0]  <- saved bp (pushed by function prologue)
        #   [bp - 8]  <- first local variable
        paramOffset = 16  # First parameter at [bp+16]
        for paramName in getattr(node, 'parameterIds', []):
            stackSlots[paramName] = paramOffset
            # Positive offset means [bp + offset]
            registerAllocation[paramName] = {"kind": "param", "value": paramOffset}
            self.allocator.debugPrint(f"  {paramName} -> parameter at bp+{paramOffset}")
            paramOffset += 8  # 8 bytes per parameter
        
        # Allocate local variables at NEGATIVE offsets (below bp)
        # Start at -8 for first local
        localOffset = 8  # Represents [bp-8], [bp-16], etc.
        for vreg in virtualRegs:
            if vreg not in paramNames:
                stackSlots[vreg] = localOffset
                # Mark as spilled with negative offset
                registerAllocation[vreg] = {"kind": "spill", "value": localOffset}
                self.allocator.debugPrint(f"  {vreg} -> stack slot at bp-{localOffset}")
                localOffset += 8  # 8 bytes per slot
        
        # Round up to 16-byte alignment for locals
        if localOffset % 16 != 0:
            localOffset = ((localOffset + 15) // 16) * 16
        
        # Store allocation info in the function node
        node.registerAllocation = registerAllocation
        node.spillSlots = stackSlots
        node.stackFrameSize = localOffset  # Size needed for local variables
        
        self.allocator.debugPrint(f"Total stack frame size: {localOffset} bytes")
        self.allocator.debugPrint(f"Allocated {len(paramNames)} parameters, spilled {len(virtualRegs) - len(paramNames)} locals")
        
        return node
    
    def _collectVirtualRegisters(self, instructions):
        """
        Collect all unique virtual register names from a list of instructions.
        Preserves order of first occurrence.
        """
        virtualRegs = []
        self.seen = set()  # Reset for each function
        
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
            if node.id not in self.seen:
                virtualRegs.append(node.id)
                self.seen.add(node.id)
        elif isinstance(node, ASM_AST.RegisterNode):
            # Check if it's a virtual register by name
            if hasattr(node, 'id') and isinstance(node.id, str) and node.id.startswith('%'):
                if node.id not in self.seen:
                    virtualRegs.append(node.id)
                    self.seen.add(node.id)
    
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
