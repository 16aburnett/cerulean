# CeruleanIR Compiler - Register Allocation Pass
# By Amy Burnett
# =================================================================================================
# This pass performs register allocation on virtual CeruleanRISC.
# It uses a linear scan algorithm with live range analysis.
#
# Input:  Virtual ASM with unlimited virtual registers (%var1, %var2, etc.)
# Output: Virtual ASM with physical registers (r0-r7) and spill annotations
# =================================================================================================

from . import ceruleanVirtualRISCAST as ASM_AST
from .ceruleanVirtualRISCASTVisitor import ASMASTVisitor

# =================================================================================================

class RegisterAllocator:
    """
    Performs register allocation using linear scan algorithm.
    """
    
    def __init__(self, availableRegs=None, scratchRegs=None, shouldPrintDebug=False):
        self.shouldPrintDebug = shouldPrintDebug
        
        # Physical registers available for allocation
        if availableRegs is None:
            self.availableRegs = [f"r{i}" for i in range(8)]  # r0-r7
        else:
            self.availableRegs = availableRegs
            
        # Scratch/temporary registers (not used for allocation, reserved for operations)
        if scratchRegs is None:
            self.scratchRegs = ["r8", "r9", "r10"]
        else:
            self.scratchRegs = scratchRegs
        
        # Allocation state (per function)
        self.virtualToPhysical = {}  # Maps virtual reg -> physical reg or spill slot
        self.activeRanges = []       # Currently active live ranges
        self.spillSlots = {}         # Maps virtual reg -> spill slot index
        self.nextSpillSlot = 0       # Next available spill slot
        
    def allocate(self, virtualASM, livenessInfo):
        """
        Main entry point for register allocation.
        
        Args:
            virtualASM: AST with virtual registers
            livenessInfo: Liveness analysis results
            
        Returns:
            Modified AST with physical registers and spill information
        """
        self.debugPrint("Starting register allocation...")
        
        # Allocate registers for each function
        allocator = AllocationVisitor(self, livenessInfo)
        allocatedASM = virtualASM.accept(allocator)
        
        self.debugPrint("Register allocation complete!")
        return allocatedASM
    
    def allocateRegisterForVariable(self, virtualReg, liveRange):
        """
        Allocates a physical register or spill slot for a virtual register.
        
        Args:
            virtualReg: Virtual register name (e.g., "%var1")
            liveRange: (start, end) tuple of instruction indices
            
        Returns:
            dict with "kind" ("reg" or "spill") and "value" (register name or slot index)
        """
        # Check if already allocated
        if virtualReg in self.virtualToPhysical:
            return self.virtualToPhysical[virtualReg]
        
        # Expire old live ranges that have ended
        self._expireOldRanges(liveRange[0])
        
        # Try to find a free physical register
        usedRegs = {r["value"] for r in self.activeRanges}
        for physReg in self.availableRegs:
            if physReg not in usedRegs:
                # Found a free register!
                allocation = {"kind": "reg", "value": physReg}
                self.virtualToPhysical[virtualReg] = allocation
                self.activeRanges.append({
                    "virtual": virtualReg,
                    "value": physReg,
                    "end": liveRange[1]
                })
                self.debugPrint(f"  Allocated {physReg} for {virtualReg}")
                return allocation
        
        # No free registers - must spill
        return self._spillVariable(virtualReg, liveRange)
    
    def _expireOldRanges(self, currentPos):
        """
        Removes live ranges that have ended before currentPos.
        This frees up physical registers for reuse.
        """
        # Sort by end position
        self.activeRanges.sort(key=lambda r: r["end"])
        
        # Remove ranges that have ended
        while self.activeRanges and self.activeRanges[0]["end"] < currentPos:
            expired = self.activeRanges.pop(0)
            self.debugPrint(f"  Expired range for {expired['virtual']} ({expired['value']})")
    
    def _spillVariable(self, virtualReg, liveRange):
        """
        Spills a variable to the stack when no registers are available.
        
        Strategy: Spill the virtual register with the furthest end point.
        This is a simple heuristic that works well in practice.
        """
        # Find the variable with the furthest end point
        spillCandidate = max(self.activeRanges, key=lambda r: r["end"])
        
        if spillCandidate["end"] > liveRange[1]:
            # Spill the candidate and take its register
            spilledVirtual = spillCandidate["virtual"]
            physReg = spillCandidate["value"]
            
            # Allocate spill slot for the spilled variable
            spillSlot = self.nextSpillSlot
            self.nextSpillSlot += 1
            self.spillSlots[spilledVirtual] = spillSlot
            self.virtualToPhysical[spilledVirtual] = {"kind": "spill", "value": spillSlot}
            
            self.debugPrint(f"  Spilled {spilledVirtual} (was in {physReg}) to slot {spillSlot}")
            
            # Update active ranges
            self.activeRanges.remove(spillCandidate)
            
            # Allocate the freed register to our variable
            allocation = {"kind": "reg", "value": physReg}
            self.virtualToPhysical[virtualReg] = allocation
            self.activeRanges.append({
                "virtual": virtualReg,
                "value": physReg,
                "end": liveRange[1]
            })
            
            self.debugPrint(f"  Allocated {physReg} for {virtualReg}")
            return allocation
        else:
            # Our variable has a longer range - spill it immediately
            spillSlot = self.nextSpillSlot
            self.nextSpillSlot += 1
            self.spillSlots[virtualReg] = spillSlot
            allocation = {"kind": "spill", "value": spillSlot}
            self.virtualToPhysical[virtualReg] = allocation
            
            self.debugPrint(f"  Spilled {virtualReg} immediately to slot {spillSlot}")
            return allocation
    
    def reset(self):
        """Reset allocator state for a new function."""
        self.virtualToPhysical = {}
        self.activeRanges = []
        self.spillSlots = {}
        self.nextSpillSlot = 0
    
    def getStackFrameSize(self):
        """Returns the number of bytes needed for spilled variables."""
        return self.nextSpillSlot * 8  # 8 bytes per spill slot
    
    def debugPrint(self, *args, **kwargs):
        if self.shouldPrintDebug:
            print("[debug] [register-allocator]", *args, **kwargs)

# =================================================================================================

class AllocationVisitor(ASMASTVisitor):
    """
    Visitor that applies register allocation to the virtual ASM AST.
    """
    
    def __init__(self, allocator, livenessInfo):
        self.allocator = allocator
        self.livenessInfo = livenessInfo
        self.currentFunction = None
    
    def visitProgramNode(self, node):
        """Visit each function and allocate registers."""
        allocatedFunctions = []
        for function in node.codeunits:
            if isinstance(function, ASM_AST.FunctionNode):
                allocatedFunc = function.accept(self)
                allocatedFunctions.append(allocatedFunc)
            else:
                allocatedFunctions.append(function)
        
        return ASM_AST.ProgramNode(allocatedFunctions, node.externSymbols, node.globalVars)
    
    def visitFunctionNode(self, node):
        """
        Allocate registers for a function.
        """
        self.allocator.debugPrint(f"\nAllocating registers for function: {node.id}")
        self.currentFunction = node
        
        # Reset allocator state for this function
        self.allocator.reset()
        
        # Get liveness info for this function
        funcLiveness = self.livenessInfo.get(node.id, {})
        
        # Build live ranges for all virtual registers
        liveRanges = self._buildLiveRanges(node.instructions, funcLiveness)
        
        # Sort variables by start of live range (for linear scan)
        sortedVars = sorted(liveRanges.items(), key=lambda x: x[1][0])
        
        # Allocate registers in order
        for virtualReg, liveRange in sortedVars:
            self.allocator.allocateRegisterForVariable(virtualReg, liveRange)
        
        # Store allocation info in the function node
        node.registerAllocation = self.allocator.virtualToPhysical.copy()
        node.spillSlots = self.allocator.spillSlots.copy()
        node.stackFrameSize = self.allocator.getStackFrameSize()
        
        self.allocator.debugPrint(f"Stack frame size: {node.stackFrameSize} bytes")
        
        # Instructions remain unchanged at this point
        # (actual rewriting happens in a later pass or during emission)
        return node
    
    def _buildLiveRanges(self, instructions, funcLiveness):
        """
        Build live ranges for all virtual registers in the function.
        
        Returns:
            dict mapping virtual register -> (start_index, end_index)
        """
        liveRanges = {}
        
        for idx, instr in enumerate(instructions):
            # Get variables defined at this instruction
            defsAt = funcLiveness.get(f"def_{idx}", [])
            for var in defsAt:
                if var not in liveRanges:
                    liveRanges[var] = [idx, idx]
                else:
                    liveRanges[var][0] = min(liveRanges[var][0], idx)
            
            # Get variables used at this instruction
            usesAt = funcLiveness.get(f"use_{idx}", [])
            for var in usesAt:
                if var not in liveRanges:
                    liveRanges[var] = [idx, idx]
                else:
                    liveRanges[var][1] = max(liveRanges[var][1], idx)
            
            # Get variables live-out at this instruction
            # This captures variables that need to stay alive beyond their last explicit use
            liveOutAt = funcLiveness.get(f"liveOut_{idx}", [])
            for var in liveOutAt:
                if var not in liveRanges:
                    liveRanges[var] = [idx, idx]
                else:
                    liveRanges[var][1] = max(liveRanges[var][1], idx)
        
        # Convert to tuples
        return {var: tuple(range_) for var, range_ in liveRanges.items()}
    
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
    
    def visitGlobalVariableNode(self, node):
        # Global variables are in data section, no allocation needed
        return node

# =================================================================================================
