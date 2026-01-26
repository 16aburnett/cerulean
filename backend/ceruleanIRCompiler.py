# CeruleanIR Compiler
# CeruleanIR is a low-level IR language
# Author: Amy Burnett
# ========================================================================

import sys
import os
from sys import exit
from enum import Enum
import argparse

from .tokenizer import tokenize
from .ceruleanIRAST import *
from .printVisitor import PrintVisitor
from .irEmitter import IREmitterVisitor
from .parser import Parser
from .visitor import *
from .builtins import addBuiltinsToSymbolTable
from .semanticAnalyzer import *
from .backends.ceruleanasm.codegen import CodeGenVisitor_CeruleanASM, AllocatorStrategy
from .backends.amyasm.codegen_amyasm import CodeGenVisitor_AmyAssembly
from .backends.x86.codegen_x86 import CodeGenVisitor_x86

# ========================================================================

class TargetLang(Enum):
    CERULEANASM = "ceruleanasm"
    AMYASM = "amyasm"
    X86    = "x86"
    # PYTHON = "python"
    # CPP    = "cpp"

BUILTIN_PREFIX = "__builtin__"

# ========================================================================

class CeruleanIRCompiler:

    def __init__(self, debug=False):
        self.shouldPrintDebug = debug

    #---------------------------------------------------------------------

    def compile (self, rawSourceCode, sourceFilename, emitTokens=False, emitAST=False, emitIR=False, target=TargetLang.AMYASM, allocator="naive"):

        lines = rawSourceCode.split ("\n")

        #=== TOKENIZATION ================================================
        # Group source code characters into tokens to identify symbols/operators,
        # keywords, identifiers/variables, and number/string/char literals.
        # This simplifies/eliminates whitespace with the exception of newlines
        # which are needed for parsing instruction lines.
        # Tokenization will throw errors for invalid symbols and invalid
        # identifiers.

        self.printDebug ("Tokenizing...")
        tokens = tokenize (rawSourceCode, sourceFilename)

        # DEBUG - print tokens to a file
        if emitTokens:
            tokensString = []
            for token in tokens:
                if (token.type == "IDENTIFIER" or token.type == "GVARIABLE" or token.type == "LVARIABLE"):
                    tokensString += [f"{token.type}({token.lexeme}) "]
                elif token.type == "NEWLINE":
                    tokensString += ["\n"]
                else:
                    tokensString += [f"{token.type} "]
            tokensString = "".join (tokensString)
            tokensFilename = f"{sourceFilename}.tokens"
            self.printDebug (f"Writing Tokens to \"{tokensFilename}\"")
            tokensFile = open (tokensFilename, "w")
            tokensFile.write (tokensString)
            tokensFile.close ()

        #=== PARSING =====================================================
        # Parsing groups tokens into code structures like instructions,
        # functions, and data structures.
        # Parsing results in an abstract syntax tree (AST) which describes how
        # each code structure is linked to each other, like the command and args
        # that define an instruction, and the instructions that define a function,
        # and the functions that define a file.
        # Since the parser is looking for specific code structures, it will
        # give an error if incorrect syntax is found.

        self.printDebug ("Parsing...")
        parser = Parser (tokens, lines, False)
        ast = parser.parse ()

        #=== SEMANTIC ANALYSIS ===========================================

        self.printDebug ("Analyzing semantics...")
        semanticAnalyzer = SemanticAnalysisVisitor (lines, False)

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

        # keyed by filename
        self.printDebug (f"Generating code...")
        if target == TargetLang.CERULEANASM:
            allocatorStrategy = AllocatorStrategy(allocator)  # Convert string to enum
            codeGenerator = CodeGenVisitor_CeruleanASM (lines, sourceFilename, shouldPrintDebug=self.shouldPrintDebug, emitVirtualASM=True, allocatorStrategy=allocatorStrategy)
        elif target == TargetLang.AMYASM:
            codeGenerator = CodeGenVisitor_AmyAssembly (lines)
        elif target == TargetLang.X86:
            codeGenerator = CodeGenVisitor_x86 (lines)
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

def printAST (ast):
    printVisitor = PrintVisitor ()
    output = printVisitor.print (ast)
    return output

# ========================================================================

def analyzeSemantics (ast, sourceCodeLines):
    semanticAnalyzer = SemanticAnalysisVisitor (sourceCodeLines, False)
    # Add built-in functions/variables to the symbol table
    # So we know what functions exist for checking for undefined symbols
    addBuiltinsToSymbolTable (semanticAnalyzer.table)
    # Check ast
    wasSuccessful = semanticAnalyzer.analyze (ast)
    return wasSuccessful

# ========================================================================

def generateCode (ast, sourceCodeLines, target):
    if target == TargetLang.CERULEANASM:
        codeGenerator = CodeGenVisitor_CeruleanASM (sourceCodeLines, shouldPrintDebug=self.shouldPrintDebug)
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

# ========================================================================

if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="CeruleanIR Compiler")

    argparser.add_argument(dest="sourceFiles", nargs="+", help="source files to compile (first file should be the main file)")
    argparser.add_argument("-o", "--outputFilename", dest="outputFilename", help="name of the outputted compiled file")
    argparser.add_argument("--emitTokens", dest="emitTokens", action="store_true", help="output the parsed tokens to a file")
    argparser.add_argument("--emitAST", dest="emitAST", action="store_true", help="output the Abstract Syntax Tree (AST)")
    argparser.add_argument("--emitIR", dest="emitIR", action="store_true", help="output the IR")
    argparser.add_argument("--target", dest="target", type=str,
        choices=[lang.value for lang in TargetLang], default=TargetLang.AMYASM.value,
        help="specifies the target language to compile to [default: amyasm]")
    argparser.add_argument("--allocator", dest="allocator", type=str,
        choices=["naive", "linear-scan"], default="naive",
        help="register allocator strategy: 'naive' (spill all, always correct) or 'linear-scan' (optimized, requires CFG) [default: naive]")
    argparser.add_argument("--debug", dest="debug", action="store_true", help="output debug info")

    args = argparser.parse_args()

    target = TargetLang(args.target)
    sourceFilename = args.sourceFiles[0]
    # otherFilenames = args.sourceFiles[1:]
    destFilename = None
    if args.outputFilename: # provided target filename
        destFilename = args.outputFilename
    elif target == TargetLang.CERULEANASM:
        destFilename = os.path.splitext (sourceFilename)[0] + ".ceruleanasm"
    elif target == TargetLang.AMYASM:
        destFilename = os.path.splitext (sourceFilename)[0] + ".amyasm"
    elif target == TargetLang.X86:
        destFilename = os.path.splitext (sourceFilename)[0] + ".asm"
    else:
        print (f"Error: unknown target, {target}")
        exit (1)

    # output compilation info
    print ("target      :", target)
    print ("destFilename:", destFilename)

    # Read source code
    with open (sourceFilename, "r") as f:
        rawSourceCode = f.read ()

    # compile code 
    compiler = CeruleanIRCompiler (debug=args.debug)
    targetCode = compiler.compile (
        rawSourceCode,
        sourceFilename,
        emitTokens=args.emitTokens,
        emitAST=args.emitAST,
        emitIR=args.emitIR,
        target=target,
        allocator=args.allocator
    )

    # Write target code
    print (f"Writing compiled code to \"{destFilename}\"")
    with open (destFilename, "w") as f:
        f.write (targetCode)
