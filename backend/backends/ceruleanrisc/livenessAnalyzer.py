# CeruleanIR Compiler - Liveness Analysis for CeruleanRISC
# By Amy Burnett
# =================================================================================================
# Performs liveness analysis to determine which variables are live at each program point.
# This information is used by the register allocator.
#
# Can work on either:
# 1. CeruleanIR AST (for reference tracking)
# 2. Virtual CeruleanRISC AST (for proper liveness analysis with live ranges)
# =================================================================================================

from sys import exit

from ...ceruleanIRAST import *
from ...visitor import ASTVisitor

try:
    from . import ceruleanVirtualRISCAST as ASM_AST
    from .ceruleanVirtualRISCASTVisitor import ASMASTVisitor
except ImportError:
    # Fallback if ASM AST not available yet
    ASM_AST = None
    ASMASTVisitor = object

# =================================================================================================

class LivenessAnalyzer (ASTVisitor):
    """
    Liveness analyzer for CeruleanIR (original AST).
    This is the legacy path - just tracks references.
    """

    def __init__(self, shouldPrintDebug=False):
        self.shouldPrintDebug = shouldPrintDebug

    def analyze (self, ast):
        """
        Analyze an AST and return liveness information.
        Returns a dictionary with liveness data per function.
        """
        # Determine which AST type we're working with
        if ASM_AST and isinstance(ast, ASM_AST.ProgramNode):
            # Virtual ASM - use proper liveness analysis
            self.debugPrint("Analyzing Virtual ASM for liveness...")
            analyzer = VirtualASMLivenessAnalyzer(self.shouldPrintDebug)
            return analyzer.analyze(ast)
        else:
            # CeruleanIR - use legacy reference tracking
            self.debugPrint("Analyzing CeruleanIR for references...")
            ast.accept(self)
            return {}  # Return empty dict for now (legacy compatibility)

    # === HELPER FUNCTIONS ===============================================
    
    def debugPrint (self, *args, **kwargs):
        if (self.shouldPrintDebug):
            print ("[debug] [liveness]", *args, **kwargs)

    # === VISITOR FUNCTIONS ==============================================

    def visitProgramNode (self, node):
        for codeunit in node.codeunits:
            if codeunit != None:
                codeunit.accept (self)

    #=====================================================================

    def visitTypeSpecifierNode (self, node):
        pass

    #=====================================================================

    def visitParameterNode (self, node):
        pass

    #=====================================================================

    def visitGlobalVariableDeclarationNode (self, node):
        pass

    #=====================================================================

    def visitVariableDeclarationNode (self, node):
        pass

    #=====================================================================

    def visitFunctionNode (self, node):
        for i in range(len(node.params)):
            node.params[i].accept (self)

        for basicBlock in node.basicBlocks:
            basicBlock.accept (self)

    #=====================================================================

    def visitBasicBlockNode (self, node):
        for instruction in node.instructions:
            instruction.accept (self)

    #=====================================================================

    def visitInstructionNode (self, node):
        for arg in node.arguments:
            arg.accept (self)

    #=====================================================================

    def visitCallInstructionNode (self, node):
        for arg in node.arguments:
            arg.accept (self)

    #=====================================================================

    # writes any code it needs to
    # returns the parsed argument
    def visitArgumentExpressionNode (self, node):
        return node.expression.accept (self)

    #=====================================================================

    # root node - should not be used
    def visitExpressionNode (self, node):
        pass

    #=====================================================================

    def visitGlobalVariableExpressionNode (self, node):
        # Ensure reference has a decl
        if node.decl == None:
            raise ValueError (f"LivenessAnalyzer: ERROR: Reference does not have a matching declaration - this is an error with the compiler")
        self.debugPrint (f"Counting global reference for '{node.id}'")
        node.decl.references.append (node)

    #=====================================================================

    def visitLocalVariableExpressionNode (self, node):
        # Ensure reference has a decl
        if node.decl == None:
            raise ValueError (f"LivenessAnalyzer: ERROR: Reference does not have a matching declaration - this is an error with the compiler")
        self.debugPrint (f"Counting reference for '{node.id}'")
        node.decl.references.append (node)

    #=====================================================================

    def visitBasicBlockExpressionNode (self, node):
        pass

    #=====================================================================

    def visitIntLiteralExpressionNode (self, node):
        pass

    #=====================================================================

    def visitFloatLiteralExpressionNode (self, node):
        pass

    #=====================================================================

    def visitCharLiteralExpressionNode (self, node):
        pass

    #=====================================================================

    def visitStringLiteralExpressionNode (self, node):
        pass

# =================================================================================================

class VirtualASMLivenessAnalyzer:
    """
    Proper liveness analyzer for Virtual CeruleanRISC.
    Computes def/use sets and live ranges for register allocation.
    """
    
    def __init__(self, shouldPrintDebug=False):
        self.shouldPrintDebug = shouldPrintDebug
        self.livenessInfo = {}
    
    def analyze(self, virtualASM):
        """
        Analyze virtual ASM and compute liveness information.
        
        Returns:
            dict mapping function_id -> {
                "def_<idx>": [vars defined at instruction idx],
                "use_<idx>": [vars used at instruction idx],
                "liveIn_<idx>": [vars live at instruction entry],
                "liveOut_<idx>": [vars live at instruction exit]
            }
        """
        self.debugPrint("Computing liveness for Virtual ASM...")
        
        # Process each function
        for codeunit in virtualASM.codeunits:
            if ASM_AST and isinstance(codeunit, ASM_AST.FunctionNode):
                funcLiveness = self._analyzeFunctionLiveness(codeunit)
                self.livenessInfo[codeunit.id] = funcLiveness
        
        return self.livenessInfo
    
    def _analyzeFunctionLiveness(self, funcNode):
        """Analyze liveness for a single function."""
        self.debugPrint(f"  Analyzing function: {funcNode.id}")
        
        instructions = funcNode.instructions
        numInstructions = len(instructions)
        
        # Initialize def/use sets
        defSets = [set() for _ in range(numInstructions)]
        useSets = [set() for _ in range(numInstructions)]
        
        # Compute def/use for each instruction
        for idx, instr in enumerate(instructions):
            defs, uses = self._getDefUse(instr)
            defSets[idx] = defs
            useSets[idx] = uses
            self.debugPrint(f"    Instr {idx}: def={defs}, use={uses}")
        
        # Compute live-in and live-out via iterative dataflow
        # liveIn[i] = use[i] ∪ (liveOut[i] - def[i])
        # liveOut[i] = ∪ liveIn[successor]
        liveIn = [set() for _ in range(numInstructions)]
        liveOut = [set() for _ in range(numInstructions)]
        
        # Iterate until fixed point (simple version: just backwards pass)
        # For single basic block, this is straightforward
        # NOTE: This doesn't handle control flow correctly - loops will have issues
        # TODO: Implement proper CFG-based liveness analysis
        changed = True
        iterations = 0
        maxIterations = 100
        
        while changed and iterations < maxIterations:
            changed = False
            iterations += 1
            
            # Backwards pass
            for idx in range(numInstructions - 1, -1, -1):
                # liveOut = liveIn of next instruction
                oldLiveOut = liveOut[idx].copy()
                if idx < numInstructions - 1:
                    liveOut[idx] = liveIn[idx + 1].copy()
                else:
                    liveOut[idx] = set()  # Nothing live after function
                
                # liveIn = use ∪ (liveOut - def)
                oldLiveIn = liveIn[idx].copy()
                liveIn[idx] = useSets[idx] | (liveOut[idx] - defSets[idx])
                
                if oldLiveIn != liveIn[idx] or oldLiveOut != liveOut[idx]:
                    changed = True
        
        self.debugPrint(f"    Converged after {iterations} iterations")
        
        # Build result dictionary
        result = {}
        for idx in range(numInstructions):
            result[f"def_{idx}"] = list(defSets[idx])
            result[f"use_{idx}"] = list(useSets[idx])
            result[f"liveIn_{idx}"] = list(liveIn[idx])
            result[f"liveOut_{idx}"] = list(liveOut[idx])
        
        return result
    
    def _getDefUse(self, instr):
        """
        Extract def and use sets from an instruction.
        
        Returns:
            (defs, uses) - both are sets of variable names
        """
        defs = set()
        uses = set()
        
        if not ASM_AST:
            return defs, uses
        
        # Check if it's an instruction node
        if isinstance(instr, ASM_AST.InstructionNode):
            command = instr.command.lower() if isinstance(instr.command, str) else str(instr.command).lower()
            
            # Determine def/use pattern based on instruction type
            # Most instructions: dest, src1, src2 (dest is def, rest are use)
            # Load/Store have different patterns
            # Branches/jumps have no defs
            
            if command in ['ret', 'jmp', 'je', 'jne', 'jl', 'jle', 'jg', 'jge', 'call']:
                # Control flow - no defs, all args are uses
                for arg in instr.arguments:
                    self._addIfVirtual(uses, arg)
            elif command in ['push']:
                # Push - no defs, arg is use
                for arg in instr.arguments:
                    self._addIfVirtual(uses, arg)
            elif command in ['pop']:
                # Pop - arg is def
                if len(instr.arguments) > 0:
                    self._addIfVirtual(defs, instr.arguments[0])
            elif command.startswith('load'):
                # load dest, [src] - dest is def, src is use
                if len(instr.arguments) > 0:
                    self._addIfVirtual(defs, instr.arguments[0])
                if len(instr.arguments) > 1:
                    self._addIfVirtual(uses, instr.arguments[1])
            elif command.startswith('store'):
                # store [dest], src - both are uses
                for arg in instr.arguments:
                    self._addIfVirtual(uses, arg)
            else:
                # Standard pattern: dest, src1, src2, ...
                # First arg is def, rest are uses
                if len(instr.arguments) > 0:
                    self._addIfVirtual(defs, instr.arguments[0])
                for i in range(1, len(instr.arguments)):
                    self._addIfVirtual(uses, instr.arguments[i])
        
        elif isinstance(instr, ASM_AST.CallInstructionNode):
            # Call instruction - all arguments are uses, no defs
            # (return value would be in a register but that's implicit)
            for arg in instr.arguments:
                self._addIfVirtual(uses, arg)
        
        return defs, uses
    
    def _addIfVirtual(self, targetSet, node):
        """Add a node to the target set if it's a virtual register."""
        if not ASM_AST:
            return
        
        # Check for virtual registers (start with %)
        if isinstance(node, (ASM_AST.VirtualRegisterNode, ASM_AST.VirtualTempRegisterNode)):
            targetSet.add(node.id)
        elif isinstance(node, ASM_AST.RegisterNode):
            # Check if it's a virtual register by name
            if hasattr(node, 'id') and str(node.id).startswith('%'):
                targetSet.add(node.id)
    
    def debugPrint(self, *args, **kwargs):
        if self.shouldPrintDebug:
            print("[debug] [liveness-vasm]", *args, **kwargs)

# =================================================================================================
