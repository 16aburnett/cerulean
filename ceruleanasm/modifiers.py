# Modifiers that can be placed on labels
MODIFIERS = {
    # (high), bits 48-63, the highest 16-bit chunk of a 64-bit number/address
    "hi",
    # (middle-high), bits 32-47, the 2nd highest 16-bit chunk of a 64-bit number/address
    "mh",
    # (middle-low), bits 16-31, the 2nd lowest 16-bit chunk of a 64-bit number/address
    "ml",
    # (low), bits 0-15, the lowest 16-bit chunk of a 64-bit number/address
    "lo",
}
