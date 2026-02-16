import codecs
import struct

DATA_DIRECTIVES = {
    # 8-bit signed integer
    "int8"    : {"size": 1   , "format": '<b', "alignment": 1},
    # 8-bit unsigned integer
    "uint8"   : {"size": 1   , "format": '<B', "alignment": 1},
    # 16-bit signed integer
    "int16"   : {"size": 2   , "format": '<h', "alignment": 2},
    # 16-bit unsigned integer
    "uint16"  : {"size": 2   , "format": '<H', "alignment": 2},
    # 32-bit signed integer
    "int32"   : {"size": 4   , "format": '<i', "alignment": 4},
    # 32-bit unsigned integer
    "uint32"  : {"size": 4   , "format": '<I', "alignment": 4},
    # 64-bit signed integer
    "int64"   : {"size": 8   , "format": '<q', "alignment": 8},
    # 64-bit unsigned integer
    "uint64"  : {"size": 8   , "format": '<Q', "alignment": 8},
    # 32-bit IEEE-754 float
    "float32" : {"size": 4   , "format": '<f', "alignment": 4},
    # 64-bit IEEE-754 double
    "float64" : {"size": 8   , "format": '<d', "alignment": 8},
    # 64-bit address (can take a label as an argument)
    "addr"    : {"size": 8   , "format": '<Q', "alignment": 8},
    # Raw ASCII bytes (not null-terminated), size is variable
    "ascii"   : {"size": None, "format": None, "alignment": 1},
    # ASCII string with a null-terminating byte, size is variable
    "string"  : {"size": None, "format": None, "alignment": 1},
}

def getDirectiveSize (directive, value):
    # Fixed-width types
    if directive in {'int8', 'uint8'}:
        return 1
    elif directive in {'int16', 'uint16'}:
        return 2
    elif directive in {'int32', 'uint32', 'float32'}:
        return 4
    elif directive in {'int64', 'uint64', 'float64', 'addr'}:
        return 8
    # Variable-length string types
    elif directive == 'ascii':
        return len (decodeEscapeSequences (value))
    elif directive == 'string':
        return len (decodeEscapeSequences (value)) + 1  # Null terminator
    else:
        print (f"Unknown data directive type '{directive}'")
        print (f"this is a compiler error, this should have been caught during semantic analysis")
        exit (1)

def decodeEscapeSequences (rawStr):
    stripped = rawStr.strip ('"')
    return codecs.decode (stripped, 'unicode_escape')

def encodeDataDirective (directive, value):
    if directive in {'ascii', 'string'}:
        # value should be a bytearray
        if directive == 'string':
            value.append (0)  # add null terminator
        return value
    if directive in DATA_DIRECTIVES:
        format = DATA_DIRECTIVES[directive]["format"]
        # Struct will return the raw bytes of the value
        # Format string specifies type and Endianness
        return struct.pack (format, value)
    # Unknown data directive
    print (f"ERROR: Unknown directive '{directive}' in encodeDataDirective")
    print (f"If this is reached, then the semantic analysis pass failed to catch this case")
    exit (1)
