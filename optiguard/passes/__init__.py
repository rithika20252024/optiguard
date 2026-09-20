"""Optimization passes package for OptiGuard."""

from optiguard.passes.constant_folding import ConstantFoldingPass
from optiguard.passes.algebraic_simplification import AlgebraicSimplificationPass
from optiguard.passes.dead_code_elimination import DeadCodeEliminationPass

__all__ = [
    "ConstantFoldingPass",
    "AlgebraicSimplificationPass",
    "DeadCodeEliminationPass"
]
