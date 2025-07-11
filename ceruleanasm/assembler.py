# CeruleanASM Assembler
# By Amy Burnett
# ========================================================================

import os
import sys 
from sys import exit
from enum import Enum
import argparse 

from .tokenizer import tokenize
from .AST import *
from .parser import Parser
from .visitor import *
from .printVisitor import PrintVisitor
from .semanticAnalysis import SemanticAnalysisVisitor
from .addressAssigner import AddressAssignerVisitor
from .referenceResolver import ReferenceResolverVisitor
from .bytecodeGenerator import BytecodeGeneratorVisitor

# ========================================================================

class CeruleanAssembler:

    def __init__(self, sourceFilename, destFilename, debug=False, emitTokens=False, emitAST=False):
        self.sourceFilename = sourceFilename
        self.destFilename = destFilename
        self.shouldPrintDebug = debug

        self.emitTokens = emitTokens
        self.tokensFilename = sourceFilename + ".tokens"
        self.emitAST = emitAST
        self.astFilename = sourceFilename + ".ast"

        self.debugLines = []

    def printDebug (self, *args, **kwargs):
        """Custom debug print function."""
        if (self.shouldPrintDebug):
            print(*args, **kwargs)

    #---------------------------------------------------------------------

    def assemble (self):

        # -----------------------------------------------------------------------------------------
        # READING

        # Ensure source file exists
        if not os.path.isfile (self.sourceFilename):
            print (f"Error: '{self.sourceFilename}' does not exist or is not a file")
            exit (1)

        with open (self.sourceFilename, "r") as f:
            rawSourceCode = f.read ()
            lines = rawSourceCode.split ("\n")

        # -----------------------------------------------------------------------------------------
        # TOKENIZATION

        self.printDebug ("Tokenizing...")
        # tokens = tokenize (rawSourceCode, self.sourceFilename, self.debugLines)
        tokens = tokenize (rawSourceCode, self.sourceFilename, lines)
        if self.emitTokens:
            tokenStrings = [""]
            currline = 1
            for token in tokens:
                if token.type == "NEWLINE":
                    tokenStrings.append (f"{token.type} ")
                    tokenStrings.append ("\n")
                else:
                    tokenStrings.append (f"{token.type}({token.lexeme}) ")
            self.printDebug (f"Writing Tokens to \"{self.tokensFilename}\"")
            file = open (self.tokensFilename, "w")
            file.write ("".join (tokenStrings))

        # -----------------------------------------------------------------------------------------
        # PARSING

        self.printDebug ("Parsing...")    
        parser = Parser (tokens, lines, False)
        ast = parser.parse ()

        # -----------------------------------------------------------------------------------------
        # PRINT AST

        # DEBUG - print AST to file
        if self.emitAST:
            self.printDebug (f"Printing AST to '{self.astFilename}'...")
            printVisitor = PrintVisitor ()
            output = printVisitor.print (ast)
            astFile = open (self.astFilename, "w")
            astFile.write (output)
            astFile.close ()

        # -----------------------------------------------------------------------------------------
        # Semantic analysis

        semanticAnalyzer = SemanticAnalysisVisitor ()
        ast.accept (semanticAnalyzer)

        if not semanticAnalyzer.wasSuccessful:
            print ("ERROR: Semantic Analysis failed")
            exit (1)

        # -----------------------------------------------------------------------------------------
        # Assign addresses to instructions

        symbolTable = {}
        addressAssigner = AddressAssignerVisitor (symbolTable)
        ast.accept (addressAssigner)

        print ("symbolTable: ", symbolTable)

        # for instruction in ast.codeunits:
        #     if isinstance (instruction, InstructionNode):
        #         print (f"{hex (instruction.address)}: {instruction.opcode}")

        # -----------------------------------------------------------------------------------------
        # Resolve labels

        referenceResolver = ReferenceResolverVisitor (symbolTable)
        ast.accept (referenceResolver)

        print ("relocationTable: ", referenceResolver.relocationTable)

        # for instruction in ast.codeunits:
        #     if isinstance (instruction, InstructionNode):
        #         for arg in instruction.args:
        #             if isinstance (arg, LabelExpressionNode):
        #                 print (arg.id, ":", arg.address)

        # -----------------------------------------------------------------------------------------
        # Bytecode encoding/generation

        codegenerator = BytecodeGeneratorVisitor (symbolTable)
        ast.accept (codegenerator)

        # print ("bytecode:", codegenerator.bytecode)
        # for i in range (0, len(codegenerator.bytecode), 4):
        #     print (
        #         f"{codegenerator.bytecode[i+0]:02x}",
        #         f"{codegenerator.bytecode[i+1]:02x}",
        #         f"{codegenerator.bytecode[i+2]:02x}",
        #         f"{codegenerator.bytecode[i+3]:02x}"
        #         )

        # -----------------------------------------------------------------------------------------
        # Output bytecode

        print (f"Writing bytecode to \"{self.destFilename}\"")
        with open (self.destFilename, "wb") as f:
            f.write (codegenerator.bytecode)

        #=== END =================================================================


# ========================================================================

if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="CeruleanASM Assembler")
    argparser.add_argument(dest="sourceFile", help="CeruleanASM file to assemble")
    argparser.add_argument("-o", "--outputFilename", dest="outputFilename", help="name to give the outputted assembled file")
    argparser.add_argument("--debug", dest="debug", action="store_true", help="enable debug output")
    argparser.add_argument("--emitTokens", dest="emitTokens", action="store_true", help="output the lexed tokens")
    argparser.add_argument("--emitAST", dest="emitAST", action="store_true", help="output the ast")

    args = argparser.parse_args()

    if args.outputFilename:
        destFilename = args.outputFilename
    else:
        destFilename = os.path.splitext(args.sourceFile)[0] + ".ceruleanobj"

    assembler = CeruleanAssembler (
        args.sourceFile,
        destFilename=destFilename,
        debug=args.debug,
        emitTokens=args.emitTokens,
        emitAST=args.emitAST,
    )
    destCode = assembler.assemble ()
