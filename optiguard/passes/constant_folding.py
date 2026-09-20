"""Constant Folding and Propagation Pass for OptiGuard."""

from typing import Tuple, Dict, Union
from optiguard.ir.tac import TACInstruction, TACProgram

class ConstantFoldingPass:
    """Pass 1: Folds compile-time constant arithmetic and propagates known constant values."""

    name = "ConstantFolding"

    def run(self, program: TACProgram) -> Tuple[TACProgram, bool]:
        modified = False
        new_program = TACProgram()
        # Symbol table mapping variable/temporary -> constant value (int or float)
        constants: Dict[str, Union[int, float]] = {}

        for instr in program.instructions:
            arg1 = instr.arg1
            arg2 = instr.arg2
            op = instr.op
            result = instr.result

            # 1. Constant Propagation on arg1
            if isinstance(arg1, str) and arg1 in constants:
                arg1 = constants[arg1]
                modified = True

            # 2. Constant Propagation on arg2
            if isinstance(arg2, str) and arg2 in constants:
                arg2 = constants[arg2]
                modified = True

            # 3. Constant Folding on binary operations with two numeric operands
            if op in {'+', '-', '*', '/'} and self._is_number(arg1) and self._is_number(arg2):
                num1 = self._to_number(arg1)
                num2 = self._to_number(arg2)
                folded_val = self._evaluate_binop(op, num1, num2)

                if folded_val is not None:
                    # Replace binary operation with direct assignment of folded constant
                    new_instr = TACInstruction(op=None, arg1=folded_val, arg2=None, result=result)
                    new_program.add(new_instr)
                    constants[result] = folded_val
                    modified = True
                    continue

            # 4. Handle copy assignment: result = arg1
            if (op is None or op == '=') and arg2 is None:
                if self._is_number(arg1):
                    constants[result] = self._to_number(arg1)
                elif isinstance(arg1, str) and arg1 in constants:
                    constants[result] = constants[arg1]
                elif result in constants:
                    del constants[result]
            else:
                # If result was previously a constant, it is now reassigned an unknown value
                if result in constants:
                    del constants[result]

            new_program.add(TACInstruction(op=op, arg1=arg1, arg2=arg2, result=result))

        return new_program, modified

    @staticmethod
    def _is_number(val) -> bool:
        if isinstance(val, (int, float)):
            return True
        if isinstance(val, str):
            try:
                float(val)
                return True
            except ValueError:
                return False
        return False

    @staticmethod
    def _to_number(val) -> Union[int, float]:
        if isinstance(val, (int, float)):
            return val
        f = float(val)
        return int(f) if f.is_integer() else f

    @staticmethod
    def _evaluate_binop(op: str, a: Union[int, float], b: Union[int, float]) -> Union[int, float, None]:
        try:
            if op == '+':
                res = a + b
            elif op == '-':
                res = a - b
            elif op == '*':
                res = a * b
            elif op == '/':
                if b == 0:
                    return None  # Do not fold divide by zero
                res = a / b
            else:
                return None
            return int(res) if isinstance(res, float) and res.is_integer() else res
        except Exception:
            return None
