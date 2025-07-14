# CeruleanASM: AST Semantic Analysis Checker Visitor
# By Amy Burnett
# =================================================================================================

from abc import ABC, abstractmethod
from sys import exit

from .visitor import ASTVisitor
from .modifiers import MODIFIERS
from .tokenizer import getTokenContextAsString, Token
from .dataDirectives import *
from .opcodes import *
from .AST import *
from .pseudoInstructions import *

# =================================================================================================

class SemanticAnalysisVisitor (ASTVisitor):

    def __init__(self):
        self.symbolTable = {}
        # Assume semantics pass initially and try to break this assumption
        self.wasSuccessful = True
        self.errorMessages = []
        # We have to defer label expression node checks until the end
        # bc the symbol table needs to be populated first
        self.labelExpressionNodes = []

    def analyze (self, ast):
        ast.accept (self)
        # Ensure label expressions have definitions
        for labelExpressionNode in self.labelExpressionNodes:
            if labelExpressionNode.id not in self.symbolTable:
                self.error (f"Label '{labelExpressionNode.id}' was not defined", labelExpressionNode.token)

    # ---------------------------------------------------------------------------------------------
    # Helper functions

    def error (self, msg, debugToken:Token):
        print ("Semantic Analysis ERROR:", msg)
        if debugToken:
            print (getTokenContextAsString (debugToken))
        self.wasSuccessful = False

    # ---------------------------------------------------------------------------------------------

    def visitProgramNode (self, node):
        for codeunit in node.codeunits:
            if codeunit != None:
                codeunit.accept (self)

    def visitLabelNode (self, node):
        # Ensure this is not a duplicate label
        if node.id in self.symbolTable:
            self.error (f"Duplicate label '{node.id}'", node.token)
        self.symbolTable[node.id] = node

    def visitDataDirectiveNode (self, node):
        # Ensure it is a valid data directive
        if node.id.lower() not in DATA_DIRECTIVES:
            self.error (f"'{node.id}' is not a valid data directive", node.token)
        for label in node.labels:
            label.accept (self)
        # TODO: Ensure argument matches directive
        for argument in node.args:
            argument.accept (self)

    def visitInstructionNode (self, node):
        for label in node.labels:
            label.accept (self)
        for argument in node.args:
            argument.accept (self)

        if node.id in PSEUDO_INSTRUCTIONS:
            # Ensure arguments match instruction format
            expectedArgTypes = PSEUDO_INSTRUCTIONS[node.id].argTypes
            argTypes = []
            for argument in node.args:
                if isinstance (argument, RegisterExpressionNode):
                    argTypes += ['reg']
                elif isinstance (argument, (IntLiteralExpressionNode, CharLiteralExpressionNode, NullExpressionNode)):
                    argTypes += ['imm']
                elif isinstance (argument, LabelExpressionNode):
                    argTypes += ['label']
            if argTypes != expectedArgTypes:
                self.error (f"pseudo-instruction '{node.id}' expects '{expectedArgTypes}', but received '{argTypes}'", node.token)
        elif node.id.upper() in INSTRUCTION_MAPPING:
            # Ensure arguments match instruction format
            expectedFormat = INSTRUCTION_MAPPING[node.id.upper ()]["format"]
            argFormat = ""
            for argument in node.args:
                if isinstance (argument, RegisterExpressionNode):
                    argFormat += 'R'
                if isinstance (argument, (IntLiteralExpressionNode, CharLiteralExpressionNode, NullExpressionNode, LabelExpressionNode)):
                    argFormat += 'I'
            if argFormat == "":
                argFormat = "NONE"
            if argFormat != expectedFormat:
                self.error (f"instruction '{node.id}' expects '{expectedFormat}' arg format, but received '{argFormat}' arg format", node.token)
        else:
            self.error (f"'{node.id}' is not a valid opcode", node.token)

    def visitRegisterExpressionNode (self, node):
        pass

    def visitLabelExpressionNode (self, node):
        # Ensure the modifier is correct if it has one
        if node.modifier != None and node.modifier not in MODIFIERS:
            self.error (f"'{node.modifier}' is not a valid modifier", node.modifierToken)
        # Save to check for missing symbols later
        self.labelExpressionNodes += [node]

    def visitIntLiteralExpressionNode (self, node):
        pass

    def visitFloatLiteralExpressionNode (self, node):
        pass

    def visitCharLiteralExpressionNode (self, node):
        pass

    def visitStringLiteralExpressionNode (self, node):
        pass

    def visitNullExpressionNode (self, node):
        pass
