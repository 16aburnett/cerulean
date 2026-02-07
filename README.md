# Cerulean Compiler Suite

Cerulean is a suite of programming languages, interpreters, and compilers.

The main purpose of this project is to explore making different compilers and programming languages. This is just meant to be a fun project and is meant to work similarly to something like [LLVM](https://github.com/llvm/llvm-project) with multiple frontend compilers, an intermediate language, and backend compilers to different target languages. This is also expected to have custom programming languages and interpreters.

This project is a work-in-progress. Currently, the following are implemented:
- Cerulean - A high-ish-level programming language with a compiler (`cerulean/compiler.py`)
    - this language closesly mirrors a language like C
    - the compiler compiles Cerulean code to CeruleanIR code that the backend compiler can convert to different target languages (Currently, CeruleanASM(WIP) or AmyAssembly)
- CeruleanIR - A low-level Intermediate Representation (IR) programming language with its own frontend compiler (`ceruleanir/compiler.py`)
    - this is the main glue language of the Cerulean project as all the frontends compile to CeruleanIR and the backend compiles this IR to many target languages
    - The CeruleanIR Frontend compiler just converts CeruleanIR text-code to an IR AST that is passed to the backend compiler
- Backend - the backend compiler (`backend/compiler.py`)
    - This takes in IR code (in AST form) and generates equivalent target-language code.
- CeruleanASM - A custom assembly language with an assembler (`ceruleanasm/assembler.py`)
    - the assembler converts CeruleanASM code to CeruleanObj code that can be passed to the linker (`ceruleanld/linker.py`) to generate CeruleanBytecode
- CeruleanBytecode - A custom RISC-like ISA with an interpreter/virtual machine stored in `ceruleanvm/` for running a CeruleanBytecode program

