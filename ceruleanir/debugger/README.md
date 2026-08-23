# CeruleanIR Debugger

Interactive debugger for CeruleanIR programs with breakpoints, stepping, and variable inspection.

## Quick Start

```bash
# Start debugging a program
python -m ceruleanir.debugger program.ceruleanir

# Debug with multiple files
python -m ceruleanir.debugger lib.ceruleanir main.ceruleanir
```

## Commands

### Execution Control
```
run (r)              - Start program execution
continue (c)         - Continue execution until breakpoint
step (s) [N]         - Step N instructions (into calls)
next (n) [N]         - Step N instructions (over calls)
finish (fin)         - Run until current function returns
quit (q)             - Exit debugger
```

### Breakpoints
```
break (b) <location> - Set breakpoint
  Examples:
    break @main              - Break at start of @main
    break @main.entry        - Break at entry block
    break @main.entry.5      - Break at instruction 5 in entry block
    
info breakpoints     - List all breakpoints
delete (d) <n>       - Delete breakpoint N
disable <n>          - Disable breakpoint N
enable <n>           - Enable breakpoint N
```

### Inspection
```
print (p) <var>      - Print variable value
  Examples:
    print %result
    print %i

info locals          - Show all local variables
info globals         - Show all global variables
list (l)             - Show current instruction
where (bt)           - Show call stack
```

### Help
```
help (h) [command]   - Show help for commands
```

## Example Session

```bash
$ python -m ceruleanir.debugger helloworld.ceruleanir
CeruleanIR Debugger
Type 'help' for list of commands, 'quit' to exit

(cirdb) break @main
Breakpoint 1 set at @main

(cirdb) run
Breakpoint at @main.entry.0
=> %0 = load (type(ptr), ptr(@customary_greeting), i32(0))

(cirdb) break @main.entry.2
Breakpoint 2 set at @main.entry.2

(cirdb) run
Breakpoint at @main.entry.2
=> call @print_greeting (ptr(%0), i32(%1))

(cirdb) info locals
Local variables:
  %0 = "Hello, World!"
  %1 = 13

(cirdb) break @print_greeting
Breakpoint 3 set at @print_greeting

(cirdb) run
Breakpoint at @print_greeting.entry.0
=> %i_ptr = alloca (type(i32), i32(1))

(cirdb) where
Call stack:
=> #0 @print_greeting
   #1 @main

(cirdb) info locals
Local variables:
  %greeting = "Hello, World!"
  %length = 13

(cirdb) delete 1
(cirdb) delete 2
(cirdb) delete 3

(cirdb) run
Hello, World!

Program exited with code 0

(cirdb) quit
```
Call stack:
=> #0 @factorial__i32
   #1 @main

(cirdb) continue
120
3628800

Program exited with code 0

(cirdb) quit
```

## Location Format

Breakpoint locations use the format: `@function_name[.block_name[.instruction_index]]`

Examples:
- `@main` - Any instruction in @main
- `@main.entry` - Any instruction in entry block
- `@main.entry.5` - Instruction 5 in entry block

## Current Limitations (MVP)

1. **Conditional breakpoints** - Syntax exists but conditions are not yet evaluated. All breakpoints are unconditional.

2. **Memory examination** - Not yet implemented.

3. **List command** - Cannot list source while paused, but context is shown automatically when hitting breakpoints.

### What Works ✅

✅ Set breakpoints at specific locations (`@function`, `@function.block.N`)  
✅ Program stops at breakpoints and shows current instruction  
✅ Variable inspection with `print` and `info locals/globals`  
✅ Call stack display with `where`  
✅ **Step command** - Execute one instruction at a time, including stepping into function calls  
✅ **Continue command** - Resume execution until next breakpoint or completion  
✅ Restart execution with `run` command

## Implementation Notes

The debugger works by registering a callback with the interpreter visitor. Before each instruction, the callback checks for breakpoints and stepping conditions. When a break condition is met, a `DebuggerBreakException` is raised to pause execution.

## Future Enhancements

- Conditional breakpoints with expression evaluation
- Watchpoints (break on variable change)
- Memory examination commands
- Better resume/pause support
- Command history (readline integration)
- Pretty printing for complex data structures
- REPL for CeruleanIR expression evaluation
