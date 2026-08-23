"""
Execution controller for stepping through CeruleanIR programs.

Provides fine-grained control over program execution, allowing pausing and resuming
at instruction boundaries.
"""

from enum import Enum


class ExecutionMode(Enum):
    """Execution control mode."""
    RUNNING = "running"          # Run until breakpoint or completion
    STEPPING = "stepping"        # Execute one instruction then pause
    PAUSED = "paused"           # Currently paused
    FINISHED = "finished"       # Execution completed


class ExecutionController:
    """
    Controls step-by-step execution of a CeruleanIR program.
    
    This wraps the interpreter visitor and provides the ability to pause/resume
    execution at instruction boundaries. Used by the debugger to implement
    step/continue functionality.
    """
    
    def __init__(self, visitor, program_ast):
        """
        Initialize execution controller.
        
        Args:
            visitor: InterpreterVisitor instance configured with debug callback
            program_ast: Root AST node (Program)
        """
        self.visitor = visitor
        self.program_ast = program_ast
        self.mode = ExecutionMode.PAUSED
        self.should_pause = False
        self.result = None
        
        # Execution state for resume
        self.generator = None
        
    def start(self):
        """Start program execution. Returns generator that yields after each instruction."""
        # Create generator that executes the program
        self.mode = ExecutionMode.RUNNING
        self.generator = self._execute_with_yields()
        return self.generator
    
    def _execute_with_yields(self):
        """
        Execute program as generator, yielding after each instruction.
        
        This allows the debugger to pause/resume execution naturally.
        """
        try:
            # Execute the program, but visitor will yield control via callback
            self.result = self.program_ast.accept(self.visitor)
            self.mode = ExecutionMode.FINISHED
            yield ('FINISHED', self.result)
        except Exception as e:
            self.mode = ExecutionMode.FINISHED
            yield ('ERROR', e)
    
    def step(self):
        """
        Execute one instruction.
        
        Returns:
            Tuple of (status, value) where status is 'PAUSED', 'FINISHED', or 'ERROR'
        """
        if self.generator is None:
            self.start()
        
        try:
            return next(self.generator)
        except StopIteration:
            self.mode = ExecutionMode.FINISHED
            return ('FINISHED', self.result)
    
    def run_to_completion_or_break(self):
        """
        Run until completion or breakpoint hit.
        
        Returns:
            Tuple of (status, value)
        """
        if self.generator is None:
            self.start()
        
        # Keep stepping until paused or finished
        for status_value in self.generator:
            status, value = status_value
            if status in ('PAUSED', 'FINISHED', 'ERROR'):
                return status_value
        
        return ('FINISHED', self.result)
    
    def is_finished(self):
        """Check if execution is complete."""
        return self.mode == ExecutionMode.FINISHED
