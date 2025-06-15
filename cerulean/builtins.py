# Cerulean Compiler - builtin functions/variables
# By Amy Burnett
# June 15, 2025
# ========================================================================

from .ceruleanAST import *
from .symbolTable import *

# ========================================================================

BUILTIN_PREFIX = "__builtin__"

# ========================================================================

def addBuiltinsToSymbolTable (symbolTable):
    #  char[] input ();
    inputFunc = FunctionNode (TypeSpecifierNode (Type.CHAR, "char", None, arrayDimensions=1), "input", None, [], None)
    inputFunc.scopeName = BUILTIN_PREFIX+"input"
    inputFunc.label = inputFunc.scopeName
    # create signature for node
    signature = [f"{inputFunc.id}("]
    if len(inputFunc.params) > 0:
        signature += [inputFunc.params[0].type.__str__()]
    for i in range(1, len(inputFunc.params)):
        signature += [f", {inputFunc.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    inputFunc.signature = signature
    symbolTable.insert (inputFunc, inputFunc.id, Kind.FUNC)

    #  void print (char[] str);
    param0 = ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None), "str", None)
    param0.type.arrayDimensions += 1
    printFunc = FunctionNode (TypeSpecifierNode (Type.VOID, "void", None), "print", None, [param0], None)
    printFunc.scopeName = BUILTIN_PREFIX+"print__char__1"
    printFunc.label = printFunc.scopeName
    # create signature for node
    signature = [f"{printFunc.id}("]
    if len(printFunc.params) > 0:
        signature += [printFunc.params[0].type.__str__()]
    for i in range(1, len(printFunc.params)):
        signature += [f", {printFunc.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    printFunc.signature = signature
    symbolTable.insert (printFunc, printFunc.id, Kind.FUNC)

    #  void print (int intToPrint);
    param0 = ParameterNode(TypeSpecifierNode (Type.INT32, "int32", None), "intToPrint", None)
    printIntFunc = FunctionNode (TypeSpecifierNode (Type.VOID, "void", None), "print", None, [param0], None)
    printIntFunc.scopeName = BUILTIN_PREFIX+"print__int32"
    printIntFunc.label = printIntFunc.scopeName
    # create signature for node
    signature = [f"{printIntFunc.id}("]
    if len(printIntFunc.params) > 0:
        signature += [printIntFunc.params[0].type.__str__()]
    for i in range(1, len(printIntFunc.params)):
        signature += [f", {printIntFunc.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    printIntFunc.signature = signature
    symbolTable.insert (printIntFunc, printIntFunc.id, Kind.FUNC)

    #  void print (float floatToPrint);
    param0 = ParameterNode(TypeSpecifierNode (Type.FLOAT32, "float32", None), "val", None)
    printFloatFunc = FunctionNode (TypeSpecifierNode (Type.VOID, "void", None), "print", None, [param0], None)
    printFloatFunc.scopeName = BUILTIN_PREFIX+"print__float32"
    printFloatFunc.label = printFloatFunc.scopeName
    # create signature for node
    signature = [f"{printFloatFunc.id}("]
    if len(printFloatFunc.params) > 0:
        signature += [printFloatFunc.params[0].type.__str__()]
    for i in range(1, len(printFloatFunc.params)):
        signature += [f", {printFloatFunc.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    printFloatFunc.signature = signature
    symbolTable.insert (printFloatFunc, printFloatFunc.id, Kind.FUNC)

    #  void print (char c);
    param0 = ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None), "val", None)
    printCharFunc = FunctionNode (TypeSpecifierNode (Type.VOID, "void", None), "print", None, [param0], None)
    printCharFunc.scopeName = BUILTIN_PREFIX+"print__char"
    printCharFunc.label = printCharFunc.scopeName
    # create signature for node
    signature = [f"{printCharFunc.id}("]
    if len(printCharFunc.params) > 0:
        signature += [printCharFunc.params[0].type.__str__()]
    for i in range(1, len(printCharFunc.params)):
        signature += [f", {printCharFunc.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    printCharFunc.signature = signature
    symbolTable.insert (printCharFunc, printCharFunc.id, Kind.FUNC)

    #  void print (Enum e);
    param0 = ParameterNode(TypeSpecifierNode (Type.USERTYPE, "Enum", None), "e", None)
    printEnumFunc = FunctionNode (TypeSpecifierNode (Type.VOID, "void", None), "print", None, [param0], None)
    printEnumFunc.scopeName = BUILTIN_PREFIX+"print__Enum"
    printEnumFunc.label = printEnumFunc.scopeName
    # create signature for node
    signature = [f"{printEnumFunc.id}("]
    if len(printEnumFunc.params) > 0:
        signature += [printEnumFunc.params[0].type.__str__()]
    for i in range(1, len(printEnumFunc.params)):
        signature += [f", {printEnumFunc.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    printEnumFunc.signature = signature
    symbolTable.insert (printEnumFunc, printEnumFunc.id, Kind.FUNC)

    #  void println (char[] str);
    param0 = ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None), "str", None)
    param0.type.arrayDimensions += 1
    printlnFunc = FunctionNode (TypeSpecifierNode (Type.VOID, "void", None), "println", None, [param0], None)
    printlnFunc.scopeName = BUILTIN_PREFIX+"println__char__1"
    printlnFunc.label = printlnFunc.scopeName
    # create signature for node
    signature = [f"{printlnFunc.id}("]
    if len(printlnFunc.params) > 0:
        signature += [printlnFunc.params[0].type.__str__()]
    for i in range(1, len(printlnFunc.params)):
        signature += [f", {printlnFunc.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    printlnFunc.signature = signature
    symbolTable.insert (printlnFunc, printlnFunc.id, Kind.FUNC)

    #  void println (int intToPrint);
    param0 = ParameterNode(TypeSpecifierNode (Type.INT32, "int32", None), "intToPrint", None)
    printIntFunc = FunctionNode (TypeSpecifierNode (Type.VOID, "void", None), "println", None, [param0], None)
    printIntFunc.scopeName = BUILTIN_PREFIX+"println__int32"
    printIntFunc.label = printIntFunc.scopeName
    # create signature for node
    signature = [f"{printIntFunc.id}("]
    if len(printIntFunc.params) > 0:
        signature += [printIntFunc.params[0].type.__str__()]
    for i in range(1, len(printIntFunc.params)):
        signature += [f", {printIntFunc.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    printIntFunc.signature = signature
    symbolTable.insert (printIntFunc, printIntFunc.id, Kind.FUNC)

    #  void println (float floatToPrint);
    param0 = ParameterNode(TypeSpecifierNode (Type.FLOAT32, "float32", None), "val", None)
    printFloatFunc = FunctionNode (TypeSpecifierNode (Type.VOID, "void", None), "println", None, [param0], None)
    printFloatFunc.scopeName = BUILTIN_PREFIX+"println__float32"
    printFloatFunc.label = printFloatFunc.scopeName
    # create signature for node
    signature = [f"{printFloatFunc.id}("]
    if len(printFloatFunc.params) > 0:
        signature += [printFloatFunc.params[0].type.__str__()]
    for i in range(1, len(printFloatFunc.params)):
        signature += [f", {printFloatFunc.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    printFloatFunc.signature = signature
    symbolTable.insert (printFloatFunc, printFloatFunc.id, Kind.FUNC)

    #  void println (char c);
    param0 = ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None), "val", None)
    printCharFunc = FunctionNode (TypeSpecifierNode (Type.VOID, "void", None), "println", None, [param0], None)
    printCharFunc.scopeName = BUILTIN_PREFIX+"println__char"
    printCharFunc.label = printCharFunc.scopeName
    # create signature for node
    signature = [f"{printCharFunc.id}("]
    if len(printCharFunc.params) > 0:
        signature += [printCharFunc.params[0].type.__str__()]
    for i in range(1, len(printCharFunc.params)):
        signature += [f", {printCharFunc.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    printCharFunc.signature = signature
    symbolTable.insert (printCharFunc, printCharFunc.id, Kind.FUNC)

    #  void println (Enum e);
    param0 = ParameterNode(TypeSpecifierNode (Type.USERTYPE, "Enum", None), "e", None)
    printEnumFunc = FunctionNode (TypeSpecifierNode (Type.VOID, "void", None), "println", None, [param0], None)
    printEnumFunc.scopeName = BUILTIN_PREFIX+"println__Enum"
    printEnumFunc.label = printEnumFunc.scopeName
    # create signature for node
    signature = [f"{printEnumFunc.id}("]
    if len(printEnumFunc.params) > 0:
        signature += [printEnumFunc.params[0].type.__str__()]
    for i in range(1, len(printEnumFunc.params)):
        signature += [f", {printEnumFunc.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    printEnumFunc.signature = signature
    symbolTable.insert (printEnumFunc, printEnumFunc.id, Kind.FUNC)

    #  void println ();
    printCharFunc = FunctionNode (TypeSpecifierNode (Type.VOID, "void", None), "println", None, [], None)
    printCharFunc.scopeName = BUILTIN_PREFIX+"println"
    printCharFunc.label = printCharFunc.scopeName
    # create signature for node
    signature = [f"{printCharFunc.id}("]
    if len(printCharFunc.params) > 0:
        signature += [printCharFunc.params[0].type.__str__()]
    for i in range(1, len(printCharFunc.params)):
        signature += [f", {printCharFunc.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    printCharFunc.signature = signature
    symbolTable.insert (printCharFunc, printCharFunc.id, Kind.FUNC)

    #  void exit ();
    # for x86 this directly calls the system exit
    exitFunc = FunctionNode (TypeSpecifierNode (Type.VOID, "void", None), "exit", None, [], None)
    exitFunc.scopeName = BUILTIN_PREFIX+"exit"
    exitFunc.label = exitFunc.scopeName
    # create signature for node
    exitFunc.signature = "exit()"
    symbolTable.insert (exitFunc, exitFunc.id, Kind.FUNC)

    #  void exit (int exit_status);
    # for x86 this directly calls the system exit
    param0 = ParameterNode(TypeSpecifierNode (Type.INT32, "int32", None), "exit_status", None)
    exitFunc = FunctionNode (TypeSpecifierNode (Type.VOID, "void", None), "exit", None, [param0], None)
    exitFunc.scopeName = BUILTIN_PREFIX+"exit__int32"
    exitFunc.label = exitFunc.scopeName
    # create signature for node
    exitFunc.signature = "exit(int)"
    symbolTable.insert (exitFunc, exitFunc.id, Kind.FUNC)

    #  float float ();
    builtinFunction = FunctionNode (TypeSpecifierNode (Type.FLOAT32, "float32", None, []), "float", None, [], None)
    builtinFunction.scopeName = BUILTIN_PREFIX+"float32"
    builtinFunction.label = builtinFunction.scopeName
    # create signature for node
    signature = [f"{builtinFunction.id}("]
    if len(builtinFunction.params) > 0:
        signature += [builtinFunction.params[0].type.__str__()]
    for i in range(1, len(builtinFunction.params)):
        signature += [f", {builtinFunction.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    builtinFunction.signature = signature
    symbolTable.insert (builtinFunction, builtinFunction.id, Kind.FUNC)

    #  float intToFloat (int val);
    param0 = ParameterNode(TypeSpecifierNode (Type.INT32, "int32", None), "val", None)
    builtinFunction = FunctionNode (TypeSpecifierNode (Type.FLOAT32, "float32", None), "intToFloat", None, [param0], None)
    builtinFunction.scopeName = BUILTIN_PREFIX+"intToFloat__int32"
    builtinFunction.label = builtinFunction.scopeName
    # create signature for node
    signature = [f"{builtinFunction.id}("]
    if len(builtinFunction.params) > 0:
        signature += [builtinFunction.params[0].type.__str__()]
    for i in range(1, len(builtinFunction.params)):
        signature += [f", {builtinFunction.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    builtinFunction.signature = signature
    symbolTable.insert (builtinFunction, builtinFunction.id, Kind.FUNC)

    #  float stringToFloat (char[]);
    param0 = ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None), "val", None)
    param0.type.arrayDimensions = 1
    builtinFunction = FunctionNode (TypeSpecifierNode (Type.FLOAT32, "float32", None), "stringToFloat", None, [param0], None)
    builtinFunction.scopeName = BUILTIN_PREFIX+"stringToFloat__char__1"
    builtinFunction.label = builtinFunction.scopeName
    # create signature for node
    signature = [f"{builtinFunction.id}("]
    if len(builtinFunction.params) > 0:
        signature += [builtinFunction.params[0].type.__str__()]
    for i in range(1, len(builtinFunction.params)):
        signature += [f", {builtinFunction.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    builtinFunction.signature = signature
    symbolTable.insert (builtinFunction, builtinFunction.id, Kind.FUNC)

    #  int int ();
    builtinFunction = FunctionNode (TypeSpecifierNode (Type.INT32, "int32", None, []), "int", None, [], None)
    builtinFunction.scopeName = BUILTIN_PREFIX+"int32"
    builtinFunction.label = builtinFunction.scopeName
    # create signature for node
    signature = [f"{builtinFunction.id}("]
    if len(builtinFunction.params) > 0:
        signature += [builtinFunction.params[0].type.__str__()]
    for i in range(1, len(builtinFunction.params)):
        signature += [f", {builtinFunction.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    builtinFunction.signature = signature
    symbolTable.insert (builtinFunction, builtinFunction.id, Kind.FUNC)

    #  char char ();
    builtinFunction = FunctionNode (TypeSpecifierNode (Type.CHAR, "char", None, []), "char", None, [], None)
    builtinFunction.scopeName = BUILTIN_PREFIX+"char"
    builtinFunction.label = builtinFunction.scopeName
    # create signature for node
    signature = [f"{builtinFunction.id}("]
    if len(builtinFunction.params) > 0:
        signature += [builtinFunction.params[0].type.__str__()]
    for i in range(1, len(builtinFunction.params)):
        signature += [f", {builtinFunction.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    builtinFunction.signature = signature
    symbolTable.insert (builtinFunction, builtinFunction.id, Kind.FUNC)

    #  int floatToInt (float);
    param0 = ParameterNode(TypeSpecifierNode (Type.FLOAT32, "float32", None), "val", None)
    builtinFunction = FunctionNode (TypeSpecifierNode (Type.INT32, "int32", None), "floatToInt", None, [param0], None)
    builtinFunction.scopeName = BUILTIN_PREFIX+"floatToInt__float32"
    builtinFunction.label = builtinFunction.scopeName
    # create signature for node
    signature = [f"{builtinFunction.id}("]
    if len(builtinFunction.params) > 0:
        signature += [builtinFunction.params[0].type.__str__()]
    for i in range(1, len(builtinFunction.params)):
        signature += [f", {builtinFunction.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    builtinFunction.signature = signature
    symbolTable.insert (builtinFunction, builtinFunction.id, Kind.FUNC)

    #  int stringToInt (char[]);
    param0 = ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None), "val", None)
    param0.type.arrayDimensions = 1
    builtinFunction = FunctionNode (TypeSpecifierNode (Type.INT32, "int32", None), "stringToInt", None, [param0], None)
    builtinFunction.scopeName = BUILTIN_PREFIX+"stringToInt__char__1"
    builtinFunction.label = builtinFunction.scopeName
    # create signature for node
    signature = [f"{builtinFunction.id}("]
    if len(builtinFunction.params) > 0:
        signature += [builtinFunction.params[0].type.__str__()]
    for i in range(1, len(builtinFunction.params)):
        signature += [f", {builtinFunction.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    builtinFunction.signature = signature
    symbolTable.insert (builtinFunction, builtinFunction.id, Kind.FUNC)

    #  int charToInt (char);
    param0 = ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None), "val", None)
    builtinFunction = FunctionNode (TypeSpecifierNode (Type.INT32, "int32", None), "charToInt", None, [param0], None)
    builtinFunction.scopeName = BUILTIN_PREFIX+"charToInt__char"
    builtinFunction.label = builtinFunction.scopeName
    # create signature for node
    signature = [f"{builtinFunction.id}("]
    if len(builtinFunction.params) > 0:
        signature += [builtinFunction.params[0].type.__str__()]
    for i in range(1, len(builtinFunction.params)):
        signature += [f", {builtinFunction.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    builtinFunction.signature = signature
    symbolTable.insert (builtinFunction, builtinFunction.id, Kind.FUNC)

    #  char[] string (int);
    param0 = ParameterNode(TypeSpecifierNode (Type.INT32, "int32", None), "val", None)
    builtinFunction = FunctionNode (TypeSpecifierNode (Type.CHAR, "char", None), "string", None, [param0], None)
    builtinFunction.type.arrayDimensions = 1
    builtinFunction.scopeName = BUILTIN_PREFIX+"string__int32"
    builtinFunction.label = builtinFunction.scopeName
    # create signature for node
    signature = [f"{builtinFunction.id}("]
    if len(builtinFunction.params) > 0:
        signature += [builtinFunction.params[0].type.__str__()]
    for i in range(1, len(builtinFunction.params)):
        signature += [f", {builtinFunction.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    builtinFunction.signature = signature
    symbolTable.insert (builtinFunction, builtinFunction.id, Kind.FUNC)

    #  char[] string (float);
    param0 = ParameterNode(TypeSpecifierNode (Type.FLOAT32, "float32", None), "val", None)
    builtinFunction = FunctionNode (TypeSpecifierNode (Type.CHAR, "char", None), "string", None, [param0], None)
    builtinFunction.type.arrayDimensions = 1
    builtinFunction.scopeName = BUILTIN_PREFIX+"string__float32"
    builtinFunction.label = builtinFunction.scopeName
    # create signature for node
    signature = [f"{builtinFunction.id}("]
    if len(builtinFunction.params) > 0:
        signature += [builtinFunction.params[0].type.__str__()]
    for i in range(1, len(builtinFunction.params)):
        signature += [f", {builtinFunction.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    builtinFunction.signature = signature
    symbolTable.insert (builtinFunction, builtinFunction.id, Kind.FUNC)

    #  null null ();
    builtinFunction = FunctionNode (TypeSpecifierNode (Type.NULL, "null", None, []), "null", None, [], None)
    builtinFunction.scopeName = BUILTIN_PREFIX+"null"
    builtinFunction.label = builtinFunction.scopeName
    # create signature for node
    signature = [f"{builtinFunction.id}("]
    if len(builtinFunction.params) > 0:
        signature += [builtinFunction.params[0].type.__str__()]
    for i in range(1, len(builtinFunction.params)):
        signature += [f", {builtinFunction.params[i].type.__str__()}"]
    signature += [")"]
    signature = "".join(signature)
    builtinFunction.signature = signature
    symbolTable.insert (builtinFunction, builtinFunction.id, Kind.FUNC)


    # LIBRARY OBJECTS

    # create default object type 
    # class Object
    # {
    #   public virtual char[] toString ()
    #   {
    #       return "<Object>";
    #   }
    # }
    objClass = ClassDeclarationNode (TypeSpecifierNode (Type.USERTYPE, "Object", None), "Object", None, None, [], [], [], [], [])
    objClass.scopeName = BUILTIN_PREFIX+"__main__Object"
    symbolTable.insert (objClass, "Object", Kind.TYPE)

    # create default object type 
    enumClass = ClassDeclarationNode (TypeSpecifierNode (Type.USERTYPE, "Enum", None), "Enum", None, None, ["Object"], [], [], [], [])
    enumClass.scopeName = BUILTIN_PREFIX+"__main__Enum"
    symbolTable.insert (enumClass, "Enum", Kind.TYPE)

