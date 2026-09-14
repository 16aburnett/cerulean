# CeruleanIR REPL

Interactive Read-Eval-Print Loop for CeruleanIR programs.

## Quick Start

```bash
# Start the REPL
python -m ceruleanir.repl

# Start with preloaded files
python -m ceruleanir.repl lib.ceruleanir utils.ceruleanir
```

## Usage

### Basic Instructions

Execute CeruleanIR instructions directly:

```
>>> %x = add (i32(5), i32(3))
=> 8

>>> %y = mul (i32(%x), i32(2))
=> 16

>>> %greeting = ptr ("Hello, REPL!")
```

### Define Functions

Define functions with multi-line input (use proper CeruleanIR syntax):

```
>>> function i32 @square () {
... block entry {
...   %val = mul (i32(5), i32(5))
...   return (i32(%val))
... }
... }
Defined @square
```

### Call Functions

```
>>> %result = call @square ()
=> 25
```

### Load Files

Load CeruleanIR files into the session:

```
>>> :load math.ceruleanir
Loaded math.ceruleanir

>>> :functions
Defined functions:
  @factorial
  @fibonacci
  @square
```

## Commands

All REPL commands start with `:` to distinguish them from CeruleanIR code.

### Session Management
```
:load <file>         Load a .ceruleanir file
:reset               Clear all state and restart
:quit (or :q)        Exit the REPL
```

### Inspection
```
:vars (or :v)        Show all variables
:globals (or :g)     Show global variables
:print <var> (or :p) Print value of a specific variable (e.g. :p %x)
:functions (or :f)   List all defined functions
```

### Help
```
:help (or :h, :?)    Show all commands
:help <command>      Show help for specific command
```

## Example Session

```bash
$ python -m ceruleanir.repl
CeruleanIR REPL
Type :help for commands, :quit to exit

>>> %x = add (i32(5), i32(3))
=> 8

>>> %y = mul (i32(%x), i32(2))
=> 16

>>> :vars
Variables:
  %x = 8
  %y = 16

>>> function i32 @double () {
... block entry {
...   %result = mul (i32(8), i32(2))
...   return (i32(%result))
... }
... }
Defined @double

>>> %z = call @double ()
=> 16

>>> :functions
Defined functions:
  @double

>>> :reset
Session reset

>>> :quit
```

## Features

- **Interactive execution** - Execute instructions immediately
- **Function definitions** - Define and call functions
- **Persistent state** - Variables persist across commands
- **Multi-line input** - Automatic detection of function definitions
- **File loading** - Import functions from .ceruleanir files
- **Error handling** - Graceful error messages without crashes
- **Command history** - Use up/down arrows for history (terminal dependent)

## Implementation Details

### Execution Model

When you enter an instruction, the REPL:
1. Wraps it in a temporary function
2. Executes the function
3. Preserves variables in global scope
4. Discards the temporary function

This allows immediate execution while maintaining a clean execution environment.

### Multi-line Input

Function definitions automatically trigger multi-line mode:
- Detects when a line starts with `@` and contains `{`
- Tracks brace nesting to detect completion
- Prompts with `...` until all braces are closed

### State Management

- **Variables**: Persist in the global scope across all commands
- **Functions**: Remain defined until `:reset` is called
- **Isolation**: Each instruction executes independently but shares state

## Tips

- Use **Ctrl+D** (Unix) or **Ctrl+Z** (Windows) to exit
- Use **Ctrl+C** to cancel multi-line input
- Start commands with `:` to avoid ambiguity
- Load common libraries at startup: `python -m ceruleanir.repl stdlib.ceruleanir`

## Future Enhancements

- Tab completion for function/variable names
- Syntax highlighting
- `:save session.ceruleanir` - Export current session
- `:debug <function>` - Drop into debugger for a function call
- Expression evaluation mode
