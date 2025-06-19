# Cerulean IR Compiler - builtin functions/variables
# By Amy Burnett
# June 17, 2025
# ========================================================================

from .ceruleanIRAST import *
from .symbolTable import *

# ========================================================================

BUILTIN_PREFIX = "__builtin__"

# ========================================================================

def addBuiltinsToSymbolTable (symbolTable):
    def add_builtin_function (return_type, function_name, parameters):
        builtin_function_node = FunctionNode (return_type, f"@{function_name}", None, parameters, None)
        builtin_function_node.scopeName = function_name
        builtin_function_node.label = builtin_function_node.scopeName
        # create signature for node
        signature = [f"{builtin_function_node.id}("]
        if len(builtin_function_node.params) > 0:
            signature += [builtin_function_node.params[0].type.__str__()]
        for i in range(1, len(builtin_function_node.params)):
            signature += [f", {builtin_function_node.params[i].type.__str__()}"]
        signature += [")"]
        signature = "".join(signature)
        builtin_function_node.signature = signature
        symbolTable.insert (builtin_function_node, builtin_function_node.id, Kind.FUNC)

    # Add built-in functions/variables 
    #  char[] input ();
    add_builtin_function (
        TypeSpecifierNode (Type.PTR, "ptr", None, 0),
        f"{BUILTIN_PREFIX}input",
        []
    )
    #  void print (char[] str);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}print__char__1",
        [ParameterNode(TypeSpecifierNode (Type.PTR, "ptr", None, 0), "str", None)]
    )
    #  void print__int32 (int32 val);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}print__int32",
        [ParameterNode(TypeSpecifierNode (Type.INT32, "int32", None, 0), "val", None)]
    )
    #  void print__int64 (int64 val);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}print__int64",
        [ParameterNode(TypeSpecifierNode (Type.INT64, "int64", None, 0), "val", None)]
    )
    #  void @print__float32 (float32 val);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}print__float32",
        [ParameterNode(TypeSpecifierNode (Type.FLOAT32, "float32", None, 0), "val", None)]
    )
    #  void @print__float64 (float64 val);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}print__float64",
        [ParameterNode(TypeSpecifierNode (Type.FLOAT64, "float64", None, 0), "val", None)]
    )
    #  void @print__char (char val);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}print__char",
        [ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None, 0), "val", None)]
    )

#     #  void print (Enum e);
#     param0 = ParameterNode(TypeSpecifierNode (Type.USERTYPE, "Enum", None), "e", None)
#     printEnumFunc = FunctionNode (TypeSpecifierNode (Type.VOID, "void", None), "print", None, [param0], None)
#     printEnumFunc.scopeName = BUILTIN_PREFIX+"print__Enum"
#     printEnumFunc.label = printEnumFunc.scopeName
#     # create signature for node
#     signature = [f"{printEnumFunc.id}("]
#     if len(printEnumFunc.params) > 0:
#         signature += [printEnumFunc.params[0].type.__str__()]
#     for i in range(1, len(printEnumFunc.params)):
#         signature += [f", {printEnumFunc.params[i].type.__str__()}"]
#     signature += [")"]
#     signature = "".join(signature)
#     printEnumFunc.signature = signature
#     symbolTable.insert (printEnumFunc, printEnumFunc.id, Kind.FUNC)

    #  void println (char[] str);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}println__char__1",
        [ParameterNode(TypeSpecifierNode (Type.PTR, "ptr", None, 0), "str", None)]
    )
    #  void println (int32 intToPrint);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}println__int32",
        [ParameterNode(TypeSpecifierNode (Type.INT32, "int32", None, 0), "intToPrint", None)]
    )
    #  void println (int64 intToPrint);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}println__int64",
        [ParameterNode(TypeSpecifierNode (Type.INT64, "int64", None, 0), "intToPrint", None)]
    )
    #  void println (float32 floatToPrint);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}println__float32",
        [ParameterNode(TypeSpecifierNode (Type.FLOAT32, "float32", None, 0), "floatToPrint", None)]
    )
    #  void println (float64 floatToPrint);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}println__float64",
        [ParameterNode(TypeSpecifierNode (Type.FLOAT64, "float64", None, 0), "floatToPrint", None)]
    )
    #  void println (char c);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}println__char",
        [ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None, 0), "c", None)]
    )

#     #  void println (Enum e);
#     param0 = ParameterNode(TypeSpecifierNode (Type.USERTYPE, "Enum", None), "e", None)
#     printEnumFunc = FunctionNode (TypeSpecifierNode (Type.VOID, "void", None), "println", None, [param0], None)
#     printEnumFunc.scopeName = BUILTIN_PREFIX+"println__Enum"
#     printEnumFunc.label = printEnumFunc.scopeName
#     # create signature for node
#     signature = [f"{printEnumFunc.id}("]
#     if len(printEnumFunc.params) > 0:
#         signature += [printEnumFunc.params[0].type.__str__()]
#     for i in range(1, len(printEnumFunc.params)):
#         signature += [f", {printEnumFunc.params[i].type.__str__()}"]
#     signature += [")"]
#     signature = "".join(signature)
#     printEnumFunc.signature = signature
#     symbolTable.insert (printEnumFunc, printEnumFunc.id, Kind.FUNC)

    #  void println ();
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}println",
        []
    )
    #  void exit ();
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}exit",
        []
    )
    #  void exit (int exit_status);
    # for x86 this directly calls the system exit
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}exit__int32",
        [ParameterNode(TypeSpecifierNode (Type.INT32, "int32", None), "exit_status", None)]
    )
    #  float32 float32 ();
    add_builtin_function (
        TypeSpecifierNode (Type.FLOAT32, "float32", None, 0),
        f"{BUILTIN_PREFIX}float32",
        []
    )
    #  float64 float64 ();
    add_builtin_function (
        TypeSpecifierNode (Type.FLOAT64, "float64", None, 0),
        f"{BUILTIN_PREFIX}float64",
        []
    )
    # float32 int32ToFloat32 (int32 val);
    add_builtin_function (
        TypeSpecifierNode (Type.FLOAT32, "float32", None, 0),
        f"{BUILTIN_PREFIX}int32ToFloat32",
        [ParameterNode(TypeSpecifierNode (Type.INT32, "int32", None, 0), "val", None)]
    )
    # float64 int64ToFloat64 (int64 val);
    add_builtin_function (
        TypeSpecifierNode (Type.FLOAT64, "float64", None, 0),
        f"{BUILTIN_PREFIX}int64ToFloat64",
        [ParameterNode(TypeSpecifierNode (Type.INT64, "int64", None, 0), "val", None)]
    )
    # TODO: float64 int32ToFloat64 (int32 val);
    # TODO: float32 int64ToFloat32 (int64 val);
    #  float32 stringToFloat32 (char[]);
    add_builtin_function (
        TypeSpecifierNode (Type.FLOAT32, "float32", None, 0),
        f"{BUILTIN_PREFIX}stringToFloat32__char__1",
        [ParameterNode(TypeSpecifierNode (Type.PTR, "ptr", None, 0), "val", None)]
    )
    #  float64 stringToFloat64 (char[]);
    add_builtin_function (
        TypeSpecifierNode (Type.FLOAT64, "float64", None, 0),
        f"{BUILTIN_PREFIX}stringToFloat64__char__1",
        [ParameterNode(TypeSpecifierNode (Type.PTR, "ptr", None, 0), "val", None)]
    )
    #  int32 int32 ();
    add_builtin_function (
        TypeSpecifierNode (Type.INT32, "int32", None, 0),
        f"{BUILTIN_PREFIX}int32",
        []
    )
    #  int64 int64 ();
    add_builtin_function (
        TypeSpecifierNode (Type.INT64, "int64", None, 0),
        f"{BUILTIN_PREFIX}int64",
        []
    )
    #  char char ();
    add_builtin_function (
        TypeSpecifierNode (Type.CHAR, "char", None, 0),
        f"{BUILTIN_PREFIX}char",
        []
    )
    #  int32 float32ToInt32 (float32);
    add_builtin_function (
        TypeSpecifierNode (Type.INT32, "int32", None, 0),
        f"{BUILTIN_PREFIX}float32ToInt32__float32",
        [ParameterNode(TypeSpecifierNode (Type.FLOAT32, "float32", None, 0), "val", None)]
    )
    #  int64 float64ToInt64 (float64);
    add_builtin_function (
        TypeSpecifierNode (Type.INT64, "int64", None, 0),
        f"{BUILTIN_PREFIX}float64ToInt64__float64",
        [ParameterNode(TypeSpecifierNode (Type.FLOAT64, "float64", None, 0), "val", None)]
    )
    # TODO: int32 float64ToInt64 (float64 val);
    # TODO: int64 float64ToInt64 (float32 val);
    #  int32 stringToInt32 (char[]);
    add_builtin_function (
        TypeSpecifierNode (Type.INT32, "int32", None, 0),
        f"{BUILTIN_PREFIX}stringToInt32__char__1",
        [ParameterNode(TypeSpecifierNode (Type.PTR, "ptr", None, 0), "val", None)]
    )
    #  int64 stringToInt64 (char[]);
    add_builtin_function (
        TypeSpecifierNode (Type.INT64, "int64", None, 0),
        f"{BUILTIN_PREFIX}stringToInt64__char__1",
        [ParameterNode(TypeSpecifierNode (Type.PTR, "ptr", None, 0), "val", None)]
    )
    #  int32 charToInt32 (char);
    add_builtin_function (
        TypeSpecifierNode (Type.INT32, "int32", None, 0),
        f"{BUILTIN_PREFIX}charToInt32__char",
        [ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None, 0), "val", None)]
    )
    #  int64 charToInt64 (char);
    add_builtin_function (
        TypeSpecifierNode (Type.INT64, "int64", None, 0),
        f"{BUILTIN_PREFIX}charToInt64__char",
        [ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None, 0), "val", None)]
    )
    #  char[] string (int32);
    add_builtin_function (
        TypeSpecifierNode (Type.PTR, "ptr", None, 0),
        f"{BUILTIN_PREFIX}string__int32",
        [ParameterNode(TypeSpecifierNode (Type.INT32, "int32", None, 0), "val", None)]
    )
    #  char[] string (int64);
    add_builtin_function (
        TypeSpecifierNode (Type.PTR, "ptr", None, 0),
        f"{BUILTIN_PREFIX}string__int64",
        [ParameterNode(TypeSpecifierNode (Type.INT64, "int64", None, 0), "val", None)]
    )
    #  char[] string (float32);
    add_builtin_function (
        TypeSpecifierNode (Type.PTR, "ptr", None, 0),
        f"{BUILTIN_PREFIX}string__float32",
        [ParameterNode(TypeSpecifierNode (Type.FLOAT32, "float32", None, 0), "val", None)]
    )
    #  char[] string (float64);
    add_builtin_function (
        TypeSpecifierNode (Type.PTR, "ptr", None, 0),
        f"{BUILTIN_PREFIX}string__float64",
        [ParameterNode(TypeSpecifierNode (Type.FLOAT64, "float64", None, 0), "val", None)]
    )
    #  void* null ();
    add_builtin_function (
        TypeSpecifierNode (Type.PTR, "ptr", None, 0),
        f"{BUILTIN_PREFIX}null",
        []
    )


    # # LIBRARY OBJECTS

    # # create default object type 
    # # class Object
    # # {
    # #   public virtual char[] toString ()
    # #   {
    # #       return "<Object>";
    # #   }
    # # }
    # objClass = ClassDeclarationNode (TypeSpecifierNode (Type.USERTYPE, "Object", None), "Object", None, None, [], [], [], [], [])
    # objClass.scopeName = BUILTIN_PREFIX+"__main__Object"
    # symbolTable.insert (objClass, "Object", Kind.TYPE)

    # # create default object type 
    # enumClass = ClassDeclarationNode (TypeSpecifierNode (Type.USERTYPE, "Enum", None), "Enum", None, None, ["Object"], [], [], [], [])
    # enumClass.scopeName = BUILTIN_PREFIX+"__main__Enum"
    # symbolTable.insert (enumClass, "Enum", Kind.TYPE)
