# CeruleanASM: Tokenizer
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

def getTokenContextAsString (token:Token, tabSpace="   "):
    output = []
    output.append (f"{tabSpace}in file {token.originalFilename}\n")
    for includer in token.includeChain:
        output.append (f"{tabSpace}   included from {includer[0]}:{includer[1]}\n")
    output.append (f"{tabSpace}on line {token.originalLine}:{token.column}\n")
    output.append (f"{tabSpace}   {token.lineStr}\n")
    output.append (f"{tabSpace}   ")
    for i in range(token.column-1):
        output.append (" ")
    output.append ("^\n")
    return "".join (output)

# ========================================================================

token_specification = [
# Comments 
    ('COMMENT',  r'//.*\n?'),      # single line comment 
# literals 
    ('BINARY',   r'[-+]?0[bB][01]+'),                        # includes sign
    ('HEX',      r'[-+]?0[xX][0-9a-fA-F]+'),                 # includes sign
    ('FLOAT',    r'[-+]?[0-9]+[.][0-9]*([eE][-+]?[0-9]+)?'), # includes sign
    ('INT',      r'[-+]?[0-9]+'),                            # includes sign
    # ('FLOAT',    r'[0-9]+[.][0-9]*([eE][-+]?[0-9]+)?'),    # does not include sign
    # ('INT',      r'[0-9]+'),                               # does not include sign
    ('CHAR',     r'\'(\\[A-Za-z_0-9\'\"]*|.)\''),   # '0' '\n' '\101'
    ('STRING',   r'\"([^"\\]|\\.)*\"'),
# Identifier
    ('DATA_DIRECTIVE', r'\.[A-Za-z_][A-Za-z_0-9]*'), # .ascii, .string, .float
    ('MODIFIER'  ,r'%[A-Za-z_][A-Za-z_0-9]*'), # %hi, %lo
    ('IDENTIFIER',r'[A-Za-z_][A-Za-z_0-9]*'),  # Identifiers
# Operators
    ('ASSIGN_ADD',r'\+\='),
    ('ASSIGN_SUB',r'\-\='),
    ('ASSIGN_MUL',r'\*\='),
    ('ASSIGN_DIV',r'\/\='),
    ('ASSIGN_MOD',r'\%\='),
    ('LTEMP',    r'\<\:'),
    ('RTEMP',    r'\:\>'),
    ('INCR',     r'\+\+'),
    ('DECR',     r'\-\-'),
    ('PLUS',     r'\+'),
    ('MINUS',    r'\-'),
    ('TIMES',    r'\*'),
    ('DIVIDE',   r'\/'),
    ('MOD',      r'\%'),
    ('LTE',      r'\<\='),
    ('LT',       r'\<'),
    ('GTE',      r'\>\='),
    ('GT',       r'\>'),
    ('EQ',       r'\=\='),
    ('NE',       r'\!\='),
    ('ASSIGN',   r'\='),
    ('LOR',      r'\|\|'),
    ('LAND',     r'\&\&'),
    ('LNOT',     r'\!'),
    ('BNOT',     r'\~'),
    ('DOT',      r'\.'),
    ('COLON',    r'\:'),
# Punctuators 
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('LBRACE',   r'\{'),
    ('RBRACE',   r'\}'),
    ('COMMA',    r'\,'),
    ('SEMI',     r'\;'),
# Whitespace 
    ('NEWLINE',  r'\n'),           # Line endings
    ('SKIP',     r'[ \t\r]+'),       # Skip over spaces and tabs
# Everything else - non accepted 
    ('ERROR',    r'.'),          
]

# ========================================================================

def tokenize(code, mainFilename, debugLines):
    tokens = [] 
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    line_num = 1
    line_start = 0
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        lexeme = value
        # + 1 bc 1-based indexes for columns 
        column = mo.start() - line_start + 1
        if kind == 'INT':
            value = int(value)
        elif kind == 'FLOAT':
            value = float(value)
        elif kind == 'CHAR':
            value = value[1:-1]
        elif kind == 'COMMENT':
            line_start = mo.end()
            line_num += 1
            # continue
            # Just treat the comment as a newline
            # since the parser expects a newline to end an instruction
            kind = 'NEWLINE'
        elif kind == 'NEWLINE':
            line_start = mo.end()
            line_num += 1
            # continue
        elif kind == 'SKIP':
            continue
        elif kind == 'ERROR':
            pass
        # match keywords 
        elif kind == 'IDENTIFIER':
            if (lexeme == "true"):
                kind = "TRUE"
            elif (lexeme == "false"):
                kind = "FALSE"
            pass
        # get original line numbers and filename
        originalFile = mainFilename
        originalLine = line_num
        includeChain = []
        lineStr = debugLines[line_num - 1].rstrip()
        # Ad hoc adjust for newlines moving to a, well,, new line.
        if kind == "NEWLINE":
            originalLine = line_num - 1
            lineStr = debugLines[line_num - 2].rstrip()
        tokens += [Token(kind, lexeme, value, line_num, column, originalFile, originalLine, includeChain, lineStr)]
    # add end of file token
    tokens += [Token("END_OF_FILE", "EOF", 0, line_num, len(code) - line_start + 1, mainFilename, line_num, [], "")]
    return tokens 

# ========================================================================

