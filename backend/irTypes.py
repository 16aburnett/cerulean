# Cerulean IR Compiler - Type Enum
# By Amy Burnett
# ========================================================================

from enum import Enum

# ========================================================================

class Type(Enum):
    BOOL     = 0
    BYTE     = 1
    CHAR     = 2
    INT32    = 3
    INT64    = 4
    FLOAT32  = 5
    FLOAT64  = 6
    VOID     = 7
    BLOCK    = 8
    TYPE     = 9
    PTR      = 10
    UNKNOWN  = 11
    USERTYPE = 12 # SHOULD NOT BE USED - YET

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
    'TYPE_BLOCK':   (Type.BLOCK,   "block"),
    'TYPE_TYPE':    (Type.TYPE,    "type"),
    'TYPE_PTR':     (Type.PTR,     "ptr"),
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
    "block":   "TYPE_BLOCK",
    "type":    "TYPE_TYPE",
    "ptr":     "TYPE_PTR",
}
