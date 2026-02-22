# CeruleanRISC Backend - Type System
# By Amy Burnett
# Feb 21, 2026
# =================================================================================================
# Defines type-to-directive mappings for the CeruleanRISC backend.
# Maps CeruleanIR types directly to CeruleanRISC assembly data directives.
# =================================================================================================

from ...irTypes import Type as IRType

# =================================================================================================
# Type to Directive Mappings
# =================================================================================================

# Maps CeruleanIR Type enum directly to CeruleanRISC assembly data directives
IR_TYPE_TO_DATA_DIRECTIVE = {
    IRType.INT8:     ".i8",
    IRType.INT16:    ".i16",
    IRType.INT32:    ".i32",
    IRType.INT64:    ".i64",
    IRType.UINT8:    ".u8",
    IRType.UINT16:   ".u16",
    IRType.UINT32:   ".u32",
    IRType.UINT64:   ".u64",
    IRType.CHAR:     ".u8",        # char is unsigned 8-bit
    IRType.BYTE:     ".i8",        # byte is signed 8-bit
    IRType.BOOL:     ".u8",        # bool is 1 byte
    IRType.FLOAT32:  ".f32",
    IRType.FLOAT64:  ".f64",
    IRType.PTR:      ".addr",      # Pointer address
    IRType.VOID:     None,          # void has no directive
}

# Default directive for unknown types
DEFAULT_DATA_DIRECTIVE = ".i64"

# =================================================================================================
# Helper Functions
# =================================================================================================

def getDataDirective(irType):
    """
    Get the CeruleanRISC data directive for a given CeruleanIR type.
    
    Args:
        irType: IRType enum from backend.irTypes
        
    Returns:
        CeruleanRISC data directive string (e.g., ".i32", ".u8", ".addr")
    """
    return IR_TYPE_TO_DATA_DIRECTIVE.get(irType, DEFAULT_DATA_DIRECTIVE)
