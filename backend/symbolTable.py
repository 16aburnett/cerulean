# Amy Script Compiler
# By Amy Burnett
# April 11 2021
# ========================================================================

from enum import Enum
from sys import exit

from .tokenizer import printToken
from .ceruleanIRAST import *

# ========================================================================

class Symbol:
    def __init__(self):
        self.id = ""
        self.typeDec = {}
        self.varDec = None 
        self.funDec = {0:[]} 

class Kind(Enum):
    TYPE = 0
    VAR  = 1
    FUNC = 2
    LABEL = 3

class ScopeType (Enum):
    FUNCTION = 0
    OTHER    = 1

# ========================================================================

class SymbolTable:

    def __init__(self, debug=False):
        self.nestLevel = 0
        # list of dictionaries
        self.table = [{}]
        self.scopeTypes = [ScopeType.FUNCTION]
        self.lines = []

        # for x86
        self.linksFollowed = 0

        self.debug = debug

    def enterScope (self, scopeType=ScopeType.OTHER):
        self.table.append ({})
        self.scopeTypes.append(scopeType)
        self.nestLevel += 1

    def exitScope (self):
        self.table.pop ()
        self.scopeTypes.pop ()
        self.nestLevel -= 1

    # table [
    #   scope0 : {
    #       add : Symbol {
    #           typeDec : None,
    #           varDec : None,
    #           funDec : templates {
    #              0 template params : overloads[]
    #              1 template param  : TemplateFunction()
    #                  instances[]
    #              2 template params : TemplateFunction()
    #                  instances[]
    #           }
    #       }   
    #       vector : Symbol {
    #           typeDec : templates {
    #               0 template params : ClassDec
    #               1 template param  : TemplateClass()
    #                   instances[
    #                       vector<int>
    #                       vector<float>
    #                   ]
    #           }
    #           varDec : None,
    #           funDec : None
    #       }
    #       vector<int>::push_back : Symbol {
    #           typeDec : None
    #           varDec  : None,
    #           funDec  : templates {
    #               0 template params : overloads[]
    #           }
    #       }
    # 
    # ]
    def insert (self, decl, name, kind):
        if (self.debug):
            print (f"[SymbolTable] [insert] [debug] '{name}' as {kind}")

        # TYPES (CLASS, CLASSTEMP, ENUM)
        if kind == Kind.TYPE:
            # ** ensure decl is a type 
            # ensure type wasnt already declared in this scope
            if (name in self.table[-1] and self.table[-1][name].typeDec != {}):

                # CLASS TEMPLATES
                if isinstance (decl, ClassTemplateDeclarationNode):
                    # print (f"  {decl.templateParams}")
                    # ensure there isnt already a template with the same amount of template params 
                    if len(decl.templateParams) in self.table[-1][name].typeDec:
                        originalDec = self.table[-1][name].typeDec[len(decl.templateParams)].type
                        print (f"Semantic Error: Redeclaration of class template '{decl.id}' with {len(decl.templateParams)} template parameters")
                        print (f"   Original:")
                        printToken (originalDec.token, "      ")
                        print (f"   Redeclaration:")
                        printToken (decl._class.token, "      ")
                        print ()
                        return False
                # CLASS & ENUM
                else:
                    if 0 in self.table[-1][name].typeDec:
                        originalDec = self.table[-1][name].typeDec[0].type
                        print (f"Semantic Error: Redeclaration of class/enum '{decl.id}'")
                        print (f"   Original:")
                        printToken (originalDec.token, "      ")
                        print (f"   Redeclaration:")
                        printToken (decl.type.token, "      ")
                        print ()
                        return False

            # ensure symbol is in table 
            if (name not in self.table[-1]):
                self.table[-1][name] = Symbol ()

            # CLASS TEMPLATE
            if isinstance (decl, (ClassTemplateDeclarationNode)):
                # insert new type
                self.table[-1][name].typeDec[len(decl.templateParams)] = decl
            # CLASS & ENUM
            else:
                # insert new type
                self.table[-1][name].typeDec[0] = decl

            return True
        
        # VARIABLES, FIELDS
        elif kind == Kind.VAR:
            # ** ensure decl is a VAR 
            # ensure VAR wasnt already declared in this scope
            if (name in self.table[-1] and self.table[-1][name].varDec != None):
                return False

            # ensure symbol is in table 
            if (name not in self.table[-1]):
                self.table[-1][name] = Symbol ()

            # insert new VAR
            self.table[-1][name].varDec = decl
            return True
        
        # LABELS
        # labels are VAR for simplicity
        # elif kind == Kind.LABEL:
        #     # TODO: Ensure decl is a LABEL
        #     # Ensure LABEL wasnt already declared in this scope
        #     if (name in self.table[-1] and self.table[-1][name].varDec != None):
        #         # LABEL already exists, failed to insert
        #         return False

        #     # ensure symbol is in table
        #     if (name not in self.table[-1]):
        #         self.table[-1][name] = Symbol ()

        #     # insert new LABEL
        #     self.table[-1][name].varDec = decl
        #     return True

        # FUNCTIONS
        elif kind == Kind.FUNC:
            # ** ensure decl is a FUNC
            # ensure FUNC wasnt already declared in this scope
            if (name in self.table[-1]):
                # Ensure function overload doesnt already exist
                if (isinstance (decl, (FunctionNode))):
                    # ensure that parameters dont match
                    for overload in self.table[-1][name].funDec[0]:
                        # params dont match if nParams is different
                        if len(overload.params) != len(decl.params):
                            continue
                        # check if param types match
                        for i in range(len(overload.params)):
                            # found nonmatching param
                            if overload.params[i].type.__str__() != decl.params[i].type.__str__():
                                # param types do not match
                                break
                        # param types match 
                        else:
                            return False 
                    # reaches here if no overloads match
                # functions can be overloaded by the number of template parameters
                elif isinstance (decl, FunctionTemplateDeclarationNode):
                    # print (f"  {decl.types}")
                    # ensure there isnt already a template with the same amount of template params 
                    if len(decl.types) in self.table[-1][name].funDec:
                        originalDec = self.table[-1][name].funDec[len(decl.types)].type
                        print (f"Semantic Error: Redeclaration of template function '{decl.id}' with {len(decl.types)} template parameters")
                        print (f"   Original:")
                        printToken (originalDec.token, "      ")
                        print (f"   Redeclaration:")
                        printToken (decl.type.token, "      ")
                        print ()
                        return False
            # reaches here if not a redeclaration 

            # ensure symbol is in table 
            if (name not in self.table[-1]):
                self.table[-1][name] = Symbol ()

            # add function to overload list in table
            if isinstance (decl, (FunctionNode)):
                # add to overload list 
                self.table[-1][name].funDec[0].append (decl)
                return True

            # add function template to template overloads 
            elif isinstance (decl, FunctionTemplateDeclarationNode):
                # add template function
                self.table[-1][name].funDec[len(decl.types)] = decl 
                return True

        return False

    def lookup (self, name, kind, params=[], templateParams=[], visitor=None):
        if (self.debug):
            print (f"[SymbolTable] [lookup] [debug] {name} {kind} {[param.type.__str__() for param in params]}")

        self.linksFollowed = 0

        # for each scope
        # march through the scopes 
        # use closest suitable match 
        for i in range(len(self.table)-1, -1, -1):

            # ensure var is in this scope
            if (name not in self.table[i]):
                if self.scopeTypes[i] == ScopeType.FUNCTION:
                    self.linksFollowed += 1
                continue

            # TYPES (CLASS, CLASSTEMP, ENUM)
            if (kind == Kind.TYPE):
                # CLASS TEMP
                if len(templateParams) > 0:
                    # ensure template params match 
                    if len(templateParams) not in self.table[i][name].typeDec:
                        if self.scopeTypes[i] == ScopeType.FUNCTION:
                            self.linksFollowed += 1
                        continue 

                    # create template instance if DNE
                    tempSignature = [f"<:{templateParams[0]}"]
                    for j in range(1, len(templateParams)):
                        tempSignature += [f", {templateParams[j]}"]
                    tempSignature += [f":>"]
                    tempSignature = "".join(tempSignature)
                    if tempSignature not in self.table[i][name].typeDec[len(templateParams)].instantiations:
                        # print ("creating template instance...")
                        # print (name, tempSignature)
                        # create instance
                        _class = self.table[i][name].typeDec[len(templateParams)]._class.copy()
                        self.table[i][name].typeDec[len(templateParams)].instantiations[tempSignature] = _class
                        # overrite template aliases with their new types 
                        _class.templateParams = templateParams
                        _class.type.templateParams = templateParams
                        templateVisitor = TemplateVisitor (self.table[i][name].typeDec[len(templateParams)].templateParams, templateParams)
                        _class.accept (templateVisitor)
                        # analyze new instance 
                        visitor.insertFunc = False
                        oldWasSuccessful = visitor.wasSuccessful
                        visitor.wasSuccessful = True
                        _class.accept (visitor)
                        if not visitor.wasSuccessful:
                            print (f"^~~~From instantiation of class '{_class.id+tempSignature}'", end="\n\n")
                            exit (1)
                        # restore previous success
                        visitor.wasSuccessful = visitor.wasSuccessful and oldWasSuccessful
                        visitor.insertFunc = True
                    return self.table[i][name].typeDec[len(templateParams)].instantiations[tempSignature]

                # CLASS & ENUM
                else:
                    # ensure symbol is a variable
                    if 0 not in self.table[i][name].typeDec:
                        if self.scopeTypes[i] == ScopeType.FUNCTION:
                            self.linksFollowed += 1
                        continue
                    return self.table[i][name].typeDec[0]

            # VARIABLES, FIELDS
            elif (kind == Kind.VAR):
                # ensure symbol is a variable
                if self.table[i][name].varDec == None:
                    if self.scopeTypes[i] == ScopeType.FUNCTION:
                        self.linksFollowed += 1
                    continue
                return self.table[i][name].varDec
                
            # FUNCTIONS
            elif (kind == Kind.FUNC):

                # FUNCTION, METHOD, CONSTRUCTOR 
                if (isinstance (self.table[i][name].funDec, dict)):
                    # check each overload and determine initial candidates 
                    candidates = []
                    for overload in self.table[i][name].funDec[0]:
                        # check the number of parameters 
                        if (len(params) != len(overload.params)):
                            continue
                        # check parameter types 
                        # steps is the number of steps up from the derived class arguments to the overload's parameters 
                        # For example:
                        # C inherits B, B inherits A 
                        #   functioncall func(C, C);
                        # with:
                        #   declaration func(A, A); // 2 steps, 2 steps -> 4 total steps (C->B->A, C->B->A)
                        #   declaration func(B, B); // 1 step , 1 step  -> 2 total steps (C->B, C->B)
                        steps = 0
                        for j in range(len(params)):
                            # check if param type does not match
                            # print (params[j].type, overload.params[j].type)
                            if params[j].type.__str__() != overload.params[j].type.__str__():
                                # make sure types are not related
                                isObject = overload.params[j].type.type == Type.USERTYPE
                                isArray = overload.params[j].type.arrayDimensions > 0
                                if params[j].type.id == "null" and (isObject or isArray):
                                    continue
                                # ensure array dim match
                                if params[j].type.arrayDimensions != overload.params[j].type.arrayDimensions:
                                    break
                                # ensure types are objects; for checking subtypes
                                if overload.params[j].type.type != Type.USERTYPE or params[j].type.type != Type.USERTYPE:
                                    break
                                # make sure lhs is not a subtype of rhs
                                # get class declaration
                                parent = params[j].type.decl.pDecl 
                                match = False 
                                steps += 1
                                while parent != None:
                                    # print (" ", parent.type, overload.params[j].type)
                                    # check ids instead of __str__ because overload could be array but the parent type wouldn't be 
                                    if parent.type.id == overload.params[j].type.id:
                                        match = True
                                        break
                                    parent = parent.pDecl 
                                    steps += 1
                                # found matching parent class
                                # params[j] is of the same type as overload.params[j]
                                if match:
                                    continue 
                                break
                        # all param types match - found a viable function decl overload
                        else: 
                            candidates += [(overload, steps)]
                        # check next overload 
                    # check if viable overloads were found 
                    if len(candidates) == 0:
                        # no viable overloads found at this scope
                        print (f"Semantic Error: no viable candidates found for \"{name}\"")
                        if self.scopeTypes[i] == ScopeType.FUNCTION:
                            self.linksFollowed += 1
                        # return None 
                        continue
                    # found viable overloads 
                    # check for best viable overload 
                    # best viable overload is the one with the least number of steps 
                    # throws an ambiguity error if there are multiple 
                    maxVal = float("inf")
                    maxI = [0]
                    for j in range(len(candidates)):
                        if candidates[j][1] < maxVal:
                            maxVal = candidates[j][1]
                            maxI = [j]
                        # same steps 
                        elif candidates[j][1] == maxVal:
                            maxI += [j]
                    # check for ambiguity 
                    if len(maxI) > 1:
                        print (f"Semantic Error: Ambiguity in function lookup")
                        print (f"   Desired:    {name}(", end="")
                        if len(params) > 0:
                            print (f"{params[0].type}", end="")
                        for j in range(1, len(params)):
                            print (f", {params[j].type}",end="")
                        print (f")")
                        for j in maxI:
                            print (f"   Candidate: {candidates[j][0].signature}")
                            print (f"      Steps: {candidates[j][1]}")
                        return None
                    # no ambiguity -> found viable candidate
                    return candidates[maxI[0]][0]
                    # reaches here if no overloads match 
            if self.scopeTypes[i] == ScopeType.FUNCTION:
                self.linksFollowed += 1
                
        # reaches here if no matching declaration was found
        return None

# ========================================================================