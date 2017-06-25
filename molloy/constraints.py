import ast
from functools import reduce
import operator

import numpy as np

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
    """Exception raised when the constraints
    are not able to be handled, or not able to
    be understood, by the program.
    """
    pass


class BaseConstraintHandler(object):
    """This class is the parent class for more specific
    constraint handlers that should define the
    methods to build polynomials depending on the type
    of generating function that is needed.

    It contains utility functions for creating/modifying
    polynomials and processing operations from the AST.
    """

    def _multiply_polynomials(self):
        return reduce(np.convolve, self.polynomials.values())

    def _modify_polynomials_using_contraints(self):
        expr = self.tree.body[0].value
        if not isinstance(expr, (ast.BoolOp, ast.Compare)):
            raise ConstraintError('Contraint string must be a boolean expression'
                    ' or a single boolean comparison')
        if isinstance(expr.op, ast.Or):
            raise NotImplementedError('Disjunction is not yet supported')

        for operation in expr.values:
            if isinstance(operation, ast.Compare):
                self._handle_compare_op(operation)
            else:
                raise ConstraintError('Constraint not understood')

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
                # compare is of form 'item in (3, 5, 7)'
                item = operation.left.id
                nums = [num.n for num in operation.comparators[0].elts]
            except (AttributeError, TypeError):
                raise ConstraintError('Constraint not understood')
            else:
                return self._constraint_contains(item, op, nums)

        else:
            raise ConstraintError('Constraint not understood')


class SetConstraintHandler(BaseConstraintHandler):
    """Parse string specifying contraints build
    the AST and then dispatch to functions to
    make and modify a polynomial for each item.
    """
    def __init__(self, constraint_string, items, max_degree):
        self.max_degree = max_degree
        self.polynomials = self._init_polynomials_from_items(items)

        if constraint_string:
            self.tree = ast.parse(constraint_string)
            self._modify_polynomials_using_contraints()

        self.power_series = self._multiply_polynomials()

    @property
    def solution(self):
        return self.power_series[self.max_degree]

    @staticmethod
    def _init_polynomials_from_items(items):
        return {item: np.ones(count+1, dtype=np.int_) for item, count in items.items()}

    def _add_missing_polynomial(self, item):
        self.polynomials[item] = np.ones(self.max_degree + 1, dtype=np.int_)

    # When modifying polynomials for an item, we have to
    # make sure that constraints on the same item are
    # applied correctly. For example we should have:
    #
    #     [1, 1, 1, 1, 1, 1] -> initial polynomial
    #     [1, 1, 1, 0, 0, 1] -> item not in [3, 4]
    #     [1, 1, 0, 0, 0, 0] -> item < 2
    #     [0, 1, 0, 0, 0, 0] -> item != 0
    #
    # The result should be the same regardless of the
    # order the constraints were applied.
    #
    # One way to achieve this is to create a temporary
    # array each for each constraint and then '&=' the
    # temporary array with the main polynomial. This
    # approach is implemented below.

    # TODO: remove boilerplate in the methods below and
    # possibly find a better way to dispatch on type.

    def _handle_order_op(self, op, item, num):
        op_to_method = {
            ast.Eq: self._constraint_eq,
            ast.NotEq: self._constraint_noteq,
            ast.Gt: self._constraint_gt,
            ast.GtE: self._constraint_gte,
            ast.Lt: self._constraint_lt,
            ast.LtE: self._constraint_lte,
        }
        return op_to_method[type(op)](item, num)

    def _constraint_eq(self, item, num):
        # set all coefficients except num to 0
        try:
            array = np.ones_like(self.polynomials[item])
        except KeyError:
            self._add_missing_polynomial(item)
            array = np.ones_like(self.polynomials[item])

        array[num] = 0
        self.polynomials[item] &= (1 - array)

    def _constraint_noteq(self, item, num):
        # set coefficient num to 0
        try:
            array = np.ones_like(self.polynomials[item])
        except KeyError:
            self._add_missing_polynomial(item)
            array = np.ones_like(self.polynomials[item])

        array[num] = 0
        self.polynomials[item] &= array

    def _constraint_gt(self, item, num):
        # set coefficients up to and including num to 0
        try:
            array = np.ones_like(self.polynomials[item])
        except KeyError:
            self._add_missing_polynomial(item)
            array = np.ones_like(self.polynomials[item])

        array[:num+1] = 0
        self.polynomials[item] &= array

    def _constraint_gte(self, item, num):
        # set coefficients up to num to 0
        try:
            array = np.ones_like(self.polynomials[item])
        except KeyError:
            self._add_missing_polynomial(item)
            array = np.ones_like(self.polynomials[item])

        array[:num] = 0
        self.polynomials[item] &= array

    def _constraint_lt(self, item, num):
        # set coefficients at num and above to 0
        try:
            array = np.ones_like(self.polynomials[item])
        except KeyError:
            self._add_missing_polynomial(item)
            array = np.ones_like(self.polynomials[item])

        array[num:] = 0
        self.polynomials[item] &= array

    def _constraint_lte(self, item, num):
        # set coefficients at above num to 0
        try:
            array = np.ones_like(self.polynomials[item])
        except KeyError:
            self._add_missing_polynomial(item)
            array = np.ones_like(self.polynomials[item])

        array[num+1:] = 0
        self.polynomials[item] &= array

    def _constraint_contains(self, item, op, nums):
        try:
            array = np.ones_like(self.polynomials[item])
        except KeyError:
            self._add_missing_polynomial(item)
            array = np.ones_like(self.polynomials[item])

        array[nums] = 0
        if isinstance(op, ast.In):
            self.polynomials[item] &= (1 - array)
        else:
            self.polynomials[item] &= array

    def _constraint_modulo(self, item, mod, op, rem):
        try:
            rng = np.arange(self.polynomials[item].size)
        except KeyError:
            self._add_missing_polynomial(item)
            rng = np.arange(self.polynomials[item].size)

        try:
            array = ast_op_to_operator[type(op)](rng % mod, rem)
        except KeyError:
            # TODO: allow constraints like 'item % mod in [rem1, rem2]'
            raise ConstraintError('Constraint not understood')
        else:
            self.polynomials[item] &= array
