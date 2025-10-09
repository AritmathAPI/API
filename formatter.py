import re
from typing import List, Tuple


class FormatConverter:
    """Converter for arithmetic expressions to LaTeX and MathML formats."""

    @staticmethod
    def to_latex(expression: str) -> str:
        """
        Convert arithmetic expression string to LaTeX format.

        Args:
            expression (str): Normalized arithmetic expression string

        Returns:
            str: Expression in LaTeX format
        """
        # Tokenize the expression for better conversion
        tokens = FormatConverter._tokenize_expression(expression)

        latex_parts = []
        for token in tokens:
            if token in ["+", "-"]:
                latex_parts.append(f" {token} ")
            elif token == "*":
                latex_parts.append(r" \times ")
            elif token == "/":
                latex_parts.append(r" \div ")
            elif token == "(":
                latex_parts.append(r"\left(")
            elif token == ")":
                latex_parts.append(r"\right)")
            else:
                # Handle numbers (integers and floats)
                if "." in token:
                    # Format float with proper decimal separator
                    latex_parts.append(token.replace(".", "{,}"))
                else:
                    latex_parts.append(token)

        latex_expression = "".join(latex_parts).strip()
        return f"${latex_expression}$"

    @staticmethod
    def to_mathml(expression: str) -> str:
        """
        Convert arithmetic expression string to Presentation MathML format.

        Args:
            expression (str): Normalized arithmetic expression string

        Returns:
            str: Expression in MathML format
        """
        tokens = FormatConverter._tokenize_expression(expression)

        mathml_parts = ["<math><mrow>"]

        for token in tokens:
            if token in ["+", "-", "*", "/"]:
                operator_symbol = {
                    "+": "<mo>+</mo>",
                    "-": "<mo>-</mo>",
                    "*": "<mo>×</mo>",
                    "/": "<mo>÷</mo>",
                }[token]
                mathml_parts.append(operator_symbol)
            elif token == "(":
                mathml_parts.append("<mo>(</mo>")
            elif token == ")":
                mathml_parts.append("<mo>)</mo>")
            else:
                # Handle numbers
                if "." in token:
                    # Float number with decimal point
                    integer_part, decimal_part = token.split(".")
                    mathml_parts.append(f"<mn>{integer_part}</mn>")
                    mathml_parts.append("<mo>.</mo>")
                    mathml_parts.append(f"<mn>{decimal_part}</mn>")
                else:
                    mathml_parts.append(f"<mn>{token}</mn>")

        mathml_parts.append("</mrow></math>")
        return "".join(mathml_parts)

    @staticmethod
    def _tokenize_expression(expression: str) -> List[str]:
        """
        Tokenize expression into operators, numbers, and parentheses.

        Args:
            expression (str): Arithmetic expression string

        Returns:
            List[str]: List of tokens
        """
        # Remove all whitespace first
        expression = re.sub(r"\s+", "", expression)

        tokens = []
        current_number = ""

        for char in expression:
            if char in "+-*/()":
                # If we were building a number, add it first
                if current_number:
                    tokens.append(current_number)
                    current_number = ""
                tokens.append(char)
            else:
                # Part of a number
                current_number += char

        # Add the last number if exists
        if current_number:
            tokens.append(current_number)

        return tokens

    @staticmethod
    def expression_to_readable(expression: str) -> str:
        """
        Convert normalized expression to human-readable format.

        Args:
            expression (str): Normalized arithmetic expression

        Returns:
            str: Human-readable expression
        """
        readable = expression.replace("*", "×").replace("/", "÷")
        return readable

    @staticmethod
    def format_step(step: str) -> str:
        """
        Format a calculation step for display.

        Args:
            step (str): Raw step string from parser

        Returns:
            str: Formatted step with proper symbols
        """
        # Replace operator symbols for better readability
        formatted = step.replace("*", "×").replace("/", "÷")
        return formatted
