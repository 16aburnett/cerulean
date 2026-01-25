# CeruleanIR Compiler - Type Utilities
# By Amy Burnett
# =================================================================================================
# Type size definitions for CeruleanIR.
# 
# Most CeruleanIR types have fixed sizes encoded in their names (e.g., int32 = 4 bytes).
# Architecture-specific types like 'ptr' should be overridden by backends if needed.
# =================================================================================================

# =================================================================================================
# Type Size Mappings
# =================================================================================================

# Maps CeruleanIR type names to their size in bytes
# These sizes are part of the CeruleanIR specification and should not change.
TYPE_SIZES = {
    "char": 1,      # 8-bit character
    "int8": 1,      # 8-bit signed integer
    "int16": 2,     # 16-bit signed integer
    "int32": 4,     # 32-bit signed integer
    "int64": 8,     # 64-bit signed integer
    "float32": 4,   # 32-bit floating point
    "float64": 8,   # 64-bit floating point
    "ptr": 8,       # Pointer (default 64-bit, can be overridden by backend)
    "void": 0,      # void has no size
}

# Default type size for unknown types
DEFAULT_TYPE_SIZE = 8

# =================================================================================================
# Type Size Functions
# =================================================================================================

def getTypeSize(typeName):
    """
    Get the size in bytes for a given CeruleanIR type name.
    
    Args:
        typeName: String name of the type (e.g., "int32", "char", "ptr")
        
    Returns:
        Size in bytes as an integer
    """
    return TYPE_SIZES.get(typeName, DEFAULT_TYPE_SIZE)

def getTypeSizeWithFallback(typeName, defaultSize=None):
    """
    Get the size in bytes for a given type name with custom fallback.
    
    Args:
        typeName: String name of the type
        defaultSize: Size to return if type not found (uses DEFAULT_TYPE_SIZE if None)
        
    Returns:
        Size in bytes as an integer
    """
    if defaultSize is None:
        defaultSize = DEFAULT_TYPE_SIZE
    return TYPE_SIZES.get(typeName, defaultSize)

def setPointerSize(sizeInBytes):
    """
    Override the pointer size for architecture-specific backends.
    
    Args:
        sizeInBytes: Size of pointers in bytes (typically 4 or 8)
    """
    TYPE_SIZES["ptr"] = sizeInBytes

# =================================================================================================
