# CeruleanRISC Linker

CeruleanRISC linker is a linker for linking together 1 or more CeruleanRISC object code files into a single CeruleanRISC bytecode file that can be run with the CeruleanRISC VM.

# Linking a program

```bash
python3 -m ceruleanrisc.linker.linker <obj_files> -o <dest_file>
```

# Simple hello world example

```bash
python3 -m ceruleanrisc.linker.linker ceruleanrisc/linker/test_files/helloworld.crisco -o ceruleanrisc/linker/test_files/helloworld.criscbc
ceruleanrisc/vm/build/criscvm ceruleanrisc/linker/test_files/helloworld.criscbc
```
