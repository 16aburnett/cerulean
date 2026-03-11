# CeruleanIR Interpreter

A tree-walking interpreter for CeruleanIR programs with support for multi-file projects.

## Quick Start

### Command Line

**Single file:**
```bash
python3 -m ceruleanir.interpreter program.ceruleanir
```

**Multiple files:**
```bash
python3 -m ceruleanir.interpreter lib.ceruleanir utils.ceruleanir main.ceruleanir
```

**Debug mode:**
```bash
python3 -m ceruleanir.interpreter program.ceruleanir -d
```

### Python API

```python
from ceruleanir.interpreter import CeruleanIRInterpreter

# Single file
interpreter = CeruleanIRInterpreter()
interpreter.load_file('program.ceruleanir')
exit_code = interpreter.run()

# Multiple files
interpreter = CeruleanIRInterpreter()
interpreter.load_file('lib.ceruleanir')
interpreter.load_file('main.ceruleanir')
exit_code = interpreter.run()

# Load source code directly
interpreter = CeruleanIRInterpreter()
interpreter.load_source('function i32 @main() { ... }', '<input>')
exit_code = interpreter.run()

# Legacy single-file method
interpreter = CeruleanIRInterpreter()
exit_code = interpreter.interpret(source_code, 'filename.ceruleanir')
```

## Features

- **Multi-file programs** - Order-independent file loading with automatic linking
- **Extern declarations** - Forward declare functions defined in other files
- **SSA validation** - Semantic analysis catches variable reassignments
- **20+ instructions** - Full CeruleanIR instruction set support
- **15+ builtins** - Print, println, and input functions for various types
- **Global variables** - Module-level variable declarations
- **Memory operations** - Stack allocation (alloca), heap allocation (malloc/free), load/store

## Architecture

### Three-Phase Execution

1. **Load** - Parse each source file into an AST
2. **Link** - Merge all ASTs, check for duplicates, run semantic analysis
3. **Execute** - Interpret the linked program

### Multi-File Support

Files can reference functions defined in other files:

**lib.ceruleanir:**
```ceruleanir
function i32 @add(i32(%a), i32(%b)) {
    block entry {
        %result = add(i32(%a), i32(%b))
        return (i32(%result))
    }
}
```

**main.ceruleanir:**
```ceruleanir
extern function i32 @add(i32(%a), i32(%b));

function i32 @main() {
    block entry {
        %sum = call @add(i32(10), i32(20))
        call @__builtin__println__int32(i32(%sum))
        return (i32(0))
    }
}
```

Run with: `python3 -m ceruleanir.interpreter lib.ceruleanir main.ceruleanir`

## Error Handling

The interpreter provides clean error messages without stack traces for user errors:

- **File not found** - Missing source files
- **Parse errors** - Syntax errors in source code
- **Link errors** - Duplicate functions or globals across files
- **Semantic errors** - SSA violations, undefined variables, type mismatches

## Implementation

- **interpreter.py** - Main orchestrator (load/link/run phases)
- **visitor.py** - Tree-walking interpreter implementing all instructions
- **builtins.py** - Python implementations of builtin functions
- **__main__.py** - CLI entry point

## Testing

Run the test suite:
```bash
cd ceruleanir/test_files
python3 -m ceruleanir.interpreter helloworld.ceruleanir
python3 -m ceruleanir.interpreter multifile_lib.ceruleanir multifile_main.ceruleanir
python3 -m ceruleanir.interpreter test_math.ceruleanir
python3 -m ceruleanir.interpreter test_cmp.ceruleanir
```

## Future Enhancements

- **REPL** - Interactive interpreter with incremental code evaluation
- **Debugger** - Source-level debugging with breakpoints and step execution
- **Optimization** - Constant folding, dead code elimination
