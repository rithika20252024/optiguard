"""IR package for OptiGuard."""

from optiguard.ir.tac import TACInstruction, TACProgram, Operand
from optiguard.ir.ir_generator import IRGenerator

__all__ = ["TACInstruction", "TACProgram", "Operand", "IRGenerator"]
