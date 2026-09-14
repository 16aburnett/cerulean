# CeruleanIR REPL - Session Management
# Manages execution state for the REPL
# Author: Amy Burnett
# =================================================================================================

from backend.ceruleanIRAST import ProgramNode, FunctionNode, BasicBlockNode, InstructionNode
from ..interpreter.visitor import InterpreterVisitor

# =================================================================================================

class REPLSession:
    """
    Manages REPL execution state including functions, variables, and the interpreter.
    """
    
    def __init__(self):
        # Core state
        self.visitor = InterpreterVisitor(debug=False)
        self.temp_counter = 0  # For generating temporary function names
        
        # Track what's been defined
        self.user_functions = set()  # Function names defined by user
        
    def add_function(self, function_node):
        """
        Add a function definition to the session.
        
        Args:
            function_node: FunctionNode to add
        """
        # Register with visitor
        self.visitor.functions[function_node.id] = function_node
        self.user_functions.add(function_node.id)
    
    def execute_instructions(self, instructions):
        """
        Execute a list of instructions immediately in the global context.
        Wraps them in a temporary function, executes, and cleans up.
        
        Args:
            instructions: List of InstructionNode objects
            
        Returns:
            The return value (if any) or None
        """
        # Create temporary function to wrap the instructions
        temp_func_name = f"@__repl_exec_{self.temp_counter}__"
        self.temp_counter += 1
        
        # Build basic block with the instructions
        # Add an implicit return at the end
        from backend.ceruleanIRAST import (
            InstructionNode, ArgumentExpressionNode, 
            IntLiteralExpressionNode, TypeSpecifierNode
        )
        
        # Create return (i32(0)) instruction
        ret_instruction = InstructionNode(
            lhsVariable=None,
            command="return",
            arguments=[
                ArgumentExpressionNode(
                    type=TypeSpecifierNode(type='i32', id=None, token=None, arrayDimensions=[]),
                    expression=IntLiteralExpressionNode(value=0)
                )
            ]
        )
        
        instructions_with_return = instructions + [ret_instruction]
        
        basic_block = BasicBlockNode(
            name="entry",
            instructions=instructions_with_return
        )
        
        # Create function node
        temp_func = FunctionNode(
            type=TypeSpecifierNode(type='i32', id=None, token=None, arrayDimensions=[]),
            id=temp_func_name,
            token=None,
            params=[],
            basicBlocks=[basic_block],
            isExtern=False
        )
        
        # Temporarily add to visitor
        self.visitor.functions[temp_func_name] = temp_func
        
        try:
            # Push a locals frame that is actually the globals dict
            # This way, variables created in the "function" persist globally
            self.visitor.locals_stack.append(self.visitor.globals)
            
            # Set up execution context manually
            old_function = self.visitor.current_function
            old_blocks = self.visitor.blocks
            old_block_order = self.visitor.block_order
            old_block_list = self.visitor.block_list
            self.visitor.current_function = temp_func
            
            # Build blocks map for this function
            self.visitor.blocks = {block.name: block for block in temp_func.basicBlocks}
            self.visitor.block_order = {block.name: i for i, block in enumerate(temp_func.basicBlocks)}
            self.visitor.block_list = temp_func.basicBlocks
            
            # Execute the block
            self.visitor.current_block = temp_func.basicBlocks[0].name
            self.visitor.execute_block(self.visitor.current_block)
            
            # Restore state
            self.visitor.locals_stack.pop()
            self.visitor.current_function = old_function
            self.visitor.blocks = old_blocks
            self.visitor.block_order = old_block_order
            self.visitor.block_list = old_block_list
            
            # Return the value of the assigned variable if the last instruction has an assignment
            last_instr = instructions[-1]
            if getattr(last_instr, 'hasAssignment', False) and getattr(last_instr, 'lhsVariable', None):
                var_id = last_instr.lhsVariable.id
                return self.visitor.globals.get(var_id)
            
            return None
        finally:
            # Clean up temporary function
            del self.visitor.functions[temp_func_name]
    
    def call_function(self, func_name, args):
        """
        Call a function with given arguments.
        
        Args:
            func_name: Name of function to call (e.g., '@main')
            args: List of argument values
            
        Returns:
            The function's return value
        """
        return self.visitor.call_function(func_name, args)
    
    def get_globals(self):
        """Return dictionary of global variables."""
        return self.visitor.globals.copy()
    
    def get_user_functions(self):
        """Return list of user-defined function names."""
        return sorted([f for f in self.user_functions if not f.startswith('@__')])
    
    def get_all_functions(self):
        """Return list of all function names (including builtins)."""
        return sorted(self.visitor.functions.keys())
    
    def reset(self):
        """Clear all state and start fresh."""
        self.__init__()
    
    def has_function(self, func_name):
        """Check if a function is defined."""
        return func_name in self.visitor.functions
