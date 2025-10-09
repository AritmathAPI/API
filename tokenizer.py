import re
from typing import List, Tuple


class LexicalAnalyzer:
    """Lexical analyzer for arithmetic expressions using finite automaton principles."""

    def __init__(self):
        """Initialize the lexical analyzer with token definitions."""
        self.token_patterns = [
            ("NUMBER", r"\d+(\.\d+)?"),
            ("PLUS", r"\+"),
            ("MINUS", r"-"),
            ("MULTIPLY", r"\*"),
            ("DIVIDE", r"/"),
            ("LPAREN", r"\("),
            ("RPAREN", r"\)"),
            ("WHITESPACE", r"\s+"),
        ]

        self.token_regex = "|".join(
            f"(?P<{name}>{pattern})" for name, pattern in self.token_patterns
        )

        self.pattern = re.compile(self.token_regex)

    def tokenize(self, expression: str) -> List[Tuple[str, str]]:
        """
        Tokenize an arithmetic expression string.

        Args:
            expression (str): The arithmetic expression string

        Returns:
            List[Tuple[str, str]]: List of tokens as (value, type) tuples

        Raises:
            ValueError: If invalid characters are found in the expression
        """
        tokens = []
        position = 0

        while position < len(expression):
            match = self.pattern.match(expression, position)

            if match:
                token_type = match.lastgroup
                token_value = match.group(token_type)

                if token_type != "WHITESPACE":
                    tokens.append((token_value, token_type))

                position = match.end()
            else:
                invalid_char = expression[position]

                raise ValueError(
                    f"Invalid character '{invalid_char}' at position {position}"
                )

        return tokens

    def _is_number(self, char: str) -> bool:
        """Check if character is part of a number."""
        return char.isdigit() or char == "."

    def _is_operator(self, char: str) -> bool:
        """Check if character is an operator."""
        return char in "+-*/"

    def _is_parenthesis(self, char: str) -> bool:
        """Check if character is a parenthesis."""
        return char in "()"

    def _is_whitespace(self, char: str) -> bool:
        """Check if character is whitespace."""
        return char.isspace()

    def validate_tokens(self, tokens: List[Tuple[str, str]]) -> bool:
        """
        Validate the token sequence for basic syntactic correctness.

        Args:
            tokens (List[Tuple[str, str]]): List of tokens to validate

        Returns:
            bool: True if tokens are valid, False otherwise
        """
        if not tokens:
            return False

        prev_type = None
        paren_count = 0

        for value, token_type in tokens:
            if token_type == "LPAREN":
                paren_count += 1

            elif token_type == "RPAREN":
                paren_count -= 1
                if paren_count < 0:
                    return False

            if prev_type:
                if prev_type in ["PLUS", "MINUS", "MULTIPLY", "DIVIDE"]:
                    if token_type in ["PLUS", "MINUS", "MULTIPLY", "DIVIDE", "RPAREN"]:
                        return False

                if prev_type == "NUMBER" and token_type == "NUMBER":
                    return False

                if token_type == "LPAREN":
                    if prev_type not in [
                        "PLUS",
                        "MINUS",
                        "MULTIPLY",
                        "DIVIDE",
                        "LPAREN",
                    ]:
                        return False

            prev_type = token_type

        if paren_count != 0:
            return False

        if tokens[-1][1] in ["PLUS", "MINUS", "MULTIPLY", "DIVIDE"]:
            return False

        return True
