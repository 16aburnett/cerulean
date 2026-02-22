# CeruleanIR Compiler - Type Utilities
# By Amy Burnett
# Feb 21, 2026
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
    "uint8": 1,     # 8-bit unsigned integer
    "uint16": 2,    # 16-bit unsigned integer
    "uint32": 4,    # 32-bit unsigned integer
    "uint64": 8,    # 64-bit unsigned integer
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

def getTypeSize(typeEnum):
    """
    Get the size in bytes for a given CeruleanIR type.
    
    Args:
        typeEnum: IRType enum value (from backend.irTypes)
        
    Returns:
        Size in bytes as an integer
    """
    # Convert enum to lowercase string for dictionary lookup
    typeName = typeEnum.name.lower()
    return TYPE_SIZES.get(typeName, DEFAULT_TYPE_SIZE)

def getTypeSizeWithFallback(typeEnum, defaultSize=None):
    """
    Get the size in bytes for a given type with custom fallback.
    
    Args:
        typeEnum: IRType enum value (from backend.irTypes)
        defaultSize: Size to return if type not found (uses DEFAULT_TYPE_SIZE if None)
        
    Returns:
        Size in bytes as an integer
    """
    # Convert enum to lowercase string for dictionary lookup
    typeName = typeEnum.name.lower()
    
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

def isUnsignedType(typeEnum):
    """
    Check if a type represents an unsigned integer type.
    
    Args:
        typeEnum: IRType enum value (from backend.irTypes)
        
    Returns:
        True if the type is unsigned (char, uint8, uint16, uint32, uint64), False otherwise
    """
    # Convert enum to lowercase string for comparison
    typeName = typeEnum.name.lower()
    
    # char is treated as unsigned (u8 equivalent) to avoid sign-extending characters
    return typeName in ["char", "uint8", "uint16", "uint32", "uint64"]

def isSignedIntegerType(typeEnum):
    """
    Check if a type represents a signed integer type.
    
    Args:
        typeEnum: IRType enum value (from backend.irTypes)
        
    Returns:
        True if the type is a signed integer (int8, int16, int32, int64, byte, char), False otherwise
    """
    # Convert enum to lowercase string for comparison
    typeName = typeEnum.name.lower()
    
    return typeName in ["int8", "int16", "int32", "int64", "byte", "char"]

# =================================================================================================
