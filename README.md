# Cerulean Compiler Suite

Cerulean is a suite of programming languages, interpreters, and compilers.

The main purpose of this project is to explore making different compilers and programming languages. This is just meant to be a fun project and is meant to work similarly to something like [LLVM](https://github.com/llvm/llvm-project) with multiple frontend compilers, an intermediate language, and backend compilers to different target languages. This is also expected to have custom programming languages and interpreters.

This project is currently a work-in-progress. Currently, the following are implemented:
- Cerulean - A high-ish-level programming language with a compiler (`cerulean/ceruleanCompiler.py`)
    - the compiler compiles Cerulean code to CeruleanIR code and uses the backend to compile CeruleanIR to different target languages (Currently, CeruleanASM(WIP) or AmyAssembly)
- CeruleanIR - An low-level Intermediate Representation (IR) programming language with a compiler (`backend/ceruleanIRCompiler.py`)
    - the compiler compiles CeruleanIR code to various target languages (Currently, CeruleanASM(WIP) or AmyAssembly)
- CeruleanASM - A custom assembly language with an assembler (`ceruleanasm/assembler.py`)
    - the assembler converts CeruleanASM code to CeruleanObj code that can be passed to the linker (`ceruleanld/linker.py`) to generate CeruleanBytecode
- CeruleanBytecode - A custom RISC-like ISA with an interpreter/virtual machine stored in `ceruleanvm/` for running a CeruleanBytecode program
