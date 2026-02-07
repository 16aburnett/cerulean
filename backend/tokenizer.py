# Cerulean IR Compiler - Tokenizer
# By Amy Burnett
# ========================================================================

from typing import NamedTuple
from enum import Enum, auto 
from sys import exit
import re
import sys

# ========================================================================

class Token(NamedTuple):
    type: str
    lexeme: str
    value: str
    line: int
    column: int
    originalFilename: str
    originalLine: str
    includeChain: list
    lineStr: str

def printToken (token:Token, tabSpace="   "):
    print (f"{tabSpace}in file {token.originalFilename}")
    for includer in token.includeChain:
        print (f"{tabSpace}   included from {includer[0]}:{includer[1]}")
    print (f"{tabSpace}on line {token.originalLine}:{token.column}")
    print (f"{tabSpace}   {token.lineStr}")
    print (f"{tabSpace}   ",end="")
    for i in range(token.column-1):
        print (" ", end="")
    print ("^")
