from sympy.parsing.latex import parse_latex

expressions = [
    "( (10 + 5) \\times 2 ) / ( 10 - 4 )",
    "\\frac{200}{4}"
]

def eval_expression(expression: str):
    sympy_exp = parse_latex(expression)
    result = sympy_exp.evalf()

    print(str(sympy_exp), result)

[eval_expression(exp) for exp in expressions]
