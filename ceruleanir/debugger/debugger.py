# CeruleanIR Debugger - Core Implementation
# Author: Amy Burnett
# =================================================================================================

import sys
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, List, Any

from ..interpreter import CeruleanIRInterpreter
from ..interpreter.visitor import InterpreterVisitor
from .commands import CommandParser
from .breakpoint import BreakpointManager

# =================================================================================================
# Debug State
# =================================================================================================

class DebugMode(Enum):
    """Current execution mode of the debugger."""
    STOPPED = 1      # Not started yet
    RUNNING = 2      # Running freely until breakpoint
    STEPPING = 3     # Stepping N instructions
    INTERACTIVE = 4  # Paused at breakpoint/step, waiting for user
    FINISHED = 5     # Program completed

class DebugAction(Enum):
    """Action to take after debug callback."""
    CONTINUE = 1     # Continue execution
    BREAK = 2        # Pause and return to REPL

@dataclass
class DebugContext:
    """Context information passed to debug callback."""
    instruction: Any
    function_name: str
    block_name: str
    instruction_index: int
    locals_dict: Dict[str, Any]
    globals_dict: Dict[str, Any]
    call_stack: List[str]

class DebuggerBreakException(Exception):
    """Exception raised to pause execution and return control to debugger."""
    def __init__(self, is_breakpoint=True):
        self.is_breakpoint = is_breakpoint
        super().__init__()

# =================================================================================================
# Main Debugger Class
# =================================================================================================

class CeruleanIRDebugger:
    """
    Interactive debugger for CeruleanIR programs.
    Supports breakpoints, stepping, variable inspection, and more.
    """
    
    def __init__(self, debug=False):
        self.debug = debug  # Debug the debugger itself
        
        # Interpreter state
        self.interpreter = None
        self.visitor = None
        self.execution_generator = None  # Generator for step-by-step execution
        
        # Debugger state
        self.mode = DebugMode.STOPPED
        self.step_count = 0
        self.step_into_calls = True
        
        # Current execution location
        self.current_context = None
        self.last_context = None
        
        # Subsystems
        self.breakpoints = BreakpointManager()
        self.command_parser = CommandParser(self)
        
        # Execution tracking
        self.call_depth = 0
        self.target_call_depth = None  # For 'finish' command
    
    # ========================================================================
    # Program Loading
    # ========================================================================
    
    def load_file(self, filename):
        """Load a CeruleanIR source file into the debugger."""
        if self.interpreter is None:
            self.interpreter = CeruleanIRInterpreter()
        
        if self.debug:
            print(f"[Debugger] Loading file: {filename}")
        
        self.interpreter.load_file(filename)
    
    # ========================================================================
    # Debug Callback (called by interpreter)
    # ========================================================================
    
    def debug_callback(self, context: DebugContext) -> DebugAction:
        """
        Called by the interpreter before each instruction.
        Determines whether to pause execution.
        """
        self.current_context = context
        location = self.get_location_string(context)
        
        if self.debug:
            print(f"[Debugger] At {location}")
        
        # Check for breakpoints (but skip if we're actively stepping)
        if self.mode != DebugMode.STEPPING:
            if self.breakpoints.should_break_at(location, context):
                if self.debug:
                    print(f"[Debugger] Hit breakpoint at {location}")
                self.mode = DebugMode.INTERACTIVE
                # Don't call show_context() here - let _drive_execution handle display
                raise DebuggerBreakException(is_breakpoint=True)
        
        # Check 'finish' mode (run until return from current function)
        if self.target_call_depth is not None:
            if self.call_depth <= self.target_call_depth:
                self.target_call_depth = None
                self.mode = DebugMode.INTERACTIVE
                # Don't call show_context() here - let _drive_execution handle display
                raise DebuggerBreakException(is_breakpoint=False)
        
        return DebugAction.CONTINUE
    
    def get_location_string(self, context: DebugContext) -> str:
        """Format current location as string."""
        return f"{context.function_name}.{context.block_name}.{context.instruction_index}"
    
    # ========================================================================
    # REPL (Read-Eval-Print Loop)
    # ========================================================================
    
    def repl(self):
        """Main interactive loop."""
        print("CeruleanIR Debugger")
        print("Type 'help' for list of commands, 'quit' to exit")
        print()
        
        while True:
            try:
                # Read command
                try:
                    line = input("(cirdb) ").strip()
                except EOFError:
                    print()
                    break
                
                if not line:
                    # Repeat last command
                    line = getattr(self, 'last_command', '')
                
                if not line:
                    continue
                
                self.last_command = line
                
                # Parse and execute command
                try:
                    should_quit = self.command_parser.execute(line)
                    if should_quit:
                        break
                except Exception as e:
                    print(f"Error: {e}")
                    if self.debug:
                        import traceback
                        traceback.print_exc()
            
            except KeyboardInterrupt:
                print()
                print("Interrupted")
                self.mode = DebugMode.INTERACTIVE
                continue
    
    # ========================================================================
    # Execution Control
    # ========================================================================
    
    def run(self):
        """Start or restart program execution."""
        # Always restart from beginning (reset visitor and generator)
        self.visitor = None
        self.execution_generator = None
        self.mode = DebugMode.RUNNING
        self.resume_execution()
    
    def step(self, count=1, into_calls=True):
        """Step N instructions."""
        self.mode = DebugMode.STEPPING
        self.step_count = count
        self.step_into_calls = into_calls
        self.resume_execution()
    
    def continue_execution(self):
        """Continue running until breakpoint or end."""
        self.mode = DebugMode.RUNNING
        self.resume_execution()
    
    def finish(self):
        """Run until current function returns."""
        self.target_call_depth = self.call_depth - 1
        self.mode = DebugMode.RUNNING
        self.resume_execution()
    
    def resume_execution(self):
        """Resume execution with current mode settings."""
        try:
            # If not started yet, need to link and start
            if self.visitor is None:
                # Create visitor with our debug callback
                self.visitor = InterpreterVisitor(
                    debug=False,
                    debug_callback=self.debug_callback
                )
                self.interpreter.visitor = self.visitor
                
                # Link the program
                self.interpreter.link()
                
                # Get the program AST
                program_ast = self.interpreter.linked_ast
                
                # Create generator for step-by-step execution
                self.execution_generator = program_ast.accept(self.visitor)
                
            # If we have a generator, drive it
            if self.execution_generator:
                self._drive_execution()
            else:
                print("ERROR: No execution generator available")
        
        except DebuggerBreakException:
            # Normal break - return to interactive mode
            self.mode = DebugMode.INTERACTIVE
        except StopIteration as e:
            # Execution completed
            result = e.value if hasattr(e, 'value') else 0
            print(f"\nProgram exited with code {result}")
            self.mode = DebugMode.FINISHED
    
    def _drive_execution(self):
        """Drive the execution generator based on current mode."""
        try:
            while True:
                # Get next step from generator
                status_value = next(self.execution_generator)
                status, context = status_value
                
                # Update current context
                if status in ('STEP', 'BREAK'):
                    self.current_context = context
                
                # Handle based on status
                if status == 'BREAK':
                    # Explicit break requested
                    self.mode = DebugMode.INTERACTIVE
                    self.show_context(is_breakpoint=True)
                    return
                elif status == 'STEP':
                    # Check if we should pause based on mode
                    if self.mode == DebugMode.STEPPING:
                        if self.step_count > 0:
                            self.step_count -= 1
                        if self.step_count == 0:
                            self.mode = DebugMode.INTERACTIVE
                            self.show_context(is_breakpoint=False)
                            return
                    # Otherwise continue
                elif status == 'FINISHED':
                    result = context
                    print(f"\nProgram exited with code {result}")
                    self.mode = DebugMode.FINISHED
                    return
                
        except StopIteration as e:
            # Generator exhausted - program finished
            result = e.value if hasattr(e, 'value') else 0
            print(f"\nProgram exited with code {result}")
            self.mode = DebugMode.FINISHED
    
    # ========================================================================
    # Display / Output
    # ========================================================================
    
    def show_context(self, is_breakpoint=True):
        """Show current execution context."""
        if self.current_context is None:
            print("Not running")
            return
        
        ctx = self.current_context
        location = self.get_location_string(ctx)
        
        if is_breakpoint:
            print(f"\nBreakpoint at {location}")
        else:
            print(f"\n{location}")
        print(f"=> {ctx.instruction}")
        print()
    
    def print_variable(self, var_name):
        """Print value of a variable."""
        if self.current_context is None:
            print("Not running")
            return
        
        # Check locals
        if var_name in self.current_context.locals_dict:
            value = self.current_context.locals_dict[var_name]
            print(f"{var_name} = {self.format_value(value)}")
            return
        
        # Check globals
        if var_name in self.current_context.globals_dict:
            value = self.current_context.globals_dict[var_name]
            print(f"{var_name} = {self.format_value(value)}")
            return
        
        print(f"No variable named '{var_name}'")
    
    def format_value(self, value):
        """Format a value for display."""
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, list):
            return f"[{', '.join(str(v) for v in value)}]"
        else:
            return str(value)
    
    def info_locals(self):
        """Show all local variables."""
        if self.current_context is None:
            print("Not running")
            return
        
        locals_dict = self.current_context.locals_dict
        if not locals_dict:
            print("No local variables")
            return
        
        print("Local variables:")
        for name, value in sorted(locals_dict.items()):
            print(f"  {name} = {self.format_value(value)}")
    
    def info_globals(self):
        """Show all global variables."""
        if self.current_context is None:
            print("Not running")
            return
        
        globals_dict = self.current_context.globals_dict
        if not globals_dict:
            print("No global variables")
            return
        
        print("Global variables:")
        for name, value in sorted(globals_dict.items()):
            print(f"  {name} = {self.format_value(value)}")
    
    def show_call_stack(self):
        """Show current call stack."""
        if self.current_context is None:
            print("Not running")
            return
        
        stack = self.current_context.call_stack
        if not stack:
            print("Call stack empty")
            return
        
        print("Call stack:")
        for i, frame in enumerate(reversed(stack)):
            marker = "=>" if i == 0 else "  "
            print(f"{marker} #{i} {frame}")
    
    # ========================================================================
    # Command File Execution
    # ========================================================================
    
    def execute_command_file(self, filename):
        """Execute commands from a file."""
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                print(f"(cirdb) {line}")
                self.command_parser.execute(line)
