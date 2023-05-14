from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.sympy_parser import standard_transformations, convert_xor,\
                                       implicit_multiplication_application


class MathSolver:
    def __init__(self) -> None:
        self.transformations = (standard_transformations +
                               (implicit_multiplication_application, convert_xor))
        
    def solve(self, expression: str, return_str: bool = True) -> str:
        var = ''
        if '=' in expression: 
            var, expression = expression.split('=')
        try:
            result = parse_expr(expression, transformations=self.transformations)
        except Exception as exc: 
            return 'ERROR'
        if return_str:
            return f"{var + ' = ' if var else ''}{str(result)}"
        else:
            return result