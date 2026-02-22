# Cerulean Compiler - Type Enum
# By Amy Burnett
# Feb 21, 2026
# ========================================================================

from enum import Enum

# ========================================================================

class Type(Enum):
    BOOL     = 1
    BYTE     = 2
    CHAR     = 3
    INT8     = 4
    INT16    = 5
    INT32    = 6
    INT64    = 7
    UINT8    = 8
    UINT16   = 9
    UINT32   = 10
    UINT64   = 11
    FLOAT32  = 12
    FLOAT64  = 13
    VOID     = 14
    USERTYPE = 15
    NULL     = 16
    UNKNOWN  = 17

# ========================================================================
# Type Token Mappings
# ========================================================================
# Maps token types to (Type enum, type string) tuples
# Used by parser to convert tokens to TypeSpecifierNodes

TYPE_TOKEN_MAP = {
    'TYPE_BOOL':    (Type.BOOL,    "bool"),
    'TYPE_BYTE':    (Type.BYTE,    "byte"),
    'TYPE_CHAR':    (Type.CHAR,    "char"),
    'TYPE_INT8':    (Type.INT8,    "int8"),
    'TYPE_INT16':   (Type.INT16,   "int16"),
    'TYPE_INT32':   (Type.INT32,   "int32"),
    'TYPE_INT64':   (Type.INT64,   "int64"),
    'TYPE_UINT8':   (Type.UINT8,   "uint8"),
    'TYPE_UINT16':  (Type.UINT16,  "uint16"),
    'TYPE_UINT32':  (Type.UINT32,  "uint32"),
    'TYPE_UINT64':  (Type.UINT64,  "uint64"),
    'TYPE_FLOAT32': (Type.FLOAT32, "float32"),
    'TYPE_FLOAT64': (Type.FLOAT64, "float64"),
    'TYPE_VOID':    (Type.VOID,    "void"),
}

# Maps type keywords to token types (for tokenizer)
TYPE_KEYWORDS = {
    "bool":    "TYPE_BOOL",
    "byte":    "TYPE_BYTE",
    "char":    "TYPE_CHAR",
    "int8":    "TYPE_INT8",
    "int16":   "TYPE_INT16",
    "int32":   "TYPE_INT32",
    "int64":   "TYPE_INT64",
    "uint8":   "TYPE_UINT8",
    "uint16":  "TYPE_UINT16",
    "uint32":  "TYPE_UINT32",
    "uint64":  "TYPE_UINT64",
    "float32": "TYPE_FLOAT32",
    "float64": "TYPE_FLOAT64",
    "void":    "TYPE_VOID",
}
