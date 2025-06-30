# CeruleanVM

CeruleanVM is a Virtual Machine for running CeruleanBytecode.

# Building

CeruleanVM uses a CMake build system. The following commands should build the project:
```bash
cmake -S . -B build/
cmake --build build
```

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

# Unit testing

```bash
./build/test_helloworld
./build/test_helloworld2
```
