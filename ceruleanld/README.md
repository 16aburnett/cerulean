# CeruleanLD Linker

CeruleanLD is a linker for linking together 1 or more CeruleanObj object code files into a single CeruleanBytecode file that can be run with the CeruleanVM.

# Linking a program

```bash
python3 -m ceruleanld.linker <obj_files> -o <dest_file>
```

# Simple hello world example

```bash
python3 -m ceruleanld.linker ceruleanld/testFiles/helloworld.ceruleanobj -o ceruleanld/testFiles/helloworld.ceruleanbc
ceruleanvm/build/ceruleanvm ceruleanld/testFiles/helloworld.ceruleanbc
```
