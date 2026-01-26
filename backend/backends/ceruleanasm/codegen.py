# CeruleanIR Compiler - Code Generation for CeruleanASM
# By Amy Burnett
# =================================================================================================

from enum import Enum
from ...visitor import ASTVisitor
from .lowering import LoweringVisitor
from .livenessAnalyzer import LivenessAnalyzer
from .registerAllocator import RegisterAllocator
from .naiveAllocator import NaiveAllocator
from .frameLowering import FrameLowering
from .asmEmitter import ASMEmitter

# =================================================================================================

class AllocatorStrategy(Enum):
    """Register allocator strategies."""
    NAIVE = "naive"              # Spill everything, always correct
    LINEAR_SCAN = "linear-scan"  # Linear scan allocation (requires CFG for loops)
    # Future options:
    # GRAPH_COLORING = "graph-coloring"

# =================================================================================================

class CodeGenVisitor_CeruleanASM (ASTVisitor):

    def __init__(self, lines, sourceFilename, shouldPrintDebug=False, emitVirtualASM=False, allocatorStrategy=AllocatorStrategy.NAIVE):
        self.sourceFilename = sourceFilename
        self.shouldPrintDebug = shouldPrintDebug
        self.emitVirtualASM = emitVirtualASM
        self.allocatorStrategy = allocatorStrategy
        self.wasSuccessful = True  # Used by compiler to check for errors
        
        # Configuration for register allocation (passed to RegisterAllocator)
        self.MAX_AVAILABLE_REGISTERS = 8
        self.scratchRegisters = ["r8", "r9", "r10"]

    def generate (self, ast):

        # ========================================================================
        # MULTI-PASS COMPILATION PIPELINE
        # ========================================================================
        
        # Pass 1: Lower IR to Virtual ASM (unlimited virtual registers)
        self.debugPrint("Pass 1: Lowering CeruleanIR to Virtual ASM...")
        loweringVisitor = LoweringVisitor (self.shouldPrintDebug)
        virtualASM = loweringVisitor.lower (ast)

        if self.emitVirtualASM:
            # Virtual Assembly
            vasmFilename = f"{self.sourceFilename}.virtasm"
            self.debugPrint (f"Emitting Virtual Assembly to '{vasmFilename}'...")
            file = open (vasmFilename, "w")
            file.write (str (virtualASM))
            # Virtual Assembly AST
            vasmastFilename = f"{self.sourceFilename}.virtasmast"
            self.debugPrint (f"Emitting Virtual Assembly AST to '{vasmastFilename}'...")
            file = open (vasmastFilename, "w")
            file.write (repr (virtualASM))

        # Pass 2: Liveness Analysis (only needed for some allocators)
        self.debugPrint("Pass 2: Analyzing variable liveness...")
        if self.allocatorStrategy == AllocatorStrategy.NAIVE:
            self.debugPrint("  Skipped (not needed for naive allocation)")
            livenessInfo = None
        else:
            livenessAnalyzer = LivenessAnalyzer (self.shouldPrintDebug)
            livenessInfo = livenessAnalyzer.analyze (virtualASM)
        
        # Pass 3: Register Allocation (virtual -> physical registers + spills)
        self.debugPrint("Pass 3: Allocating registers...")
        if self.allocatorStrategy == AllocatorStrategy.NAIVE:
            self.debugPrint("  Using naive allocator (spill everything)")
            registerAllocator = NaiveAllocator(shouldPrintDebug=self.shouldPrintDebug)
        elif self.allocatorStrategy == AllocatorStrategy.LINEAR_SCAN:
            self.debugPrint("  Using linear scan allocator")
            registerAllocator = RegisterAllocator(
                availableRegs=[f"r{i}" for i in range(self.MAX_AVAILABLE_REGISTERS)],
                scratchRegs=self.scratchRegisters,
                shouldPrintDebug=self.shouldPrintDebug
            )
        else:
            raise ValueError(f"Unknown allocator strategy: {self.allocatorStrategy}")
        
        allocatedASM = registerAllocator.allocate(virtualASM, livenessInfo)
        
        # Pass 4: Frame Lowering (stack frame setup)
        self.debugPrint("Pass 4: Lowering stack frames...")
        frameLowering = FrameLowering(self.shouldPrintDebug)
        finalASM = frameLowering.lower(allocatedASM)
        
        # Pass 5: Code Emission (convert AST to text)
        self.debugPrint("Pass 5: Emitting final assembly...")
        emitter = ASMEmitter(self.shouldPrintDebug)
        assemblyText = emitter.emit(finalASM)
        return assemblyText

    # === HELPER FUNCTIONS ===============================================
    
    def debugPrint (self, *args, **kwargs):
        if (self.shouldPrintDebug):
            print ("[debug] [codegen-ceruleanasm]", *args, **kwargs)

    # === VISITOR STUBS (Required by ASTVisitor, but unused in multi-pass pipeline) ===
    
    def visitProgramNode(self, node):
        raise NotImplementedError("Old single-pass visitor pattern replaced by multi-pass pipeline")
    
    def visitTypeSpecifierNode(self, node):
        raise NotImplementedError("Old single-pass visitor pattern replaced by multi-pass pipeline")
    
    def visitParameterNode(self, node):
        raise NotImplementedError("Old single-pass visitor pattern replaced by multi-pass pipeline")
    
    def visitGlobalVariableDeclarationNode(self, node):
        raise NotImplementedError("Old single-pass visitor pattern replaced by multi-pass pipeline")
    
    def visitVariableDeclarationNode(self, node):
        raise NotImplementedError("Old single-pass visitor pattern replaced by multi-pass pipeline")
    
    def visitFunctionNode(self, node):
        raise NotImplementedError("Old single-pass visitor pattern replaced by multi-pass pipeline")
    
    def visitBasicBlockNode(self, node):
        raise NotImplementedError("Old single-pass visitor pattern replaced by multi-pass pipeline")
    
    def visitInstructionNode(self, node):
        raise NotImplementedError("Old single-pass visitor pattern replaced by multi-pass pipeline")
    
    def visitCallInstructionNode(self, node):
        raise NotImplementedError("Old single-pass visitor pattern replaced by multi-pass pipeline")
    
    def visitArgumentExpressionNode(self, node):
        raise NotImplementedError("Old single-pass visitor pattern replaced by multi-pass pipeline")
    
    def visitExpressionNode(self, node):
        raise NotImplementedError("Old single-pass visitor pattern replaced by multi-pass pipeline")
    
    def visitGlobalVariableExpressionNode(self, node):
        raise NotImplementedError("Old single-pass visitor pattern replaced by multi-pass pipeline")
    
    def visitLocalVariableExpressionNode(self, node):
        raise NotImplementedError("Old single-pass visitor pattern replaced by multi-pass pipeline")
    
    def visitBasicBlockExpressionNode(self, node):
        raise NotImplementedError("Old single-pass visitor pattern replaced by multi-pass pipeline")
    
    def visitIntLiteralExpressionNode(self, node):
        raise NotImplementedError("Old single-pass visitor pattern replaced by multi-pass pipeline")
    
    def visitFloatLiteralExpressionNode(self, node):
        raise NotImplementedError("Old single-pass visitor pattern replaced by multi-pass pipeline")
    
    def visitCharLiteralExpressionNode(self, node):
        raise NotImplementedError("Old single-pass visitor pattern replaced by multi-pass pipeline")
    
    def visitStringLiteralExpressionNode(self, node):
        raise NotImplementedError("Old single-pass visitor pattern replaced by multi-pass pipeline")

# =================================================================================================

