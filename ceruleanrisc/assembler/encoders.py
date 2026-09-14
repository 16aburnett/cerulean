
def wordToBytes (word):
    return [
        (word >> 24) & 0xFF,
        (word >> 16) & 0xFF,
        (word >> 8) & 0xFF,
        word & 0xFF
    ]

# Encoding instructions with 3 register arguments (RRR)
# instruction: opcode a, b, c
# binary:      oooooooo aaaaabbb bbccccc0 00000000
def encodeRRR (opcode, r0, r1, r2):
    word = ((opcode & 0xFF) << 24) | ((r0 & 0x1F) << 19) | ((r1 & 0x1F) << 14) | ((r2 & 0x1F) << 9)
    return wordToBytes (word)

# Encoding instructions with 2 registers and an immediate (RRI)
# instruction: opcode a, b, imm
# binary:      oooooooo aaaaabbb bbiiiiii iiiiiiii
def encodeRRI (opcode, r0, r1, imm):
    word = ((opcode & 0xFF) << 24) | ((r0 & 0x1F) << 19) | ((r1 & 0x1F) << 14) | (imm & 0x3FFF)
    return wordToBytes (word)

# Encoding instructions with 2 registers (RR)
# instruction: opcode a, b
# binary:      oooooooo aaaaabbb bb000000 00000000
def encodeRR (opcode, r0, r1):
    word = ((opcode & 0xFF) << 24) | ((r0 & 0x1F) << 19) | ((r1 & 0x1F) << 14)
    return wordToBytes (word)

# Encoding instructions with 1 register and 1 immediate (RI)
# instruction: opcode a, imm
# binary:      oooooooo aaaaa000 iiiiiiii iiiiiiii
def encodeRI (opcode, r0, imm):
    byte0 = opcode & 0xFF
    byte1 = ((r0 & 0x1F) << 3) & 0xFF
    immHigh = (imm >> 8) & 0xFF
    immLow = imm & 0xFF
    return [byte0, byte1, immHigh, immLow]

# Encoding instructions with 1 register (R)
# instruction: opcode a
# binary:      oooooooo aaaaa000 00000000 00000000
def encodeR (opcode, r0):
    word = ((opcode & 0xFF) << 24) | ((r0 & 0x1F) << 19)
    return wordToBytes (word)

# Encoding instructions with 1 immediate (I)
# instruction: opcode imm
# binary:      oooooooo 00000000 iiiiiiii iiiiiiii
def encodeI (opcode, imm):
    byte0 = opcode & 0xFF
    byte1 = 0x00
    immLow = imm & 0xFF
    immHigh = (imm >> 8) & 0xFF
    return [byte0, byte1, immHigh, immLow]

# Encoding instructions with no arguments
# instruction: opcode
# binary:      oooooooo 00000000 00000000 00000000
def encodeNONE (opcode):
    word = (opcode & 0xFF) << 24
    return wordToBytes (word)

FORMAT_ENCODERS = {
    'RRR' : encodeRRR,
    'RRI' : encodeRRI,
    'RR'  : encodeRR,
    'RI'  : encodeRI,
    'R'   : encodeR,
    'I'   : encodeI,
    'NONE': encodeNONE
}
