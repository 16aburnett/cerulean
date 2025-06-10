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

            def add_builtin_function (return_type, function_name, parameters):
                builtin_function_node = FunctionNode (return_type, f"@{function_name}", None, parameters, None)
                builtin_function_node.scopeName = function_name
                builtin_function_node.label = builtin_function_node.scopeName
                # create signature for node
                signature = [f"{builtin_function_node.id}("]
                if len(builtin_function_node.params) > 0:
                    signature += [builtin_function_node.params[0].type.__str__()]
                for i in range(1, len(builtin_function_node.params)):
                    signature += [f", {builtin_function_node.params[i].type.__str__()}"]
                signature += [")"]
                signature = "".join(signature)
                builtin_function_node.signature = signature
                semanticAnalysisVisitor.table.insert (builtin_function_node, builtin_function_node.id, Kind.FUNC)

            # Add built-in functions/variables 
            #  char[] input ();
            add_builtin_function (
                TypeSpecifierNode (Type.PTR, "ptr", None, 0),
                f"{BUILTIN_PREFIX}input",
                []
            )
            #  void print (char[] str);
            add_builtin_function (
                TypeSpecifierNode (Type.VOID, "void", None, 0),
                f"{BUILTIN_PREFIX}print__char__1",
                [ParameterNode(TypeSpecifierNode (Type.PTR, "ptr", None, 0), "str", None)]
            )
            #  void print__int32 (int32 val);
            add_builtin_function (
                TypeSpecifierNode (Type.VOID, "void", None, 0),
                f"{BUILTIN_PREFIX}print__int32",
                [ParameterNode(TypeSpecifierNode (Type.INT32, "int32", None, 0), "val", None)]
            )
            #  void print__int64 (int64 val);
            add_builtin_function (
                TypeSpecifierNode (Type.VOID, "void", None, 0),
                f"{BUILTIN_PREFIX}print__int64",
                [ParameterNode(TypeSpecifierNode (Type.INT64, "int64", None, 0), "val", None)]
            )
            #  void @print__float32 (float32 val);
            add_builtin_function (
                TypeSpecifierNode (Type.VOID, "void", None, 0),
                f"{BUILTIN_PREFIX}print__float32",
                [ParameterNode(TypeSpecifierNode (Type.FLOAT32, "float32", None, 0), "val", None)]
            )
            #  void @print__float64 (float64 val);
            add_builtin_function (
                TypeSpecifierNode (Type.VOID, "void", None, 0),
                f"{BUILTIN_PREFIX}print__float64",
                [ParameterNode(TypeSpecifierNode (Type.FLOAT64, "float64", None, 0), "val", None)]
            )
            #  void @print__char (char val);
            add_builtin_function (
                TypeSpecifierNode (Type.VOID, "void", None, 0),
                f"{BUILTIN_PREFIX}print__char",
                [ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None, 0), "val", None)]
            )

        #     #  void print (Enum e);
        #     param0 = ParameterNode(TypeSpecifierNode (Type.USERTYPE, "Enum", None), "e", None)
        #     printEnumFunc = FunctionNode (TypeSpecifierNode (Type.VOID, "void", None), "print", None, [param0], None)
        #     printEnumFunc.scopeName = BUILTIN_PREFIX+"print__Enum"
        #     printEnumFunc.label = printEnumFunc.scopeName
        #     # create signature for node
        #     signature = [f"{printEnumFunc.id}("]
        #     if len(printEnumFunc.params) > 0:
        #         signature += [printEnumFunc.params[0].type.__str__()]
        #     for i in range(1, len(printEnumFunc.params)):
        #         signature += [f", {printEnumFunc.params[i].type.__str__()}"]
        #     signature += [")"]
        #     signature = "".join(signature)
        #     printEnumFunc.signature = signature
        #     semanticAnalysisVisitor.table.insert (printEnumFunc, printEnumFunc.id, Kind.FUNC)

            #  void println (char[] str);
            add_builtin_function (
                TypeSpecifierNode (Type.VOID, "void", None, 0),
                f"{BUILTIN_PREFIX}println__char__1",
                [ParameterNode(TypeSpecifierNode (Type.PTR, "ptr", None, 0), "str", None)]
            )
            #  void println (int32 intToPrint);
            add_builtin_function (
                TypeSpecifierNode (Type.VOID, "void", None, 0),
                f"{BUILTIN_PREFIX}println__int32",
                [ParameterNode(TypeSpecifierNode (Type.INT32, "int32", None, 0), "intToPrint", None)]
            )
            #  void println (int64 intToPrint);
            add_builtin_function (
                TypeSpecifierNode (Type.VOID, "void", None, 0),
                f"{BUILTIN_PREFIX}println__int64",
                [ParameterNode(TypeSpecifierNode (Type.INT64, "int64", None, 0), "intToPrint", None)]
            )
            #  void println (float32 floatToPrint);
            add_builtin_function (
                TypeSpecifierNode (Type.VOID, "void", None, 0),
                f"{BUILTIN_PREFIX}println__float32",
                [ParameterNode(TypeSpecifierNode (Type.FLOAT32, "float32", None, 0), "floatToPrint", None)]
            )
            #  void println (float64 floatToPrint);
            add_builtin_function (
                TypeSpecifierNode (Type.VOID, "void", None, 0),
                f"{BUILTIN_PREFIX}println__float64",
                [ParameterNode(TypeSpecifierNode (Type.FLOAT64, "float64", None, 0), "floatToPrint", None)]
            )
            #  void println (char c);
            add_builtin_function (
                TypeSpecifierNode (Type.VOID, "void", None, 0),
                f"{BUILTIN_PREFIX}println__char",
                [ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None, 0), "c", None)]
            )

        #     #  void println (Enum e);
        #     param0 = ParameterNode(TypeSpecifierNode (Type.USERTYPE, "Enum", None), "e", None)
        #     printEnumFunc = FunctionNode (TypeSpecifierNode (Type.VOID, "void", None), "println", None, [param0], None)
        #     printEnumFunc.scopeName = BUILTIN_PREFIX+"println__Enum"
        #     printEnumFunc.label = printEnumFunc.scopeName
        #     # create signature for node
        #     signature = [f"{printEnumFunc.id}("]
        #     if len(printEnumFunc.params) > 0:
        #         signature += [printEnumFunc.params[0].type.__str__()]
        #     for i in range(1, len(printEnumFunc.params)):
        #         signature += [f", {printEnumFunc.params[i].type.__str__()}"]
        #     signature += [")"]
        #     signature = "".join(signature)
        #     printEnumFunc.signature = signature
        #     semanticAnalysisVisitor.table.insert (printEnumFunc, printEnumFunc.id, Kind.FUNC)

            #  void println ();
            add_builtin_function (
                TypeSpecifierNode (Type.VOID, "void", None, 0),
                f"{BUILTIN_PREFIX}println",
                []
            )
            #  void exit ();
            add_builtin_function (
                TypeSpecifierNode (Type.VOID, "void", None, 0),
                f"{BUILTIN_PREFIX}exit",
                []
            )
            #  void exit (int exit_status);
            # for x86 this directly calls the system exit
            add_builtin_function (
                TypeSpecifierNode (Type.VOID, "void", None, 0),
                f"{BUILTIN_PREFIX}exit__int32",
                [ParameterNode(TypeSpecifierNode (Type.INT32, "int32", None), "exit_status", None)]
            )
            #  float32 float32 ();
            add_builtin_function (
                TypeSpecifierNode (Type.FLOAT32, "float32", None, 0),
                f"{BUILTIN_PREFIX}float32",
                []
            )
            #  float64 float64 ();
            add_builtin_function (
                TypeSpecifierNode (Type.FLOAT64, "float64", None, 0),
                f"{BUILTIN_PREFIX}float64",
                []
            )
            # float32 int32ToFloat32 (int32 val);
            add_builtin_function (
                TypeSpecifierNode (Type.FLOAT32, "float32", None, 0),
                f"{BUILTIN_PREFIX}int32ToFloat32",
                [ParameterNode(TypeSpecifierNode (Type.INT32, "int32", None, 0), "val", None)]
            )
            # float64 int64ToFloat64 (int64 val);
            add_builtin_function (
                TypeSpecifierNode (Type.FLOAT64, "float64", None, 0),
                f"{BUILTIN_PREFIX}int64ToFloat64",
                [ParameterNode(TypeSpecifierNode (Type.INT64, "int64", None, 0), "val", None)]
            )
            # TODO: float64 int32ToFloat64 (int32 val);
            # TODO: float32 int64ToFloat32 (int64 val);
            #  float32 stringToFloat32 (char[]);
            add_builtin_function (
                TypeSpecifierNode (Type.FLOAT32, "float32", None, 0),
                f"{BUILTIN_PREFIX}stringToFloat32__char__1",
                [ParameterNode(TypeSpecifierNode (Type.PTR, "ptr", None, 0), "val", None)]
            )
            #  float64 stringToFloat64 (char[]);
            add_builtin_function (
                TypeSpecifierNode (Type.FLOAT64, "float64", None, 0),
                f"{BUILTIN_PREFIX}stringToFloat64__char__1",
                [ParameterNode(TypeSpecifierNode (Type.PTR, "ptr", None, 0), "val", None)]
            )
            #  int32 int32 ();
            add_builtin_function (
                TypeSpecifierNode (Type.INT32, "int32", None, 0),
                f"{BUILTIN_PREFIX}int32",
                []
            )
            #  int64 int64 ();
            add_builtin_function (
                TypeSpecifierNode (Type.INT64, "int64", None, 0),
                f"{BUILTIN_PREFIX}int64",
                []
            )
            #  char char ();
            add_builtin_function (
                TypeSpecifierNode (Type.CHAR, "char", None, 0),
                f"{BUILTIN_PREFIX}char",
                []
            )
            #  int32 float32ToInt32 (float32);
            add_builtin_function (
                TypeSpecifierNode (Type.INT32, "int32", None, 0),
                f"{BUILTIN_PREFIX}float32ToInt32__float32",
                [ParameterNode(TypeSpecifierNode (Type.FLOAT32, "float32", None, 0), "val", None)]
            )
            #  int64 float64ToInt64 (float64);
            add_builtin_function (
                TypeSpecifierNode (Type.INT64, "int64", None, 0),
                f"{BUILTIN_PREFIX}float64ToInt64__float64",
                [ParameterNode(TypeSpecifierNode (Type.FLOAT64, "float64", None, 0), "val", None)]
            )
            # TODO: int32 float64ToInt64 (float64 val);
            # TODO: int64 float64ToInt64 (float32 val);
            #  int32 stringToInt32 (char[]);
            add_builtin_function (
                TypeSpecifierNode (Type.INT32, "int32", None, 0),
                f"{BUILTIN_PREFIX}stringToInt32__char__1",
                [ParameterNode(TypeSpecifierNode (Type.PTR, "ptr", None, 0), "val", None)]
            )
            #  int64 stringToInt64 (char[]);
            add_builtin_function (
                TypeSpecifierNode (Type.INT64, "int64", None, 0),
                f"{BUILTIN_PREFIX}stringToInt64__char__1",
                [ParameterNode(TypeSpecifierNode (Type.PTR, "ptr", None, 0), "val", None)]
            )
            #  int32 charToInt32 (char);
            add_builtin_function (
                TypeSpecifierNode (Type.INT32, "int32", None, 0),
                f"{BUILTIN_PREFIX}charToInt32__char",
                [ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None, 0), "val", None)]
            )
            #  int64 charToInt64 (char);
            add_builtin_function (
                TypeSpecifierNode (Type.INT64, "int64", None, 0),
                f"{BUILTIN_PREFIX}charToInt64__char",
                [ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None, 0), "val", None)]
            )
            #  char[] string (int32);
            add_builtin_function (
                TypeSpecifierNode (Type.PTR, "ptr", None, 0),
                f"{BUILTIN_PREFIX}string__int32",
                [ParameterNode(TypeSpecifierNode (Type.INT32, "int32", None, 0), "val", None)]
            )
            #  char[] string (int64);
            add_builtin_function (
                TypeSpecifierNode (Type.PTR, "ptr", None, 0),
                f"{BUILTIN_PREFIX}string__int64",
                [ParameterNode(TypeSpecifierNode (Type.INT64, "int64", None, 0), "val", None)]
            )
            #  char[] string (float32);
            add_builtin_function (
                TypeSpecifierNode (Type.PTR, "ptr", None, 0),
                f"{BUILTIN_PREFIX}string__float32",
                [ParameterNode(TypeSpecifierNode (Type.FLOAT32, "float32", None, 0), "val", None)]
            )
            #  char[] string (float64);
            add_builtin_function (
                TypeSpecifierNode (Type.PTR, "ptr", None, 0),
                f"{BUILTIN_PREFIX}string__float64",
                [ParameterNode(TypeSpecifierNode (Type.FLOAT64, "float64", None, 0), "val", None)]
            )
            #  void* null ();
            add_builtin_function (
                TypeSpecifierNode (Type.PTR, "ptr", None, 0),
                f"{BUILTIN_PREFIX}null",
                []
            )


            # # LIBRARY OBJECTS

            # # create default object type 
            # # class Object
            # # {
            # #   public virtual char[] toString ()
            # #   {
            # #       return "<Object>";
            # #   }
            # # }
            # objClass = ClassDeclarationNode (TypeSpecifierNode (Type.USERTYPE, "Object", None), "Object", None, None, [], [], [], [], [])
            # objClass.scopeName = BUILTIN_PREFIX+"__main__Object"
            # semanticAnalysisVisitor.table.insert (objClass, "Object", Kind.TYPE)

            # # create default object type 
            # enumClass = ClassDeclarationNode (TypeSpecifierNode (Type.USERTYPE, "Enum", None), "Enum", None, None, ["Object"], [], [], [], [])
            # enumClass.scopeName = BUILTIN_PREFIX+"__main__Enum"
            # semanticAnalysisVisitor.table.insert (enumClass, "Enum", Kind.TYPE)

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

if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Tests argparse")

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


