"""Algebraic Simplification Pass for OptiGuard."""

from typing import Tuple, Union
from optiguard.ir.tac import TACInstruction, TACProgram

class AlgebraicSimplificationPass:
    """Pass 2: Replaces algebraic identities with simpler forms (strength reduction and identity elimination).
    
    Identities handled:
      x + 0 -> x
      0 + x -> x
      x - 0 -> x
      x - x -> 0
      x * 1 -> x
      1 * x -> x
      x * 0 -> 0
      0 * x -> 0
      x / 1 -> x
    """

    name = "AlgebraicSimplification"

    def run(self, program: TACProgram) -> Tuple[TACProgram, bool]:
        modified = False
        new_program = TACProgram()

        for instr in program.instructions:
            if not instr.is_binary():
                new_program.add(instr)
                continue

            op = instr.op
            a1 = instr.arg1
            a2 = instr.arg2
            res = instr.result

            # Check for identities:
            # 1. Addition (+): x + 0 -> x, 0 + x -> x
            if op == '+':
                if self._is_zero(a2):
                    new_program.add(TACInstruction(op=None, arg1=a1, arg2=None, result=res))
                    modified = True
                    continue
                elif self._is_zero(a1):
                    new_program.add(TACInstruction(op=None, arg1=a2, arg2=None, result=res))
                    modified = True
                    continue

            # 2. Subtraction (-): x - 0 -> x, x - x -> 0
            elif op == '-':
                if self._is_zero(a2):
                    new_program.add(TACInstruction(op=None, arg1=a1, arg2=None, result=res))
                    modified = True
                    continue
                elif str(a1) == str(a2):
                    new_program.add(TACInstruction(op=None, arg1=0, arg2=None, result=res))
                    modified = True
                    continue

            # 3. Multiplication (*): x * 1 -> x, 1 * x -> x, x * 0 -> 0, 0 * x -> 0
            elif op == '*':
                if self._is_one(a2):
                    new_program.add(TACInstruction(op=None, arg1=a1, arg2=None, result=res))
                    modified = True
                    continue
                elif self._is_one(a1):
                    new_program.add(TACInstruction(op=None, arg1=a2, arg2=None, result=res))
                    modified = True
                    continue
                elif self._is_zero(a1) or self._is_zero(a2):
                    new_program.add(TACInstruction(op=None, arg1=0, arg2=None, result=res))
                    modified = True
                    continue

            # 4. Division (/): x / 1 -> x
            elif op == '/':
                if self._is_one(a2):
                    new_program.add(TACInstruction(op=None, arg1=a1, arg2=None, result=res))
                    modified = True
                    continue
                elif self._is_zero(a1) and not self._is_zero(a2):
                    new_program.add(TACInstruction(op=None, arg1=0, arg2=None, result=res))
                    modified = True
                    continue

            # No simplification applied
            new_program.add(instr)

        return new_program, modified

    @staticmethod
    def _is_zero(val: Union[str, int, float]) -> bool:
        if isinstance(val, (int, float)):
            return val == 0
        if isinstance(val, str):
            try:
                return float(val) == 0
            except ValueError:
                return False
        return False

    @staticmethod
    def _is_one(val: Union[str, int, float]) -> bool:
        if isinstance(val, (int, float)):
            return val == 1
        if isinstance(val, str):
            try:
                return float(val) == 1
            except ValueError:
                return False
        return False
