"""IR Generator: Lowers AST to Three-Address Code (TAC)."""

from typing import Union
from optiguard.frontend.ast_nodes import (
    ASTNode, ProgramNode, AssignNode, BinaryOpNode, NumberNode, VariableNode
)
from optiguard.ir.tac import TACInstruction, TACProgram, Operand

class IRGenerator:
    """Visits the AST and generates Three-Address Code instructions."""

    def __init__(self):
        self.temp_counter = 0
        self.program = TACProgram()

    def new_temp(self) -> str:
        name = f"t{self.temp_counter}"
        self.temp_counter += 1
        return name

    def generate(self, ast: ProgramNode) -> TACProgram:
        self.temp_counter = 0
        self.program = TACProgram()

        for stmt in ast.statements:
            self._visit(stmt)

        return self.program

    def _visit(self, node: ASTNode) -> Operand:
        if isinstance(node, AssignNode):
            return self._visit_assign(node)
        elif isinstance(node, BinaryOpNode):
            return self._visit_binop(node)
        elif isinstance(node, NumberNode):
            return node.value
        elif isinstance(node, VariableNode):
            return node.name
        else:
            raise NotImplementedError(f"Unhandled AST node type: {type(node).__name__}")

    def _visit_assign(self, node: AssignNode) -> Operand:
        if isinstance(node.expression, BinaryOpNode):
            # Evaluate binary op into a temporary first, then assign to target
            temp_res = self._visit_binop(node.expression)
            self.program.add(TACInstruction(op=None, arg1=temp_res, arg2=None, result=node.target))
            return node.target
        elif isinstance(node.expression, (NumberNode, VariableNode)):
            val = self._visit(node.expression)
            self.program.add(TACInstruction(op=None, arg1=val, arg2=None, result=node.target))
            return node.target
        else:
            val = self._visit(node.expression)
            self.program.add(TACInstruction(op=None, arg1=val, arg2=None, result=node.target))
            return node.target

    def _visit_binop(self, node: BinaryOpNode) -> str:
        left_op = self._visit(node.left)
        right_op = self._visit(node.right)
        temp = self.new_temp()
        self.program.add(TACInstruction(op=node.operator, arg1=left_op, arg2=right_op, result=temp))
        return temp
