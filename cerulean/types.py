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
    I8       = 4
    I16      = 5
    I32      = 6
    I64      = 7
    U8       = 8
    U16      = 9
    U32      = 10
    U64      = 11
    F32      = 12
    F64      = 13
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
}
