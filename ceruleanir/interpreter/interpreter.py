# CeruleanIR Interpreter
# This is an interpreter for CeruleanIR programs. It takes CeruleanIR code as input and executes it
# according to the semantics defined for the language.
# Supports multi-file programs with phase-based execution: parse → link → execute
# Author: Amy Burnett
# =================================================================================================

import sys
from pathlib import Path

# Use existing tokenizer and parser from ceruleanir frontend
from ..tokenizer import tokenize
from ..parser import Parser

# Import semantic analyzer from backend
from backend.semanticAnalyzer import SemanticAnalysisVisitor
from backend.builtins import addBuiltinsToSymbolTable
from backend.ceruleanIRAST import ProgramNode, FunctionNode, GlobalVariableDeclarationNode

# Import the interpreter visitor
from .visitor import InterpreterVisitor

# =================================================================================================

class CeruleanIRInterpreter:
    """
    Main interpreter class that handles parsing, linking, and execution of CeruleanIR programs.
    Supports multi-file programs and incremental loading (useful for REPL).
    
    Usage:
        # Single file
        interpreter = CeruleanIRInterpreter()
        interpreter.load_file('program.ceruleanir')
        exit_code = interpreter.run()
        
        # Multi-file
        interpreter = CeruleanIRInterpreter()
        interpreter.load_file('lib.ceruleanir')
        interpreter.load_file('main.ceruleanir')
        exit_code = interpreter.run()
        
        # Incremental (REPL-style)
        interpreter.load_source('function i32 @test() { ... }', '<repl>')
        interpreter.run()
    """
    
    def __init__(self, debug=False, visitor=None):
        self.debug = debug
        self.modules = []           # List of (filename, source_lines, ast) tuples
        self.linked_ast = None      # Merged program AST
        self.needs_relink = True    # Track if linking is needed
        self.visitor = visitor      # Optional custom visitor (for debugging)
    
    # ========================================================================
    # Loading Phase - Parse files into ASTs
    # ========================================================================
    
    def load_file(self, filename):
        """
        Load and parse a CeruleanIR source file.
        
        Args:
            filename: Path to the source file
            
        Returns:
            The parsed AST for this file
        """
        filepath = Path(filename)
        if not filepath.exists():
            print(f"ERROR: File not found: {filename}")
            sys.exit(1)
        
        with open(filepath, 'r') as f:
            source_code = f.read()
        
        return self.load_source(source_code, str(filepath))
    
    def load_source(self, source_code, filename="<input>"):
        """
        Load and parse CeruleanIR source code.
        Useful for REPL or dynamic code execution.
        
        Args:
            source_code: CeruleanIR source code as string
            filename: Name to use for this source (for error messages)
            
        Returns:
            The parsed AST
        """
        source_lines = source_code.split("\n")
        
        # Tokenization
        if self.debug:
            print(f"Tokenizing {filename}...")
        tokens = tokenize(source_code, filename)
        
        # Parsing
        if self.debug:
            print(f"Parsing {filename}...")
        parser = Parser(tokens, source_lines, doDebug=self.debug)
        ast = parser.parse()
        
        # Store module for later linking
        self.modules.append((filename, source_lines, ast))
        self.needs_relink = True
        
        return ast
    
    # ========================================================================
    # Linking Phase - Merge modules and validate
    # ========================================================================
    
    def link(self):
        """
        Link all loaded modules into a single program.
        Performs semantic analysis on the merged program.
        
        Returns:
            The linked program AST
            
        Exits:
            If duplicate functions/globals are found or semantic analysis fails
        """
        if self.debug:
            print(f"Linking {len(self.modules)} module(s)...")
        
        if not self.modules:
            print("ERROR: No modules loaded")
            sys.exit(1)
        
        # Merge all module ASTs
        merged_functions = {}
        merged_globals = {}
        
        for filename, source_lines, ast in self.modules:
            for codeunit in ast.codeunits:
                if isinstance(codeunit, FunctionNode):
                    func_id = codeunit.id
                    
                    # Skip extern declarations - they're forward declarations, not definitions
                    if codeunit.isExtern:
                        continue
                    
                    # Check for duplicate non-extern definitions
                    if func_id in merged_functions:
                        prev_file, prev_func = merged_functions[func_id]
                        print(f"Link Error: Duplicate function {func_id}")
                        print(f"  First defined in: {prev_file}")
                        print(f"  Redefined in: {filename}")
                        sys.exit(1)
                    merged_functions[func_id] = (filename, codeunit)
                    
                elif isinstance(codeunit, GlobalVariableDeclarationNode):
                    global_id = codeunit.id
                    if global_id in merged_globals:
                        prev_file = merged_globals[global_id][0]
                        print(f"Link Error: Duplicate global variable {global_id}")
                        print(f"  First defined in: {prev_file}")
                        print(f"  Redefined in: {filename}")
                        sys.exit(1)
                    merged_globals[global_id] = (filename, codeunit)
        
        # Create merged program AST
        merged_codeunits = (
            [codeunit for _, codeunit in merged_globals.values()] +
            [codeunit for _, codeunit in merged_functions.values()]
        )
        self.linked_ast = ProgramNode(merged_codeunits)
        
        # Semantic analysis on merged program
        if self.debug:
            print("Analyzing semantics...")
        
        # Collect all source lines for error reporting
        all_source_lines = []
        for _, source_lines, _ in self.modules:
            all_source_lines.extend(source_lines)
        
        semantic_analyzer = SemanticAnalysisVisitor(all_source_lines, debug=False)
        addBuiltinsToSymbolTable(semantic_analyzer.table)
        
        was_successful = semantic_analyzer.analyze(self.linked_ast)
        if not was_successful:
            print("ERROR: Semantic analysis failed")
            sys.exit(1)
        
        if self.debug:
            print("Semantic analysis passed")
        
        self.needs_relink = False
        return self.linked_ast
    
    # ========================================================================
    # Execution Phase - Run the program
    # ========================================================================
    
    def run(self):
        """
        Execute the linked program.
        Automatically links if needed.
        
        Returns:
            Exit code from @main function
        """
        # Link if we haven't already or if modules were added
        if self.needs_relink:
            self.link()
        
        # Execute
        if self.debug:
            print("Executing...")
        
        # Use custom visitor if provided (e.g., for debugging), otherwise create a new one
        visitor = self.visitor if self.visitor else InterpreterVisitor(debug=self.debug)
        result = self.linked_ast.accept(visitor)
        
        # If result is a generator (debug mode), we need to consume it
        # This happens when visitor has debug_callback set
        if hasattr(result, '__iter__') and hasattr(result, '__next__'):
            # It's a generator, consume it to get return value
            try:
                while True:
                    next(result)
            except StopIteration as e:
                # Generator returns result via StopIteration.value
                result = e.value if hasattr(e, 'value') else 0
        
        return result if result is not None else 0
    
    # ========================================================================
    # Convenience Methods
    # ========================================================================
    
    def interpret(self, source_code, filename="<input>"):
        """
        Legacy method: Load source and execute in one step.
        Kept for backward compatibility.
        
        Args:
            source_code: CeruleanIR source code as string
            filename: Name for this source
            
        Returns:
            Exit code from @main function
        """
        self.load_source(source_code, filename)
        return self.run()

