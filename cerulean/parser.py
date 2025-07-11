# Cerulean Compiler
# By Amy Burnett
# April 10 2021
# ========================================================================

from sys import exit

if __name__ == "parser":
    from tokenizer import printToken
    from ceruleanAST import *
else:
    from .tokenizer import printToken
    from .ceruleanAST import *

# ========================================================================

class Node:
    def __init__(self, name, token=None):
        self.name = name
        self.token = token
        self.children = []

class Parser:

    def __init__(self, tokens, lines, doDebug=False):
        self.tokens = tokens
        self.currentToken = 0
        self.doDebug = doDebug
        self.level = 0
        self.lines = lines

    # <start> -> { <codeunit> }
    def parse(self):

        codeunits = [] 
        
        while self.currentToken < len(self.tokens) and self.tokens[self.currentToken].type != "END_OF_FILE":
            codeunits += [self.codeunit ()]
        
        return ProgramNode(codeunits)

    def match(self, function, expectedToken, additional=""):
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

    # Generic syntax start state 
    # <codeunit> -> <function>
    #            -> <struct>
    #            -> <globalVariable>
    def codeunit (self):
        self.enter ("codeunit")

        node = None

        # <codeunit> -> <function>
        if (self.tokens[self.currentToken].type == 'FUNCTION'):
            node = self.function ()
        # <codeunit> -> <struct>
        elif (self.tokens[self.currentToken].type == "STRUCT"):
            # node = self.structDeclaration ()
            pass
        # <codeunit> -> <globalVariable>
        else:
            node = self.globalVariableDeclaration ()
        
        self.leave ("codeunit")

        return node

    # ====================================================================
    # function declaration
    # <function> -> FUNCTION <typeSpecifier> IDENTIFIER <paramlist> <codeblock>
    
    def function (self):
        self.enter ("function")

        self.match ("function", "FUNCTION")
        
        type = self.typeSpecifier ()

        id = self.tokens[self.currentToken].lexeme
        token = self.tokens[self.currentToken]
        self.match ("function", "IDENTIFIER")
        
        params = self.paramlist()

        body = self.codeblock()

        self.leave ("function")

        return FunctionNode (type, id, token, params, body)

    # ====================================================================
    # class declaration
    # <class> -> CLASS IDENTIFIER [ INHERITS <inheritanceList> ] LBRACE { ( <fieldDeclaration> | <methodDeclaration> ) } RBRACE
    # <classForwardDeclaration> -> CLASS IDENTIFIER [ INHERITS <inheritanceList> ] SEMI
    
    def classDeclaration (self):
        self.enter ("classDeclaration")

        self.match ("classDeclaration", "CLASS")

        id = self.tokens[self.currentToken].lexeme
        token = self.tokens[self.currentToken]
        type = TypeSpecifierNode (Type.USERTYPE, id, token)
        self.match ("classDeclaration", "IDENTIFIER")

        # inheritance 
        # if no inheritance specified, 
        # then it inherits Object by default 
        parent = "Object"
        pToken = None
        if self.tokens[self.currentToken].type == "INHERITS":
            self.match ("classDeclaration", "INHERITS")
            parent, pToken = self.inheritanceList ()[0]

        # print (id, parent)

        # check if it is a forward declaration 
        if self.tokens[self.currentToken].type == "SEMI":
            self.match ("classDeclaration", "SEMI")

            self.leave ("classDeclaration")

            decl = ClassDeclarationNode (type, id, token, parent, pToken, [], [], [], [])
            decl.isForwardDeclaration = True
            return decl
        
        self.match ("classDeclaration", "LBRACE")

        constructors = []
        fields = []
        methods = [] 
        while (self.tokens[self.currentToken].type == "PUBLIC"\
            or self.tokens[self.currentToken].type == "PRIVATE"\
            or self.tokens[self.currentToken].type == "FIELD"\
            or self.tokens[self.currentToken].type == "VIRTUAL"\
            or self.tokens[self.currentToken].type == "METHOD"\
            or self.tokens[self.currentToken].type == "CONSTRUCTOR"):
            if (self.tokens[self.currentToken].type == "PUBLIC"
                or self.tokens[self.currentToken].type == "PRIVATE"):
                if (self.tokens[self.currentToken+1].type == "FIELD"):
                    fields += [self.fieldDeclaration ()]
                elif (self.tokens[self.currentToken+1].type == "VIRTUAL"):
                    methods += [self.virtualMethodDeclaration ()]
                elif (self.tokens[self.currentToken+1].type == "METHOD"):
                    methods += [self.methodDeclaration ()]
                else: 
                    self.error ("classDeclaration", "FIELD", "Expected a field or method in class body")
            else:
                if (self.tokens[self.currentToken].type == "FIELD"):
                    fields += [self.fieldDeclaration ()]
                elif (self.tokens[self.currentToken].type == "VIRTUAL"):
                    methods += [self.virtualMethodDeclaration ()]
                elif (self.tokens[self.currentToken].type == "METHOD"):
                    methods += [self.methodDeclaration ()]
                elif (self.tokens[self.currentToken].type == "CONSTRUCTOR"):
                    constructors += [self.constructorDeclaration ()]
                else: 
                    self.error ("classDeclaration", "FIELD", "Expected a field, virtual method, or method in class body")
            
        self.match ("classDeclaration", "RBRACE")

        # if there are no constructors, 
        # add an empty default constructor
        # the token points to the class declaration
        if len(constructors) == 0:
            constructors += [ConstructorDeclarationNode (token, [], CodeBlockNode ([]))]

        self.leave ("classDeclaration")

        return ClassDeclarationNode (type, id, token, parent, pToken, constructors, fields, [], methods)

    # ====================================================================
    # inheritance list 
    # <inheritanceList> -> IDENTIFIER { COMMA IDENTIFIER }
    # **currently only single inheritance is supported 
    # <inheritanceList> -> IDENTIFIER
    
    def inheritanceList (self):
        self.enter ("inheritanceList")

        parents = [] 

        if (self.tokens[self.currentToken].type == "IDENTIFIER"):
            parents += [[self.tokens[self.currentToken].lexeme, self.tokens[self.currentToken]]]
            self.match ("inheritanceList", "IDENTIFIER")
        else:
            self.error ("inheritanceList", "IDENTIFIER", "Inherits clause requires a classname")
        
        # while (self.tokens[self.currentToken].type == "COMMA"):
        #     self.match ("inheritanceList", "COMMA")
        #     parents += [self.tokens[self.currentToken].lexeme]
        #     self.match ("inheritanceList", "IDENTIFIER")

        self.leave ("inheritanceList")

        return parents

    # ====================================================================
    # field declaration
    # <fieldDeclaration> -> [ VISIBILITY ] FIELD <typeSpecifier> IDENTIFIER SEMI
    
    def fieldDeclaration (self):
        self.enter ("fieldDeclaration")

        # private by default 
        security = Security.PRIVATE
        if (self.tokens[self.currentToken].type == "PUBLIC"):
            security = Security.PUBLIC
            self.match ("methodDeclaration", "PUBLIC")
        elif (self.tokens[self.currentToken].type == "PRIVATE"):
            security = Security.PRIVATE
            self.match ("methodDeclaration", "PRIVATE")

        self.match ("fieldDeclaration", "FIELD")

        type = self.typeSpecifier ()

        id = self.tokens[self.currentToken].lexeme
        token = self.tokens[self.currentToken]
        self.match ("fieldDeclaration", "IDENTIFIER")

        self.match ("fieldDeclaration", "SEMI")

        self.leave ("fieldDeclaration")

        return FieldDeclarationNode (security, type, id, token)

    # ====================================================================
    # virtual method declaration
    # <virtualMethodDeclaration> -> [ SECURITY ] VIRTUAL <typeSpecifier> IDENTIFIER <paramlist> <codeblock>
    
    def virtualMethodDeclaration (self):
        self.enter ("virtualMethodDeclaration")

        # private by default 
        security = Security.PRIVATE
        if (self.tokens[self.currentToken].type == "PUBLIC"):
            security = Security.PUBLIC
            self.match ("virtualMethodDeclaration", "PUBLIC")
        elif (self.tokens[self.currentToken].type == "PRIVATE"):
            security = Security.PRIVATE
            self.match ("virtualMethodDeclaration", "PRIVATE")

        self.match ("virtualMethodDeclaration", "VIRTUAL")

        type = self.typeSpecifier ()

        id = self.tokens[self.currentToken].lexeme
        token = self.tokens[self.currentToken]
        self.match ("virtualMethodDeclaration", "IDENTIFIER")
        
        params = self.paramlist()

        body = self.codeblock()

        self.leave ("virtualMethodDeclaration")

        return MethodDeclarationNode (security, type, id, token, params, body, True)

    # ====================================================================
    # method declaration
    # <methodDeclaration> -> [ SECURITY ] METHOD <typeSpecifier> IDENTIFIER <paramlist> <codeblock>
    
    def methodDeclaration (self):
        self.enter ("methodDeclaration")

        # private by default 
        security = Security.PRIVATE
        if (self.tokens[self.currentToken].type == "PUBLIC"):
            security = Security.PUBLIC
            self.match ("methodDeclaration", "PUBLIC")
        elif (self.tokens[self.currentToken].type == "PRIVATE"):
            security = Security.PRIVATE
            self.match ("methodDeclaration", "PRIVATE")

        self.match ("fieldDeclaration", "METHOD")

        type = self.typeSpecifier ()

        id = self.tokens[self.currentToken].lexeme
        token = self.tokens[self.currentToken]
        self.match ("methodDeclaration", "IDENTIFIER")
        
        params = self.paramlist()

        body = self.codeblock()

        self.leave ("methodDeclaration")

        return MethodDeclarationNode (security, type, id, token, params, body, False)

    # ====================================================================
    # constructor declaration
    # <constructorDeclaration> -> CONSTRUCTOR <paramlist> <codeblock>
    
    def constructorDeclaration (self):
        self.enter ("constructorDeclaration")

        token = self.tokens[self.currentToken]
        self.match ("constructorDeclaration", "CONSTRUCTOR")
        
        params = self.paramlist()

        body = self.codeblock()

        self.leave ("constructorDeclaration")

        return ConstructorDeclarationNode (token, params, body)

    # ====================================================================
    # parameter list for a function declaration
    # <paramlist> -> '(' [ <typeSpecifier> IDENTIFIER { COMMA <typeSpecifier> IDENTIFIER } ] ')'

    def paramlist (self): 
        self.enter ("paramlist")

        params = []

        self.match ("paramlist", "LPAREN")

        if self.tokens[self.currentToken].type != "RPAREN":

            type = self.typeSpecifier ()

            id = self.tokens[self.currentToken].lexeme
            token = self.tokens[self.currentToken]
            self.match ("paramlist", "IDENTIFIER")
            params += [ParameterNode (type, id, token)]

            while self.tokens[self.currentToken].type == "COMMA":
                self.match ("paramlist", "COMMA")

                type = self.typeSpecifier ()

                id = self.tokens[self.currentToken].lexeme
                token = self.tokens[self.currentToken]
                self.match ("paramlist", "IDENTIFIER")
                params += [ParameterNode (type, id, token)]

        self.match ("paramlist", "RPAREN")

        self.leave ("paramlist")

        return params

    # ====================================================================

    def isType (self):
        # <typeSpecifier> -> INTTYPE
        return self.tokens[self.currentToken].type == 'TYPE_BYTE'   \
            or self.tokens[self.currentToken].type == 'TYPE_CHAR'   \
            or self.tokens[self.currentToken].type == 'TYPE_INT32'  \
            or self.tokens[self.currentToken].type == 'TYPE_INT64'  \
            or self.tokens[self.currentToken].type == 'TYPE_FLOAT32'\
            or self.tokens[self.currentToken].type == 'TYPE_FLOAT64'\
            or self.tokens[self.currentToken].type == 'TYPE_BOOL'   \
            or self.tokens[self.currentToken].type == 'TYPE_VOID'

    # <typeSpecifier> -> TYPE_BYTE { '[' ']' }
    #                  | TYPE_CHAR { '[' ']' }
    #                  | TYPE_INT32 { '[' ']' }
    #                  | TYPE_INT64 { '[' ']' }
    #                  | TYPE_FLOAT32 { '[' ']' }
    #                  | TYPE_FLOAT64 { '[' ']' }
    #                  | TYPE_BOOL { '[' ']' }
    #                  | TYPE_VOID { '[' ']' }
    #                  | IDENTIFIER { '[' ']' }
    def typeSpecifier (self):
        self.enter ("typeSpecifier")

        # unknown by default 
        type = None
        temp = self.currentToken

        # <typeSpecifier> -> TYPE_BOOL
        if (self.tokens[self.currentToken].type == 'TYPE_BOOL'):
            self.match ("typeSpecifier", 'TYPE_BOOL')
            type = TypeSpecifierNode (Type.BOOL, "bool", self.tokens[self.currentToken])
        # <typeSpecifier> -> TYPE_BYTE
        elif (self.tokens[self.currentToken].type == 'TYPE_BYTE'):
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
        # <typeSpecifier> -> IDENTIFIER
        elif (self.tokens[self.currentToken].type == 'IDENTIFIER'):
            type = TypeSpecifierNode (Type.USERTYPE, self.tokens[self.currentToken].lexeme, self.tokens[self.currentToken])
            self.match ("typeSpecifier", 'IDENTIFIER')

            # match template params 
            # LTEMP <typeSpec> { COMMA <typeSpec> } RTEMP
            # <: T, K :>
            templateParams = []
            if self.tokens[self.currentToken].type == "LTEMP":
                self.match ("factor", "LTEMP")
                templateParams += [self.typeSpecifier()]
                while self.tokens[self.currentToken].type == "COMMA":
                    self.match ("factor", "COMMA")
                    templateParams += [self.typeSpecifier()]
                self.match ("factor", "RTEMP")
            type.templateParams = templateParams
        
        # match array 
        if type != None:
            while (self.tokens[self.currentToken].type == "LBRACKET"):
                self.match ("typeSpecifier", "LBRACKET")
                # possibly not a type spec
                if (self.tokens[self.currentToken].type != "RBRACKET"):
                    self.currentToken = temp
                    self.leave ("typeSpecifier")
                    return None
                self.match ("typeSpecifier", "RBRACKET")
                type.arrayDimensions += 1
        
        self.leave ("typeSpecifier")

        return type

    # ====================================================================
    # enum class declaration
    # <enum> -> ENUM IDENTIFIER LBRACE [ IDENTIFIER { COMMA IDENTIFIER } ] RBRACE
    # <enumForwardDeclaration> -> ENUM IDENTIFIER SEMI
    
    def enumDeclaration (self):
        self.enter ("enumDeclaration")

        self.match ("enumDeclaration", "ENUM")

        id = self.tokens[self.currentToken].lexeme
        token = self.tokens[self.currentToken]
        type = TypeSpecifierNode (Type.USERTYPE, id, token)
        self.match ("enumDeclaration", "IDENTIFIER")

        # check if it is a forward declaration 
        if self.tokens[self.currentToken].type == "SEMI":
            self.match ("enumDeclaration", "SEMI")
            self.leave ("enumDeclaration")

            decl = EnumDeclarationNode (type, id, token, [])
            decl.isForwardDeclaration = True
            return decl
        
        self.match ("enumDeclaration", "LBRACE")

        fields = []

        if self.tokens[self.currentToken].type == "IDENTIFIER":
            fields += [FieldDeclarationNode (Security.PUBLIC, type, self.tokens[self.currentToken].lexeme, self.tokens[self.currentToken])]
            self.match ("enumDeclaration", "IDENTIFIER")

            # match zero or more COMMA IDENTIFIER
            while self.tokens[self.currentToken].type == "COMMA":
                self.match ("enumDeclaration", "COMMA")
                fields += [FieldDeclarationNode (Security.PUBLIC, type, self.tokens[self.currentToken].lexeme, self.tokens[self.currentToken])]
                self.match ("enumDeclaration", "IDENTIFIER")
            
        self.match ("enumDeclaration", "RBRACE")

        self.leave ("enumDeclaration")

        return EnumDeclarationNode (type, id, token, fields)

    # ====================================================================
    # template declaration
    # <template> -> TEMPLATE LTEMP <typeSpecifier { COMMA IDENTIFIER } RTEMP ( <functionDeclaration> | <classDeclaration> )
    # Example:
    #   template <:T:> function T add (T a, T b) { return a + b; }

    def templateDeclaration (self):
        self.enter ("templateDeclaration")

        token = self.tokens[self.currentToken]
        self.match ("templateDeclaration", "TEMPLATE")

        self.match ("templateDeclaration", "LTEMP")

        t = self.typeSpecifier ()
        t.isGeneric = True
        templateParams = [GenericDeclarationNode (t, t.id, t.token)]

        while self.tokens[self.currentToken].type == "COMMA":
            self.match ("templateDeclaration", "COMMA")
            t = self.typeSpecifier ()
            t.isGeneric = True
            templateParams += [GenericDeclarationNode (t, t.id, t.token)]

        self.match ("templateDeclaration", "RTEMP")

        # function declaration
        if self.tokens[self.currentToken].type == "FUNCTION":
            func = self.function ()
            node = FunctionTemplateDeclarationNode (func.type, func.id, token, templateParams, func)
        # class declaration
        elif self.tokens[self.currentToken].type == "CLASS":
            _class = self.classDeclaration ()
            node = ClassTemplateDeclarationNode (_class.type, _class.id, token, templateParams, _class)
        else:
            self.error ("templateDeclaration", "FUNCTION", "Expected function or class declaration after template clause")

        self.leave ("templateDeclaration")

        return node

    # ====================================================================
    # Global Variable Declaration
    # <globalVariable> -> GLOBAL <typeSpecifier> IDENTIFIER ( ASSIGN <literal> ) SEMI
    # Example:
    # 1.  global int32 x;
    # 2.  global int32 x = 10;

    def globalVariableDeclaration (self):
        self.enter ("globalVariableDeclaration")
        expectedSyntax = "Global Variable Declaration Syntax:\nglobal <type> <varname>;\nglobal <type> <varname> = <literal>;"
        type = self.typeSpecifier ()
        id = self.tokens[self.currentToken].lexeme
        token = self.tokens[self.currentToken]
        self.match ("globalVariableDeclaration", "IDENTIFIER", expectedSyntax)
        # Optional rhs
        rhs = None
        if self.tokens[self.currentToken].type == "ASSIGN":
            self.match ("globalVariableDeclaration", "ASSIGN", expectedSyntax)
            rhs = self.literal ()
        self.match ("globalVariableDeclaration", "SEMI", expectedSyntax)
        node = GlobalVariableDeclarationNode (type, id, token, rhs)
        self.leave ("globalVariableDeclaration")
        return node

    # ====================================================================
    # statement 
    # <statement> -> <codeblock>
    #             -> <forloop>
    #             -> <whileloop>
    #             -> <condition>
    #             -> <returnStatement>
    #             -> <continueStatement>
    #             -> <breakStatement>
    #             -> <expressionStatement>

    def statement (self):
        self.enter ("statement")

        node = None

        # <statement> -> <codeblock>
        if (self.tokens[self.currentToken].type == "LBRACE"):
            node = self.codeblock ()
        # <statement> -> <forloop>
        elif (self.tokens[self.currentToken].type == "FOR"):
            node = self.forloop ()
        # <statement> -> <whileloop>
        elif (self.tokens[self.currentToken].type == "WHILE"):
            node = self.whileloop ()
        # <statement> -> <condition>
        elif (self.tokens[self.currentToken].type == "IF"):
            node = self.conditional ()
        # <statement> -> <returnStatement>
        elif (self.tokens[self.currentToken].type == "RETURN"):
            node = self.returnStatement ()
        # <statement> -> <continueStatement>
        elif (self.tokens[self.currentToken].type == "CONTINUE"):
            node = self.continueStatement ()
        # <statement> -> <breakStatement>
        elif (self.tokens[self.currentToken].type == "BREAK"):
            node = self.breakStatement ()
        # <statement> -> <expressionStatement> 
        else:
            node = self.expressionStatement ()

        self.leave ("statement")

        return node

    # ====================================================================
    # codeblock 
    # <codeblock> -> '{' { <statement> } '}'

    def codeblock (self):
        self.enter ("codeblock")

        statements = []

        self.match ("codeblock", "LBRACE")
        
        while self.tokens[self.currentToken].type != "RBRACE":
            statements += [self.statement ()]
        
        self.match ("codeblock", "RBRACE")

        self.leave ("codeblock")

        return CodeBlockNode (statements)

    # ====================================================================
    # for loop 
    # <forloop> -> for ( <expr> ; <expr> ; <expr> ) <statement> [ <else> ]

    def forloop (self):
        self.enter ("forloop")

        self.match ("forloop", "FOR")
        self.match ("forloop", "LPAREN")
        init = self.expression ()
        self.match ("forloop", "SEMI")
        cond = self.expression ()
        self.match ("forloop", "SEMI")
        update = self.expression ()
        self.match ("forloop", "RPAREN")
        body = self.statement ()

        # match 0 or 1 else
        elseStmt = None
        if (self.tokens[self.currentToken].type == "ELSE"):
            elseStmt = self.elseStatement ()

        self.leave ("forloop")

        return ForStatementNode (init, cond, update, body, elseStmt)

    # ====================================================================
    # while loop 
    # <whileloop> -> while ( <expr> ) <statement>

    def whileloop (self):
        self.enter ("whileloop")

        self.match ("whileloop", "WHILE")
        self.match ("whileloop", "LPAREN")
        cond = self.expression ()
        self.match ("whileloop", "RPAREN")
        body = self.statement ()

        self.leave ("whileloop")

        return WhileStatementNode (cond, body)

    # ====================================================================
    # if statement 
    # <conditional> -> if ( <expr> ) <statement> { <elif> } [ <else> ]

    def conditional (self):
        self.enter ("conditional")

        self.match ("conditional", "IF")
        
        self.match ("conditional", "LPAREN")

        cond = self.expression ()
        
        self.match ("conditional", "RPAREN")

        body = self.statement ()

        # match 0 or more elifs 
        elifs = []
        while (self.tokens[self.currentToken].type == "ELIF"):
            elifs += [self.elifStatement ()]
        
        # match 0 or 1 else
        elseStmt = None
        if (self.tokens[self.currentToken].type == "ELSE"):
            elseStmt = self.elseStatement ()

        self.leave ("conditional")

        return IfStatementNode (cond, body, elifs, elseStmt)

    # ====================================================================
    # elif statement 
    # <elifStatement> -> ELIF ( <expr> ) <statement>

    def elifStatement (self):
        self.enter ("elifStatement")

        self.match ("elifStatement", "ELIF")
        self.match ("elifStatement", "LPAREN")

        cond = self.expression ()

        self.match ("elifStatement", "RPAREN")

        body = self.statement ()

        self.leave ("elifStatement")

        return ElifStatementNode (cond, body)

    # ====================================================================
    # else statement 
    # <elseStatement> -> ELSE <statement>

    def elseStatement (self):
        self.enter ("elseStatement")

        self.match ("elseStatement", "ELSE")

        body = self.statement ()

        self.leave ("elseStatement")

        return ElseStatementNode (body)

    # ====================================================================
    # expressionStatement
    # <expressionStatement> -> [ <expression> ] SEMI

    def expressionStatement (self):
        self.enter ("expressionStatement")

        # optionally an expression
        expr = None
        if (self.tokens[self.currentToken].type != "SEMI"):
            expr = self.expression ()

        # could give error message here saying
        # "hey fricker, you missed a semi"
        self.match ("expressionStatement", "SEMI", "You should add a semicolon")

        self.leave ("expressionStatement")

        return ExpressionStatementNode (expr)

    # ====================================================================
    # return statement
    # <returnStatement> -> RETURN [ <expression> ] ; 

    def returnStatement (self):
        self.enter ("returnStatement")

        token = self.tokens[self.currentToken]
        self.match ("returnStatement", "RETURN")

        # optionally an expression
        expr = None
        if (self.tokens[self.currentToken].type != "SEMI"):
            expr = self.expression ()

        # could give error message here saying
        # "hey fricker, you missed a semi"
        self.match ("returnStatement", "SEMI", "You should add a semicolon")

        self.leave ("returnStatement")

        return ReturnStatementNode (token, expr)

    # ====================================================================
    # break statement
    # <breakStatement> -> BREAK; 

    def breakStatement (self):
        self.enter ("breakStatement")

        token = self.tokens[self.currentToken]
        self.match ("breakStatement", "BREAK")

        # could give error message here saying
        # "hey fricker, you missed a semi"
        self.match ("breakStatement", "SEMI", "You should add a semicolon")

        self.leave ("breakStatement")

        return BreakStatementNode (token)

    # ====================================================================
    # continue statement
    # <continueStatement> -> CONTINUE; 

    def continueStatement (self):
        self.enter ("continueStatement")

        token = self.tokens[self.currentToken]
        self.match ("continueStatement", "CONTINUE")

        # could give error message here saying
        # "hey fricker, you missed a semi"
        self.match ("continueStatement", "SEMI", "You should add a semicolon")

        self.leave ("continueStatement")

        return ContinueStatementNode (token)

    # ====================================================================
    # expression
    # <expression> -> <tuple>

    def expression (self):
        self.enter ("expression")
        
        node = self.tuple ()

        self.leave ("expression")

        return node

    # ====================================================================
    # tuple 
    # <tuple> -> <assignexpr> { , <assignexpr> }

    def tuple (self):
        self.enter ("tuple")

        lhs = self.assignexpr ()

        while (self.tokens[self.currentToken].type == "COMMA"):
            self.match ("tuple", "COMMA")
            rhs = self.assignexpr ()

            lhs = TupleExpressionNode (lhs, rhs)

        self.leave ("tuple")

        return lhs

    # ====================================================================
    # varDeclaration 
    # <varDeclaration> -> ( TYPE [ "[]" ] ID | ID [ "[]" ] ID | <logicalOR> )

    def varDeclaration (self):
        self.enter ("varDeclaration")

        lhs = None

        #     -> ID { '[' ']' } ID 
        #     -> <logicalOR> 
        if (self.isType () or self.tokens[self.currentToken].type == "IDENTIFIER"):

            varIndex = self.currentToken
            # match type
            type = self.typeSpecifier ()

            # assumption was wrong
            # -> <logicalOR> 
            if (type == None or self.tokens[self.currentToken].type != "IDENTIFIER"):
                # restore state
                self.currentToken = varIndex
                lhs = self.logicalOR ()
            else:
                id = self.tokens[self.currentToken].lexeme
                token = self.tokens[self.currentToken]
                self.match ("varDeclaration", "IDENTIFIER")
                lhs = VariableDeclarationNode (type, id, token)
        # assumption was wrong
        else:
            lhs = self.logicalOR ()

        self.leave ("varDeclaration")

        return lhs

    # ====================================================================
    # assignment expressions 
    # <assignexpr> -> { <varDeclaration> = } <varDeclaration>
    def assignexpr (self):
        self.enter ("assignexpr")

        root = None
        lastAssign = None

        # while lhs is var or var declaration
        while (self.tokens[self.currentToken].type == "THIS" \
            or self.tokens[self.currentToken].type == "IDENTIFIER" \
            or self.isType()):
            # save return state
            varIndex = self.currentToken
            lhs = self.varDeclaration ()

            # if there is an assign
            if (   self.tokens[self.currentToken].type == "ASSIGN" \
                or self.tokens[self.currentToken].type == "ASSIGN_ADD" \
                or self.tokens[self.currentToken].type == "ASSIGN_SUB" \
                or self.tokens[self.currentToken].type == "ASSIGN_MUL" \
                or self.tokens[self.currentToken].type == "ASSIGN_DIV" \
                or self.tokens[self.currentToken].type == "ASSIGN_MOD"):
                line = self.tokens[self.currentToken].line
                column = self.tokens[self.currentToken].column
                assignToken = self.tokens[self.currentToken]
                self.match ("assignexpr", self.tokens[self.currentToken].type)
                rhs = AssignExpressionNode (assignToken, lhs, None, line, column)
                # if this is the first assignment expression
                if (root == None):
                    # make this the root 
                    root = rhs 
                    lastAssign = root 
                # not the first assignment statement
                else:
                    lastAssign.rhs = rhs 
                    lastAssign = rhs 
            # no ASSIGN
            # assumption was wrong
            else:
                # assumption was wrong, the var should be a logicalOR
                self.currentToken = varIndex
                break 

        # if there was at least one assign expr 
        if (root != None):
            lastAssign.rhs = self.varDeclaration ()
            self.leave ("assignexpr")
            return root 
        
        lhs = self.varDeclaration ()

        self.leave ("assignexpr")
        return lhs

    # ====================================================================
    # logical OR 
    # <logicalOR> -> <logicalAND> { || <logicalAND> }

    def logicalOR (self):
        self.enter ("logicalOR")

        lhs = self.logicalAND ()

        while self.tokens[self.currentToken].type == "LOR":
            
            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            orToken = self.tokens[self.currentToken]
            self.match ("logicalOR", "LOR")
            rhs = self.logicalAND ()

            lhs = LogicalOrExpressionNode (orToken, lhs, rhs, line, column)

        self.leave ("logicalOR")

        return lhs

    # ====================================================================
    # logical AND
    # <logicalAND> -> <equalop> { && <equalop> }

    def logicalAND (self):
        self.enter ("logicalAND")

        lhs = self.equalop ()

        while self.tokens[self.currentToken].type == "LAND":

            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            andToken = self.tokens[self.currentToken]
            self.match ("logicalOR", "LAND")
            rhs = self.equalop ()

            lhs = LogicalAndExpressionNode (andToken, lhs, rhs, line, column)

        self.leave ("logicalAND")

        return lhs

    # ====================================================================
    # equal operator
    # <equalop> -> <inequalop> -> { ( == | != ) <inequalop> }

    def equalop (self):
        self.enter ("equalop")

        lhs = self.inequalop ()

        while self.tokens[self.currentToken].type == "EQ" \
            or self.tokens[self.currentToken].type == "NE": 

            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            opToken = self.tokens[self.currentToken]
            if self.tokens[self.currentToken].type == "EQ":
                self.match ("equalop", "EQ")
            else:
                self.match ("equalop", "NE")
            rhs = self.inequalop ()

            lhs = EqualityExpressionNode (opToken, lhs, rhs, line, column)

        self.leave ("equalop")

        return lhs

    # ====================================================================
    # inequal operator
    # <inequalop> -> <addsub> -> { (  ) <addsub> }

    def inequalop (self):
        self.enter ("inequalop")

        lhs = self.addsub ()

        while self.tokens[self.currentToken].type == "LT"   \
            or self.tokens[self.currentToken].type == "LTE" \
            or self.tokens[self.currentToken].type == "GT"  \
            or self.tokens[self.currentToken].type == "GTE":

            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            op = self.tokens[self.currentToken]
            self.match ("inequalop", self.tokens[self.currentToken].type)
            rhs = self.addsub ()

            lhs = InequalityExpressionNode (op, lhs, rhs, line, column)

        self.leave ("inequalop")

        return lhs

    # ====================================================================
    # addition and subtraction 
    # <addsub> -> <term> { ( + | - ) <term> }

    def addsub (self):
        self.enter ("addsub")

        lhs = self.term ()

        while  self.tokens[self.currentToken].type == "PLUS"  \
            or self.tokens[self.currentToken].type == "MINUS":

            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            op = self.tokens[self.currentToken]
            self.match ("addsub", self.tokens[self.currentToken].type)
            rhs = self.term ()

            lhs = AdditiveExpressionNode (op, lhs, rhs, line, column)

        self.leave ("addsub")

        return lhs

    # ====================================================================
    # multiplication / division / remainder (mod)
    # <term> -> <unaryleft> { ( * | / | % ) <unaryleft> }

    def term (self):
        self.enter ("term")

        lhs = self.unaryleft ()

        while self.tokens[self.currentToken].type == "TIMES"   \
            or self.tokens[self.currentToken].type == "DIVIDE" \
            or self.tokens[self.currentToken].type == "MOD":

            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            op = self.tokens[self.currentToken]
            self.match ("term", self.tokens[self.currentToken].type)
            rhs = self.unaryleft ()

            lhs = MultiplicativeExpressionNode (op, lhs, rhs, line, column)

        self.leave ("term")

        return lhs 

    # ====================================================================
    # unary left operators
    # <unaryleft> -> [ ( ++ | -- | + | - | ! | ~ ) ] <unaryright>

    def unaryleft (self):
        self.enter ("unaryleft")

        op = None
        line = 0
        column = 0
        if self.tokens[self.currentToken].type == "INCR":
            op = self.tokens[self.currentToken]
            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            self.match ("unaryleft", self.tokens[self.currentToken].type)
            rhs = self.unaryright ()
            rhs = PreIncrementExpressionNode (op, rhs, line, column)
        elif self.tokens[self.currentToken].type == "DECR":
            op = self.tokens[self.currentToken]
            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            self.match ("unaryleft", self.tokens[self.currentToken].type)
            rhs = self.unaryright ()
            rhs = PreDecrementExpressionNode (op, rhs, line, column)
        elif self.tokens[self.currentToken].type == "PLUS":
            # Just ignore the plus since it doesnt do anything
            # op = self.tokens[self.currentToken]
            # line = self.tokens[self.currentToken].line
            # column = self.tokens[self.currentToken].column
            self.match ("unaryleft", self.tokens[self.currentToken].type)
            rhs = self.unaryright ()
            # rhs = UnaryLeftExpressionNode (op, rhs, line, column)
        elif self.tokens[self.currentToken].type == "MINUS":
            op = self.tokens[self.currentToken]
            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            self.match ("unaryleft", self.tokens[self.currentToken].type)
            rhs = self.unaryright ()
            rhs = NegativeExpressionNode (op, rhs, line, column)
        elif self.tokens[self.currentToken].type == "LNOT":
            op = self.tokens[self.currentToken]
            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            self.match ("unaryleft", self.tokens[self.currentToken].type)
            rhs = self.unaryright ()
            rhs = LogicalNotExpressionNode (op, rhs, line, column)
        elif self.tokens[self.currentToken].type == "BNOT":
            op = self.tokens[self.currentToken]
            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            self.match ("unaryleft", self.tokens[self.currentToken].type)
            rhs = self.unaryright ()
            rhs = BitwiseNegatationExpressionNode (op, rhs, line, column)
        else:
            rhs = self.unaryright ()

        self.leave ("unaryleft")
        return rhs

    # ====================================================================
    # unary right operators 
    # <unaryright> -> <arrayAccess> [ ( ++ | -- ) ]

    def unaryright (self):
        self.enter ("unaryright")
        
        lhs = self.arrayAccess ()

        # <unaryright> -> <arrayAccess> [ ++ ]
        if self.tokens[self.currentToken].type == "INCR":
            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            op = self.tokens[self.currentToken]
            self.match ("unaryright", "INCR")
            lhs = PostIncrementExpressionNode (op, lhs, line, column)
        # <unaryright> -> <arrayAccess> [ -- ]
        elif self.tokens[self.currentToken].type == "DECR":
            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            op = self.tokens[self.currentToken]
            self.match ("unaryright", "DECR")
            lhs = PostDecrementExpressionNode (op, lhs, line, column)

        self.leave ("unaryright")

        return lhs

    # ====================================================================
    # array accessor and function call and member accessor
    # string.length
    # string.substring(0, 12).size()
    # string.data[10]
    # (matrixA * matrixB).transpose()
    # <arrayAccess> -> <factor> { ( '(' [ <assignExpression> { COMMA <assignExpression> } ] ')' | '[' [ <expression> ] ']' | DOT <factor> ) }
    def arrayAccess (self):
        self.enter ("arrayAccess")

        lhs = self.factor ()

        while (self.tokens[self.currentToken].type == "LPAREN"  \
            or self.tokens[self.currentToken].type == "LTEMP"   \
            or self.tokens[self.currentToken].type == "LBRACKET"\
            or self.tokens[self.currentToken].type == "DOT"):

            # function call 
            # <arrayAccess> -> <factor> [ LTEMP <typeSpec> { <typeSpec> } RTEMP ] { '(' [ <assignExpression> { COMMA <assignExpression> } ] ')' }
            if self.tokens[self.currentToken].type == "LPAREN" or self.tokens[self.currentToken].type == "LTEMP":
                # grab any template parameters 
                templateParams = []
                if self.tokens[self.currentToken].type == "LTEMP":
                    self.match ("arrayAccess", "LTEMP")
                    templateParams += [self.typeSpecifier ()]
                    while self.tokens[self.currentToken].type == "COMMA":
                        self.match ("arrayAccess", "COMMA")
                        templateParams += [self.typeSpecifier ()]
                    self.match ("arrayAccess", "RTEMP")

                line = self.tokens[self.currentToken].line
                column = self.tokens[self.currentToken].column
                opToken = self.tokens[self.currentToken]
                self.match ("arrayAccess", "LPAREN")
                args = []
                # optional arguments 
                if self.tokens[self.currentToken].type != "RPAREN":
                    args += [self.assignexpr ()]
                    # 0 or more additional arguments 
                    while self.tokens[self.currentToken].type == "COMMA":
                        self.match ("arrayAccess", "COMMA")
                        args += [self.assignexpr ()]
                self.match ("arrayAccess", "RPAREN")
                lhs = FunctionCallExpressionNode (opToken, lhs, args, templateParams, line, column)
            # subscript operator 
            # <arrayAccess> -> <factor> { '[' <expr> ']' }
            elif self.tokens[self.currentToken].type == "LBRACKET":
                line = self.tokens[self.currentToken].line
                column = self.tokens[self.currentToken].column
                opToken = self.tokens[self.currentToken]
                self.match ("arrayAccess", "LBRACKET")
                offset = self.expression ()
                self.match ("arrayAccess", "RBRACKET")
                lhs = SubscriptExpressionNode (opToken, lhs, offset, line, column)
            # member accessor
            # <arrayAccess> -> <factor> { DOT <factor> [ '(' [ <assignExpression> { COMMA <assignExpression> } ] ')' ] }
            elif (self.tokens[self.currentToken].type == "DOT"):
                line = self.tokens[self.currentToken].line
                column = self.tokens[self.currentToken].column
                opToken = self.tokens[self.currentToken]
                self.match ("arrayAccess", "DOT")
                rhs = self.factor ()
                # method call
                if (self.tokens[self.currentToken].type == "LPAREN"):
                    self.match ("arrayAccess", "LPAREN")
                    args = []
                    # optional arguments 
                    if self.tokens[self.currentToken].type != "RPAREN":
                        args += [self.assignexpr ()]
                        # 0 or more additional arguments 
                        while self.tokens[self.currentToken].type == "COMMA":
                            self.match ("arrayAccess", "COMMA")
                            args += [self.assignexpr ()]
                    self.match ("arrayAccess", "RPAREN")
                    lhs = MethodAccessorExpressionNode (opToken, lhs, rhs, args, line, column)
                # field accessor
                else:
                    lhs = MemberAccessorExpressionNode (opToken, lhs, rhs, line, column)

        self.leave ("arrayAccess")

        return lhs

    # ====================================================================
    # parentheses / indentifiers / list / literals 
    # <factor> -> '(' [ <expr> ] ')'
    #          -> THIS
    #          -> IDENTIFIER
    #          -> '[' [ [ <assignExpression> { COMMA <assignExpression> } ] ] ']'
    #          -> HEAPALLOC '(' <typeSpecifier>, <expr> ')'
    #          -> <literal>

    def factor (self):
        self.enter ("factor")

        lhs = None 

        # <factor> -> '(' [ <expr> ] ')'
        if self.tokens[self.currentToken].type == "LPAREN":
            self.match ("factor", "LPAREN")
            if self.tokens[self.currentToken].type != "RPAREN":
                lhs = self.expression ()
                lhs.hasParentheses = True
            self.match ("factor", "RPAREN")
        # <factor> -> THIS
        elif self.tokens[self.currentToken].type == "THIS":
            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            token = self.tokens[self.currentToken]
            self.match ("factor", "THIS")
            lhs = ThisExpressionNode (token, line, column)
        # <factor> -> IDENTIFIER
        elif self.tokens[self.currentToken].type == "IDENTIFIER":
            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            id = self.tokens[self.currentToken].lexeme
            token = self.tokens[self.currentToken]
            self.match ("factor", "IDENTIFIER")
            lhs = IdentifierExpressionNode (token, id, line, column)
        # list constructor operator  
        # <factor> -> '[' [ [ <assignExpression> { COMMA <assignExpression> } ] ] ']'
        elif self.tokens[self.currentToken].type == "LBRACKET":
            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            opToken = self.tokens[self.currentToken]
            self.match ("factor", "LBRACKET")
            items = []
            # optional items 
            if self.tokens[self.currentToken].type != "RBRACKET":
                items += [self.assignexpr ()]
                # 0 or more additional items 
                while self.tokens[self.currentToken].type == "COMMA":
                    self.match ("factor", "COMMA")
                    items += [self.assignexpr ()]
            self.match ("factor", "RBRACKET")
            lhs = ListConstructorExpressionNode (opToken, items, line, column)
        # <factor> -> HEAPALLOC '(' <typeSpecifier>, <expr> ')'
        elif self.tokens[self.currentToken].type == "HEAPALLOC":
            token = self.tokens[self.currentToken]
            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            self.match ("factor", "HEAPALLOC")
            self.match ("factor", "LPAREN")
            elementType = self.typeSpecifier ()
            self.match ("factor", "COMMA")
            sizeExpr = self.expression ()
            self.match ("factor", "RPAREN")
            lhs = ArrayAllocatorExpressionNode (token, elementType, sizeExpr, [], line, column)
        # <factor> -> SIZEOF ( <expression> ) 
        elif self.tokens[self.currentToken].type == "SIZEOF":
            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            self.match ("factor", "SIZEOF")
            opToken = self.tokens[self.currentToken]
            self.match ("factor", "LPAREN")
            type = TypeSpecifierNode (Type.INT, "int", None)
            # ensure there is an expression
            if self.tokens[self.currentToken].type == "RPAREN":
                print (f"Parsing Error: Sizeof requires an expression")
                print (f"   in file {opToken.originalFilename}")
                print (f"   on line {opToken.originalLine}:{opToken.column}")
                print (f"   {self.lines[opToken.line-1]}")
                print (f"   ",end="")
                for i in range(opToken.column-1):
                    print (" ", end="")
                print ("^")
                print ()
                exit(1)
            # assignexpr instead of expression because expressions could be tuples 
            # tuples are not yet supported 
            rhs = self.assignexpr ()
            # ensure user didn't try to provide more than one expression
            if self.tokens[self.currentToken].type == "COMMA":
                print (f"Parsing Error: Sizeof only takes one array parameter")
                print (f"   in file {opToken.originalFilename}")
                print (f"   on line {opToken.originalLine}:{opToken.column}")
                print (f"   {self.lines[opToken.line-1]}")
                print (f"   ",end="")
                for i in range(opToken.column-1):
                    print (" ", end="")
                print ("^")
                print ()
                exit(1)
            self.match ("factor", "RPAREN")
            lhs = SizeofExpressionNode (opToken, type, rhs, line, column)

        # <factor> -> FREE ( <expression> ) 
        elif self.tokens[self.currentToken].type == "FREE":
            line = self.tokens[self.currentToken].line
            column = self.tokens[self.currentToken].column
            self.match ("factor", "FREE")
            opToken = self.tokens[self.currentToken]
            self.match ("factor", "LPAREN")
            type = TypeSpecifierNode (Type.VOID, "void", None)
            # ensure there is an expression
            if self.tokens[self.currentToken].type == "RPAREN":
                print (f"Parsing Error: Free requires an expression")
                print (f"   in file {opToken.originalFilename}")
                print (f"   on line {opToken.originalLine}:{opToken.column}")
                print (f"   {self.lines[opToken.line-1]}")
                print (f"   ",end="")
                for i in range(opToken.column-1):
                    print (" ", end="")
                print ("^")
                print ()
                exit(1)
            # assignexpr instead of expression because expressions could be tuples 
            # tuples are not yet supported 
            rhs = self.assignexpr ()
            # ensure user didn't try to provide more than one expression
            if self.tokens[self.currentToken].type == "COMMA":
                print (f"Parsing Error: Free only takes one array parameter")
                print (f"   in file {opToken.originalFilename}")
                print (f"   on line {opToken.originalLine}:{opToken.column}")
                print (f"   {self.lines[opToken.line-1]}")
                print (f"   ",end="")
                for i in range(opToken.column-1):
                    print (" ", end="")
                print ("^")
                print ()
                exit(1)
            self.match ("factor", "RPAREN")
            lhs = FreeExpressionNode (opToken, type, rhs, line, column)

        else:
            lhs = self.literal ()

        self.leave ("factor")

        return lhs

    # ====================================================================
    # literals
    # <literal> -> INT
    #           -> FLOAT
    #           -> CHAR
    #           -> STRING
    #           -> NULL

    def literal (self):
        self.enter ("literal")

        node = None

        if self.tokens[self.currentToken].type == "INT":
            value = self.tokens[self.currentToken].value
            node = IntLiteralExpressionNode (self.tokens[self.currentToken], value)
            self.match ("literal", "INT")
        elif self.tokens[self.currentToken].type == "FLOAT":
            value = self.tokens[self.currentToken].value
            node = FloatLiteralExpressionNode (self.tokens[self.currentToken], value)
            self.match ("literal", "FLOAT")
        elif self.tokens[self.currentToken].type == "CHAR":
            value = self.tokens[self.currentToken].value
            node = CharLiteralExpressionNode (self.tokens[self.currentToken], value)
            self.match ("literal", "CHAR")
        elif self.tokens[self.currentToken].type == "STRING":
            value = self.tokens[self.currentToken].value
            node = StringLiteralExpressionNode (self.tokens[self.currentToken], value)
            self.match ("literal", "STRING")
        elif self.tokens[self.currentToken].type == "NULL":
            node = NullExpressionNode (self.tokens[self.currentToken], self.tokens[self.currentToken].line, self.tokens[self.currentToken].column)
            self.match ("literal", "NULL")
        # expected literal but didnt get one 
        else:
            self.error ("literal", "INT")

        self.leave ("literal")

        return node

# ========================================================================