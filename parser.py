from typing import List, Tuple, Union, Optional
from dataclasses import dataclass
import math


@dataclass
class ASTNode:
    """Abstract Syntax Tree node for arithmetic expressions."""

    value: Union[str, float]
    left: Optional["ASTNode"] = None
    right: Optional["ASTNode"] = None
    node_type: str = ""


class SyntacticAnalyzer:
    """Recursive descent parser for arithmetic expressions with AST construction."""

    def __init__(self, tokens: List[Tuple[str, str]]):
        """
        Initialize the parser with tokens.

        Args:
            tokens (List[Tuple[str, str]]): List of tokens from lexical analyzer
        """
        self.tokens = tokens
        self.current_token_index = 0
        self.steps: List[str] = []

    def current_token(self) -> Optional[Tuple[str, str]]:
        """Get the current token."""
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None

    def consume(self, expected_type: Optional[str] = None) -> Tuple[str, str]:
        """
        Consume the current token and move to the next.

        Args:
            expected_type (str): Expected token type for validation

        Returns:
            Tuple[str, str]: The consumed token

        Raises:
            SyntaxError: If token doesn't match expected type
        """
        if self.current_token_index >= len(self.tokens):
            raise SyntaxError("Unexpected end of expression")

        token = self.tokens[self.current_token_index]
        if expected_type and token[1] != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {token[1]}")

        self.current_token_index += 1
        return token

    def peek(self) -> Optional[Tuple[str, str]]:
        """Peek at the next token without consuming it."""
        if self.current_token_index < len(self.tokens) - 1:
            return self.tokens[self.current_token_index + 1]
        return None

    def parse(self) -> ASTNode:
        """
        Parse the expression and build the AST.

        Returns:
            ASTNode: Root node of the AST

        Raises:
            SyntaxError: If expression is invalid
        """
        self.current_token_index = 0
        self.steps = []
        return self._expression()

    def _expression(self) -> ASTNode:
        """Parse an expression (addition and subtraction)."""
        node = self._term()

        while self.current_token() and self.current_token()[1] in ["PLUS", "MINUS"]:
            token = self.consume()
            right = self._term()
            node = ASTNode(token[0], node, right, "BINARY_OP")

        return node

    def _term(self) -> ASTNode:
        """Parse a term (multiplication and division)."""
        node = self._factor()

        while self.current_token() and self.current_token()[1] in [
            "MULTIPLY",
            "DIVIDE",
        ]:
            token = self.consume()
            right = self._factor()
            node = ASTNode(token[0], node, right, "BINARY_OP")

        return node

    def _factor(self) -> ASTNode:
        """Parse a factor (numbers and parentheses)."""
        token = self.current_token()

        if not token:
            raise SyntaxError("Unexpected end of expression")

        if token[1] == "NUMBER":
            return ASTNode(float(token[0]), node_type="NUMBER")

        elif token[1] == "LPAREN":
            self.consume("LPAREN")
            node = self._expression()
            self.consume("RPAREN")
            return node

        elif token[1] in ["PLUS", "MINUS"]:
            token = self.consume()
            operand = self._factor()
            return ASTNode(token[0], None, operand, "UNARY_OP")

        else:
            raise SyntaxError(f"Unexpected token: {token[0]}")

    def evaluate(self, node: Optional[ASTNode] = None) -> float:
        """
        Evaluate the AST to compute the final result.

        Args:
            node (ASTNode): Root node of AST (if None, parses first)

        Returns:
            float: Final numerical result

        Raises:
            ValueError: For division by zero or other evaluation errors
        """
        if node is None:
            node = self.parse()

        return self._evaluate_node(node)

    def _evaluate_node(self, node: ASTNode) -> float:
        """Recursively evaluate an AST node."""
        if node.node_type == "NUMBER":
            return node.value

        elif node.node_type == "UNARY_OP":
            operand = self._evaluate_node(node.right)
            if node.value == "+":
                return operand
            else:  # '-'
                return -operand

        elif node.node_type == "BINARY_OP":
            left_val = self._evaluate_node(node.left)
            right_val = self._evaluate_node(node.right)

            if node.value == "+":
                result = left_val + right_val
            elif node.value == "-":
                result = left_val - right_val
            elif node.value == "*":
                result = left_val * right_val
            elif node.value == "/":
                if right_val == 0:
                    raise ValueError("Division by zero")
                result = left_val / right_val
            else:
                raise ValueError(f"Unknown operator: {node.value}")

            return result

        else:
            raise ValueError("Unknown node type")

    def solve_step_by_step(self, node: Optional[ASTNode] = None) -> List[str]:
        """
        Generate step-by-step solution with intermediate results.

        Args:
            node (ASTNode): Root node of AST (if None, parses first)

        Returns:
            List[str]: List of step descriptions
        """
        if node is None:
            node = self.parse()

        self.steps = []
        self._solve_with_steps(node)
        return self.steps

    def _solve_with_steps(self, node: ASTNode) -> float:
        """Recursively solve with step tracking."""
        if node.node_type == "NUMBER":
            return node.value

        elif node.node_type == "UNARY_OP":
            operand = self._solve_with_steps(node.right)
            result = operand if node.value == "+" else -operand
            self.steps.append(f"{node.value}{operand} = {result}")
            return result

        elif node.node_type == "BINARY_OP":
            left_val = self._solve_with_steps(node.left)
            right_val = self._solve_with_steps(node.right)

            # Format the operation for display
            left_str = (
                f"{left_val:.1f}" if isinstance(left_val, float) else str(left_val)
            )
            right_str = (
                f"{right_val:.1f}" if isinstance(right_val, float) else str(right_val)
            )

            if node.value == "+":
                result = left_val + right_val
                step = f"{left_str} + {right_str} = {result:.1f}"
            elif node.value == "-":
                result = left_val - right_val
                step = f"{left_str} - {right_str} = {result:.1f}"
            elif node.value == "*":
                result = left_val * right_val
                step = f"{left_str} * {right_str} = {result:.1f}"
            elif node.value == "/":
                if right_val == 0:
                    raise ValueError("Division by zero")
                result = left_val / right_val
                step = f"{left_str} / {right_str} = {result:.1f}"
            else:
                raise ValueError(f"Unknown operator: {node.value}")

            self.steps.append(step)
            return result

        else:
            raise ValueError("Unknown node type")

    def to_string(self, node: Optional[ASTNode] = None) -> str:
        """
        Convert AST back to expression string.

        Args:
            node (ASTNode): Root node of AST (if None, uses parsed AST)

        Returns:
            str: Expression string
        """
        if node is None:
            node = self.parse()

        return self._node_to_string(node)

    def _node_to_string(self, node: ASTNode) -> str:
        """Recursively convert node to string."""
        if node.node_type == "NUMBER":
            return str(node.value)

        elif node.node_type == "UNARY_OP":
            return f"{node.value}{self._node_to_string(node.right)}"

        elif node.node_type == "BINARY_OP":
            left_str = self._node_to_string(node.left)
            right_str = self._node_to_string(node.right)
            return f"({left_str} {node.value} {right_str})"

        else:
            return "?"
