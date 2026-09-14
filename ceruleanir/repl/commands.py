# CeruleanIR REPL - Command Parser
# Handles special REPL commands (starting with :)
# Author: Amy Burnett
# =================================================================================================

from ..interpreter.interpreter import CeruleanIRInterpreter

# =================================================================================================

class REPLCommandParser:
    """
    Parses and executes REPL commands.
    Commands start with ':' to distinguish from IR code.
    """
    
    def __init__(self, repl):
        self.repl = repl
        
        # Command registry: name -> (handler, help_text, aliases)
        self.commands = {
            'help': (self.cmd_help, 'Show this help message', ['h', '?']),
            'quit': (self.cmd_quit, 'Exit the REPL', ['q', 'exit']),
            'load': (self.cmd_load, 'Load a .ceruleanir file', []),
            'functions': (self.cmd_functions, 'List all defined functions', ['funcs', 'f']),
            'vars': (self.cmd_vars, 'Show all variables', ['v']),
            'globals': (self.cmd_globals, 'Show global variables', ['g']),
            'print': (self.cmd_print, 'Print value of a variable', ['p']),
            'reset': (self.cmd_reset, 'Clear all state and restart', ['clear']),
        }
        
        # Build alias map
        self.aliases = {}
        for cmd_name, (_, _, aliases) in self.commands.items():
            for alias in aliases:
                self.aliases[alias] = cmd_name
    
    def execute(self, line):
        """
        Parse and execute a command line.
        
        Args:
            line: Command line (starting with ':')
            
        Returns:
            True if should exit REPL, False otherwise
        """
        # Strip the leading ':'
        line = line[1:].strip()
        
        if not line:
            return False
        
        # Parse command and arguments
        parts = line.split()
        cmd = parts[0]
        args = parts[1:]
        
        # Resolve aliases
        if cmd in self.aliases:
            cmd = self.aliases[cmd]
        
        # Execute command
        if cmd in self.commands:
            handler, _, _ = self.commands[cmd]
            return handler(args)
        else:
            print(f"Unknown command: :{cmd}")
            print("Type :help for list of commands")
            return False
    
    # ========================================================================
    # Command Handlers
    # ========================================================================
    
    def cmd_help(self, args):
        """Show help for commands."""
        if args:
            # Help for specific command
            cmd = args[0]
            if cmd in self.aliases:
                cmd = self.aliases[cmd]
            if cmd in self.commands:
                _, help_text, aliases = self.commands[cmd]
                print(f":{cmd} - {help_text}")
                if aliases:
                    print(f"  Aliases: {', '.join([':' + a for a in aliases])}")
            else:
                print(f"Unknown command: :{cmd}")
        else:
            # General help
            print("CeruleanIR REPL Commands:")
            print()
            for cmd_name in sorted(self.commands.keys()):
                _, help_text, aliases = self.commands[cmd_name]
                alias_str = f" ({', '.join([':'+a for a in aliases])})" if aliases else ""
                cmd_str = f":{cmd_name}{alias_str}"
                print(f"  {cmd_str:<25} {help_text}")
        return False
    
    def cmd_quit(self, args):
        """Exit the REPL."""
        return True
    
    def cmd_load(self, args):
        """Load a .ceruleanir file into the session."""
        if not args:
            print("Usage: :load <file.ceruleanir>")
            return False
        
        filename = args[0]
        try:
            # Use the interpreter to load and parse the file
            interpreter = CeruleanIRInterpreter()
            interpreter.load_file(filename)
            
            # Link to get the AST
            program_ast = interpreter.link()
            
            # Add all functions to our session
            for codeunit in program_ast.codeunits:
                if isinstance(codeunit, type(codeunit)) and hasattr(codeunit, 'id'):
                    # It's a function
                    self.repl.session.add_function(codeunit)
            
            print(f"Loaded {filename}")
            
        except FileNotFoundError:
            print(f"Error: File not found: {filename}")
        except Exception as e:
            print(f"Error loading {filename}: {e}")
        
        return False
    
    def cmd_functions(self, args):
        """List all defined functions."""
        user_funcs = self.repl.session.get_user_functions()
        
        if not user_funcs:
            print("No functions defined")
        else:
            print("Defined functions:")
            for func in user_funcs:
                print(f"  {func}")
        
        return False
    
    def cmd_vars(self, args):
        """Show all variables."""
        variables = self.repl.session.get_globals()
        
        if not variables:
            print("No variables defined")
        else:
            print("Variables:")
            for name, value in sorted(variables.items()):
                print(f"  {name} = {self._format_value(value)}")
        
        return False
    
    def cmd_globals(self, args):
        """Show global variables (same as vars for now)."""
        return self.cmd_vars(args)
    
    def cmd_print(self, args):
        """Print the value of a specific variable."""
        if not args:
            print("Usage: :print <var_name> (e.g., :print %x)")
            return False
        
        var_name = args[0]
        variables = self.repl.session.get_globals()
        
        if var_name in variables:
            print(f"{var_name} = {self._format_value(variables[var_name])}")
        elif not var_name.startswith('%') and ('%' + var_name) in variables:
            # Handle user typing `:print x` instead of `:print %x`
            full_name = '%' + var_name
            print(f"{full_name} = {self._format_value(variables[full_name])}")
        else:
            print(f"Undefined variable: {var_name}")
        
        return False
    
    def cmd_reset(self, args):
        """Clear all state and restart."""
        self.repl.session.reset()
        print("Session reset")
        return False
    
    # ========================================================================
    # Utilities
    # ========================================================================
    
    def _format_value(self, value):
        """Format a value for display."""
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, list):
            return f"[{', '.join(str(v) for v in value)}]"
        else:
            return str(value)
