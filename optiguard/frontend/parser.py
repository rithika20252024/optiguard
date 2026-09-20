"""Recursive descent parser for OptiGuard language frontend."""

from typing import List
from optiguard.frontend.lexer import Token, TokenType
from optiguard.frontend.ast_nodes import (
    ASTNode, ProgramNode, AssignNode, BinaryOpNode, NumberNode, VariableNode
)

class ParserError(Exception):
    pass

class Parser:
    """Parses a stream of tokens into an Abstract Syntax Tree (AST)."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def _peek(self) -> Token:
        return self.tokens[self.pos]

    def _match(self, token_type: TokenType) -> bool:
        return self._peek().type == token_type

    def _consume(self, token_type: TokenType, err_msg: str = "") -> Token:
        tok = self._peek()
        if tok.type != token_type:
            msg = err_msg or f"Expected {token_type.name} but got {tok.type.name} at line {tok.line}, col {tok.column}"
            raise ParserError(msg)
        self.pos += 1
        return tok

    def parse(self) -> ProgramNode:
        """Entry point: parses the full program."""
        statements: List[ASTNode] = []
        while not self._match(TokenType.EOF):
            stmt = self._statement()
            if stmt:
                statements.append(stmt)
        return ProgramNode(statements=statements)

    def _statement(self) -> ASTNode:
        """Parses an assignment statement: identifier = expr ;"""
        ident_tok = self._consume(TokenType.IDENTIFIER, "Expected variable identifier in assignment statement")
        self._consume(TokenType.ASSIGN, "Expected '=' after variable identifier")
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' terminating assignment statement")
        return AssignNode(target=ident_tok.value, expression=expr, line=ident_tok.line)

    def _expression(self) -> ASTNode:
        """expression : term (('+' | '-') term)*"""
        node = self._term()
        while self._match(TokenType.PLUS) or self._match(TokenType.MINUS):
            op_tok = self._peek()
            self.pos += 1
            right = self._term()
            node = BinaryOpNode(operator=op_tok.value, left=node, right=right, line=op_tok.line)
        return node

    def _term(self) -> ASTNode:
        """term : factor (('*' | '/') factor)*"""
        node = self._factor()
        while self._match(TokenType.MUL) or self._match(TokenType.DIV):
            op_tok = self._peek()
            self.pos += 1
            right = self._factor()
            node = BinaryOpNode(operator=op_tok.value, left=node, right=right, line=op_tok.line)
        return node

    def _factor(self) -> ASTNode:
        """factor : NUMBER | IDENTIFIER | '(' expression ')' | ('-' factor)"""
        tok = self._peek()

        if self._match(TokenType.MINUS):
            self.pos += 1
            # Treat unary negation as 0 - factor
            operand = self._factor()
            return BinaryOpNode(operator="-", left=NumberNode(value=0, line=tok.line), right=operand, line=tok.line)

        if self._match(TokenType.NUMBER):
            self.pos += 1
            val = float(tok.value) if '.' in tok.value else int(tok.value)
            return NumberNode(value=val, line=tok.line)

        if self._match(TokenType.IDENTIFIER):
            self.pos += 1
            return VariableNode(name=tok.value, line=tok.line)

        if self._match(TokenType.LPAREN):
            self.pos += 1
            expr = self._expression()
            self._consume(TokenType.RPAREN, "Expected matching ')' after expression")
            return expr

        raise ParserError(f"Unexpected token '{tok.value}' ({tok.type.name}) at line {tok.line}, col {tok.column}")
