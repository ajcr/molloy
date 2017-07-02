import ast
from functools import reduce

import numpy as np

from .constraintutils import *


class BaseConstraintHandler(object):
    """This class is the parent class for more specific
    constraint handlers that define the methods to build
    polynomials depending on the type of generating
    function that is needed.

    It contains utility functions for creating/modifying
    polynomials and processing operations from the AST.
    """

    def _multiply_polynomials(self):
        return reduce(np.convolve, self.polynomials.values())

    def _modify_polynomials_using_contraints(self):
        expr = self.tree.body[0].value

        if isinstance(expr, ast.Compare):
            self._handle_compare_op(expr)

        elif isinstance(expr, ast.BoolOp):
            if isinstance(expr.op, ast.Or):
                raise NotImplementedError('Disjunction is not yet supported')
            for operation in expr.values:
                if isinstance(operation, ast.Compare):
                    self._handle_compare_op(operation)
                else:
                    raise ConstraintError('Constraint not understood')

        else:
            raise ConstraintError('Contraint string must be a boolean expression'
                    ' or a single boolean comparison')

    def _handle_compare_op(self, operation):
        """Process the compare operations in the AST.
        Currently supports comparisons using the operators
        ==, !=, <, <=, >, >= that take either of the forms:

            item < num
            num < item

        or comparisons using in:

            item in (3, 5, 7)
            item not in [1, 2, 4, 8]

        or comparisons where the left-hand side is a binary
        modulo operation, such as:

            item % mod == rem

        Chained operations (e.g. '3 < item <= 27') are not
        currently supported.
        """
        if len(operation.ops) > 1:
            raise NotImplementedError('Operator chaining is not yet supported')

        op = operation.ops[0]

        if isinstance(op, ast_ordering_ops):
            try:
                # compare is of form 'item < num'
                item, num = operation.left.id, operation.comparators[0].n
            except (AttributeError, TypeError):
                # fall through and try the next format
                pass
            else:
                return self._handle_order_op(op, item, num)

            try:
                # compare is of form 'num < item'
                item, num = operation.left.n, operation.comparators[0].id
            except (AttributeError, TypeError):
                # fall through and try the next format
                pass
            else:
                return self._handle_order_op(op, item, num)

            try:
                # compare is of form 'item % mod == rem'
                # note: rem must be a number, not a list/tuple/set
                assert isinstance(operation.left.op, ast.Mod)
                item = operation.left.left.id
                mod = operation.left.right.n
                op = operation.ops[0]
                rem = operation.comparators[0].n
            except (AttributeError, TypeError, AssertionError):
                raise ConstraintError('Constraint not understood')
            else:
                return self._constraint_modulo(item, mod, op, rem)

        elif isinstance(op, ast_contains_ops):
            try:
                # compare is of form 'item in (3, 5, 7)' or
                # 'item not in (3, 5, 7)'
                item = operation.left.id
                nums = [num.n for num in operation.comparators[0].elts]
            except (AttributeError, TypeError):
                raise ConstraintError('Constraint not understood')
            else:
                return self._constraint_contains(item, op, nums)

        else:
            raise ConstraintError('Constraint not understood')

