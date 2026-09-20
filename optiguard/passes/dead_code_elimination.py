"""Dead Code Elimination (DCE) Pass for OptiGuard."""

from typing import Tuple, Set, List
from optiguard.ir.tac import TACInstruction, TACProgram

class DeadCodeEliminationPass:
    """Pass 3: Eliminates dead and unreferenced instructions using backward liveness analysis."""

    name = "DeadCodeElimination"

    def run(self, program: TACProgram) -> Tuple[TACProgram, bool]:
        current_prog = program
        any_modified = False

        # Run iteratively until fixed point is reached
        while True:
            new_prog, modified = self._run_single_pass(current_prog)
            if not modified:
                break
            any_modified = True
            current_prog = new_prog

        return current_prog, any_modified

    def _run_single_pass(self, program: TACProgram) -> Tuple[TACProgram, bool]:
        instructions = program.instructions
        if not instructions:
            return program, False

        # Identify all user-defined variables (non-temporaries)
        # By default, the last assignment to any user variable is considered live (program output).
        user_vars = set()
        for instr in instructions:
            for v in instr.get_defs() | instr.get_uses():
                if not self._is_temporary(v):
                    user_vars.add(v)

        # Variables that are live at the current analysis point
        # Initially, all user variables are considered live at the exit of the program.
        live_variables: Set[str] = set(user_vars)

        surviving_instructions: List[TACInstruction] = []
        modified = False

        # Process instructions in reverse order (backward liveness analysis)
        for instr in reversed(instructions):
            result = instr.result
            defs = instr.get_defs()
            uses = instr.get_uses()

            is_dead = False
            # An instruction is dead if its result is a temporary that is never used downstream
            if self._is_temporary(result) and result not in live_variables:
                is_dead = True
            # Also dead if an assignment targets a variable that is immediately overwritten without being read
            elif result not in live_variables and not self._is_critical(result, user_vars):
                is_dead = True

            if is_dead:
                modified = True
                # Skip this instruction (eliminate it)
                continue

            # If instruction survives:
            surviving_instructions.append(instr)

            # Update live variables:
            # Result is defined here, so it is killed before this point
            live_variables.discard(result)
            # Operands are used here, so they become live before this point
            live_variables.update(uses)

        surviving_instructions.reverse()
        result_prog = TACProgram(instructions=surviving_instructions)
        return result_prog, modified

    @staticmethod
    def _is_temporary(var_name: str) -> bool:
        """Returns True if the variable is a compiler-generated temporary (e.g., t0, t1)."""
        if not var_name or not isinstance(var_name, str):
            return False
        return var_name.startswith('t') and var_name[1:].isdigit()

    @staticmethod
    def _is_critical(var_name: str, user_vars: Set[str]) -> bool:
        """Variables that represent primary program outputs are considered critical."""
        return var_name in user_vars
