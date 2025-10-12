import copy
from typing import List, Tuple, Union, Optional, Dict
from dataclasses import dataclass


@dataclass
class ASTNode:
    """Abstract Syntax Tree node for arithmetic expressions."""

    value: Union[str, float]
    left: Optional["ASTNode"] = None
    right: Optional["ASTNode"] = None
    node_type: str = ""


def _format_number(num: float) -> str:
    """Formats a float as an int if it has no fractional part."""
    if num == int(num):
        return str(int(num))

    return f"{num:.10g}"


class SyntacticAnalyzer:
    PRECEDENCE: Dict[str, int] = {"+": 1, "-": 1, "*": 2, "/": 2}

    def __init__(self, tokens: List[Tuple[str, str]]):
        self.tokens = tokens
        self.current_token_index = 0
        self.steps: List[str] = []

    def consume(self, expected_type: Optional[str] = None) -> Tuple[str, str]:
        if self.current_token_index >= len(self.tokens):
            raise SyntaxError("Unexpected end of expression")

        token = self.tokens[self.current_token_index]
        if expected_type and token[1] != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {token[1]}")

        self.current_token_index += 1

        return token

    def current_token(self) -> Optional[Tuple[str, str]]:
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]

        return None

    def parse(self) -> ASTNode:
        self.current_token_index = 0
        self.steps = []

        return self._expression()

    def _expression(self) -> ASTNode:
        node = self._term()

        while self.current_token() and self.current_token()[1] in ["PLUS", "MINUS"]:
            token = self.consume()
            right = self._term()
            node = ASTNode(token[0], node, right, "BINARY_OP")

        return node

    def _term(self) -> ASTNode:
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
        token = self.current_token()
        if not token:
            raise SyntaxError("Unexpected end of expression")

        if token[1] == "NUMBER":
            consumed_token = self.consume("NUMBER")

            return ASTNode(float(consumed_token[0]), node_type="NUMBER")
        elif token[1] == "LPAREN":
            self.consume("LPAREN")
            node = self._expression()
            self.consume("RPAREN")

            return ASTNode("()", left=node, node_type="GROUP")
        elif token[1] in ["PLUS", "MINUS"]:
            token = self.consume()
            operand = self._factor()

            return ASTNode(token[0], None, operand, "UNARY_OP")
        else:
            raise SyntaxError(f"Unexpected token: {token[0]}")

    def evaluate(self, node: Optional[ASTNode] = None) -> float:
        if node is None:
            node = self.parse()

        return self._evaluate_node(node)

    def _evaluate_node(self, node: ASTNode) -> float:
        if node.node_type == "NUMBER":
            return node.value
        if node.node_type == "GROUP":
            return self._evaluate_node(node.left)
        if node.node_type == "UNARY_OP":
            return self._evaluate_node(node.right) * (-1 if node.value == "-" else 1)

        if node.node_type == "BINARY_OP":
            left = self._evaluate_node(node.left)
            right = self._evaluate_node(node.right)
            if node.value == "+":
                return left + right
            if node.value == "-":
                return left - right
            if node.value == "*":
                return left * right
            if node.value == "/":
                return left / right

        raise ValueError(f"Unknown node type: {node.node_type}")

    def solve_by_substitution(self) -> List[str]:
        root_node = self.parse()
        working_node = copy.deepcopy(root_node)
        self.steps = [self.to_string(working_node)]

        self._collapse_and_record_steps(working_node, working_node)

        return self.steps

    def _collapse_and_record_steps(
        self, current_node: ASTNode, root_for_string: ASTNode
    ):
        if current_node is None or current_node.node_type == "NUMBER":
            return

        if current_node.left:
            self._collapse_and_record_steps(current_node.left, root_for_string)
        if current_node.right:
            self._collapse_and_record_steps(current_node.right, root_for_string)

        if current_node.node_type in ("GROUP", "BINARY_OP", "UNARY_OP"):
            result = self._evaluate_node(current_node)

            current_node.node_type = "NUMBER"
            current_node.value = result
            current_node.left = None
            current_node.right = None

            new_step = self.to_string(root_for_string)
            if self.steps[-1] != new_step:
                self.steps.append(new_step)

    def to_string(self, node: Optional[ASTNode] = None) -> str:
        if node is None:
            node = self.parse()

        return self._node_to_string(node)

    def _node_to_string(self, node: ASTNode) -> str:
        if node.node_type == "NUMBER":
            return _format_number(node.value)
        if node.node_type == "GROUP":
            return f"({self._node_to_string(node.left)})"
        if node.node_type == "BINARY_OP":
            left_str = self._node_to_string(node.left)
            right_str = self._node_to_string(node.right)

            if (
                node.left.node_type == "BINARY_OP"
                and self.PRECEDENCE[node.left.value] < self.PRECEDENCE[node.value]
            ):
                left_str = f"({left_str})"
            if (
                node.right.node_type == "BINARY_OP"
                and self.PRECEDENCE[node.right.value] < self.PRECEDENCE[node.value]
            ):
                right_str = f"({right_str})"

            return f"{left_str} {node.value} {right_str}"
        if node.node_type == "UNARY_OP":
            operand_str = self._node_to_string(node.right)
            if node.value == "-":
                return f"-{operand_str}"
            else:
                return operand_str

        return "?"
