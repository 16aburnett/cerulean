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
    #  void print__i32 (i32 val);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}print__i32",
        [ParameterNode(TypeSpecifierNode (Type.I32, "i32", None, 0), "val", None)]
    )
    #  void print__i64 (i64 val);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}print__i64",
        [ParameterNode(TypeSpecifierNode (Type.I64, "i64", None, 0), "val", None)]
    )
    #  void @print__f32 (f32 val);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}print__f32",
        [ParameterNode(TypeSpecifierNode (Type.F32, "f32", None, 0), "val", None)]
    )
    #  void @print__f64 (f64 val);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}print__f64",
        [ParameterNode(TypeSpecifierNode (Type.F64, "f64", None, 0), "val", None)]
    )
    #  void @print__char (char val);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}print__char",
        [ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None, 0), "val", None)]
    )
    #  void print__ptr (ptr val);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}print__ptr",
        [ParameterNode(TypeSpecifierNode (Type.PTR, "ptr", None, 0), "val", None)]
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
    #  void println (i32 intToPrint);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}println__i32",
        [ParameterNode(TypeSpecifierNode (Type.I32, "i32", None, 0), "intToPrint", None)]
    )
    #  void println (i64 intToPrint);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}println__i64",
        [ParameterNode(TypeSpecifierNode (Type.I64, "i64", None, 0), "intToPrint", None)]
    )
    #  void println (f32 floatToPrint);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}println__f32",
        [ParameterNode(TypeSpecifierNode (Type.F32, "f32", None, 0), "floatToPrint", None)]
    )
    #  void println (f64 floatToPrint);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}println__f64",
        [ParameterNode(TypeSpecifierNode (Type.F64, "f64", None, 0), "floatToPrint", None)]
    )
    #  void println (char c);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}println__char",
        [ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None, 0), "c", None)]
    )
    #  void println (ptr val);
    add_builtin_function (
        TypeSpecifierNode (Type.VOID, "void", None, 0),
        f"{BUILTIN_PREFIX}println__ptr",
        [ParameterNode(TypeSpecifierNode (Type.PTR, "ptr", None, 0), "val", None)]
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
        f"{BUILTIN_PREFIX}exit__i32",
        [ParameterNode(TypeSpecifierNode (Type.I32, "i32", None), "exit_status", None)]
    )
    #  f32 f32 ();
    add_builtin_function (
        TypeSpecifierNode (Type.F32, "f32", None, 0),
        f"{BUILTIN_PREFIX}f32",
        []
    )
    #  f64 f64 ();
    add_builtin_function (
        TypeSpecifierNode (Type.F64, "f64", None, 0),
        f"{BUILTIN_PREFIX}f64",
        []
    )
    # f32 i32Tof32 (i32 val);
    add_builtin_function (
        TypeSpecifierNode (Type.F32, "f32", None, 0),
        f"{BUILTIN_PREFIX}i32Tof32",
        [ParameterNode(TypeSpecifierNode (Type.I32, "i32", None, 0), "val", None)]
    )
    # f64 i64Tof64 (i64 val);
    add_builtin_function (
        TypeSpecifierNode (Type.F64, "f64", None, 0),
        f"{BUILTIN_PREFIX}i64Tof64",
        [ParameterNode(TypeSpecifierNode (Type.I64, "i64", None, 0), "val", None)]
    )
    # TODO: f64 i32Tof64 (i32 val);
    # TODO: f32 i64Tof32 (i64 val);
    #  f32 stringTof32 (char[]);
    add_builtin_function (
        TypeSpecifierNode (Type.F32, "f32", None, 0),
        f"{BUILTIN_PREFIX}stringTof32__char__1",
        [ParameterNode(TypeSpecifierNode (Type.PTR, "ptr", None, 0), "val", None)]
    )
    #  f64 stringTof64 (char[]);
    add_builtin_function (
        TypeSpecifierNode (Type.F64, "f64", None, 0),
        f"{BUILTIN_PREFIX}stringTof64__char__1",
        [ParameterNode(TypeSpecifierNode (Type.PTR, "ptr", None, 0), "val", None)]
    )
    #  i32 i32 ();
    add_builtin_function (
        TypeSpecifierNode (Type.I32, "i32", None, 0),
        f"{BUILTIN_PREFIX}i32",
        []
    )
    #  i64 i64 ();
    add_builtin_function (
        TypeSpecifierNode (Type.I64, "i64", None, 0),
        f"{BUILTIN_PREFIX}i64",
        []
    )
    #  char char ();
    add_builtin_function (
        TypeSpecifierNode (Type.CHAR, "char", None, 0),
        f"{BUILTIN_PREFIX}char",
        []
    )
    #  i32 f32Toi32 (f32);
    add_builtin_function (
        TypeSpecifierNode (Type.I32, "i32", None, 0),
        f"{BUILTIN_PREFIX}f32Toi32__f32",
        [ParameterNode(TypeSpecifierNode (Type.F32, "f32", None, 0), "val", None)]
    )
    #  i64 f64Toi64 (f64);
    add_builtin_function (
        TypeSpecifierNode (Type.I64, "i64", None, 0),
        f"{BUILTIN_PREFIX}f64Toi64__f64",
        [ParameterNode(TypeSpecifierNode (Type.F64, "f64", None, 0), "val", None)]
    )
    # TODO: i32 f64Toi64 (f64 val);
    # TODO: i64 f64Toi64 (f32 val);
    #  i32 stringToi32 (char[]);
    add_builtin_function (
        TypeSpecifierNode (Type.I32, "i32", None, 0),
        f"{BUILTIN_PREFIX}stringToi32__char__1",
        [ParameterNode(TypeSpecifierNode (Type.PTR, "ptr", None, 0), "val", None)]
    )
    #  i64 stringToi64 (char[]);
    add_builtin_function (
        TypeSpecifierNode (Type.I64, "i64", None, 0),
        f"{BUILTIN_PREFIX}stringToi64__char__1",
        [ParameterNode(TypeSpecifierNode (Type.PTR, "ptr", None, 0), "val", None)]
    )
    #  i32 charToi32 (char);
    add_builtin_function (
        TypeSpecifierNode (Type.I32, "i32", None, 0),
        f"{BUILTIN_PREFIX}charToi32__char",
        [ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None, 0), "val", None)]
    )
    #  i64 charToi64 (char);
    add_builtin_function (
        TypeSpecifierNode (Type.I64, "i64", None, 0),
        f"{BUILTIN_PREFIX}charToi64__char",
        [ParameterNode(TypeSpecifierNode (Type.CHAR, "char", None, 0), "val", None)]
    )
    #  char[] string (i32);
    add_builtin_function (
        TypeSpecifierNode (Type.PTR, "ptr", None, 0),
        f"{BUILTIN_PREFIX}string__i32",
        [ParameterNode(TypeSpecifierNode (Type.I32, "i32", None, 0), "val", None)]
    )
    #  char[] string (i64);
    add_builtin_function (
        TypeSpecifierNode (Type.PTR, "ptr", None, 0),
        f"{BUILTIN_PREFIX}string__i64",
        [ParameterNode(TypeSpecifierNode (Type.I64, "i64", None, 0), "val", None)]
    )
    #  char[] string (f32);
    add_builtin_function (
        TypeSpecifierNode (Type.PTR, "ptr", None, 0),
        f"{BUILTIN_PREFIX}string__f32",
        [ParameterNode(TypeSpecifierNode (Type.F32, "f32", None, 0), "val", None)]
    )
    #  char[] string (f64);
    add_builtin_function (
        TypeSpecifierNode (Type.PTR, "ptr", None, 0),
        f"{BUILTIN_PREFIX}string__f64",
        [ParameterNode(TypeSpecifierNode (Type.F64, "f64", None, 0), "val", None)]
    )
    #  void* null ();
    add_builtin_function (
        TypeSpecifierNode (Type.PTR, "ptr", None, 0),
        f"{BUILTIN_PREFIX}null",
        []
    )
    
    # === Additional builtins for interpreter ===
    #  i32 input__i32 ();
    add_builtin_function (
        TypeSpecifierNode (Type.I32, "i32", None, 0),
        f"{BUILTIN_PREFIX}input__i32",
        []
    )
    #  f64 input__f64 ();
    add_builtin_function (
        TypeSpecifierNode (Type.F64, "f64", None, 0),
        f"{BUILTIN_PREFIX}input__f64",
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
