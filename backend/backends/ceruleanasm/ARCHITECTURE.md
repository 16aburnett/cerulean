# CeruleanASM Backend - Multi-Pass Architecture

## Overview

The CeruleanASM backend uses a clean multi-pass compilation pipeline to convert CeruleanIR (SSA form) to CeruleanASM (physical machine code).

## Compilation Pipeline

```
CeruleanIR (SSA, unlimited vregs)
    ↓
[Pass 1: Lowering]
    ↓
Virtual CeruleanASM (SSA, unlimited vregs)
    ↓
[Pass 2: Liveness Analysis]
    ↓
Liveness Info (live ranges, def/use chains)
    ↓
[Pass 3: Register Allocation]
    ↓
Virtual CeruleanASM (physical regs + spill info)
    ↓
[Pass 4: Frame Lowering]
    ↓
Final CeruleanASM (with stack frames)
    ↓
[Pass 5: Code Emission]
    ↓
Assembly Text (.ceruleanasm)
```

## Pass Details

### Pass 1: Lowering (`lowering.py`)
**Purpose**: Convert high-level IR operations to low-level assembly operations

**Input**: CeruleanIR AST
- SSA form with unlimited virtual registers (`%var1`, `%var2`, ...)
- High-level instructions (`load(<type>, <ptr>, <offset>)`)
- Complex expressions

**Output**: Virtual CeruleanASM AST
- Still SSA form with unlimited virtual registers
- Low-level assembly instructions
- Expanded complex operations (e.g., `load(reg, reg)` → `add` + `load(reg, imm)`)
- Instruction selection done (e.g., `load8` vs `load64` based on types)

**Responsibilities**:
- Convert IR instructions to ASM instructions
- Expand pseudo-instructions
- Select appropriate instruction variants (e.g., `add64` vs `add64i`)
- Handle type-based instruction selection (`load8` for char, `load64` for int)
- Calling convention setup (argument passing, return values)

### Pass 2: Liveness Analysis (`livenessAnalyzer.py`)
**Purpose**: Determine which variables are live at each program point

**Input**: CeruleanIR or Virtual ASM
**Output**: Liveness information
- Live-in/live-out sets for each instruction
- Def-use chains
- Live ranges for each variable

**Responsibilities**:
- Data flow analysis
- Build control flow graph (CFG)
- Compute liveness sets via iterative algorithm
- Generate live range information

### Pass 3: Register Allocation (`registerAllocator.py`, `naiveAllocator.py`) ✅ COMPLETE!
**Purpose**: Map unlimited virtual registers to limited physical registers

**Input**: Virtual ASM + Liveness Info (optional for naive)
**Output**: Virtual ASM with allocation metadata
- Physical register assignments (linear scan) OR spill slots (naive)
- Spill slot assignments
- Stack frame size requirements

**Allocator Strategies** (via `AllocatorStrategy` enum):

1. **NAIVE** (`naiveAllocator.py`) - Default
   - Spills ALL virtual registers to stack
   - Uses scratch registers (r9-r11) only for intermediate operations
   - Always correct, no liveness analysis needed
   - Equivalent to GCC/Clang `-O0` behavior
   - Algorithm: Assign stack slot to each virtual register (offset 8, 16, 24, ...)

2. **LINEAR_SCAN** (`registerAllocator.py`)
   - Optimized allocation using linear scan algorithm
   - Requires liveness analysis
   - Algorithm:
     1. Build live ranges for each virtual register
     2. Sort variables by live range start
     3. For each variable:
        - Try to allocate a free physical register
        - If none available, spill (choose variable with furthest endpoint)
     4. Track spill slots needed

**Responsibilities**:
- Map virtual registers → physical registers (r0-r7) or stack slots
- Determine which variables need to be spilled to stack
- Calculate stack frame size
- Reserve scratch registers (r8-r10) for operations and spill handling

### Pass 4: Frame Lowering (`frameLowering.py`) ✨ NEW!
**Purpose**: Set up stack frames for functions

**Input**: Virtual ASM with register allocation
**Output**: Virtual ASM with stack frame info

**Responsibilities**:
- Calculate total stack frame size (spills + locals + alignment)
- Ensure 16-byte stack alignment (if needed)
- Annotate functions with stack frame metadata
- (Future) Insert explicit prologue/epilogue instructions

### Pass 5: Code Emission (`asmEmitter.py`) ✅ COMPLETE!
**Purpose**: Convert AST to assembly text with automatic spill handling

**Input**: Final Virtual ASM (with register allocations and stack frame info)
**Output**: Assembly text file

**Responsibilities**:
- Traverse AST and emit text
- Format instructions, labels, directives
- Use physical register assignments from allocation metadata
- **Automatic spill handling**: Load spilled operands into scratch registers, store results back
- Insert function prologue/epilogue based on frame info
- Resolve epilogue label placeholders
- Emit data section (strings, constants)
- Generate startup code that calls main

**Spilling Mechanics**:
For each instruction with spilled operands:
1. **Before instruction**: Load spilled sources into scratch registers (r9-r11)
   - `load64 r9, bp, -<offset> // load spilled %var`
2. **Execute instruction**: Use scratch registers in place of virtual registers
3. **After instruction**: Store result from scratch register back to spill slot
   - `store64 bp, r9, -<offset> // store to spilled %var`

**Instruction-specific handling**:
- **Store instructions**: All operands are sources (base address + value)
- **Load instructions**: First operand is destination, rest are sources
- **Branch instructions**: All operands are sources
- **Arithmetic/Logic**: First operand is destination, rest are sources

## Orchestrator: `codegen.py`

The `CodeGenVisitor_CeruleanASM` class serves as the orchestrator that:
1. Instantiates each pass in sequence
2. Passes data between passes
3. Optionally emits intermediate representations for debugging
4. Returns final assembly text

**Key Methods**:
- `generate(ast)`: Main entry point that runs all 5 passes
- `debugPrint()`: Helper for debug output

**Configuration**:
- `MAX_AVAILABLE_REGISTERS = 8`: Number of general-purpose registers (r0-r7)
- `scratchRegisters = ["r8", "r9", "r10"]`: Reserved for temporary operations
- `allocatorStrategy`: `AllocatorStrategy` enum (NAIVE or LINEAR_SCAN)

**AllocatorStrategy Enum**:
```python
class AllocatorStrategy(Enum):
    NAIVE = "naive"              # Spill everything, always correct
    LINEAR_SCAN = "linear-scan"  # Linear scan allocation (requires CFG for loops)
    # Future: GRAPH_COLORING, LLVM_STYLE, etc.
```

**Command-line Usage**:
```bash
# Use naive allocator (default, always correct)
python3 -m backend.ceruleanIRCompiler input.ceruleanir --target ceruleanasm

# Use linear scan allocator (optimized, requires proper CFG)
python3 -m backend.ceruleanIRCompiler input.ceruleanir --target ceruleanasm --regalloc linear-scan
```

## Current Status

✅ **Fully Implemented**:
- Pass 1: Lowering (core instructions: loada, lli, add64, load8/32/64, store32/64, alloca, jmp, jge)
- Pass 2: Liveness Analysis (working for straight-line code, needs CFG for loops)
- Pass 3a: Naive Allocator (COMPLETE - spills everything, always correct)
- Pass 3b: Linear Scan Allocator (working for straight-line code, needs CFG for loops)
- Pass 4: Frame Lowering (working - stack frame calculation with alignment)
- Pass 5: Code Emission (COMPLETE - automatic spill handling, proper instruction semantics)
- Pipeline integration (all passes connected and working)
- Spilling mechanics (COMPLETE - automatic load/store insertion)

✅ **Tested & Working**:
- **helloworld0.ceruleanir**: Simple sequential program (linear scan: 0 spills, naive: 14 spills)
- **helloworld1.ceruleanir**: Sequential with function calls (working)
- **helloworld3.ceruleanir**: Loop program (WORKING with naive allocator!)
  - Correctly prints "Hello, World!" from loop
  - Demonstrates proper spilling for loop-carried variables
  - All variables spilled to stack, loaded/stored around each operation

✅ **Architecture Improvements**:
- Enum-based allocator selection (`AllocatorStrategy`)
- Clean separation between allocator strategies
- Extensible design (easy to add graph coloring, etc.)
- Command-line flag: `--allocator=naive` or `--allocator=linear-scan`

🚧 **Known Limitations**:
1. **Linear scan allocator**: Requires CFG analysis for loops (incorrect liveness without CFG)
2. **Naive allocator**: Very conservative (spills everything), but ALWAYS CORRECT
3. **Liveness analyzer**: Simple backward pass, doesn't handle control flow joins properly

🚧 **TODO**:
1. Implement CFG analysis (control flow graph construction)
   - Proper loop detection and back-edge handling
   - Enable linear scan allocator for all programs
2. Complete lowering pass for remaining IR instructions:
   - Remaining branch instructions: `jl`, `jle`, `jg`, `jne`, `jeq`
   - Comparison operations: `clt`, `cle`, `cgt`, `cge`, `ceq`, `cne`
   - Memory operations: `malloc`, `free`
3. Add optimization passes:
   - Dead code elimination
   - Constant folding/propagation
   - Copy propagation
4. Improve linear scan allocator:
   - Live range splitting
   - Better spill cost heuristics
   - Register hints for moves

## Architecture Benefits

1. **Separation of Concerns**: Each pass has one clear responsibility
2. **Easier Debugging**: Can inspect IR after each pass (via `--emitTokens`, `--emitAST`, etc.)
3. **Better Testing**: Test each pass independently
4. **Optimization Ready**: Can insert optimization passes between any stage
5. **Maintainability**: Much easier to understand and modify (codegen.py reduced from 980 to ~140 lines)
6. **Reusability**: Register allocator and other passes can be reused for different backends

## File Structure

```
backend/backends/ceruleanasm/
├── codegen.py              # Main orchestrator (~170 lines)
├── lowering.py             # Pass 1: IR → Virtual ASM (~505 lines)
├── livenessAnalyzer.py     # Pass 2: Liveness analysis
├── naiveAllocator.py       # Pass 3a: Naive allocator (spill everything) (~190 lines)
├── registerAllocator.py    # Pass 3b: Linear scan allocator (~310 lines)
├── frameLowering.py        # Pass 4: Stack frame setup (~155 lines)
├── asmEmitter.py           # Pass 5: AST → Text emission (~450 lines)
├── ceruleanASMAST.py       # Virtual ASM AST definitions
├── ceruleanASMASTVisitor.py # Visitor base class
└── ARCHITECTURE.md         # This document
```

## Key Design Decisions

1. **Virtual ASM as Intermediate Form**: Allows unlimited virtual registers during early passes, making instruction selection and optimization easier.

2. **Linear Scan Register Allocation**: Fast and produces good results for most code. Can be upgraded to graph coloring for better results if needed.

3. **Separate Emission Pass**: Keeps text generation separate from semantic work, making it easy to retarget or change output format.

4. **Metadata Propagation**: Each pass attaches metadata to AST nodes (register assignments, stack frame sizes) that subsequent passes read.

5. **Visitor Pattern Throughout**: All passes use consistent visitor pattern for traversing AST, making code predictable and easy to extend.

## Performance Characteristics

**Compilation Speed**: Fast - all passes are O(n) or O(n log n)
- Lowering: O(n) - single traversal
- Liveness: O(n × iterations) - typically 2-3 iterations
- Register Allocation: O(n log n) - sort + linear scan
- Frame Lowering: O(n) - single traversal
- Emission: O(n) - single traversal

**Code Quality**:
- **Naive allocator**: Always correct, but inefficient (all variables spilled)
  - Guarantees correctness for ALL programs (loops, branches, etc.)
  - Equivalent to `-O0` in mature compilers
  - Large stack frames, many load/store operations
- **Linear scan allocator**: Efficient for straight-line code
  - Optimal for simple cases (0-byte stack frames when no spills)
  - Good register reuse (variables reused when dead)
  - Requires CFG analysis for correctness with loops
- Room for improvement with graph coloring, live range splitting, better spill costs

## Future Enhancements

1. **Instruction Scheduling**: Reorder instructions to avoid pipeline stalls
2. **Peephole Optimization**: Remove redundant moves, combine instructions
3. **Better Spill Strategy**: Currently uses "furthest first", could use more sophisticated heuristics
4. **Live Range Splitting**: Break long live ranges to improve allocation
5. **SSA Deconstruction**: Proper phi elimination for control flow joins
6. **Dead Code Elimination**: Remove unreachable code and unused computations

## References

Input CeruleanIR:
```
%str_ptr = value(ptr("Hello!\n"))
%i = value(0)
%ptr = add(%str_ptr, %i)
%c = load(char, %ptr, 0)
call @print(%c)
```

After Lowering (Pass 1):
```
loada %str_ptr, str_0
lli %i, 0
add64 %ptr, %str_ptr, %i
load8 %c, %ptr, 0        # Note: load8 chosen based on type
push %c
loada %tmp, @print
call %tmp
pop %tmp
```

After Register Allocation (Pass 3):
```
# Allocation: %str_ptr→r0, %i→r1, %ptr→r2, %c→r3
loada r0, str_0
lli r1, 0
add64 r2, r0, r1
load8 r3, r2, 0
push r3
loada r8, @print         # r8 is scratch reg
call r8
pop r10                  # r10 is scratch reg
# Stack frame size: 0 bytes (no spills)
```

After Frame Lowering (Pass 4):
```
# Function: print (metadata attached)
# Stack frame: 0 bytes (aligned to 16 bytes if needed)
```

After Code Emission (Pass 5):
```asm
print:
    push bp
    mv64 bp, sp
    # sub64i sp, sp, 0  # Would allocate 0 bytes (omitted when 0)
    
    # Function body with physical registers
    loada r0, str_0
    lli r1, 0
    add64 r2, r0, r1
    load8 r3, r2, 0
    push r3
    loada r8, @__builtin__print__char
    call r8
    pop r10
    
    # Function epilogue
    mv64 sp, bp
    pop bp
    ret

__start:
    loada r0, main
    call r0
    halt
```

## Architecture Benefits

- LLVM's register allocation: https://llvm.org/docs/CodeGenerator.html#register-allocation
- Linear Scan algorithm: Poletto & Sarkar, "Linear Scan Register Allocation"
- SSA deconstruction: Briggs et al., "Practical Improvements to the Construction and Destruction of SSA"
