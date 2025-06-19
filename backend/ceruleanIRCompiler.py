# CeruleanIR Compiler
# CeruleanIR is a low-level IR language
# Author: Amy Burnett
# March 20, 2024
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
from .codegen_amyasm import CodeGenVisitor_AmyAssembly
from .codegen_x86 import CodeGenVisitor_x86

# ========================================================================

TARGET_AMYASM = "amyasm"
TARGET_X86    = "x86"
TARGET_PYTHON = "python"
TARGET_CPP    = "cpp"

BUILTIN_PREFIX = "__builtin__"

# ========================================================================

class CeruleanIRCompiler:

    def __init__(self, mainFilename, otherFilenames, destFilename="a.amyasm", debug=False, emitAST=False, emitIR=False, target=TARGET_AMYASM):
        self.mainFilename = mainFilename
        self.otherFilenames = otherFilenames
        self.destFilename = destFilename
        self.files = {}
        self.shouldPrintDebug = debug
        self.ast = ""

        self.emitAST = emitAST
        self.emitIR = emitIR

        self.astFilename = mainFilename + ".ast"
        self.debugLines = []

        self.target = target

    #---------------------------------------------------------------------

    def compile (self):

        #=== GATHERING INPUT =============================================
        # Start by reading in the contents of the files to compile.
        
        rootDir = os.path.abspath("")

        # ensure main file exists
        if (not os.path.exists(os.path.abspath(self.mainFilename))):
            print (f"Compiler Error: '{self.mainFilename}' does not exist")
            print (f"   Current Dir: {os.getcwd()}")
            print (f"   Absolute Path: {os.path.abspath(self.mainFilename)}")
            exit (1)

        # Read in file contents
        print ("file:", self.mainFilename)
        self.files[os.path.abspath(self.mainFilename)] = open (os.path.abspath(self.mainFilename), "r").readlines ()
        
        # ensure last line ends in newline
        if len(self.files[os.path.abspath(self.mainFilename)]) > 0:
            if not self.files[os.path.abspath(self.mainFilename)][-1].endswith ("\n"):
                self.files[os.path.abspath(self.mainFilename)][-1] = self.files[os.path.abspath(self.mainFilename)][-1] + "\n"
        for i in range(len(self.otherFilenames)):
            # print ("file:", os.path.abspath(self.otherFilenames[i]))
            # ensure file exists
            if (not os.path.exists(os.path.abspath(self.otherFilenames[i]))):
                print (f"Compiler Error: '{self.otherFilenames[i]}' does not exist")
                print (f"   Current Dir: {os.getcwd()}")
                print (f"   Absolute Path: {os.path.abspath(self.otherFilenames[i])}")
                exit (1)
            # add file to included files 
            self.files[os.path.abspath(self.otherFilenames[i])] = open (os.path.abspath(self.otherFilenames[i]), "r").readlines ()
            # ensure last line ends in newline
            if len(self.files[os.path.abspath(self.otherFilenames[i])]) > 0:
                if not self.files[os.path.abspath(self.otherFilenames[i])][-1].endswith ("\n"):
                    self.files[os.path.abspath(self.otherFilenames[i])][-1] = self.files[os.path.abspath(self.otherFilenames[i])][-1] + "\n"

        #=== TOKENIZATION ================================================
        # Group source code characters into tokens to identify symbols/operators,
        # keywords, identifiers/variables, and number/string/char literals.
        # This simplifies/eliminates whitespace with the exception of newlines
        # which are needed for parsing instruction lines.
        # Tokenization will throw errors for invalid symbols and invalid
        # identifiers.

        self.debug ("Tokenizing...")
        # Tokenize each file
        fileTokens = {}
        for filename in self.files:
            self.debug (f"   Tokenizing '{filename}'...")
            fileLines = self.files[filename]
            fileContentsString = "".join (fileLines)
            fileTokens[filename] = tokenize (fileContentsString, filename, )

        # DEBUG - print tokens to a file
        for filename in fileTokens:
            tokens = fileTokens[filename]
            tokens_string = []
            for token in tokens:
                if (token.type == "IDENTIFIER" or token.type == "GVARIABLE" or token.type == "LVARIABLE"):
                    tokens_string += [f"{token.type}({token.lexeme}) "]
                elif token.type == "NEWLINE":
                    tokens_string += ["\n"]
                else:
                    tokens_string += [f"{token.type} "]
            tokens_string = "".join (tokens_string)
            tokens_file = open (f"{filename}.tokens", "w")
            tokens_file.write (tokens_string)
            tokens_file.close ()

        #=== PARSING =====================================================
        # Parsing groups tokens into code structures like instructions,
        # functions, and data structures.
        # Parsing results in an abstract syntax tree (AST) which describes how
        # each code structure is linked to each other, like the command and args
        # that define an instruction, and the instructions that define a function,
        # and the functions that define a file.
        # Since the parser is looking for specific code structures, it will
        # give an error if incorrect syntax is found.

        self.debug ("Parsing...")
        
        # Parse each file 
        fileASTs = {}
        for filename in self.files:
            self.debug (f"   Parsing '{filename}'...")
            fileLines = self.files[filename]
            tokens = fileTokens[filename]
            # Parse file
            parser = Parser (tokens, fileLines, False)
            fileASTs[filename] = parser.parse ()

        #=== SEMANTIC ANALYSIS ===========================================

        self.debug ("Analyzing semantics...")

        # semantically analyze each file's AST
        for filename in fileASTs:
            self.debug (f"   Analyzing semantics of AST for '{filename}'...")
            ast = fileASTs[filename]
            source_code_lines = self.files[filename]

            semanticAnalysisVisitor = SemanticAnalysisVisitor (source_code_lines, False)

            # Add built-in functions/variables to the symbol table
            # So we know what functions exist for checking for undefined symbols
            addBuiltinsToSymbolTable (semanticAnalysisVisitor.table)

            # Check AST
            # checks for:
            # - undeclared vars
            # - redeclared vars
            # - matching operand types
            # - valid instructions
            ast.accept (semanticAnalysisVisitor)
            # ensure it was successful 
            if (not semanticAnalysisVisitor.wasSuccessful):
                exit (1)

            # Reaches here if the file is semantically valid
            self.debug ("   Semantic analysis passes successfully")
        
        #=== PRINT AST ===================================================

        # DEBUG - print AST to file
        if self.emitAST:
            self.debug (f"Printing AST...")
            for filename in fileASTs:
                self.debug (f"   Printing AST for '{filename}'...")
                printVisitor = PrintVisitor ()
                ast = fileASTs[filename]
                ast.accept (printVisitor)
                astFilename = f"{filename}.ast"
                astFile = open (astFilename, "w")
                self.debug (f"   Writing AST to '{astFilename}'...")
                astFile.write ("".join (printVisitor.outputstrings))
                astFile.close ()

        #=== EMITTING IR =================================================
        # Regenerates the IR code and outputs to a file

        if self.emitIR:
            self.debug (f"Emitting IR...")
            for filename in fileASTs:
                ast = fileASTs[filename]
                self.debug (f"   Emitting IR for '{filename}'...")
                irEmitter = IREmitterVisitor ()
                ast.accept (irEmitter)
                irOutput = irEmitter.getIRCode ()
                irFilename = filename + ".ir"
                self.debug (f"   Writing IR to '{irFilename}'...")
                file = open (irFilename, "w")
                file.write (irOutput)

        #=== OPTIMIZATION ================================================
        # TODO: figure out what optimizations I can do

        #=== CODE GENERATION =============================================

        # keyed by filename
        self.debug (f"Generating code...")
        code_generators = {}
        for filename in fileASTs:
            ast = fileASTs[filename]
            source_code_lines = self.files[filename]
            if target == TARGET_AMYASM:
                code_generators[filename] = CodeGenVisitor_AmyAssembly (source_code_lines)
            elif target == TARGET_X86:
                code_generators[filename] = CodeGenVisitor_x86 (source_code_lines)
            else:
                print (f"Error: unknown target language '{target}'")
                exit (1)

            # generate code
            ast.accept (code_generators[filename])

            # Ensure codegen was successful
            if not code_generators[filename].wasSuccessful:
                print (f"Error: codegen failed on file '{filename}'")
                exit (1)

        #=== OUTPUT ======================================================
        # Combine generated code to a single executable/interpretable file.

        for filename in code_generators:
            code_generator = code_generators[filename]
            destCode = "".join(code_generator.code)

            # determine compiled filename
            if target == TARGET_AMYASM:
                dest_filename = f"{filename}.amyasm"
            elif target == TARGET_X86:
                dest_filename = f"{filename}.asm"
            else:
                print (f"Error: unknown target language '{target}'")
                exit (1)

            # output generated/compiled code to separate file
            self.debug (f"   Writing compiled code to \"{dest_filename}\"")
            file = open(dest_filename, "w")
            file.write (destCode)

        #=== END =========================================================

        print ("Compiled successfully!")
        return None

    def debug(self, *args, **kwargs):
        """Custom debug print function."""
        if (self.shouldPrintDebug):
            print(*args, **kwargs)

# ========================================================================

def printAST (ast):
    printVisitor = PrintVisitor ()
    ast.accept (printVisitor)
    return "".join (printVisitor.outputstrings)

# ========================================================================

def analyzeSemantics (ast, sourceCodeLines):
    semanticAnalysisVisitor = SemanticAnalysisVisitor (sourceCodeLines, False)
    # Add built-in functions/variables to the symbol table
    # So we know what functions exist for checking for undefined symbols
    addBuiltinsToSymbolTable (semanticAnalysisVisitor.table)
    # Check ast
    ast.accept (semanticAnalysisVisitor)
    return semanticAnalysisVisitor.wasSuccessful

# ========================================================================

def generateCode (ast, sourceCodeLines, target):
    if target == TARGET_AMYASM:
        codegenVisitor = CodeGenVisitor_AmyAssembly (sourceCodeLines)
    elif target == TARGET_X86:
        codegenVisitor = CodeGenVisitor_x86 (sourceCodeLines)
    else:
        print (f"Error: unknown target language '{target}'")
        exit (1)

    # generate code
    ast.accept (codegenVisitor)

    # Ensure codegen was successful
    if not codegenVisitor.wasSuccessful:
        print (f"Error: codegen failed")
        exit (1)

    # NOTE: this should be a getter .getGeneratedCode
    return "".join (codegenVisitor.code)

# ========================================================================

if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="CeruleanIR Compiler")

    argparser.add_argument(dest="sourceFiles", nargs="+", help="source files to compile (first file should be the main file)")
    argparser.add_argument("-o", "--outputFilename", dest="outputFilename", help="name of the outputted compiled file")
    argparser.add_argument("--emitAST", dest="emitAST", action="store_true", help="output the Abstract Syntax Tree (AST)")
    argparser.add_argument("--emitIR", dest="emitIR", action="store_true", help="output the IR")
    argparser.add_argument("--target", nargs=1, dest="target", help="specifies the target language to compile to [default amyasm] (amyasm, x86)")
    argparser.add_argument("--debug", dest="debug", action="store_true", help="output debug info")

    args = argparser.parse_args()

    mainFilename = args.sourceFiles[0]
    otherFilenames = args.sourceFiles[1:]
    destFilename = "a.amyasm" # this assumes target is AmyAssembly
    if args.outputFilename:
        destFilename = args.outputFilename

    # ensure valid target
    if args.target == None or args.target[0] == "amyasm": # Default 
        target=TARGET_AMYASM
    elif args.target[0] == "x86":  # Intel x86
        target=TARGET_X86
    elif args.target[0] == "python": # transpile to python
        target=TARGET_PYTHON
    elif args.target[0] == "cpp": # transpile to python
        target=TARGET_CPP
    else: # Invalid/unknown target
        print (f"Error: Unknown target '{args.target}'")
        exit (1)

    # output compilation info
    print ("target      :", target)
    print ("destFilename:", destFilename)

    # compile code 
    compiler = CeruleanIRCompiler (
        mainFilename, 
        otherFilenames, 
        destFilename=destFilename,
        emitAST=args.emitAST,
        emitIR=args.emitIR,
        target=target,
        debug=args.debug
    )
    destCode = compiler.compile ()


