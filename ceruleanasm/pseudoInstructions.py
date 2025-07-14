from dataclasses import dataclass
from typing import Callable, List

from .AST import *

# =================================================================================================

@dataclass
class PseudoSpec:
    name: str
    expander: Callable
    argTypes: List[str]
    description: str
    categories: List[str]

PSEUDO_INSTRUCTIONS = {}

def registerPseudoInstruction (name, argTypes, description="", categories=None):
    def wrapper (func):
        PSEUDO_INSTRUCTIONS[name] = PseudoSpec (
            name=name,
            expander=func,
            argTypes=argTypes,
            description=description,
            categories=categories or []
        )
        return func
    return wrapper

# =================================================================================================

@registerPseudoInstruction (
    name='loada',
    argTypes=['reg', 'label'],
    description='Load address of a label into a register',
    categories=['load/store']
)
def expand_loada (pseudoInstruction):
    token = pseudoInstruction.token
    reg, label = pseudoInstruction.args

    hi = LabelExpressionNode (label.token, label.id, modifier="hi")
    mh = LabelExpressionNode (label.token, label.id, modifier="mh")
    ml = LabelExpressionNode (label.token, label.id, modifier="ml")
    lo = LabelExpressionNode (label.token, label.id, modifier="lo")
    imm16 = IntLiteralExpressionNode (token, 16)

    # Make sure any labels on the pseudo-instruction are passed to the first instruction
    # in the expanded set
    return [
        InstructionNode (token, 'lui'   , args=[reg, hi], labels=pseudoInstruction.labels),
        InstructionNode (token, 'lli'   , args=[reg, mh]),
        InstructionNode (token, 'sll64i', args=[reg, reg, imm16]),
        InstructionNode (token, 'lli'   , args=[reg, ml]),
        InstructionNode (token, 'sll64i', args=[reg, reg, imm16]),
        InstructionNode (token, 'lli'   , args=[reg, lo]),
    ]

@registerPseudoInstruction (
    name='mv32',
    argTypes=['reg', 'reg'],
    description='Moves 32-bits from one register to another',
    categories=['move']
)
def expand_mv32 (pseudoInstruction):
    token = pseudoInstruction.token
    regDest, regSrc = pseudoInstruction.args
    imm = IntLiteralExpressionNode (token, 0)
    # Make sure any labels on the pseudo-instruction are passed to the first instruction
    # in the expanded set
    return [
        InstructionNode (token, 'add32i', args=[regDest, regSrc, imm], labels=pseudoInstruction.labels),
    ]

@registerPseudoInstruction (
    name='mv64',
    argTypes=['reg', 'reg'],
    description='Moves 64-bits from one register to another',
    categories=['move']
)
def expand_mv64 (pseudoInstruction):
    token = pseudoInstruction.token
    regDest, regSrc = pseudoInstruction.args
    imm = IntLiteralExpressionNode (token, 0)
    # Make sure any labels on the pseudo-instruction are passed to the first instruction
    # in the expanded set
    return [
        InstructionNode (token, 'add64i', args=[regDest, regSrc, imm], labels=pseudoInstruction.labels),
    ]
