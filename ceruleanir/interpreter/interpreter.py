# CeruleanIR Interpreter
# This is an interpreter for CeruleanIR programs. It takes CeruleanIR code as input and executes it
# according to the semantics defined for the language.
# Author: Amy Burnett
# =================================================================================================

import sys

# Use existing tokenizer and parser from ceruleanir frontend
from ..tokenizer import tokenize
from ..parser import Parser

# Import semantic analyzer from backend
from backend.semanticAnalyzer import SemanticAnalysisVisitor
from backend.builtins import addBuiltinsToSymbolTable

# Import the interpreter visitor
from .visitor import InterpreterVisitor

# =================================================================================================

class CeruleanIRInterpreter:
    """
    Main interpreter class that handles parsing and execution.
    """
    
    def __init__(self, debug=False):
        self.debug = debug
    
    def interpret(self, rawSourceCode, sourceFilename="<input>"):
        """
        Parse and execute CeruleanIR code.
        
        Args:
            rawSourceCode: CeruleanIR source code as string
            sourceFilename: Name of source file (for error messages)
        
        Returns:
            Exit code from main function
        """
        sourceCodeLines = rawSourceCode.split("\n")
        
        # === TOKENIZATION ===
        if self.debug:
            print("Tokenizing...")
        tokens = tokenize(rawSourceCode, sourceFilename)
        
        # === PARSING ===
        if self.debug:
            print("Parsing...")
        parser = Parser(tokens, sourceCodeLines, doDebug=self.debug)
        ast = parser.parse()
        
        # === SEMANTIC ANALYSIS ===
        if self.debug:
            print("Analyzing semantics...")
        semanticAnalyzer = SemanticAnalysisVisitor(sourceCodeLines, debug=False)
        
        # Add built-in functions to symbol table so they're recognized
        addBuiltinsToSymbolTable(semanticAnalyzer.table)
        
        # Check AST for semantic errors:
        # - Undefined variables
        # - SSA violations (variable reassignments)
        # - Redeclared functions/blocks
        # - Variables used before assignment
        wasSuccessful = semanticAnalyzer.analyze(ast)
        if not wasSuccessful:
            print("ERROR: Semantic analysis failed")
            sys.exit(1)
        
        if self.debug:
            print("Semantic analysis passed")
        
        # === INTERPRETATION ===
        if self.debug:
            print("Interpreting...")
        visitor = InterpreterVisitor(debug=self.debug)
        result = ast.accept(visitor)
        
        return result if result is not None else 0
