# CeruleanASM: AST Reference/Label Resolution Visitor
# By Amy Burnett
# ========================================================================

from abc import ABC, abstractmethod
from sys import exit

from .AST import *
from .visitor import ASTVisitor

# ========================================================================

class ReferenceResolverVisitor (ASTVisitor):

    def __init__(self):
        self.relocationTable = []

    def visitProgramNode (self, node):
        for codeunit in node.codeunits:
            if codeunit != None:
                codeunit.accept (self)

    def visitLabelNode (self, node):
        pass

    def visitVisibilityDirectiveNode (self, node):
        pass

    def determineRelocationType (self, node):
        if node.modifier == 'lo':
            return "imm16_abs_lo"
        elif node.modifier == 'ml':
            return "imm16_abs_ml"
        elif node.modifier == 'mh':
            return "imm16_abs_mh"
        elif node.modifier == 'hi':
            return "imm16_abs_hi"
        elif node.modifier == None:
            return "addr64"
        # We should never reach here, semantic analysis should catch this
        # Just adding this for completion
        print (f"ERROR: Unknown modifier '{node.modifier}'")
        exit (1)

    def visitDataDirectiveNode (self, node):
        for i, arg in enumerate (node.args):
            # Ensure we are only looking at label expressions
            # Ideally we would have wanted the visitor pattern to resolve this
            # But we need extra context than is stored with the label expresision node
            if not isinstance (arg, LabelExpressionNode):
                continue
            # Local (in file) symbols
            if arg.decl.visibility != "extern":
                # For now, let the linker handle this
                arg.address = 0
                isGlobal = arg.decl.visibility == "global"
                self.relocationTable.append ({
                    "location": node.address, # data starts at base address
                    "symbol": arg.id,
                    "type": self.determineRelocationType (arg),
                    "isGlobal": isGlobal
                })
            # External (outside of file) symbols
            elif arg.decl.visibility == "extern":
                # Just use 0 as a placeholder
                # Linker will need to resolve this
                arg.address = 0
                self.relocationTable.append ({
                    "location": node.address, # data starts at base address
                    "symbol": arg.id,
                    "type": self.determineRelocationType (arg),
                    "isGlobal": True
                })
        for label in node.labels:
            label.accept (self)

    def visitInstructionNode (self, node):
        for i, arg in enumerate (node.args):
            # Ensure we are only looking at label expressions
            # Ideally we would have wanted the visitor pattern to resolve this
            # But we need extra context than is stored with the label expresision node
            if not isinstance (arg, LabelExpressionNode):
                continue
            # Local (in file) symbols
            if arg.decl.visibility != "extern":
                # For now, let the linker handle this
                arg.address = 0
                isGlobal = arg.decl.visibility == "global"
                self.relocationTable.append ({
                    "location": node.address + 2, # imm is last 2 bytes of instruction
                    "symbol": arg.id,
                    "type": self.determineRelocationType (arg),
                    "isGlobal": isGlobal
                })
            # External (outside of file) symbols
            elif arg.decl.visibility == "extern":
                # Just use 0 as a placeholder
                # Linker will need to resolve this
                arg.address = 0
                self.relocationTable.append ({
                    "location": node.address + 2, # imm is last 2 bytes of instruction
                    "symbol": arg.id,
                    "type": self.determineRelocationType (arg),
                    "isGlobal": True
                })
        for label in node.labels:
            label.accept (self)

    def visitRegisterExpressionNode (self, node):
        pass

    def visitLabelExpressionNode (self, node):
        pass

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
