# CeruleanVM

CeruleanVM is a Virtual Machine for running CeruleanBytecode.

# Building

CeruleanVM uses a CMake build system. The following commands should build the project:
```bash
cmake -S . -B build/
cmake --build build
```
<!-- pushd ceruleanvm/ && rm -rf build/ && cmake -S . -B build/ && cmake --build build && popd -->

This should produce the CeruleanVM executable: `./build/ceruleanvm`

# Running

To run a CeruleanBytecode program, simply run the CeruleanVM executable with the CeruleanBytecode file.
```bash
./build/ceruleanvm <bytecode_file>
```

Hello World Example:
```bash
./build/ceruleanvm test_files/helloworld.ceruleanbc
```

# Debugger

CeruleanVM comes with a debugger that gives similar control over a program as something like `gdb`.
```bash
./build/ceruleandbg test_files/helloworld.ceruleanbc
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
