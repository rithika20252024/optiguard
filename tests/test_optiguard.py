"""Comprehensive Unit Tests for OptiGuard 25% Compiler Prototype."""

import unittest
from optiguard.frontend.lexer import Lexer, TokenType
from optiguard.frontend.parser import Parser
from optiguard.frontend.ast_nodes import ProgramNode, AssignNode, BinaryOpNode
from optiguard.ir.ir_generator import IRGenerator
from optiguard.passes.constant_folding import ConstantFoldingPass
from optiguard.passes.algebraic_simplification import AlgebraicSimplificationPass
from optiguard.passes.dead_code_elimination import DeadCodeEliminationPass
from optiguard.pipeline import OptiGuardPipeline
from optiguard.metrics.cost_evaluator import CostEvaluator

class TestOptiGuardFrontend(unittest.TestCase):
    def test_lexer_tokens(self):
        code = "a = 10 * 2;"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        types = [t.type for t in tokens]
        expected = [
            TokenType.IDENTIFIER,
            TokenType.ASSIGN,
            TokenType.NUMBER,
            TokenType.MUL,
            TokenType.NUMBER,
            TokenType.SEMICOLON,
            TokenType.EOF
        ]
        self.assertEqual(types, expected)
        self.assertEqual(tokens[0].value, "a")
        self.assertEqual(tokens[2].value, "10")

    def test_parser_ast(self):
        code = "a = b + 5;"
        tokens = Lexer(code).tokenize()
        ast = Parser(tokens).parse()
        self.assertIsInstance(ast, ProgramNode)
        self.assertEqual(len(ast.statements), 1)
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, AssignNode)
        self.assertEqual(stmt.target, "a")
        self.assertIsInstance(stmt.expression, BinaryOpNode)
        self.assertEqual(stmt.expression.operator, "+")

class TestOptiGuardPasses(unittest.TestCase):
    def setUp(self):
        self.pipeline = OptiGuardPipeline()

    def test_constant_folding(self):
        code = "a = 10 * 2;"
        tac = self.pipeline.compile_source(code)
        pass_cf = ConstantFoldingPass()
        opt_tac, modified = pass_cf.run(tac)
        self.assertTrue(modified)
        # Check that constant 20 is present
        folded_instrs = [i for i in opt_tac.instructions if i.arg1 == 20 or i.arg1 == '20']
        self.assertTrue(len(folded_instrs) > 0)

    def test_algebraic_simplification(self):
        code = "b = a + 0;"
        tac = self.pipeline.compile_source(code)
        pass_as = AlgebraicSimplificationPass()
        opt_tac, modified = pass_as.run(tac)
        self.assertTrue(modified)
        # Check that binary op '+' with 0 was simplified to copy
        plus_ops = [i for i in opt_tac.instructions if i.op == '+']
        self.assertEqual(len(plus_ops), 0)

    def test_dead_code_elimination(self):
        # t0 is a temporary that is overwritten or unreferenced
        code = """
t0 = 5 + 5;
a = 20;
"""
        tac = self.pipeline.compile_source(code)
        pass_dce = DeadCodeEliminationPass()
        opt_tac, modified = pass_dce.run(tac)
        self.assertTrue(modified)
        # t0 should be pruned because it's a dead temporary
        results = [i.result for i in opt_tac.instructions]
        self.assertNotIn("t0", results)
        self.assertIn("a", results)

    def test_end_to_end_canonical_spec(self):
        """Tests the exact canonical example from the project specification:
        Input:
          a = 10 * 2;
          b = a + 0;
          c = b;
        """
        code = """
a = 10 * 2;
b = a + 0;
c = b;
"""
        res = self.pipeline.optimize(code)
        self.assertGreater(res.initial_metrics.instruction_count, res.final_metrics.instruction_count)
        self.assertGreater(res.improvement_summary["instruction_reduction_pct"], 0.0)
        self.assertGreater(res.improvement_summary["cycle_reduction_pct"], 0.0)

if __name__ == "__main__":
    unittest.main()
