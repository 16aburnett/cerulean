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
    IRType.INT8:     ".int8",
    IRType.INT16:    ".int16",
    IRType.INT32:    ".int32",
    IRType.INT64:    ".int64",
    IRType.UINT8:    ".uint8",
    IRType.UINT16:   ".uint16",
    IRType.UINT32:   ".uint32",
    IRType.UINT64:   ".uint64",
    IRType.CHAR:     ".uint8",     # char is unsigned 8-bit
    IRType.BYTE:     ".int8",      # byte is signed 8-bit
    IRType.BOOL:     ".uint8",     # bool is 1 byte
    IRType.FLOAT32:  ".float32",
    IRType.FLOAT64:  ".float64",
    IRType.PTR:      ".addr",      # Pointer address
    IRType.VOID:     None,         # void has no directive
}

# Default directive for unknown types
DEFAULT_DATA_DIRECTIVE = ".int64"

# =================================================================================================
# Helper Functions
# =================================================================================================

def getDataDirective(irType):
    """
    Get the CeruleanRISC data directive for a given CeruleanIR type.
    
    Args:
        irType: IRType enum from backend.irTypes
        
    Returns:
        CeruleanRISC data directive string (e.g., ".int32", ".uint8", ".addr")
    """
    return IR_TYPE_TO_DATA_DIRECTIVE.get(irType, DEFAULT_DATA_DIRECTIVE)
