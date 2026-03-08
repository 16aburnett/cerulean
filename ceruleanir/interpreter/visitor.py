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
        
        # Push new local variable frame
        self.locals_stack.append({})
        old_function = self.current_function
        self.current_function = func_node
        
        # Initialize parameters with argument values
        for i, param in enumerate(func_node.params):
            if i < len(args):
                self.locals_stack[-1][param.name] = args[i]
        
        # Build blocks map for this function
        self.blocks = {block.name: block for block in func_node.basicBlocks}
        
        # Start execution at first block (typically "entry")
        if func_node.basicBlocks:
            self.current_block = func_node.basicBlocks[0].name
            result = self.execute_block(self.current_block)
        else:
            result = None
        
        # Pop local variable frame
        self.locals_stack.pop()
        self.current_function = old_function
        self.blocks = {}
        
        return result
    
    def execute_block(self, block_label):
        """Execute all instructions in a basic block."""
        if block_label not in self.blocks:
            print(f"ERROR: Undefined block: {block_label}")
            sys.exit(1)
        
        block = self.blocks[block_label]
        self.current_block = block_label
        self.next_block = None
        
        if self.debug:
            print(f"Executing block: {block_label}")
        
        for instruction in block.instructions:
            result = instruction.accept(self)
            
            # Check for return
            if isinstance(result, tuple) and result[0] == "RETURN":
                return result[1]
            
            # Check for control flow change
            if self.next_block is not None:
                return self.execute_block(self.next_block)
        
        return None
    
    def visitTypeSpecifierNode(self, node):
        pass  # Types are handled during execution
    
    def visitParameterNode(self, node):
        pass  # Parameters are handled in call_function
    
    def visitGlobalVariableDeclarationNode(self, node):
        """Initialize global variables."""
        # TODO: Handle initialization expressions
        self.globals[node.name] = None
        return None
    
    def visitVariableDeclarationNode(self, node):
        """Declare local variables (alloca)."""
        # TODO: Implement memory allocation
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
            # TODO: Implement alloca
            pass
        
        elif command == "load":
            # Load value from memory
            # Format: %dest = load(type(<type>), ptr(%ptr), i32(<offset>))
            # TODO: Implement load
            pass
        
        elif command == "store":
            # Store value to memory
            # Format: store(ptr(%ptr), i32(<offset>), <type>(<value>))
            # TODO: Implement store
            pass
        
        elif command == "malloc":
            # Allocate memory on heap
            # Format: %ptr = malloc(type(<type>), i32(<count>))
            # TODO: Implement malloc
            pass
        
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
            # TODO: Implement add
            pass
        
        elif command == "sub":
            # Subtraction: %dest = sub(<type>(%lhs), <type>(%rhs))
            # TODO: Implement sub
            pass
        
        elif command == "mul":
            # Multiplication: %dest = mul(<type>(%lhs), <type>(%rhs))
            # TODO: Implement mul
            pass
        
        elif command == "div":
            # Division: %dest = div(<type>(%lhs), <type>(%rhs))
            # TODO: Implement div
            pass
        
        elif command == "mod":
            # Modulo: %dest = mod(<type>(%lhs), <type>(%rhs))
            # TODO: Implement mod
            pass
        
        # Comparison Operations
        elif command == "ceq":
            # Equal: %dest = ceq(<type>(%lhs), <type>(%rhs))
            # TODO: Implement ceq
            pass
        
        elif command == "cne":
            # Not equal: %dest = cne(<type>(%lhs), <type>(%rhs))
            # TODO: Implement cne
            pass
        
        elif command == "clt":
            # Less than: %dest = clt(<type>(%lhs), <type>(%rhs))
            # TODO: Implement clt
            pass
        
        elif command == "cle":
            # Less than or equal: %dest = cle(<type>(%lhs), <type>(%rhs))
            # TODO: Implement cle
            pass
        
        elif command == "cgt":
            # Greater than: %dest = cgt(<type>(%lhs), <type>(%rhs))
            # TODO: Implement cgt
            pass
        
        elif command == "cge":
            # Greater than or equal: %dest = cge(<type>(%lhs), <type>(%rhs))
            # TODO: Implement cge
            pass
        
        # Control Flow Operations
        elif command == "jmp":
            # Unconditional jump: jmp(block(<label>))
            # TODO: Implement jmp
            pass
        
        elif command == "jcmp":
            # Conditional jump: jcmp(<type>(%condition), block(<true_label>), block(<false_label>))
            # TODO: Implement jcmp
            pass
        
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
        if node.name in self.globals:
            return self.globals[node.name]
        print(f"ERROR: Undefined global variable: {node.name}")
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
        if isinstance(value, str) and len(value) == 2 and value[0] == '\\':
            # Handle common escape sequences
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
