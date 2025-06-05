

```bash

# run as a module for correct import between cerulean and ceruleanIR backend
# needs to run from root of repo
python3 -m cerulean.ceruleanCompiler cerulean/test_files/helloworld.cerulean --debug --emitTokens --emitAST --emitIR

```


```bash
# Building CeruleanIRBackend
# this does not seem to work??
# needed to install python i guess
sudo apt update && upgrade
sudo apt install python3 python3-pip ipython3
# need pyinstaller for building exe
pip install pyinstaller
# need to add to path??
export PATH="$HOME/.local/bin:$PATH"

# Compiling with ceruleanirc
python3 cerulean_ir_compiler.py test_files/helloworld.ceruleanir


# USAGE
# Compiles multiple source files into a single executable in the desired target lang
ceruleanirc <source_files> -o <dest_filename>


# test examples
python3 -m backend.ceruleanIRCompiler backend/test_files/helloworld.ceruleanir -o backend/test_files/helloworld.amyasm --debug
python3 AmyAssembly/code/amyAssemblyInterpreter.py backend/test_files/helloworld.ceruleanir.amyasm

python3 -m backend.ceruleanIRCompiler backend/test_files/test_math.ceruleanir -o backend/test_files/test_math.amyasm --debug
python3 AmyAssembly/code/amyAssemblyInterpreter.py backend/test_files/test_math.ceruleanir.amyasm

```

### NOTES ################################################################


Architecture:
- each frontend language needs its own compiler
- we dont actually need to convert frontend to an IR language, just to the IR AST and then codegen from there
    - so the frontend compiler becomes the full compiler
- The ceruleanIR code can be a separate module that the frontend compiler imports
    - CeruleanIR module handles creating the CeruleanIR AST (API functions for doing so, makeFunction() makeInstruction() etc..)
    - and it has multiple backend codegen visitors for each target language
    - The main compiler will then convert its AST to CeruleanIR and then run the codegen
- for debugging, we can add a CeruleanIR print visitor and a CeruleanIR compiler
```
ceruleanCompiler     -> lex/parse -> AST -|                   |-> codegen_x86
ceruleanPPCompiler   -> lex/parse -> AST -|-> CeruleanIR_AST -|-> codegen_amyasm
ceruleanFuncCompiler -> lex/parse -> AST -|         |         |-> codegen_ceruleanasm
ceruleanIRCompiler   -> lex/parse -> AST -|         |-> CeruleanIR emitter/codegen
```


Similar to Zig
- able to use the c library
- Cerulean should be the system level library
- compile to LLVM IR so we can leverage LLVM optimizations
- readability should be a focus so nothing like operator overloading
- no objects/inheritence - save it for cerulean++ or somethin
- 

int * or ptr(int)

https://www.freecodecamp.org/news/the-programming-language-pipeline-91d3f449c919/

Source language ideas
- Cerulean - my take on C, a systems level language
- Cerulean++ - my take on C++
- CeruleanScript - scripting language like JS/Python
    - not strongly typed
    - looks like JavaScript
    - garbage collection
    - interpreted, but maybe also a way to compile to Cerulean like Python->C
    - maybe like Julia
- CeruleanFunc - a functional language
- CeruleanFlow - a dataflow centered language
    - not sure if would be turing complete -__-
    - would heterogenous programming be possible?
- CeruleanVisual - a visual programming language - possibly esoteric
- CeruleanEsoteric - a fully esoteric variant of cerulean - the weirder the better
- CeruleanShell - a shell language bc why not - CeruleanOS?
- what about languages that already exist? that might be a nice challenge
    - even a subset
    - C/C++ -> CeruleanIR?
- what about a language like rust?

Target languages ideas
- CeruleanAssembly - new assembly language that uses registers
    - new/separate project
    - interpreter should be written in C++ for speed?
- x86
- AmyAssembly
- RISCV?
- LLVM IR?
- Transpiling?
    - unfortunately, i dont think this is possible through IR
    - bc high level -> low level -> high level would be difficult
    - but maybe we can fast track from high -> high as a separate path entirely
    - MLIR is probably the solution here
    - it doesnt HAVE to go through IR
    - C/C++
    - python

- self hosted compiler - cerulean compiler written in cerulean!!

Additional ideas
- my own compiler explorer
    - show Cerulean (or other source), Cerulean IR, and Cerulean Assembly (or other target)
    - have a way to trace generated code to IR and back to source code
    - Should support multiple files???
    - should allow you to write/edit source code and compile and run from the site
    - if i make a visual programming language - this would be a great place for a visual editor
- documentation website!! - MUST
    - How to compile
    - How to write Cerulean, CeruleanIR, CeruleanAssembly
    - Maybe a page describing how the compiler works? - make it educational?
    - use markdown this time so it doesnt suck to write


- load/store needs to specify how many bytes to load/store in mem

LLVM
SSR IR
- static single-assignment form
- requires each variable to be assigned exactly once and defined before it
    is used
- simplifies + improves the results of compiler optimizations by
    simplifying the properties of variables.
- for named variables that are assigned multiple times, add a subscript to
    the name to differentiate
- i think it was mentioned that it could even support functional
    programming languages.
https://en.wikipedia.org/wiki/Static_single-assignment_form

LLVM IR
- strongly typed
- reduced instruction set (RISC)
- The type system consists of basic types such as integer or 
    floating-point numbers and five derived types: pointers, arrays, 
    vectors, structures, and functions.



Comments
; this is comment

Data types
e - little endian
p:64:64:64 - 64-bit pointers with 64-bit alignment. - ptr
p[n]:64:64:64 - Other address spaces are assumed to be the same as the default address space.
S0 - natural stack alignment is unspecified
i1:8:8 - i1 is 8-bit (byte) aligned
i8:8:8 - i8 is 8-bit (byte) aligned as mandated
i16:16:16 - i16 is 16-bit aligned
i32:32:32 - i32 is 32-bit aligned
i64:32:64 - i64 has ABI alignment of 32-bits but preferred alignment of 64-bits
f16:16:16 - half is 16-bit aligned
f32:32:32 - float is 32-bit aligned
f64:64:64 - double is 64-bit aligned
f128:128:128 - quad is 128-bit aligned
v64:64:64 - 64-bit vector is 64-bit aligned
v128:128:128 - 128-bit vector is 128-bit aligned
a:0:64 - aggregates are 64-bit aligned
void

Arrays
- denoted with [<size> x <element_type>]
- example: [14 x i8] ; array of 14 8-bit integers (aka 1 byte integers)

Struct
- denoted with {<element0_type> <element0_value>, [<elementi_type> <elementi_value>,]}
- Example: {f32 %x}

Variables
denoted with %<varname>



What I want
- the ability to compile multiple high level programming languages
    - likely languages that I will make
    - my own C like language
    - I REALLY want a functional programming language at some point
    - esoteric langs too
    - possibly could implement a subset of C++/C, that would be cool!
- A middle level language similar to LLVM IR
    - i want to understand how LLVM IR works so make my own IR
    - this would greatly simplify compiling for each frontend and
    backend language as each frontend only goes to IR, and each
    backend only comes from the IR
- multiple backend languages
    - x86-64 of course!
    - transpile like my AmyScript compiler ->C++,Python,Others?
    - maybe even compile to AmyScript - inception?

- AmyC language
    - must be actually useable
    - and hopefully performant
    - pointers
    - strongly typed
    - but MUST have different syntax to C/C++
    - ability to use OpenMP for parallelization
    - ability to do things with the file system - OS support
        - likely a built-in open() or something
    - dont do the stupid thing where I dont have a main() function, bc ew
    - what should it be called?
        - something blue?
        - cerulean?
        - lapis lazuli
        - amethyst - or purpleW

- AmyScript did not have any optimizations - I want optimizations


Additionals
- Build my own compiler explorer for all frontend and backends and IR
- Build my own documentation - similar to AmyScript docs
    - figure out a way to use MD files so it is easier
- make an IR interpreter
- this is separate from AmyScript, but make an AmyScript->IR frontend, why not?    

