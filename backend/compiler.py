# CeruleanIR Backend Compiler
# Takes an IR AST and compiles it to a target language
# Author: Amy Burnett
# ========================================================================

import sys
import os
from sys import exit
from enum import Enum

from .ceruleanIRAST import *
from .printVisitor import PrintVisitor
from .irEmitter import IREmitterVisitor
from .visitor import *
from .builtins import addBuiltinsToSymbolTable
from .semanticAnalyzer import *
from .backends.ceruleanrisc.codegen import CodeGenVisitor_CeruleanRISC, AllocatorStrategy
from .backends.amyasm.codegen_amyasm import CodeGenVisitor_AmyAssembly
from .backends.x86.codegen_x86 import CodeGenVisitor_x86

# ========================================================================

class TargetLang(Enum):
    CERULEANRISC = "ceruleanrisc"
    AMYASM = "amyasm"
    X86    = "x86"
    # PYTHON = "python"
    # CPP    = "cpp"

BUILTIN_PREFIX = "__builtin__"

# ========================================================================

class CeruleanIRBackendCompiler:

    def __init__(self, debug=False):
        self.shouldPrintDebug = debug

    #---------------------------------------------------------------------

    def compile (self, ast, sourceCodeLines, sourceFilename, emitAST=False, emitIR=False, target=TargetLang.AMYASM, regalloc=AllocatorStrategy.NAIVE):

        #=== SEMANTIC ANALYSIS ===========================================

        self.printDebug ("Analyzing semantics...")
        semanticAnalyzer = SemanticAnalysisVisitor (sourceCodeLines, False)

        # Add built-in functions/variables to the symbol table
        # So we know what functions exist for checking for undefined symbols
        addBuiltinsToSymbolTable (semanticAnalyzer.table)

        # Check AST
        # checks for:
        # - undeclared vars
        # - redeclared vars
        # - matching operand types
        # - valid instructions
        wasSuccessful = semanticAnalyzer.analyze (ast)
        # ensure it was successful 
        if not wasSuccessful:
            print ("ERROR: Semantic Analysis failed")
            exit (1)

        # Reaches here if the file is semantically valid
        self.printDebug ("Semantic analysis passes successfully")
        
        #=== PRINT AST ===================================================

        # DEBUG - print AST to file
        if emitAST:
            astFilename = f"{sourceFilename}.ast"
            self.printDebug (f"Printing AST to '{astFilename}'...")
            printVisitor = PrintVisitor ()
            output = printVisitor.print (ast)
            astFile = open (astFilename, "w")
            astFile.write (output)
            astFile.close ()

        #=== EMITTING IR =================================================
        # Regenerates the IR code and outputs to a file

        if emitIR:
            irFilename = f"{sourceFilename}.ir"
            self.printDebug (f"Emitting IR to '{irFilename}'...")
            irEmitter = IREmitterVisitor ()
            irOutput = irEmitter.emit (ast)
            file = open (irFilename, "w")
            file.write (irOutput)

        #=== OPTIMIZATION ================================================
        # TODO: figure out what optimizations I can do

        #=== CODE GENERATION =============================================

        self.printDebug (f"Generating code...")
        if target == TargetLang.CERULEANRISC:
            codeGenerator = CodeGenVisitor_CeruleanRISC (sourceCodeLines, sourceFilename, shouldPrintDebug=self.shouldPrintDebug, emitVirtualASM=True, allocatorStrategy=regalloc)
        elif target == TargetLang.AMYASM:
            codeGenerator = CodeGenVisitor_AmyAssembly (sourceCodeLines)
        elif target == TargetLang.X86:
            codeGenerator = CodeGenVisitor_x86 (sourceCodeLines)
        else:
            print (f"Error: unknown target language '{target}'")
            exit (1)

        # generate code
        generatedCode = codeGenerator.generate (ast)

        # Ensure codegen was successful
        if not codeGenerator.wasSuccessful:
            print (f"Error: codegen failed")
            exit (1)

        return generatedCode

    def printDebug (self, *args, **kwargs):
        """Custom debug print function."""
        if (self.shouldPrintDebug):
            print(*args, **kwargs)

# ========================================================================
