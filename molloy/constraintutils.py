""" Helper constainers and exceptions that are
used by the Constraint classes defined in other
files in this directory.
"""
import ast
import operator

ast_ordering_ops = (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)
ast_contains_ops = (ast.In, ast.NotIn)

ast_op_to_operator = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}


class ConstraintError(ValueError):
    pass
