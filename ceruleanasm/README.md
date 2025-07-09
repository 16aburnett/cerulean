# CeruleanASM Assembler

CeruleanASM Assembler is a low-level assembler for converting a CeruleanASM-language program to
CeruleanObjectCode. CeruleanObjectCode files can then be linked together using the CeruleanLinker
to a CeruleanByteCode file which can then be ran via the CeruleanVM iterpreter.

# Assembling a program

To assemble a program, run the assembler with your ASM file like below:
```bash
python3 -m ceruleanasm.assembler <INPUT_ASM_FILE> -o <OUTPUT_OBJ_FILE>
```

Example assembling the provided simple helloworld program:
```bash
python3 -m ceruleanasm.assembler ceruleanasm/test_files/helloworld.ceruleanasm -o ceruleanasm/test_files/helloworld.ceruleanobj --debug --emitTokens --emitAST
```



















# Unit testing

To use the unit tests, they need to be enabled while building:
```bash
cmake -S . -B build -DBUILD_TESTS=ON
cmake --build build
```

Then you can run all of the tests with the following:
```bash
./build/run_tests
```

You can list all the tests with `--list`:
```bash
$ ./build/run_tests --list
test_helloworld1
test_helloworld2
test_helloworld3
test_helloworld4
...
```

You can filter for different tests by passing a filter argument:
```bash
$ ./build/run_tests world3
[RUN ] test_helloworld3
Hello, World!
[ OK ] test_helloworld3 (44 µs)

1/1 tests passed. (total time: 0 ms)
```
This will run any tests whose name contains the given filter string.

You can also enable debugging prints via `--debug`:
```bash
$ ./build/run_tests world3 --debug
[RUN ] test_helloworld3
      pc | instruction | registers
00000000 | 01 00 50 00 | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ffffffff, ffffffff,
00000004 | 02 00 00 00 | 50, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ffffffff, ffffffff,
...
```
This will print out info like the program counter current instruction and current state of the registers.
