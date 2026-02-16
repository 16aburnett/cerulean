# Cerulean Compiler Suite

Cerulean is a suite of programming languages, interpreters, and compilers.

The main purpose of this project is to explore making different compilers and programming languages. This is just meant to be a fun project and is meant to work similarly to something like [LLVM](https://github.com/llvm/llvm-project) with multiple frontend compilers, an intermediate language, and backend compilers to different target languages. This is also expected to have custom programming languages and interpreters.

This project is a work-in-progress. Currently, the following are implemented:
- **Cerulean** - A high-ish-level programming language with a compiler (`cerulean/compiler.py`)
    - This language closely mirrors a language like C
    - The compiler compiles Cerulean code to CeruleanIR code that the backend compiler can convert to different target languages (Currently, CeruleanRISC or AmyAssembly)
- **CeruleanIR** - A low-level Intermediate Representation (IR) programming language with its own frontend compiler (`ceruleanir/compiler.py`)
    - This is the main glue language of the Cerulean project as all the frontends compile to CeruleanIR and the backend compiles this IR to many target languages
    - The CeruleanIR Frontend compiler just converts CeruleanIR text-code to an IR AST that is passed to the backend compiler
- **Backend** - The backend compiler (`backend/compiler.py`)
    - This takes in IR code (in AST form) and generates equivalent target-language code
- **CeruleanRISC (CRISC)** - A custom RISC-like ISA with complete toolchain (`ceruleanrisc/`)
    - **Assembler** (`ceruleanrisc/assembler/`) - Converts CeruleanRISC assembly to object files
    - **Linker** (`ceruleanrisc/linker/`) - Links object files into executable bytecode
    - **VM** (`ceruleanrisc/vm/`) - Virtual machine for executing CeruleanRISC bytecode
    - See [CeruleanRISC README](ceruleanrisc/README.md) for full ISA documentation

