"""Three-Address Code (TAC) data structures for OptiGuard."""

from dataclasses import dataclass, field
from typing import List, Optional, Set, Union
import copy

Operand = Union[str, int, float]

@dataclass
class TACInstruction:
    """Represents a single Three-Address Code instruction (quadruple format).
    
    Standard forms:
      1. Binary Operation: result = arg1 op arg2 (op in '+', '-', '*', '/')
      2. Assignment / Copy: result = arg1 (op is None or '=')
    """
    op: Optional[str]        # '+', '-', '*', '/', or None
    arg1: Operand           # Variable name or constant literal
    arg2: Optional[Operand] # Variable name or constant literal (None for simple copy)
    result: str             # Destination variable name

    def is_copy(self) -> bool:
        return self.op is None or self.op == '='

    def is_binary(self) -> bool:
        return self.op in {'+', '-', '*', '/'}

    def get_uses(self) -> Set[str]:
        """Returns the set of variables read/used by this instruction."""
        uses = set()
        if isinstance(self.arg1, str) and not self._is_constant_str(self.arg1):
            uses.add(self.arg1)
        if self.arg2 is not None and isinstance(self.arg2, str) and not self._is_constant_str(self.arg2):
            uses.add(self.arg2)
        return uses

    def get_defs(self) -> Set[str]:
        """Returns the set of variables defined/written by this instruction."""
        if self.result:
            return {self.result}
        return set()

    @staticmethod
    def _is_constant_str(val: str) -> bool:
        try:
            float(val)
            return True
        except ValueError:
            return False

    def __str__(self) -> str:
        if self.is_copy():
            return f"{self.result} = {self.arg1}"
        return f"{self.result} = {self.arg1} {self.op} {self.arg2}"

    def __repr__(self) -> str:
        return f"TACInstruction({str(self)})"


@dataclass
class TACProgram:
    """Container for a sequential list of TAC instructions."""
    instructions: List[TACInstruction] = field(default_factory=list)

    def add(self, instr: TACInstruction):
        self.instructions.append(instr)

    def clone(self) -> 'TACProgram':
        """Creates a deep copy snapshot of the current IR state for safe rollback."""
        return copy.deepcopy(self)

    def size(self) -> int:
        return len(self.instructions)

    def dump(self) -> str:
        """Returns a string representation of the TAC program with line numbers."""
        lines = []
        for idx, instr in enumerate(self.instructions):
            lines.append(f"{idx:3d}:  {instr}")
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.dump()
