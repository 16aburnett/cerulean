# CeruleanIR Frontend Compiler
# CeruleanIR is a low-level IR language
# This frontend parses CeruleanIR source text into an IR AST
# and passes it to the backend compiler for code generation
# Author: Amy Burnett
# ========================================================================

import sys
import os
from sys import exit
import argparse

# Frontend components (parsing IR text)
from .tokenizer import tokenize
from .parser import Parser

# Backend components (shared IR definitions and compilation)
from backend.ceruleanIRAST import *
from backend.compiler import CeruleanIRBackendCompiler, TargetLang
from backend.backends.ceruleanasm.codegen import AllocatorStrategy

# ========================================================================

class CeruleanIRCompiler:

    def __init__(self, debug=False):
        self.shouldPrintDebug = debug

    #---------------------------------------------------------------------

    def compile (self, rawSourceCode, sourceFilename, emitTokens=False, emitAST=False, emitIR=False, target=TargetLang.AMYASM, regalloc=AllocatorStrategy.NAIVE):

        sourceCodeLines = rawSourceCode.split ("\n")

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
        parser = Parser (tokens, sourceCodeLines, False)
        ast = parser.parse ()

        #=== CODE GENERATION =============================================

        self.printDebug (f"Generating code...")
        backendCompiler = CeruleanIRBackendCompiler (debug=self.shouldPrintDebug)
        generatedCode = backendCompiler.compile (ast, sourceCodeLines, sourceFilename,
            emitAST=emitAST, emitIR=emitIR, target=target, regalloc=regalloc)

        return generatedCode

    def printDebug (self, *args, **kwargs):
        """Custom debug print function."""
        if (self.shouldPrintDebug):
            print(*args, **kwargs)

# ========================================================================

if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="CeruleanIR Frontend Compiler")

    argparser.add_argument(dest="sourceFiles", nargs="+", help="source files to compile (first file should be the main file)")
    argparser.add_argument("-o", "--outputFilename", dest="outputFilename", help="name of the outputted compiled file")
    argparser.add_argument("--emitTokens", dest="emitTokens", action="store_true", help="output the parsed tokens to a file")
    argparser.add_argument("--emitAST", dest="emitAST", action="store_true", help="output the Abstract Syntax Tree (AST)")
    argparser.add_argument("--emitIR", dest="emitIR", action="store_true", help="output the IR")
    argparser.add_argument("--target", dest="target", type=str,
        choices=[lang.value for lang in TargetLang], default=TargetLang.AMYASM.value,
        help="specifies the target language to compile to [default: amyasm]")
    argparser.add_argument("--regalloc", dest="regalloc", type=str,
        choices=[s.value for s in AllocatorStrategy], default=AllocatorStrategy.NAIVE.value,
        help="specifies the register allocator strategy to use [default: naive]")
    argparser.add_argument("--debug", dest="debug", action="store_true", help="output debug info")

    args = argparser.parse_args()

    target = TargetLang(args.target)
    regalloc = AllocatorStrategy(args.regalloc)
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
        regalloc=regalloc
    )

    # Write target code
    print (f"Writing compiled code to \"{destFilename}\"")
    with open (destFilename, "w") as f:
        f.write (targetCode)
