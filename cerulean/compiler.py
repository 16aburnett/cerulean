# Cerulean Compiler
# Cerulean is a C/C++ like programming language
# By Amy Burnett
# June 5, 2025
# ========================================================================

import sys 
from sys import exit
from enum import Enum
import argparse 

if __name__ == "__main__":
    from .preprocessor import CeruleanPreprocessor
    from .tokenizer import tokenize
    from .ceruleanAST import *
    from .parser import Parser
    from .visitor import *
    from .printVisitor import PrintVisitor
    from .builtins import addBuiltinsToSymbolTable
    from .semanticAnalyzer import *
    from .codegen import CodeGenVisitor
    from .irGenerator import IRGeneratorVisitor
    from backend.compiler import CeruleanIRBackendCompiler, TargetLang
    from backend.backends.ceruleanrisc.codegen import AllocatorStrategy
else:
    from .preprocessor import CeruleanPreprocessor
    from .tokenizer import tokenize
    from .ceruleanAST import *
    from .parser import Parser
    from .visitor import *
    from .printVisitor import PrintVisitor
    from .semanticAnalyzer import *
    from .codeGen import CodeGenVisitor
    from .irGenerator import IRGeneratorVisitor
    from backend.printVisitor import PrintVisitor as IRPrintVisitor


# ========================================================================

class CeruleanCompiler:

    def __init__(self, mainFilename, otherFilenames, destFilename="a.amy.assembly", debug=False, emitTokens=False, emitAST=False, emitIR=False, emitIRAST=False, emitPreprocessed=False, preprocess=False, target=TargetLang.AMYASM):
        self.mainFilename = mainFilename
        self.otherFilenames = otherFilenames
        self.destFilename = destFilename
        self.files = {}
        self.debug = debug

        self.emitPreprocessed = emitPreprocessed
        self.onlyPreprocess = preprocess
        self.emitTokens = emitTokens
        self.tokensFilename = mainFilename + ".tokens"
        self.emitAST = emitAST
        self.astFilename = mainFilename + ".ast"
        self.emitIR = emitIR
        self.irFilename = mainFilename + ".ir"
        self.emitIRAST = emitIRAST
        self.irASTFilename = mainFilename + ".irast"

        self.debugLines = []

        self.target = target

    #---------------------------------------------------------------------

    def compile (self):

        #=== PREPROCESSING =======================================================

        # send through preprocessor
        pp = CeruleanPreprocessor (mainFilename, otherFilenames, emitPreprocessed=self.emitPreprocessed)
        preprocessedCode = pp.process ()
        self.debugLines = pp.outputLines
        self.files = pp.files 

        lines = preprocessedCode.split ("\n")

        # exit if only preprocessing
        if self.onlyPreprocess:
            return

        #=== TOKENIZATION ========================================================

        if (self.debug):
            print ("Tokenizing...")
        tokens = tokenize(preprocessedCode, self.mainFilename, self.debugLines)
        if self.emitTokens:
            tokenStrings = [""]
            currline = 1
            for token in tokens:
                while token.line != currline:
                    currline += 1
                    tokenStrings.append ("\n")
                tokenStrings.append (token.type)
                tokenStrings.append (' ')
            print (f"Writing Tokens to \"{self.tokensFilename}\"")
            file = open (self.tokensFilename, "w")
            file.write ("".join (tokenStrings))

        #=== PARSING =============================================================

        if (self.debug):
            print ("Parsing...")    
        parser = Parser(tokens, lines, False)
        ast = parser.parse()

        #=== SEMANTIC ANALYSIS ===================================================

        if (self.debug):
            print ("Analyzing Semantics...")
        symbolTableVisitor = SymbolTableVisitor (lines)

        # Add built-in functions/variables to the symbol table
        # So we know what functions exist for checking for undefined symbols
        addBuiltinsToSymbolTable (symbolTableVisitor.table)

        # Check AST
        # checks for 
        # - undeclared vars 
        # - redeclared vars 
        # - matching operand types 
        ast.accept (symbolTableVisitor)
        # ensure it was successful 
        if (not symbolTableVisitor.wasSuccessful):
            exit (1)

        # Reaches Here if the code is valid
        if (self.debug):
            print ("Passes Semantic Analysis")

        if self.emitAST:
            print (f"Writing AST to \"{self.astFilename}\"")
            # get a string representation of the ast 
            visitor = PrintVisitor ()
            visitor.visitProgramNode (ast)
            astOutput = "".join (visitor.outputstrings)

            file = open (self.astFilename, "w")
            file.write (astOutput)

        #=== CONVERT TO IR =======================================================

        if (self.debug):
            print ("Converting to IR...")
        irGeneratorVisitor = IRGeneratorVisitor (lines)
        # Generate IR AST
        ast.accept (irGeneratorVisitor)
        irAST = irGeneratorVisitor.ast
        
        #=== BACKEND COMPILATION =================================================
        # Backend handles: IR semantic analysis, IR emission, AST printing, code generation, and more

        if (self.debug):
            print (f"Offloading code to backend...")
        backendCompiler = CeruleanIRBackendCompiler(debug=self.debug)
        code = backendCompiler.compile(irAST, lines, self.mainFilename, 
            emitAST=self.emitIRAST, emitIR=self.emitIR, target=self.target, regalloc=AllocatorStrategy.NAIVE)

        #=== OUTPUT ==============================================================

        print (f"Writing compiled code to \"{destFilename}\"")
        file = open(destFilename, "w")
        file.write (code)

        #=== END =================================================================


# ========================================================================

if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Tests argparse")

    argparser.add_argument(dest="sourceFiles", nargs="+", help="source files to compile (first file should be the main file)")
    argparser.add_argument("-o", "--outputFilename", dest="outputFilename", help="name of the outputted compiled file")
    argparser.add_argument("--debug", dest="debug", action="store_true", help="enable debug output")
    argparser.add_argument("--emitPreprocessed", dest="emitPreprocessed", action="store_true", help="output the preprocessed code")
    argparser.add_argument("--emitTokens", dest="emitTokens", action="store_true", help="output the lexed tokens")
    argparser.add_argument("--emitAST", dest="emitAST", action="store_true", help="output the ast")
    argparser.add_argument("--emitIR", dest="emitIR", action="store_true", help="output the generated IR")
    argparser.add_argument("--emitIRAST", dest="emitIRAST", action="store_true", help="output the AST of the generated IR")
    argparser.add_argument("--preprocess", dest="preprocess", action="store_true", help="only run preprocessor")
    argparser.add_argument("--target", dest="target", type=str,
        choices=[lang.value for lang in TargetLang], default=TargetLang.AMYASM.value,
        help="specifies the target language to compile to [default: amyasm]")

    args = argparser.parse_args()

    mainFilename = args.sourceFiles[0]
    otherFilenames = args.sourceFiles[1:]
    destFilename = "a.amyasm"
    if args.outputFilename:
        destFilename = args.outputFilename

    target = TargetLang(args.target)

    # output compilation info 
    print ("target      :", target)
    print ("destFilename:", destFilename)

    # compile code 
    compiler = CeruleanCompiler (
        mainFilename, 
        otherFilenames, 
        destFilename=destFilename,
        debug=args.debug,
        emitTokens=args.emitTokens,
        emitAST=args.emitAST,
        emitIR=args.emitIR,
        emitIRAST=args.emitIRAST,
        emitPreprocessed=args.emitPreprocessed, 
        preprocess=args.preprocess,
        target=target
    )
    destCode = compiler.compile ()


