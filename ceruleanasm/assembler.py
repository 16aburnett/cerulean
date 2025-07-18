# CeruleanASM Assembler
# By Amy Burnett
# ========================================================================

import os
import sys
from sys import exit
from enum import Enum
import argparse
import json

from .tokenizer import tokenize
from .AST import *
from .parser import Parser
from .visitor import *
from .printVisitor import PrintVisitor
from .semanticAnalysis import SemanticAnalysisVisitor
from .lowering import LoweringVisitor
from .addressAssigner import AddressAssignerVisitor
from .referenceResolver import ReferenceResolverVisitor
from .bytecodeGenerator import BytecodeGeneratorVisitor

# ========================================================================

class CeruleanAssembler:

    def __init__(self, debug=False):
        self.shouldPrintDebug = debug

    def printDebug (self, *args, **kwargs):
        """Custom debug print function."""
        if (self.shouldPrintDebug):
            print(*args, **kwargs)

    #---------------------------------------------------------------------

    def assemble (self, rawSourceCode, sourceFilename, emitTokens=False, emitAST=False):

        lines = rawSourceCode.split ("\n")

        # -----------------------------------------------------------------------------------------
        # TOKENIZATION

        self.printDebug ("Tokenizing...")
        tokens = tokenize (rawSourceCode, sourceFilename, lines)

        # Printing tokens
        if emitTokens:
            tokensFilename = sourceFilename + ".tokens"
            tokenStrings = [""]
            currline = 1
            for token in tokens:
                if token.type == "NEWLINE":
                    tokenStrings.append (f"{token.type} ")
                    tokenStrings.append ("\n")
                else:
                    tokenStrings.append (f"{token.type}({token.lexeme}) ")
            self.printDebug (f"Writing Tokens to \"{tokensFilename}\"")
            file = open (tokensFilename, "w")
            file.write ("".join (tokenStrings))

        # -----------------------------------------------------------------------------------------
        # PARSING

        self.printDebug ("Parsing...")
        parser = Parser (tokens, lines, False)
        ast = parser.parse ()

        # -----------------------------------------------------------------------------------------
        # PRINT AST

        # DEBUG - print AST to file
        if emitAST:
            astFilename = sourceFilename + ".ast"
            self.printDebug (f"Printing AST to '{astFilename}'...")
            printVisitor = PrintVisitor ()
            output = printVisitor.print (ast)
            astFile = open (astFilename, "w")
            astFile.write (output)
            astFile.close ()

        # -----------------------------------------------------------------------------------------
        # Semantic analysis

        self.printDebug ("Analyzing semantics...")
        semanticAnalyzer = SemanticAnalysisVisitor ()
        semanticAnalyzer.analyze (ast)

        if not semanticAnalyzer.wasSuccessful:
            print ("ERROR: Semantic Analysis failed")
            exit (1)

        # -----------------------------------------------------------------------------------------
        # Lowering pass
        # - Expands pseudo-instructions

        self.printDebug ("Lowering AST...")
        lowerer = LoweringVisitor ()
        lowerer.lower (ast)

        # -----------------------------------------------------------------------------------------
        # PRINT AST after lowering

        # DEBUG - print AST to file
        if emitAST:
            astFilename = sourceFilename + ".ast_lowered"
            self.printDebug (f"Printing AST to '{astFilename}'...")
            printVisitor = PrintVisitor ()
            output = printVisitor.print (ast)
            astFile = open (astFilename, "w")
            astFile.write (output)
            astFile.close ()

        # -----------------------------------------------------------------------------------------
        # Assign addresses to instructions

        self.printDebug ("Assigning addresses...")
        symbolTable = {}
        addressAssigner = AddressAssignerVisitor (symbolTable)
        ast.accept (addressAssigner)

        self.printDebug ("symbolTable: ", symbolTable)

        # for instruction in ast.codeunits:
        #     if isinstance (instruction, InstructionNode):
        #         print (f"{hex (instruction.address)}: {instruction.opcode}")

        # -----------------------------------------------------------------------------------------
        # Resolve labels

        self.printDebug ("Resolving references...")
        referenceResolver = ReferenceResolverVisitor (symbolTable)
        ast.accept (referenceResolver)

        self.printDebug ("relocationTable: ", referenceResolver.relocationTable)

        # for instruction in ast.codeunits:
        #     if isinstance (instruction, InstructionNode):
        #         for arg in instruction.args:
        #             if isinstance (arg, LabelExpressionNode):
        #                 print (arg.id, ":", arg.address)

        # -----------------------------------------------------------------------------------------
        # Bytecode encoding/generation

        self.printDebug ("Generating bytecode...")
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
        # Package together object data

        objectData = {
            "filename": sourceFilename,
            "bytecode": list(codegenerator.bytecode),
            "symbols" : symbolTable,
            "relocations": referenceResolver.relocationTable
        }

        return objectData

        #=== END =================================================================


# ========================================================================

if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="CeruleanASM Assembler")
    argparser.add_argument(dest="sourceFilename", help="CeruleanASM file to assemble")
    argparser.add_argument("-o", "--outputFilename", dest="outputFilename", help="name to give the outputted assembled file")
    argparser.add_argument("--debug", dest="debug", action="store_true", help="enable debug output")
    argparser.add_argument("--emitTokens", dest="emitTokens", action="store_true", help="output the lexed tokens")
    argparser.add_argument("--emitAST", dest="emitAST", action="store_true", help="output the ast")

    args = argparser.parse_args()

    sourceFilename = args.sourceFilename
    if args.outputFilename:
        destFilename = args.outputFilename
    else:
        destFilename = os.path.splitext(args.sourceFilename)[0] + ".ceruleanobj"

    # Ensure source file exists
    if not os.path.isfile (sourceFilename):
        print (f"Error: '{sourceFilename}' does not exist or is not a file")
        exit (1)

    # Read source code
    with open (sourceFilename, "r") as f:
        rawSourceCode = f.read ()

    assembler = CeruleanAssembler (
        debug=args.debug,
    )
    objectData = assembler.assemble (
        rawSourceCode,
        sourceFilename,
        emitTokens=args.emitTokens,
        emitAST=args.emitAST
    )

    # Write target code
    print (f"Writing object code to \"{destFilename}\"")
    with open (destFilename, "w") as f:
        json.dump (objectData, f, indent=4)
