# CeruleanIR Interpreter Visitor
# This visitor executes CeruleanIR AST nodes directly
# Author: Amy Burnett
# =================================================================================================

import sys

# Import the visitor base class and AST nodes
from backend.visitor import ASTVisitor
from backend.ceruleanIRAST import *

# Import builtin function implementations
from . import builtins

# =================================================================================================

class InterpreterVisitor(ASTVisitor):
    """
    Visitor that executes CeruleanIR AST nodes.
    This is the core execution engine.
    """
    
    def __init__(self, debug=False):
        self.debug = debug
        
        # Runtime state
        self.globals = {}           # Global variable storage: name -> value
        self.locals_stack = []      # Stack of local variable frames {var_name: value, ...}
        self.functions = {}         # Function definitions: name -> FunctionNode
        self.current_function = None
        self.blocks = {}            # Basic blocks in current function: label -> BasicBlockNode
        self.current_block = None
        self.next_block = None      # For control flow (jmp, jcmp)
        
    def visitProgramNode(self, node):
        """Execute the entire program."""
        if self.debug:
            print("=== Starting CeruleanIR Interpreter ===")
        
        # First pass: register all functions and globals
        for codeunit in node.codeunits:
            if isinstance(codeunit, FunctionNode):
                functionNode = codeunit
                self.functions[functionNode.id] = functionNode
            elif isinstance(codeunit, GlobalVariableDeclarationNode):
                codeunit.accept(self)
        
        # Execute main function if it exists
        if "@main" in self.functions:
            result = self.call_function("@main", [])
            if self.debug:
                print(f"=== Program exited with code: {result} ===")
            return result
        else:
            print("ERROR: No main function found")
            sys.exit(1)
    
    def call_function(self, func_name, args):
        """Call a function with given arguments."""
        # Check if it's a builtin function first
        if builtins.is_builtin(func_name):
            return builtins.call_builtin(func_name, args)
        
        # Otherwise, execute user-defined function
        if func_name not in self.functions:
            print(f"ERROR: Undefined function: {func_name}")
            sys.exit(1)
        
        func_node = self.functions[func_name]
        
        # Push new local variable frame and save function state
        self.locals_stack.append({})
        old_function = self.current_function
        old_blocks = self.blocks  # Save the caller's blocks dictionary
        self.current_function = func_node
        
        # Initialize parameters with argument values
        for i, param in enumerate(func_node.params):
            if i < len(args):
                self.locals_stack[-1][param.id] = args[i]
        
        # Build blocks map for this function
        self.blocks = {block.name: block for block in func_node.basicBlocks}
        
        # Start execution at first block (typically "entry")
        if func_node.basicBlocks:
            self.current_block = func_node.basicBlocks[0].name
            result = self.execute_block(self.current_block)
        else:
            result = None
        
        # Pop local variable frame and restore function state
        self.locals_stack.pop()
        self.current_function = old_function
        self.blocks = old_blocks  # Restore the caller's blocks dictionary
        
        return result
    
    def execute_block(self, block_label):
        """Execute all instructions in a basic block."""
        current_label = block_label
        
        while current_label is not None:
            if current_label not in self.blocks:
                print(f"ERROR: Undefined block: {current_label}")
                sys.exit(1)
            
            block = self.blocks[current_label]
            self.current_block = current_label
            self.next_block = None
            
            if self.debug:
                print(f"Executing block: {current_label}")
            
            for instruction in block.instructions:
                result = instruction.accept(self)
                
                # Check for return
                if isinstance(result, tuple) and result[0] == "RETURN":
                    return result[1]
                
                # Check for control flow change
                if self.next_block is not None:
                    break  # Exit instruction loop to jump to next block
            
            # Move to next block, or exit if no jump occurred
            current_label = self.next_block
        
        return None
    
    def visitTypeSpecifierNode(self, node):
        pass  # Types are handled during execution
    
    def visitParameterNode(self, node):
        pass  # Parameters are handled in call_function
    
    def visitGlobalVariableDeclarationNode(self, node):
        """Initialize global variables."""
        # Handle initialization expressions
        # Format: global @name = value(<type>(<value>))
        # Global variables are memory locations, so we wrap values in a list
        if node.command == "value":
            # Evaluate the argument to get the actual value
            if len(node.arguments) > 0:
                value = node.arguments[0].accept(self)
                # Wrap in a list to make it a memory location that can be loaded from
                self.globals[node.id] = [value]
            else:
                self.globals[node.id] = [None]
        else:
            # Other initialization commands can be added here if needed
            print(f"WARNING: Unsupported global initialization command: {node.command}")
            self.globals[node.id] = [None]
        return None
    
    def visitVariableDeclarationNode(self, node):
        """Declare local variables (alloca)."""
        # Memory allocation is handled in visitInstructionNode for 'alloca' instruction
        pass
    
    def visitFunctionNode(self, node):
        """Functions are registered in first pass, not executed here."""
        pass
    
    def visitBasicBlockNode(self, node):
        """Blocks are executed via execute_block, not visited directly."""
        pass
    
    def visitInstructionNode(self, node):
        """Execute a single instruction."""
        command = node.command
        
        if self.debug:
            print(f"  Executing: {command}")
        
        # Memory Operations
        if command == "alloca":
            # Allocate memory on stack
            # Format: %ptr = alloca(type(<type>), i32(<count>))
            if len(node.arguments) != 2:
                print(f"ERROR: alloca instruction expects 2 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            # Argument 0 is the type (metadata)
            # Argument 1 is the count
            count = node.arguments[1].accept(self)
            
            # Allocate a list of None values
            allocated_memory = [None] * count
            
            # Store the pointer in local variable
            if node.hasAssignment and self.locals_stack:
                self.locals_stack[-1][node.lhsVariable.id] = allocated_memory
            
            return None
        
        elif command == "load":
            # Load value from memory
            # Format: %dest = load(type(<type>), ptr(%ptr), i32(<offset>))
            if len(node.arguments) != 3:
                print(f"ERROR: load instruction expects 3 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            # Argument 0 is the type (just metadata, skip it)
            # Argument 1 is the pointer
            ptr_value = node.arguments[1].accept(self)
            # Argument 2 is the offset
            offset = node.arguments[2].accept(self)
            
            # Load the value at ptr[offset]
            if isinstance(ptr_value, str):
                # String indexing
                if offset < len(ptr_value):
                    value = ptr_value[offset]
                else:
                    print(f"ERROR: String index out of bounds: {offset} >= {len(ptr_value)}")
                    sys.exit(1)
            elif isinstance(ptr_value, list):
                # Array indexing
                if offset < len(ptr_value):
                    value = ptr_value[offset]
                else:
                    print(f"ERROR: Array index out of bounds: {offset} >= {len(ptr_value)}")
                    sys.exit(1)
            else:
                print(f"ERROR: Cannot load from non-pointer type: {type(ptr_value)}")
                sys.exit(1)
            
            # Store result in local variable
            if node.hasAssignment and self.locals_stack:
                self.locals_stack[-1][node.lhsVariable.id] = value
            
            return None
        
        elif command == "store":
            # Store value to memory
            # Format: store(ptr(%ptr), i32(<offset>), <type>(<value>))
            if len(node.arguments) != 3:
                print(f"ERROR: store instruction expects 3 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            # Argument 0 is the pointer
            ptr_value = node.arguments[0].accept(self)
            # Argument 1 is the offset
            offset = node.arguments[1].accept(self)
            # Argument 2 is the value to store
            value = node.arguments[2].accept(self)
            
            # Store the value at ptr[offset]
            if isinstance(ptr_value, list):
                if offset < len(ptr_value):
                    ptr_value[offset] = value
                else:
                    print(f"ERROR: Array index out of bounds: {offset} >= {len(ptr_value)}")
                    sys.exit(1)
            else:
                print(f"ERROR: Cannot store to non-pointer type: {type(ptr_value)}")
                sys.exit(1)
            
            return None
        
        elif command == "malloc":
            # Allocate memory on heap
            # Format: %ptr = malloc(type(<type>), i32(<count>))
            if len(node.arguments) != 2:
                print(f"ERROR: malloc instruction expects 2 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            # Argument 0 is the type (metadata)
            # Argument 1 is the count
            count = node.arguments[1].accept(self)
            
            # Allocate a list of None values (heap vs stack doesn't matter in interpreter)
            allocated_memory = [None] * count
            
            # Store the pointer in local variable
            if node.hasAssignment and self.locals_stack:
                self.locals_stack[-1][node.lhsVariable.id] = allocated_memory
            
            return None
        
        elif command == "free":
            # Free allocated memory
            # Format: free(ptr(%ptr))
            # In Python interpreter, this is a no-op since Python handles memory management
            if len(node.arguments) != 1:
                print(f"ERROR: free instruction expects 1 argument, got {len(node.arguments)}")
                sys.exit(1)
            
            # We evaluate the argument to ensure it's valid, but don't need to do anything
            # Python's garbage collector will handle cleanup automatically
            node.arguments[0].accept(self)
            
            return None
        
        elif command == "value":
            # Load immediate value
            # Format: %dest = value(<value>)
            if len(node.arguments) != 1:
                print(f"ERROR: value instruction expects 1 argument, got {len(node.arguments)}")
                sys.exit(1)
            
            # Evaluate the argument to get the actual value
            value = node.arguments[0].accept(self)
            
            # Store in local variable
            if node.hasAssignment and self.locals_stack:
                self.locals_stack[-1][node.lhsVariable.id] = value
            
            return None
        
        # Arithmetic Operations
        elif command == "add":
            # Addition: %dest = add(<type>(%lhs), <type>(%rhs))
            if len(node.arguments) != 2:
                print(f"ERROR: add instruction expects 2 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            lhs = node.arguments[0].accept(self)
            rhs = node.arguments[1].accept(self)
            result = lhs + rhs
            
            # Store result in local variable
            if node.hasAssignment and self.locals_stack:
                self.locals_stack[-1][node.lhsVariable.id] = result
            
            return None
        
        elif command == "sub":
            # Subtraction: %dest = sub(<type>(%lhs), <type>(%rhs))
            if len(node.arguments) != 2:
                print(f"ERROR: sub instruction expects 2 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            lhs = node.arguments[0].accept(self)
            rhs = node.arguments[1].accept(self)
            result = lhs - rhs
            
            if node.hasAssignment and self.locals_stack:
                self.locals_stack[-1][node.lhsVariable.id] = result
            
            return None
        
        elif command == "mul":
            # Multiplication: %dest = mul(<type>(%lhs), <type>(%rhs))
            if len(node.arguments) != 2:
                print(f"ERROR: mul instruction expects 2 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            lhs = node.arguments[0].accept(self)
            rhs = node.arguments[1].accept(self)
            result = lhs * rhs
            
            if node.hasAssignment and self.locals_stack:
                self.locals_stack[-1][node.lhsVariable.id] = result
            
            return None
        
        elif command == "div":
            # Division: %dest = div(<type>(%lhs), <type>(%rhs))
            if len(node.arguments) != 2:
                print(f"ERROR: div instruction expects 2 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            lhs = node.arguments[0].accept(self)
            rhs = node.arguments[1].accept(self)
            
            if rhs == 0:
                print(f"ERROR: Division by zero")
                sys.exit(1)
            
            # Integer division for integers, float division otherwise
            if isinstance(lhs, int) and isinstance(rhs, int):
                result = lhs // rhs
            else:
                result = lhs / rhs
            
            if node.hasAssignment and self.locals_stack:
                self.locals_stack[-1][node.lhsVariable.id] = result
            
            return None
        
        elif command == "mod":
            # Modulo: %dest = mod(<type>(%lhs), <type>(%rhs))
            if len(node.arguments) != 2:
                print(f"ERROR: mod instruction expects 2 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            lhs = node.arguments[0].accept(self)
            rhs = node.arguments[1].accept(self)
            
            if rhs == 0:
                print(f"ERROR: Modulo by zero")
                sys.exit(1)
            
            result = lhs % rhs
            
            if node.hasAssignment and self.locals_stack:
                self.locals_stack[-1][node.lhsVariable.id] = result
            
            return None
        
        # Comparison Operations
        elif command == "ceq":
            # Equal: %dest = ceq(<type>(%lhs), <type>(%rhs))
            if len(node.arguments) != 2:
                print(f"ERROR: ceq instruction expects 2 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            lhs = node.arguments[0].accept(self)
            rhs = node.arguments[1].accept(self)
            result = 1 if lhs == rhs else 0
            
            if node.hasAssignment and self.locals_stack:
                self.locals_stack[-1][node.lhsVariable.id] = result
            
            return None
        
        elif command == "cne":
            # Not equal: %dest = cne(<type>(%lhs), <type>(%rhs))
            if len(node.arguments) != 2:
                print(f"ERROR: cne instruction expects 2 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            lhs = node.arguments[0].accept(self)
            rhs = node.arguments[1].accept(self)
            result = 1 if lhs != rhs else 0
            
            if node.hasAssignment and self.locals_stack:
                self.locals_stack[-1][node.lhsVariable.id] = result
            
            return None
        
        elif command == "clt":
            # Less than: %dest = clt(<type>(%lhs), <type>(%rhs))
            if len(node.arguments) != 2:
                print(f"ERROR: clt instruction expects 2 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            lhs = node.arguments[0].accept(self)
            rhs = node.arguments[1].accept(self)
            result = 1 if lhs < rhs else 0
            
            if node.hasAssignment and self.locals_stack:
                self.locals_stack[-1][node.lhsVariable.id] = result
            
            return None
        
        elif command == "cle":
            # Less than or equal: %dest = cle(<type>(%lhs), <type>(%rhs))
            if len(node.arguments) != 2:
                print(f"ERROR: cle instruction expects 2 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            lhs = node.arguments[0].accept(self)
            rhs = node.arguments[1].accept(self)
            result = 1 if lhs <= rhs else 0
            
            if node.hasAssignment and self.locals_stack:
                self.locals_stack[-1][node.lhsVariable.id] = result
            
            return None
        
        elif command == "cgt":
            # Greater than: %dest = cgt(<type>(%lhs), <type>(%rhs))
            if len(node.arguments) != 2:
                print(f"ERROR: cgt instruction expects 2 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            lhs = node.arguments[0].accept(self)
            rhs = node.arguments[1].accept(self)
            result = 1 if lhs > rhs else 0
            
            if node.hasAssignment and self.locals_stack:
                self.locals_stack[-1][node.lhsVariable.id] = result
            
            return None
        
        elif command == "cge":
            # Greater than or equal: %dest = cge(<type>(%lhs), <type>(%rhs))
            if len(node.arguments) != 2:
                print(f"ERROR: cge instruction expects 2 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            lhs = node.arguments[0].accept(self)
            rhs = node.arguments[1].accept(self)
            result = 1 if lhs >= rhs else 0
            
            if node.hasAssignment and self.locals_stack:
                self.locals_stack[-1][node.lhsVariable.id] = result
            
            return None
        
        # Control Flow Operations
        elif command == "jmp":
            # Unconditional jump: jmp(block(<label>))
            if len(node.arguments) != 1:
                print(f"ERROR: jmp instruction expects 1 argument, got {len(node.arguments)}")
                sys.exit(1)
            
            # Get the target block label
            target_block = node.arguments[0].accept(self)
            
            # Set next block to jump to
            self.next_block = target_block
            
            return None
        
        elif command == "jcmp":
            # Conditional jump: jcmp(<type>(%condition), block(<true_label>), block(<false_label>))
            if len(node.arguments) != 3:
                print(f"ERROR: jcmp instruction expects 3 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            # Evaluate condition
            condition = node.arguments[0].accept(self)
            # Get true and false block labels
            true_label = node.arguments[1].accept(self)
            false_label = node.arguments[2].accept(self)
            
            # Jump based on condition (non-zero is true)
            if condition:
                self.next_block = true_label
            else:
                self.next_block = false_label
            
            return None
        
        # Jump-if comparison instructions (convenience instructions)
        elif command == "jg":
            # Jump if greater: jg(<type>(%lhs), <type>(%rhs), block(<label>))
            if len(node.arguments) != 3:
                print(f"ERROR: jg instruction expects 3 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            lhs = node.arguments[0].accept(self)
            rhs = node.arguments[1].accept(self)
            label = node.arguments[2].accept(self)
            
            if lhs > rhs:
                self.next_block = label
            
            return None
        
        elif command == "jge":
            # Jump if greater or equal: jge(<type>(%lhs), <type>(%rhs), block(<label>))
            if len(node.arguments) != 3:
                print(f"ERROR: jge instruction expects 3 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            lhs = node.arguments[0].accept(self)
            rhs = node.arguments[1].accept(self)
            label = node.arguments[2].accept(self)
            
            if lhs >= rhs:
                self.next_block = label
            
            return None
        
        elif command == "jl":
            # Jump if less: jl(<type>(%lhs), <type>(%rhs), block(<label>))
            if len(node.arguments) != 3:
                print(f"ERROR: jl instruction expects 3 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            lhs = node.arguments[0].accept(self)
            rhs = node.arguments[1].accept(self)
            label = node.arguments[2].accept(self)
            
            if lhs < rhs:
                self.next_block = label
            
            return None
        
        elif command == "jle":
            # Jump if less or equal: jle(<type>(%lhs), <type>(%rhs), block(<label>))
            if len(node.arguments) != 3:
                print(f"ERROR: jle instruction expects 3 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            lhs = node.arguments[0].accept(self)
            rhs = node.arguments[1].accept(self)
            label = node.arguments[2].accept(self)
            
            if lhs <= rhs:
                self.next_block = label
            
            return None
        
        elif command == "jne":
            # Jump if not equal: jne(<type>(%lhs), <type>(%rhs), block(<label>))
            if len(node.arguments) != 3:
                print(f"ERROR: jne instruction expects 3 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            lhs = node.arguments[0].accept(self)
            rhs = node.arguments[1].accept(self)
            label = node.arguments[2].accept(self)
            
            if lhs != rhs:
                self.next_block = label
            
            return None
        
        elif command == "jeq":
            # Jump if equal: jeq(<type>(%lhs), <type>(%rhs), block(<label>))
            if len(node.arguments) != 3:
                print(f"ERROR: jeq instruction expects 3 arguments, got {len(node.arguments)}")
                sys.exit(1)
            
            lhs = node.arguments[0].accept(self)
            rhs = node.arguments[1].accept(self)
            label = node.arguments[2].accept(self)
            
            if lhs == rhs:
                self.next_block = label
            
            return None
        
        elif command == "return":
            # Return from function: return(<type>(%value)) or return()
            if len(node.arguments) == 0:
                # Return with no value
                return ("RETURN", None)
            elif len(node.arguments) == 1:
                # Return with a value
                value = node.arguments[0].accept(self)
                return ("RETURN", value)
            else:
                print(f"ERROR: return instruction expects 0 or 1 arguments, got {len(node.arguments)}")
                sys.exit(1)
        
        else:
            print(f"ERROR: Unknown instruction: {command}")
            sys.exit(1)
        
        return None
    
    def visitCallInstructionNode(self, node):
        """Execute function calls."""
        # Evaluate all arguments
        arg_values = []
        for arg in node.arguments:
            value = arg.accept(self)
            arg_values.append(value)
        
        # Call the function
        result = self.call_function(node.function_name, arg_values)
        
        # Store result if there's an assignment
        if node.hasAssignment:
            # Store in current local scope
            if self.locals_stack:
                self.locals_stack[-1][node.lhsVariable.id] = result
        
        return None
    
    def visitArgumentExpressionNode(self, node):
        """Evaluate argument expressions."""
        return node.expression.accept(self)
    
    def visitExpressionNode(self, node):
        """Evaluate generic expressions."""
        pass
    
    def visitGlobalVariableExpressionNode(self, node):
        """Load global variable value."""
        if node.id in self.globals:
            return self.globals[node.id]
        print(f"ERROR: Undefined global variable: {node.id}")
        sys.exit(1)
    
    def visitLocalVariableExpressionNode(self, node):
        """Load local variable value."""
        if self.locals_stack and node.id in self.locals_stack[-1]:
            return self.locals_stack[-1][node.id]
        print(f"ERROR: Undefined local variable: {node.id}")
        sys.exit(1)
    
    def visitBasicBlockExpressionNode(self, node):
        """Return block label for control flow."""
        return node.id
    
    def visitIntLiteralExpressionNode(self, node):
        """Return integer literal value."""
        return node.value
    
    def visitFloatLiteralExpressionNode(self, node):
        """Return float literal value."""
        return node.value
    
    def visitCharLiteralExpressionNode(self, node):
        """Return character literal value."""
        # Decode escape sequences
        value = node.value
        if isinstance(value, str):
            # Strip surrounding single quotes if present
            if len(value) >= 2 and value[0] == "'" and value[-1] == "'":
                value = value[1:-1]
            
            # Handle escape sequences
            if len(value) == 2 and value[0] == '\\':
                escape_map = {
                    'n': '\n',
                    't': '\t',
                    'r': '\r',
                    '0': '\0',
                    '\\': '\\',
                    "'": "'",
                    '"': '"'
                }
                if value[1] in escape_map:
                    return escape_map[value[1]]
        return value
    
    def visitStringLiteralExpressionNode(self, node):
        """Return string literal value."""
        # Decode escape sequences in strings
        value = node.value
        if isinstance(value, str):
            # Strip surrounding quotes
            if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
                value = value[1:-1]
            
            # Python's encode().decode('unicode_escape') would work but can have issues
            # Manual replacement is safer
            value = value.replace('\\n', '\n')
            value = value.replace('\\t', '\t')
            value = value.replace('\\r', '\r')
            value = value.replace('\\0', '\0')
            value = value.replace('\\\\', '\\')
            value = value.replace("\\'", "'")
            value = value.replace('\\"', '"')
        return value
