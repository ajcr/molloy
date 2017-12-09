import ast

import numpy as np

from .baseconstraints import BaseConstraintHandler
from .constraintutils import ConstraintError, ast_op_to_operator


class CollectionConstraintHandler(BaseConstraintHandler):
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
        try:
            return self.power_series[self.max_degree]
        except IndexError:
            # Only reached when we have a collection
            # and do not introduce any new items in
            # the constraints
            return 0

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
