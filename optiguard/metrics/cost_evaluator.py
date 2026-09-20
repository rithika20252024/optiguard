"""Metrics and Cost Evaluation Module for OptiGuard."""

from dataclasses import dataclass
from typing import Dict, Set
from optiguard.ir.tac import TACProgram

# Hardware cycle weight model for typical RISC/x86 ALU operations
CYCLE_WEIGHTS: Dict[str, int] = {
    '+': 1,
    '-': 1,
    '*': 3,
    '/': 8,
    'copy': 1,
}

@dataclass
class IRMetrics:
    instruction_count: int
    distinct_variables: int
    temporary_count: int
    estimated_cycle_cost: int

    def __str__(self) -> str:
        return (
            f"Instructions: {self.instruction_count} | "
            f"Variables: {self.distinct_variables} (Temps: {self.temporary_count}) | "
            f"Est. Cycles: {self.estimated_cycle_cost}"
        )


class CostEvaluator:
    """Evaluates quantitative metrics on Three-Address Code programs."""

    @classmethod
    def evaluate(cls, program: TACProgram) -> IRMetrics:
        inst_count = len(program.instructions)
        all_vars: Set[str] = set()
        temps: Set[str] = set()
        total_cycles = 0

        for instr in program.instructions:
            for v in instr.get_defs() | instr.get_uses():
                all_vars.add(v)
                if v.startswith('t') and v[1:].isdigit():
                    temps.add(v)

            if instr.is_binary():
                op_cost = CYCLE_WEIGHTS.get(instr.op, 1)
            else:
                op_cost = CYCLE_WEIGHTS.get('copy', 1)

            total_cycles += op_cost

        return IRMetrics(
            instruction_count=inst_count,
            distinct_variables=len(all_vars),
            temporary_count=len(temps),
            estimated_cycle_cost=total_cycles
        )

    @classmethod
    def calculate_improvement(cls, before: IRMetrics, after: IRMetrics) -> Dict[str, float]:
        """Calculates percentage improvements between before and after states."""
        if before.instruction_count == 0:
            inst_reduction = 0.0
        else:
            inst_reduction = ((before.instruction_count - after.instruction_count) / before.instruction_count) * 100.0

        if before.estimated_cycle_cost == 0:
            cycle_reduction = 0.0
        else:
            cycle_reduction = ((before.estimated_cycle_cost - after.estimated_cycle_cost) / before.estimated_cycle_cost) * 100.0

        return {
            "instruction_reduction_pct": round(inst_reduction, 2),
            "cycle_reduction_pct": round(cycle_reduction, 2),
            "instructions_saved": before.instruction_count - after.instruction_count,
            "cycles_saved": before.estimated_cycle_cost - after.estimated_cycle_cost
        }
