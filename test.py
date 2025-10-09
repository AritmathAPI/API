from sympy.parsing.latex import parse_latex

expression = "(\sqrt{57-2})^{7}"
sympy_exp = parse_latex(expression)
result = sympy_exp.evalf()

print(expression, result)
