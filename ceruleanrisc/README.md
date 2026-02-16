# CeruleanRISC (CRISC)

CeruleanRISC is a 32-bit fixed-width RISC-like instruction set architecture (ISA) with 64-bit registers. It serves as a compilation target for the Cerulean programming language and CeruleanIR intermediate representation.

## Overview

**Key Characteristics:**
- **Instruction Width:** 32 bits (fixed)
- **Register Width:** 64 bits
- **Architecture:** RISC-like, load-store
- **Registers:** 16 general-purpose registers (r0-r15)
  - `r0-r12`: General purpose
  - `ra/r13`: Return address
  - `bp/r14`: Base pointer
  - `sp/r15`: Stack pointer
- **Endianness:** Big-endian
- **Alignment:** 4-byte instruction alignment

## Directory Structure

```
ceruleanrisc/
├── README.md           # This file - ISA overview
├── assembler/          # CeruleanRISC assembler
│   ├── assembler.py    # Main assembler
│   ├── opcodes.py      # Opcode definitions
│   ├── parser.py       # Assembly parser
│   └── test_files/     # Test programs
├── vm/                 # CeruleanRISC virtual machine
│   ├── src/            # VM source (C++)
│   ├── lib/            # VM headers
│   └── tests/          # VM tests
└── linker/             # CeruleanRISC linker
    └── linker.py       # Object file linker
```

## Toolchain

### Assembler
Assembles CeruleanRISC assembly (`.crisc`) to object files (`.crisco`):
```bash
python3 -m ceruleanrisc.assembler.assembler input.crisc -o output.crisco
```

### Linker
Links object files into executable bytecode (`.criscbc`):
```bash
python3 -m ceruleanrisc.linker.linker input.crisco -o output.criscbc
```

### Virtual Machine
Executes CeruleanRISC bytecode:
```bash
ceruleanrisc/vm/build/criscvm program.criscbc
```

## Compilation Pipeline

```
Cerulean Source (.cerulean)
    ↓ [Cerulean Compiler]
CeruleanIR (.ir)
    ↓ [CeruleanIR Compiler]
CeruleanRISC Assembly (.crisc)
    ↓ [Assembler]
Object File (.crisco)
    ↓ [Linker]
Bytecode (.criscbc)
    ↓ [VM]
Execution
```

## Instruction Categories

- **Arithmetic:** add64, sub64, mul64, div64, mod64
- **Bitwise:** and64, or64, xor64, not32, not64, sll64, srl64, sra64
- **Comparison:** eq, lt, ltu, eqf32, eqf64, ltf32, ltf64, lef32, lef64
- **Memory:** load8/16/32/64, store8/16/32/64
- **Control Flow:** jmp, beq, bne, blt, bge, bltu, bgeu
- **Immediates:** lli (load lower immediate), loada (load address)
- **Stack:** push, pop, call, ret

## Documentation

- [Assembler README](assembler/README.md) - Assembly language syntax
- [VM README](vm/README.md) - Virtual machine implementation
- [Backend Architecture](../backend/backends/ceruleanrisc/ARCHITECTURE.md) - Compiler backend design

## Building the VM

```bash
cd ceruleanrisc/vm
cmake -B build
cmake --build build
./build/criscvm --help
```

## Running Tests

**Assembler Tests:**
```bash
cd ceruleanrisc/assembler
python3 -m pytest unittests/
```

**VM Tests:**
```bash
cd ceruleanrisc/vm/build
ctest
```

## License

See [LICENSE](../LICENSE) in the project root.
