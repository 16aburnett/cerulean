# Amy Script Compiler
# By Amy Burnett
# April 10 2021
# ========================================================================

from sys import exit

from .tokenizer import printToken
from .ceruleanIRAST import *

# ========================================================================

class Node:
    def __init__ (self, name, token=None):
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

    def error (self, function, expectedToken, additional=""):
        print (f"Parse Error: Attempted to parse <{function}>")
        print (f"   expected {expectedToken} but got {self.tokens[self.currentToken].type}")
        printToken (self.tokens[self.currentToken])
        if additional != "":
            print(f"   -> {additional}")
        exit (1)

    def enter (self, name):
        if (not self.doDebug): 
            return
        self.printSpaces(self.level)
        self.level += 1
        if self.currentToken < len (self.tokens):
            print (f"+-{name}: Enter, \tToken == {self.tokens[self.currentToken]}")
        else:
            print (f"+-{name}: Enter, \tToken == None")

    def leave (self, name):
        if (not self.doDebug): 
            return
        self.level -= 1
        self.printSpaces (self.level)
        if self.currentToken < len (self.tokens):
            print (f"+-{name}: Leave, \tToken == {self.tokens[self.currentToken]}")
        else:
            print (f"+-{name}: Leave, \tToken == None")
        
    def printSpaces (self, level):
        while (level > 0):
            level -= 1
            print ("| ", end="")

# ========================================================================
# syntax productions 

    # Generic syntax start state 
    # <codeunit> -> <function>
    #            -> <global>
    #            -> NEWLINE
    def codeunit (self):
        self.enter ("codeunit")

        node = None

        # <codeunit> -> <function>
        if (self.tokens[self.currentToken].type == 'FUNCTION'):
            node = self.function ()
        # <codeunit> -> <class>
        elif (self.tokens[self.currentToken].type == "GLOBAL"):
            node = self.globalVarDeclaration ()
        # <codeunit> -> NEWLINE
        # AD HOC!!
        elif (self.tokens[self.currentToken].type == "NEWLINE"):
            # consume and ignore newline
            self.match ("codeunit", "NEWLINE")
            pass
        # something unexpected
        else:
            self.error ("codeunit", "FUNCTION",
                "Program level scope expects either a function or global")
        
        self.leave ("codeunit")

        return node

    # ====================================================================
    # function declaration
    # <function> -> FUNCTION <typeSpecifier> GVARIABLE <paramlist> <codeblock>
    
    def function (self):
        self.enter ("function")
        expected_syntax = "Function Definition Syntax:\nfunction <return_type> @<function_name> (<parameter_list>) { <code_body> }"

        self.match ("function", "FUNCTION", expected_syntax)
        
        # match function's return type
        return_type = self.typeSpecifier ()

        # match function's name
        function_name = self.tokens[self.currentToken].lexeme
        token = self.tokens[self.currentToken]
        self.match ("function", "GVARIABLE", expected_syntax)
        
        # match function's parameters
        params = self.paramlist ()

        # AD HOC!! newlines before codeblock
        while self.tokens[self.currentToken].type == "NEWLINE":
            self.match ("function", "NEWLINE")

        # match function's code body
        body = self.codeblock ()

        self.leave ("function")

        return FunctionNode (return_type, function_name, token, params, body)

    # ====================================================================
    # parameter list for a function declaration
    # <paramlist> -> '(' [ <typeSpecifier>(LVARIABLE) { COMMA <typeSpecifier>(LVARIABLE) } ] ')'

    def paramlist (self): 
        self.enter ("paramlist")

        params = []

        self.match ("paramlist", "LPAREN")

        # process parameters - if there are any
        if self.tokens[self.currentToken].type != "RPAREN":

            type = self.typeSpecifier ()

            self.match ("paramlist", "LPAREN")

            id = self.tokens[self.currentToken].lexeme
            token = self.tokens[self.currentToken]
            self.match ("paramlist", "LVARIABLE")
            params += [ParameterNode (type, id, token)]
            
            self.match ("paramlist", "RPAREN")

            # match parameters while there is still more to match
            while self.tokens[self.currentToken].type == "COMMA":
                self.match ("paramlist", "COMMA")

                type = self.typeSpecifier ()

                self.match ("paramlist", "LPAREN")

                id = self.tokens[self.currentToken].lexeme
                token = self.tokens[self.currentToken]
                self.match ("paramlist", "LVARIABLE")
                params += [ParameterNode (type, id, token)]
                
                self.match ("paramlist", "RPAREN")

        self.match ("paramlist", "RPAREN")

        self.leave ("paramlist")

        return params

    # ====================================================================
    # codeblock 
    # <codeblock> -> '{' { <instruction> } '}'
    #             -> '{' { <label> } '}'

    def codeblock (self):
        self.enter ("codeblock")

        codeunits = []

        self.match ("codeblock", "LBRACE")
        
        while self.tokens[self.currentToken].type != "RBRACE":
            # AD HOC!! ignore newlines
            if self.tokens[self.currentToken].type == "NEWLINE":
                self.match ("codeblock", "NEWLINE")
                continue
            # labels
            if self.tokens[self.currentToken].type == "TYPE_LABEL":
                codeunits += [self.label ()]
            # instructions
            else:
                codeunits += [self.instruction ()]
        
        self.match ("codeblock", "RBRACE")

        self.leave ("codeblock")

        return CodeBlockNode (codeunits)

    # ====================================================================

    def isType (self):
        # <typeSpecifier> -> TYPE_{}
        return self.tokens[self.currentToken].type == 'TYPE_BYTE'   \
            or self.tokens[self.currentToken].type == 'TYPE_INT32'  \
            or self.tokens[self.currentToken].type == 'TYPE_INT64'  \
            or self.tokens[self.currentToken].type == 'TYPE_FLOAT32'\
            or self.tokens[self.currentToken].type == 'TYPE_FLOAT64'\
            or self.tokens[self.currentToken].type == 'TYPE_VOID'   \
            or self.tokens[self.currentToken].type == 'TYPE_LABEL'

    # <typeSpecifier> -> TYPE_BYTE { '*' }
    #                  | TYPE_INT32 { '*' }
    #                  | TYPE_INT64 { '*' }
    #                  | TYPE_FLOAT32 { '*' }
    #                  | TYPE_FLOAT64 { '*' }
    #                  | TYPE_VOID { '*' }
    #                  | TYPE_LABEL { '*' }
    def typeSpecifier (self):
        self.enter ("typeSpecifier")

        # unknown by default 
        type = None
        temp = self.currentToken

        # <typeSpecifier> -> TYPE_BYTE
        if (self.tokens[self.currentToken].type == 'TYPE_BYTE'):
            self.match ("typeSpecifier", 'TYPE_BYTE')
            type = TypeSpecifierNode (Type.BYTE, "byte", self.tokens[self.currentToken])
        # <typeSpecifier> -> TYPE_CHAR
        elif (self.tokens[self.currentToken].type == 'TYPE_CHAR'):
            self.match ("typeSpecifier", 'TYPE_CHAR')
            type = TypeSpecifierNode (Type.CHAR, "char", self.tokens[self.currentToken])
        # <typeSpecifier> -> TYPE_INT32
        elif (self.tokens[self.currentToken].type == 'TYPE_INT32'):
            self.match ("typeSpecifier", 'TYPE_INT32')
            type = TypeSpecifierNode (Type.INT32, "int32", self.tokens[self.currentToken])
        # <typeSpecifier> -> TYPE_INT64
        elif (self.tokens[self.currentToken].type == 'TYPE_INT64'):
            self.match ("typeSpecifier", 'TYPE_INT64')
            type = TypeSpecifierNode (Type.INT64, "int64", self.tokens[self.currentToken])
        # <typeSpecifier> -> TYPE_FLOAT32
        elif (self.tokens[self.currentToken].type == 'TYPE_FLOAT32'):
            self.match ("typeSpecifier", 'TYPE_FLOAT32')
            type = TypeSpecifierNode (Type.FLOAT32, "float32", self.tokens[self.currentToken])
        # <typeSpecifier> -> TYPE_FLOAT64
        elif (self.tokens[self.currentToken].type == 'TYPE_FLOAT64'):
            self.match ("typeSpecifier", 'TYPE_FLOAT64')
            type = TypeSpecifierNode (Type.FLOAT64, "float64", self.tokens[self.currentToken])
        # <typeSpecifier> -> TYPE_VOID
        elif (self.tokens[self.currentToken].type == 'TYPE_VOID'):
            self.match ("typeSpecifier", 'TYPE_VOID')
            type = TypeSpecifierNode (Type.VOID, "void", self.tokens[self.currentToken])
        # <typeSpecifier> -> TYPE_LABEL
        elif (self.tokens[self.currentToken].type == 'TYPE_LABEL'):
            self.match ("typeSpecifier", 'TYPE_LABEL')
            type = TypeSpecifierNode (Type.LABEL, "label", self.tokens[self.currentToken])
        else:
            # we expected some sort of type here
            self.match ("typeSpecifier", "TYPE_INT", "Expected a type")
        # <typeSpecifier> -> IDENTIFIER
        # elif (self.tokens[self.currentToken].type == 'IDENTIFIER'):
        #     type = TypeSpecifierNode (Type.USERTYPE, self.tokens[self.currentToken].lexeme, self.tokens[self.currentToken])
        #     self.match ("typeSpecifier", 'IDENTIFIER')

        #     # match template params 
        #     # LTEMP <typeSpec> { COMMA <typeSpec> } RTEMP
        #     # <: T, K :>
        #     templateParams = []
        #     if self.tokens[self.currentToken].type == "LTEMP":
        #         self.match ("factor", "LTEMP")
        #         templateParams += [self.typeSpecifier()]
        #         while self.tokens[self.currentToken].type == "COMMA":
        #             self.match ("factor", "COMMA")
        #             templateParams += [self.typeSpecifier()]
        #         self.match ("factor", "RTEMP")
        #     type.templateParams = templateParams
        
        # match array 
        # if type != None:
        #     while (self.tokens[self.currentToken].type == "LBRACKET"):
        #         self.match ("typeSpecifier", "LBRACKET")
        #         # possibly not a type spec
        #         if (self.tokens[self.currentToken].type != "RBRACKET"):
        #             self.currentToken = temp
        #             self.leave ("typeSpecifier")
        #             return None
        #         self.match ("typeSpecifier", "RBRACKET")
        #         type.arrayDimensions += 1

        # match pointers
        while self.tokens[self.currentToken].type == "TIMES":
            # increment number of dimensions
            type.arrayDimensions += 1
            # consume star
            self.match ("typeSpecifier", "TIMES")
        
        self.leave ("typeSpecifier")

        return type

    # ====================================================================
    # label 
    # <label> -> TYPE_LABEL IDENTIFIER NEWLINE

    def label (self):
        self.enter ("label")

        self.match ("label", "TYPE_LABEL")
        token = self.tokens[self.currentToken]
        labelStr = token.lexeme
        self.match ("label", "IDENTIFIER")
        self.match ("label", "NEWLINE")

        self.leave ("label")

        return LabelNode (labelStr, token)

    # ====================================================================
    # instruction 
    # <instruction> -> [ LVARIABLE '=' ] <command> <argument_list> NEWLINE
    # <instruction> -> [ LVARIABLE '=' ] CALL GVARIABLE <argument_list> NEWLINE

    def instruction (self):
        self.enter ("instruction")

        # initially assume no assignment
        lhsVariable = None
        # try to match assignment
        if self.tokens[self.currentToken].type == "LVARIABLE" and \
            self.tokens[self.currentToken+1].type == "ASSIGN":
            lhsVariable = VariableDeclarationNode (self.tokens[self.currentToken].lexeme, self.tokens[self.currentToken])
            # mark decl as being assigned
            lhsVariable.wasAssigned = True
            self.match ("instruction", "LVARIABLE")
            self.match ("instruction", "ASSIGN")

        node = None
        # match call instruction
        if self.tokens[self.currentToken].type == "CALL":
            self.match ("instruction", "CALL")

            function_name = self.tokens[self.currentToken].lexeme
            token = self.tokens[self.currentToken]
            self.match ("instruction", "GVARIABLE", "expected function name after 'call'")

            # match arguments
            arguments = self.argumentList ()

            node = CallInstructionNode (lhsVariable, function_name, token, arguments)

        # normal instruction
        else:
            command = self.tokens[self.currentToken]
            self.match ("instruction", "IDENTIFIER")

            # match arguments
            arguments = self.argumentList ()

            node = InstructionNode (lhsVariable, command, arguments)

        self.leave ("instruction")

        return node

    # ====================================================================
    # globalVarDeclaration 
    # <globalVarDeclaration> -> GLOBAL GVARIABLE ASSIGN <command> <argument_list> 

    def globalVarDeclaration (self):
        self.enter ("globalVarDeclaration")
        expected_syntax = "Global Variable Declaration Syntax:\nglobal @<gvarname> = value (<type>(<value>))"

        self.match ("globalVarDeclaration", "GLOBAL", expected_syntax)

        variableName = self.tokens[self.currentToken].lexeme
        token = self.tokens[self.currentToken]
        self.match ("globalVarDeclaration", "GVARIABLE", expected_syntax)

        self.match ("globalVarDeclaration", "ASSIGN", expected_syntax)

        # match command
        command = self.tokens[self.currentToken]
        self.match ("globalVarDeclaration", "IDENTIFIER", expected_syntax)

        # match arguments
        arguments = self.argumentList ()

        self.leave ("globalVarDeclaration")

        return GlobalVariableDeclarationNode (variableName, token, command, arguments)

    # ====================================================================
    # argumentList
    # <argumentList> -> LPAREN [ <argument> { COMMA <argument> } ] RPAREN
    # ends at a newline

    def argumentList (self):
        self.enter ("argumentList")

        self.match ("argumentList", "LPAREN")

        arguments = []
        if self.tokens[self.currentToken].type != "RPAREN":
            arguments += [self.argument ()]
            while self.tokens[self.currentToken].type == "COMMA":
                self.match ("argumentList", "COMMA")
                arguments += [self.argument ()]

        self.match ("argumentList", "RPAREN")

        self.leave ("argumentList")

        return arguments

    # ====================================================================
    # argument 
    # <argument> -> TYPE LPAREN <expression> RPAREN

    def argument (self):
        self.enter ("argument")

        type = self.typeSpecifier ()

        self.match ("argument", "LPAREN")

        value = self.expression ()
        
        self.match ("argument", "RPAREN")

        self.leave ("argument")

        return ArgumentExpressionNode (type, value)

    # ====================================================================
    # expression
    # <expression> -> GVARIABLE
    #              -> LVARIABLE
    #              -> IDENTIFIER
    #              -> INT
    #              -> FLOAT
    #              -> CHAR
    #              -> STRING

    def expression (self):
        self.enter ("expression")
        
        node = Node
        # <expression> -> GVARIABLE
        if self.tokens[self.currentToken].type == "GVARIABLE":
            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            id = self.tokens[self.currentToken].lexeme
            token = self.tokens[self.currentToken]
            self.match ("expression", "GVARIABLE")
            node = GlobalVariableExpressionNode (id, token, line, column)
        #              -> LVARIABLE
        elif self.tokens[self.currentToken].type == "LVARIABLE":
            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            id = self.tokens[self.currentToken].lexeme
            token = self.tokens[self.currentToken]
            self.match ("expression", "LVARIABLE")
            node = LocalVariableExpressionNode (id, token, line, column)
        #              -> IDENTIFIER
        # labels!
        elif self.tokens[self.currentToken].type == "IDENTIFIER":
            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            id = self.tokens[self.currentToken].lexeme
            token = self.tokens[self.currentToken]
            self.match ("expression", "IDENTIFIER")
            node = IdentifierExpressionNode (id, token, line, column)
        #              -> INT
        elif self.tokens[self.currentToken].type == "INT":
            value = self.tokens[self.currentToken].value
            self.match ("expression", "INT")
            node = IntLiteralExpressionNode (value)
        #              -> FLOAT
        elif self.tokens[self.currentToken].type == "FLOAT":
            value = self.tokens[self.currentToken].value
            self.match ("expression", "FLOAT")
            node = FloatLiteralExpressionNode (value)
        #              -> CHAR
        elif self.tokens[self.currentToken].type == "CHAR":
            value = self.tokens[self.currentToken].value
            self.match ("expression", "CHAR")
            node = CharLiteralExpressionNode (value)
        #              -> STRING
        elif self.tokens[self.currentToken].type == "STRING":
            value = self.tokens[self.currentToken].value
            self.match ("expression", "STRING")
            node = StringLiteralExpressionNode (value)

        self.leave ("expression")

        return node
