
# Encoding instructions with 3 register arguments (RRR)
# instruction: opcode a, b, c
# binary:      oooooooo aaaabbbb cccc0000 00000000
def encodeRRR (opcode, r0, r1, r2):
    byte0 = opcode
    byte1 = (r0 << 4) | r1
    byte2 = (r2 << 4) | 0x00
    byte3 = 0x00
    return [byte0, byte1, byte2, byte3]

# Encoding instructions with 2 registers and an immediate (RRI)
# instruction: opcode a, b, imm
# binary:      oooooooo aaaabbbb iiiiiiii iiiiiiii
# Immediate is little endian     LSB      MSB
def encodeRRI (opcode, r0, r1, imm):
    byte0 = opcode
    byte1 = (r0 << 4) | r1
    immLow = imm & 0xFF
    immHigh = (imm >> 8) & 0xFF
    return [byte0, byte1, immLow, immHigh]

# Encoding instructions with 2 registers (RR)
# instruction: opcode a, b
# binary:      oooooooo aaaabbbb 00000000 00000000
def encodeRR (opcode, r0, r1):
    byte0 = opcode
    byte1 = (r0 << 4) | r1
    byte2 = 0x00
    byte3 = 0x00
    return [byte0, byte1, byte2, byte3]

# Encoding instructions with 1 register and 1 immediate (RI)
# instruction: opcode a, imm
# binary:      oooooooo aaaa0000 iiiiiiii iiiiiiii
# Immediate is little endian     LSB      MSB
def encodeRI (opcode, r0, imm):
    byte0 = opcode
    byte1 = (r0 << 4)
    immLow = imm & 0xFF
    immHigh = (imm >> 8) & 0xFF
    return [byte0, byte1, immLow, immHigh]

# Encoding instructions with 1 register (R)
# instruction: opcode a
# binary:      oooooooo aaaa0000 00000000 00000000
def encodeR (opcode, r0):
    byte0 = opcode
    byte1 = (r0 << 4)
    byte2 = 0x00
    byte3 = 0x00
    return [byte0, byte1, byte2, byte3]

# Encoding instructions with 1 immediate (I)
# instruction: opcode imm
# binary:      oooooooo 00000000 iiiiiiii iiiiiiii
# Immediate is little endian     LSB      MSB
def encodeI (opcode, imm):
    byte0 = opcode
    byte1 = 0x00
    immLow = imm & 0xFF
    immHigh = (imm >> 8) & 0xFF
    return [byte0, byte1, immLow, immHigh]

# Encoding instructions with no arguments
# instruction: opcode
# binary:      oooooooo 00000000 00000000 00000000
def encodeNONE (opcode):
    return [opcode, 0x00, 0x00, 0x00]

FORMAT_ENCODERS = {
    'RRR' : encodeRRR,
    'RRI' : encodeRRI,
    'RR'  : encodeRR,
    'RI'  : encodeRI,
    'R'   : encodeR,
    'I'   : encodeI,
    'NONE': encodeNONE
}
