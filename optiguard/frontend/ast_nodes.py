"""AST nodes for OptiGuard language frontend."""

from dataclasses import dataclass
from typing import List, Optional, Union

@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    line: int = 1

@dataclass
class ProgramNode(ASTNode):
    """Represents a full program containing a list of statements."""
    statements: List[ASTNode] = None

    def __post_init__(self):
        if self.statements is None:
            self.statements = []

@dataclass
class NumberNode(ASTNode):
    """Represents a numeric constant literal (integer or float)."""
    value: Union[int, float] = 0

@dataclass
class VariableNode(ASTNode):
    """Represents a variable identifier."""
    name: str = ""

@dataclass
class BinaryOpNode(ASTNode):
    """Represents a binary arithmetic operation (left op right)."""
    operator: str = ""  # '+', '-', '*', '/'
    left: ASTNode = None
    right: ASTNode = None

@dataclass
class AssignNode(ASTNode):
    """Represents an assignment statement: target = expression;"""
    target: str = ""
    expression: ASTNode = None
