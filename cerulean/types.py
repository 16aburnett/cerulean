# Cerulean Compiler - Type Enum
# By Amy Burnett
# April 24 2021
# ========================================================================

from enum import Enum

# ========================================================================

class Type(Enum):
    BOOL     = 1
    BYTE     = 2
    CHAR     = 3
    INT32    = 4
    INT64    = 5
    FLOAT32  = 6
    FLOAT64  = 7
    VOID     = 8
    USERTYPE = 9
    NULL     = 10
    UNKNOWN  = 11

# ========================================================================
# Type Token Mappings
# ========================================================================
# Maps token types to (Type enum, type string) tuples
# Used by parser to convert tokens to TypeSpecifierNodes

TYPE_TOKEN_MAP = {
    'TYPE_BOOL':    (Type.BOOL,    "bool"),
    'TYPE_BYTE':    (Type.BYTE,    "byte"),
    'TYPE_CHAR':    (Type.CHAR,    "char"),
    'TYPE_INT32':   (Type.INT32,   "int32"),
    'TYPE_INT64':   (Type.INT64,   "int64"),
    'TYPE_FLOAT32': (Type.FLOAT32, "float32"),
    'TYPE_FLOAT64': (Type.FLOAT64, "float64"),
    'TYPE_VOID':    (Type.VOID,    "void"),
}

# Maps type keywords to token types (for tokenizer)
TYPE_KEYWORDS = {
    "bool":    "TYPE_BOOL",
    "byte":    "TYPE_BYTE",
    "char":    "TYPE_CHAR",
    "int32":   "TYPE_INT32",
    "int64":   "TYPE_INT64",
    "float32": "TYPE_FLOAT32",
    "float64": "TYPE_FLOAT64",
    "void":    "TYPE_VOID",
}
