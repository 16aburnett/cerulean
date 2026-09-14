# CeruleanIR REPL - Main REPL Class
# Interactive Read-Eval-Print Loop for CeruleanIR
# Author: Amy Burnett
# =================================================================================================

import sys
try:
    import readline  # Enable line editing, arrow keys, and command history
except ImportError:
    pass

from .session import REPLSession
from .commands import REPLCommandParser
from ..tokenizer import tokenize
from ..parser import Parser
from backend.ceruleanIRAST import FunctionNode

# =================================================================================================

class CeruleanIRREPL:
    """
    Interactive REPL for CeruleanIR.
    
    Usage:
        repl = CeruleanIRREPL()
        repl.run()
    """
    
    def __init__(self):
        self.session = REPLSession()
        self.command_parser = REPLCommandParser(self)
        
        # Multi-line input handling
        self.multiline_buffer = []
        self.in_multiline = False
        self.multiline_depth = 0  # Track brace nesting
    
    def run(self):
        """Main REPL loop."""
        self._print_welcome()
        
        while True:
            try:
                # Determine prompt
                if self.in_multiline:
                    prompt = "... "
                else:
                    prompt = ">>> "
                
                # Read input
                try:
                    line = input(prompt)
                except EOFError:
                    print()  # Newline after ^D
                    break
                
                # Handle empty lines
                if not line.strip():
                    if self.in_multiline:
                        # Empty line in multiline - continue
                        self.multiline_buffer.append(line)
                    continue
                
                # Handle commands (start with ':')
                if line.strip().startswith(':') and not self.in_multiline:
                    should_quit = self.command_parser.execute(line.strip())
                    if should_quit:
                        break
                    continue
                
                # Handle multi-line input
                if self._is_multiline_start(line) and not self.in_multiline:
                    self.in_multiline = True
                    self.multiline_buffer = [line]
                    self.multiline_depth = line.count('{') - line.count('}')
                    continue
                
                if self.in_multiline:
                    self.multiline_buffer.append(line)
                    self.multiline_depth += line.count('{') - line.count('}')
                    
                    # Check if we're done
                    if self.multiline_depth <= 0:
                        full_input = '\n'.join(self.multiline_buffer)
                        self._execute_input(full_input)
                        self.in_multiline = False
                        self.multiline_buffer = []
                        self.multiline_depth = 0
                    continue
                
                # Single-line execution
                self._execute_input(line)
                
            except KeyboardInterrupt:
                print()
                if self.in_multiline:
                    print("Multi-line input cancelled")
                    self.in_multiline = False
                    self.multiline_buffer = []
                    self.multiline_depth = 0
            except (Exception, SystemExit) as e:
                if not isinstance(e, SystemExit):
                    print(f"Unexpected error: {e}")
                if self.in_multiline:
                    self.in_multiline = False
                    self.multiline_buffer = []
                    self.multiline_depth = 0
    
    def _execute_input(self, input_text):
        """
        Parse and execute user input.
        
        Args:
            input_text: CeruleanIR code to execute
        """
        try:
            # Tokenize
            tokens = tokenize(input_text, "<repl>")
            
            # Parse
            source_lines = input_text.split('\n')
            parser = Parser(tokens, source_lines, doDebug=False)
            
            # Determine what we're parsing
            if self._looks_like_function(input_text):
                # Parse as function definition
                ast = parser.function()
                self.session.add_function(ast)
                print(f"Defined {ast.id}")
            else:
                # Parse as instruction(s)
                instructions = []
                while parser.currentToken < len(tokens) and tokens[parser.currentToken].type != "END_OF_FILE":
                    instr = parser.instruction()
                    instructions.append(instr)
                
                if instructions:
                    # Execute instructions
                    result = self.session.execute_instructions(instructions)
                    
                    # Don't print None results
                    if result is not None:
                        print(f"=> {result}")
        
        except SyntaxError as e:
            print(f"Syntax error: {e}")
        except (Exception, SystemExit) as e:
            if not isinstance(e, SystemExit):
                print(f"Error: {e}")
    
    def _is_multiline_start(self, line):
        """
        Check if this line starts a multi-line input.
        Multi-line inputs are function definitions.
        """
        stripped = line.strip()
        # Function definitions start with "function" keyword
        return stripped.startswith('function') and '{' in stripped
    
    def _looks_like_function(self, text):
        """Check if text looks like a function definition."""
        stripped = text.strip()
        return stripped.startswith('function')
    
    def _print_welcome(self):
        """Print welcome message."""
        print("CeruleanIR REPL")
        print("Type :help for commands, :quit to exit")
        print()

# =================================================================================================
# Entry Point
# =================================================================================================

def main(files=None):
    """
    Main entry point for the REPL.
    
    Args:
        files: Optional list of files to preload
    """
    repl = CeruleanIRREPL()
    
    # Load any files specified
    if files:
        for filename in files:
            try:
                repl.command_parser.cmd_load([filename])
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                sys.exit(1)
    
    # Start REPL
    repl.run()

if __name__ == '__main__':
    main()
