"""Lexer (Tokenizer) for OptiGuard C-like language."""

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import List

class TokenType(Enum):
    NUMBER = auto()
    IDENTIFIER = auto()
    ASSIGN = auto()      # '='
    PLUS = auto()        # '+'
    MINUS = auto()       # '-'
    MUL = auto()         # '*'
    DIV = auto()         # '/'
    LPAREN = auto()      # '('
    RPAREN = auto()      # ')'
    SEMICOLON = auto()   # ';'
    EOF = auto()

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', line={self.line}, col={self.column})"

class LexerError(Exception):
    pass

class Lexer:
    """Scans raw source text into a stream of Tokens."""

    def __init__(self, source_code: str):
        self.source = source_code
        self.length = len(source_code)
        self.pos = 0
        self.line = 1
        self.col = 1

    def _peek(self) -> str:
        if self.pos < self.length:
            return self.source[self.pos]
        return ""

    def _advance(self) -> str:
        ch = self._peek()
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []

        while self.pos < self.length:
            ch = self._peek()

            # Skip whitespace
            if ch.isspace():
                self._advance()
                continue

            # Skip single-line comments // ...
            if ch == '/' and self.pos + 1 < self.length and self.source[self.pos + 1] == '/':
                while self.pos < self.length and self._peek() != '\n':
                    self._advance()
                continue

            start_col = self.col
            start_line = self.line

            # Numbers
            if ch.isdigit():
                num_str = ""
                while self.pos < self.length and (self._peek().isdigit() or self._peek() == '.'):
                    num_str += self._advance()
                tokens.append(Token(TokenType.NUMBER, num_str, start_line, start_col))
                continue

            # Identifiers and keywords
            if ch.isalpha() or ch == '_':
                ident_str = ""
                while self.pos < self.length and (self._peek().isalnum() or self._peek() == '_'):
                    ident_str += self._advance()
                tokens.append(Token(TokenType.IDENTIFIER, ident_str, start_line, start_col))
                continue

            # Single-character tokens
            if ch == '=':
                self._advance()
                tokens.append(Token(TokenType.ASSIGN, "=", start_line, start_col))
            elif ch == '+':
                self._advance()
                tokens.append(Token(TokenType.PLUS, "+", start_line, start_col))
            elif ch == '-':
                self._advance()
                tokens.append(Token(TokenType.MINUS, "-", start_line, start_col))
            elif ch == '*':
                self._advance()
                tokens.append(Token(TokenType.MUL, "*", start_line, start_col))
            elif ch == '/':
                self._advance()
                tokens.append(Token(TokenType.DIV, "/", start_line, start_col))
            elif ch == '(':
                self._advance()
                tokens.append(Token(TokenType.LPAREN, "(", start_line, start_col))
            elif ch == ')':
                self._advance()
                tokens.append(Token(TokenType.RPAREN, ")", start_line, start_col))
            elif ch == ';':
                self._advance()
                tokens.append(Token(TokenType.SEMICOLON, ";", start_line, start_col))
            else:
                raise LexerError(f"Unexpected character '{ch}' at line {start_line}, column {start_col}")

        tokens.append(Token(TokenType.EOF, "", self.line, self.col))
        return tokens
