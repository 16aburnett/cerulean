# Cerulean Compiler
# By Amy Burnett
# April 10 2021
# ========================================================================

from sys import exit

from .tokenizer import printToken
from .AST import *

# ========================================================================

class Node:
    def __init__(self, name, token=None):
        self.name = name
        self.token = token
        self.children = []

class Parser:

    def __init__ (self, tokens, lines, doDebug=False):
        self.tokens = tokens
        self.currentToken = 0
        self.doDebug = doDebug
        self.level = 0
        self.lines = lines

    # <start> -> { <codeunit> }
    def parse (self):

        codeunits = [] 
        
        while self.currentToken < len (self.tokens) and self.tokens[self.currentToken].type != "END_OF_FILE":
            codeunits += [self.codeunit ()]
        
        return ProgramNode(codeunits)

    def match (self, function, expectedToken, additional=""):
        if (self.tokens[self.currentToken].type == expectedToken):
            self.currentToken += 1
        else:
            self.error(function, expectedToken, additional)

# ========================================================================
# debug 

    def error(self, function, expectedToken, additional=""):
        print (f"Parse Error: Attempted to parse <{function}>")
        print (f"   expected {expectedToken} but got {self.tokens[self.currentToken].type}")
        printToken (self.tokens[self.currentToken])
        if additional != "":
            print(f"   -> {additional}")
        exit(1)

    def enter (self, name):
        if (not self.doDebug): 
            return
        self.printSpaces(self.level)
        self.level += 1
        if self.currentToken < len(self.tokens):
            print (f"+-{name}: Enter, \tToken == {self.tokens[self.currentToken]}")
        else:
            print (f"+-{name}: Enter, \tToken == None")

    def leave (self, name):
        if (not self.doDebug): 
            return
        self.level -= 1
        self.printSpaces(self.level)
        if self.currentToken < len(self.tokens):
            print (f"+-{name}: Leave, \tToken == {self.tokens[self.currentToken]}")
        else:
            print (f"+-{name}: Leave, \tToken == None")
        
    def printSpaces (self, level):
        while (level > 0):
            level -= 1
            print("| ",end="")

# ========================================================================
# syntax productions 

    # <codeunit> -> <label> NEWLINE
    #            -> <data_directive> NEWLINE
    #            -> <instruction> NEWLINE
    #            -> NEWLINE
    def codeunit (self):
        self.enter ("codeunit")

        node = None

        # <codeunit> -> <label>
        if (self.tokens[self.currentToken].type == 'IDENTIFIER' and self.tokens[self.currentToken+1].type == 'COLON'):
            node = self.label ()
        # <codeunit> -> <data_directive>
        elif (self.tokens[self.currentToken].type == "DATA_DIRECTIVE"):
            node = self.dataDirective ()
        # <codeunit> -> <instruction>
        else:
            node = self.instruction ()
        
        self.match ("codeunit", "NEWLINE")
        self.leave ("codeunit")
        return node

    # ====================================================================
    # label 

    def label (self):
        self.enter ("label")

        token = self.tokens[self.currentToken]
        self.match ("label", "IDENTIFIER")
        node = LabelNode (token, token.lexeme)
        self.match ("label", "COLON")

        self.leave ("label")
        return node

    # ====================================================================
    # data directive 

    def dataDirective (self):
        # self.enter ("dataDirective")

        # token = self.tokens[self.currentToken]
        # self.match ("dataDirective", "IDENTIFIER")
        # node = LabelNode (token, token.lexeme, token.line, token.column)
        # self.match ("dataDirective", "COLON")

        # self.leave ("dataDirective")
        # return node
        print ("ERROR: DataDirectives not yet implemented")
        exit (1)
        return None

    # ====================================================================
    # <instruction> -> IDENTIFIER [<argument_list>]

    def instruction (self):
        self.enter ("instruction")

        token = self.tokens[self.currentToken]
        command = token.lexeme
        self.match ("instruction", "IDENTIFIER")

        # match arguments, if there are any
        if self.tokens[self.currentToken].type != "NEWLINE":
            arguments = self.argumentList ()
        else:
            arguments = []

        node = InstructionNode (token, command, arguments)

        self.leave ("instruction")
        return node

    # ====================================================================
    # argumentList
    # <argumentList> -> <argument> { COMMA <argument> }

    def argumentList (self):
        self.enter ("argumentList")

        arguments = [self.argument ()]
        while self.tokens[self.currentToken].type == "COMMA":
            self.match ("argumentList", "COMMA")
            arguments += [self.argument ()]

        self.leave ("argumentList")
        return arguments

    # ====================================================================
    # argument
    # <argument> -> INT
    #            -> FLOAT
    #            -> CHAR
    #            -> STRING
    #            -> NULL
    #            -> <register>
    #            -> IDENTIFIER

    def argument (self):
        self.enter ("argument")

        node = None

        if self.tokens[self.currentToken].type == "INT":
            value = self.tokens[self.currentToken].value
            node = IntLiteralExpressionNode (self.tokens[self.currentToken], value)
            self.match ("argument", "INT")
        elif self.tokens[self.currentToken].type == "FLOAT":
            value = self.tokens[self.currentToken].value
            node = FloatLiteralExpressionNode (self.tokens[self.currentToken], value)
            self.match ("argument", "FLOAT")
        elif self.tokens[self.currentToken].type == "CHAR":
            value = self.tokens[self.currentToken].value
            node = CharLiteralExpressionNode (self.tokens[self.currentToken], value)
            self.match ("argument", "CHAR")
        elif self.tokens[self.currentToken].type == "STRING":
            value = self.tokens[self.currentToken].value
            node = StringLiteralExpressionNode (self.tokens[self.currentToken], value)
            self.match ("argument", "STRING")
        elif self.tokens[self.currentToken].type == "NULL":
            node = NullExpressionNode (self.tokens[self.currentToken], self.tokens[self.currentToken].line, self.tokens[self.currentToken].column)
            self.match ("argument", "NULL")
        elif self.isRegister ():
            token = self.tokens[self.currentToken]
            node = RegisterExpressionNode (token, token.lexeme)
            self.match ("argument", "IDENTIFIER")
        elif self.tokens[self.currentToken].type == "IDENTIFIER":
            token = self.tokens[self.currentToken]
            node = LabelExpressionNode (token, token.lexeme)
            self.match ("argument", "IDENTIFIER")
        # expected argument but didnt get one 
        else:
            self.error ("argument", "IDENTIFIER")

        self.leave ("argument")

        return node

    # ====================================================================

    def isRegister (self):
        string = self.tokens[self.currentToken].lexeme.lower ()
        registers = ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", "r9", "r10", "r11", "r12", "ra", "bp", "sp"]
        return string in registers

# ========================================================================