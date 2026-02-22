# Cerulean IR Compiler - Type Enum
# By Amy Burnett
# Feb 21, 2026
# ========================================================================

from enum import Enum

# ========================================================================

class Type(Enum):
    BOOL     = 0
    BYTE     = 1
    CHAR     = 2
    I8       = 3
    I16      = 4
    I32      = 5
    I64      = 6
    U8       = 7
    U16      = 8
    U32      = 9
    U64      = 10
    F32      = 11
    F64      = 12
    VOID     = 13
    BLOCK    = 14
    TYPE     = 15
    PTR      = 16
    UNKNOWN  = 17
    USERTYPE = 18 # SHOULD NOT BE USED - YET

# ========================================================================
# Type Token Mappings
# ========================================================================
# Maps token types to (Type enum, type string) tuples
# Used by parser to convert tokens to TypeSpecifierNodes

TYPE_TOKEN_MAP = {
    'TYPE_BOOL':  (Type.BOOL,  "bool"),
    'TYPE_BYTE':  (Type.BYTE,  "byte"),
    'TYPE_CHAR':  (Type.CHAR,  "char"),
    'TYPE_I8':    (Type.I8,    "i8"),
    'TYPE_I16':   (Type.I16,   "i16"),
    'TYPE_I32':   (Type.I32,   "i32"),
    'TYPE_I64':   (Type.I64,   "i64"),
    'TYPE_U8':    (Type.U8,    "u8"),
    'TYPE_U16':   (Type.U16,   "u16"),
    'TYPE_U32':   (Type.U32,   "u32"),
    'TYPE_U64':   (Type.U64,   "u64"),
    'TYPE_F32':   (Type.F32,   "f32"),
    'TYPE_F64':   (Type.F64,   "f64"),
    'TYPE_VOID':  (Type.VOID,  "void"),
    'TYPE_BLOCK': (Type.BLOCK, "block"),
    'TYPE_TYPE':  (Type.TYPE,  "type"),
    'TYPE_PTR':   (Type.PTR,   "ptr"),
}

# Maps type keywords to token types (for tokenizer)
TYPE_KEYWORDS = {
    "bool":  "TYPE_BOOL",
    "byte":  "TYPE_BYTE",
    "char":  "TYPE_CHAR",
    "i8":    "TYPE_I8",
    "i16":   "TYPE_I16",
    "i32":   "TYPE_I32",
    "i64":   "TYPE_I64",
    "u8":    "TYPE_U8",
    "u16":   "TYPE_U16",
    "u32":   "TYPE_U32",
    "u64":   "TYPE_U64",
    "f32":   "TYPE_F32",
    "f64":   "TYPE_F64",
    "void":  "TYPE_VOID",
    "block": "TYPE_BLOCK",
    "type":  "TYPE_TYPE",
    "ptr":   "TYPE_PTR",
}
