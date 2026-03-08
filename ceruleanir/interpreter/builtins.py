# CeruleanIR Interpreter Built-in Functions
# Python implementations of CeruleanIR built-in functions for the interpreter
# Author: Amy Burnett
# =================================================================================================

import sys

# =================================================================================================
# Built-in Function Registry
# =================================================================================================

BUILTINS = {}

def register_builtin(name):
    """Decorator to register a builtin function implementation."""
    def decorator(func):
        BUILTINS[name] = func
        return func
    return decorator

# =================================================================================================
# Print Functions
# =================================================================================================

@register_builtin("@__builtin__print__char")
def builtin_print_char(args):
    """Print a single character."""
    if len(args) != 1:
        print(f"ERROR: __builtin__print__char expects 1 argument, got {len(args)}")
        sys.exit(1)
    char_value = args[0]
    # Convert integer character code to character if needed
    if isinstance(char_value, int):
        char_value = chr(char_value)
    print(char_value, end='')
    return None

@register_builtin("@__builtin__print__char__1")
def builtin_print_char_1(args):
    """Print a string (array of characters) given a pointer."""
    if len(args) != 1:
        print(f"ERROR: __builtin__print__char__1 expects 1 argument, got {len(args)}")
        sys.exit(1)
    string_value = args[0]
    # If it's already a string, print it
    if isinstance(string_value, str):
        print(string_value, end='')
    # If it's a list/array, iterate and print each character
    elif isinstance(string_value, list):
        for char in string_value:
            if isinstance(char, int):
                print(chr(char), end='')
            else:
                print(char, end='')
    else:
        print(string_value, end='')
    return None

@register_builtin("@__builtin__print__i32")
def builtin_print_i32(args):
    """Print a 32-bit integer."""
    if len(args) != 1:
        print(f"ERROR: __builtin__print__i32 expects 1 argument, got {len(args)}")
        sys.exit(1)
    int_value = args[0]
    print(int_value, end='')
    return None

@register_builtin("@__builtin__print__int32")
def builtin_print_int32(args):
    """Print a 32-bit integer."""
    if len(args) != 1:
        print(f"ERROR: __builtin__print__int32 expects 1 argument, got {len(args)}")
        sys.exit(1)
    int_value = args[0]
    print(int_value, end='')
    return None

@register_builtin("@__builtin__print__i64")
def builtin_print_i64(args):
    """Print a 64-bit integer."""
    if len(args) != 1:
        print(f"ERROR: __builtin__print__i64 expects 1 argument, got {len(args)}")
        sys.exit(1)
    int_value = args[0]
    print(int_value, end='')
    return None

@register_builtin("@__builtin__print__f32")
def builtin_print_f32(args):
    """Print a 32-bit float."""
    if len(args) != 1:
        print(f"ERROR: __builtin__print__f32 expects 1 argument, got {len(args)}")
        sys.exit(1)
    float_value = args[0]
    print(float_value, end='')
    return None

@register_builtin("@__builtin__print__f64")
def builtin_print_f64(args):
    """Print a 64-bit float."""
    if len(args) != 1:
        print(f"ERROR: __builtin__print__f64 expects 1 argument, got {len(args)}")
        sys.exit(1)
    float_value = args[0]
    print(float_value, end='')
    return None

@register_builtin("@__builtin__println")
def builtin_println(args):
    """Print a newline."""
    if len(args) != 0:
        print(f"ERROR: __builtin__println expects 0 arguments, got {len(args)}")
        sys.exit(1)
    print()  # Print newline
    return None

@register_builtin("@__builtin__println__int32")
def builtin_println_i32(args):
    """Print a 32-bit integer followed by newline."""
    if len(args) != 1:
        print(f"ERROR: __builtin__println__int32 expects 1 argument, got {len(args)}")
        sys.exit(1)
    int_value = args[0]
    print(int_value)
    return None

@register_builtin("@__builtin__println__int64")
def builtin_println_i64(args):
    """Print a 64-bit integer followed by newline."""
    if len(args) != 1:
        print(f"ERROR: __builtin__println__int64 expects 1 argument, got {len(args)}")
        sys.exit(1)
    int_value = args[0]
    print(int_value)
    return None

@register_builtin("@__builtin__println__float32")
def builtin_println_f32(args):
    """Print a 32-bit float followed by newline."""
    if len(args) != 1:
        print(f"ERROR: __builtin__println__float32 expects 1 argument, got {len(args)}")
        sys.exit(1)
    float_value = args[0]
    print(float_value)
    return None

@register_builtin("@__builtin__println__float64")
def builtin_println_f64(args):
    """Print a 64-bit float followed by newline."""
    if len(args) != 1:
        print(f"ERROR: __builtin__println__float64 expects 1 argument, got {len(args)}")
        sys.exit(1)
    float_value = args[0]
    print(float_value)
    return None

@register_builtin("@__builtin__println__char__1")
def builtin_println_char_1(args):
    """Print a string (array of characters) followed by newline."""
    if len(args) != 1:
        print(f"ERROR: __builtin__println__char__1 expects 1 argument, got {len(args)}")
        sys.exit(1)
    string_value = args[0]
    # If it's already a string, print it
    if isinstance(string_value, str):
        print(string_value)
    # If it's a list/array, iterate and print each character
    elif isinstance(string_value, list):
        for char in string_value:
            if isinstance(char, int):
                print(chr(char), end='')
            else:
                print(char, end='')
        print()  # Add newline
    else:
        print(string_value)
    return None

# =================================================================================================
# Input Functions
# =================================================================================================

@register_builtin("@__builtin__input__i32")
def builtin_input_i32(args):
    """Read a 32-bit integer from stdin."""
    if len(args) != 0:
        print(f"ERROR: __builtin__input__i32 expects 0 arguments, got {len(args)}")
        sys.exit(1)
    try:
        return int(input())
    except ValueError:
        print("ERROR: Invalid integer input")
        sys.exit(1)

@register_builtin("@__builtin__input__f64")
def builtin_input_f64(args):
    """Read a 64-bit float from stdin."""
    if len(args) != 0:
        print(f"ERROR: __builtin__input__f64 expects 0 arguments, got {len(args)}")
        sys.exit(1)
    try:
        return float(input())
    except ValueError:
        print("ERROR: Invalid float input")
        sys.exit(1)

# =================================================================================================
# Utility Functions
# =================================================================================================

def is_builtin(function_name):
    """Check if a function name is a builtin."""
    return function_name in BUILTINS

def call_builtin(function_name, args):
    """Call a builtin function with given arguments."""
    if function_name not in BUILTINS:
        print(f"ERROR: Unknown builtin function: {function_name}")
        sys.exit(1)
    return BUILTINS[function_name](args)
