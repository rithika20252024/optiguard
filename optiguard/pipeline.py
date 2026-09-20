"""Optimization Pipeline Driver for OptiGuard."""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from optiguard.frontend.lexer import Lexer
from optiguard.frontend.parser import Parser
from optiguard.ir.ir_generator import IRGenerator
from optiguard.ir.tac import TACProgram
from optiguard.passes.constant_folding import ConstantFoldingPass
from optiguard.passes.algebraic_simplification import AlgebraicSimplificationPass
from optiguard.passes.dead_code_elimination import DeadCodeEliminationPass
from optiguard.metrics.cost_evaluator import CostEvaluator, IRMetrics

@dataclass
class PassStepRecord:
    pass_name: str
    modified: bool
    metrics_after: IRMetrics
    tac_snapshot: TACProgram

@dataclass
class OptimizationResult:
    source_code: str
    initial_tac: TACProgram
    initial_metrics: IRMetrics
    final_tac: TACProgram
    final_metrics: IRMetrics
    steps: List[PassStepRecord] = field(default_factory=list)
    improvement_summary: Dict[str, Any] = field(default_factory=dict)

class OptiGuardPipeline:
    """Manages compilation frontend, optimization pass execution, and metrics evaluation."""

    def __init__(self):
        self.passes = [
            ConstantFoldingPass(),
            AlgebraicSimplificationPass(),
            DeadCodeEliminationPass()
        ]

    def compile_source(self, source_code: str) -> TACProgram:
        """Runs Frontend: Lexer -> Parser -> AST -> TAC Generation."""
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        ir_gen = IRGenerator()
        return ir_gen.generate(ast)

    def optimize(self, source_code: str) -> OptimizationResult:
        """Executes full optimization pipeline and records intermediate metrics."""
        initial_tac = self.compile_source(source_code)
        initial_metrics = CostEvaluator.evaluate(initial_tac)

        current_tac = initial_tac.clone()
        step_records: List[PassStepRecord] = []

        # Sequential Pass Execution with state tracking
        for opt_pass in self.passes:
            next_tac, modified = opt_pass.run(current_tac)
            metrics = CostEvaluator.evaluate(next_tac)
            step_records.append(PassStepRecord(
                pass_name=opt_pass.name,
                modified=modified,
                metrics_after=metrics,
                tac_snapshot=next_tac.clone()
            ))
            current_tac = next_tac

        final_metrics = CostEvaluator.evaluate(current_tac)
        summary = CostEvaluator.calculate_improvement(initial_metrics, final_metrics)

        return OptimizationResult(
            source_code=source_code,
            initial_tac=initial_tac,
            initial_metrics=initial_metrics,
            final_tac=current_tac,
            final_metrics=final_metrics,
            steps=step_records,
            improvement_summary=summary
        )
