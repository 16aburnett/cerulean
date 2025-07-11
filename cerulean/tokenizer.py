# Cerulean Compiler
# By Amy Burnett
# April 10 2021
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

# ========================================================================

token_specification = [
# Comments 
    ('COMMENT',  r'//.*\n?'),      # single line comment 
# literals 
    # ('FLOAT',    r'[-+]?[0-9]+[.][0-9]*([eE][-+]?[0-9]+)?'), 
    # ('INT',      r'[-+]?[0-9]+'), 
    ('FLOAT',    r'[0-9]+[.][0-9]*([eE][-+]?[0-9]+)?'), 
    ('INT',      r'[0-9]+'), 
    ('CHAR',     r'\'(\\[A-Za-z_0-9\'\"]*|.)\''),   # '0' '\n' '\101'
    # ('STRING',   r'"[^"\\]*(\\.[^"\\]*)*"'),   
    ('STRING',   r'\"([^"\\]|\\.)*\"'),   
# Keywords - handled after identifiers are matched
    # ('IF',       r'if'),  
    # ('ELIF',     r'elif'),  
    # ('ELSE',     r'else'),   
    # ('FOR',      r'for'),  
    # ('WHILE',    r'while'),  
    # ('RETURN',   r'return'),  
    # ('BREAK',    r'break'),  
    # ('CONTINUE', r'continue'),  
    # ('FUNCTION', r'function'),  
    # ('CLASS',    r'class'),  
    # ('INHERITS', r'inherits'),  
    # ('PUBLIC',   r'public'),  
    # ('PRIVATE',  r'private'),  
    # ('FIELD',    r'field'),  
    # ('METHOD',   r'method'),  
    # ('CONSTRUCTOR',r'constructor'),  
    # ('NEW',      r'new'),  
    # ('FREE',      r'free'),  
    # ('THIS',     r'this'),  
    # ('SIZEOF',   r'sizeof'),  
    # ('NULL',     r'null'),  
# Built-in types - handled after identifiers are matched
    # ('INTTYPE',   r'int'),  
    # ('FLOATTYPE', r'float'),  
    # ('BOOLTYPE',  r'bool'),  
    # ('CHARTYPE',  r'char'),  
    # ('VOIDTYPE',  r'void'),  
# Identifier
    ('IDENTIFIER',r'[A-Za-z_][A-Za-z_0-9]*'),    # Identifiers
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

def tokenize(code, mainFilename, debugLines=[]):
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
            continue 
        elif kind == 'NEWLINE':
            line_start = mo.end()
            line_num += 1
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'ERROR':
            pass
        # match keywords 
        elif kind == 'IDENTIFIER':
            if (lexeme == "if"):
                kind = "IF"
            elif (lexeme == "elif"):
                kind = "ELIF"
            elif (lexeme == "else"):
                kind = "ELSE"
            elif (lexeme == "for"):
                kind = "FOR"
            elif (lexeme == "while"):
                kind = "WHILE"
            elif (lexeme == "return"):
                kind = "RETURN"
            elif (lexeme == "break"):
                kind = "BREAK"
            elif (lexeme == "continue"):
                kind = "CONTINUE"
            elif (lexeme == "function"):
                kind = "FUNCTION"
            elif (lexeme == "struct"):
                kind = "STRUCT"
            elif (lexeme == "heapalloc"):
                kind = "HEAPALLOC"
            elif (lexeme == "free"):
                kind = "FREE"
            elif (lexeme == "sizeof"):
                kind = "SIZEOF"
            elif (lexeme == "null"):
                kind = "NULL"
            # Types
            elif (lexeme == "bool"):
                kind = "TYPE_BOOL"
            elif (lexeme == "byte"):
                kind = "TYPE_BYTE"
            elif (lexeme == "char"):
                kind = "TYPE_CHAR"
            elif (lexeme == "int32"):
                kind = "TYPE_INT32"
            elif (lexeme == "int64"):
                kind = "TYPE_INT64"
            elif (lexeme == "float32"):
                kind = "TYPE_FLOAT32"
            elif (lexeme == "float64"):
                kind = "TYPE_FLOAT64"
            elif (lexeme == "void"):
                kind = "TYPE_VOID"
        # get original line numbers and filename
        originalFile = mainFilename
        originalLine = line_num
        includeChain = []
        lineStr = ""
        if len(debugLines) != 0:
            originalFile = debugLines[line_num-1][0]
            originalLine = debugLines[line_num-1][1]
            lineStr      = debugLines[line_num-1][2].rstrip()
            includeChain = debugLines[line_num-1][3]
        tokens += [Token(kind, lexeme, value, line_num, column, originalFile, originalLine, includeChain, lineStr)]
    # add end of file token
    tokens += [Token("END_OF_FILE", "EOF", 0, line_num, len(code) - line_start + 1, mainFilename, line_num, [], "")]
    return tokens 

# ========================================================================

