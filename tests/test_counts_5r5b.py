import pytest

from molloy import Molloy

collection_5r5b = Molloy({'red': 5, 'blue': 5})

# 5 red, 5 blue, constrain red (==)
@pytest.mark.parametrize('size,red,expected', [
    (10, 5, 1),
    ( 9, 5, 1),
    ( 8, 5, 1),
    (10, 4, 0),
    ( 6, 1, 1),
    ( 5, 0, 1),
    ( 0, 1, 0),
])
def test_5r5b_constrain_red_eq(size, red, expected):
    constraints = 'red == {}'.format(red)
    assert collection_5r5b.count_sets(size, constraints) == expected

# 5 red, 5 blue, constrain red (!=)
@pytest.mark.parametrize('size,red,expected', [
    (10, 5, 0),
    ( 9, 5, 1),
    ( 1, 1, 1),
    ( 6, 3, 4),
])
def test_5r5b_constrain_red_neq(size, red, expected):
    constraints = 'red != {}'.format(red)
    assert collection_5r5b.count_sets(size, constraints) == expected

# 5 red, 5 blue, constrain red (<)
@pytest.mark.parametrize('size,red,expected', [
    (10, 6, 1),
    (10, 5, 0),
    ( 3, 3, 3),
    ( 5, 1, 1),
    ( 6, 1, 0),
    ( 6, 2, 1),
])
def test_5r5b_constrain_red_lt(size, red, expected):
    constraints = 'red < {}'.format(red)
    assert collection_5r5b.count_sets(size, constraints) == expected

# 5 red, 5 blue, constrain red (>=)
@pytest.mark.parametrize('size,red,expected', [
    (10, 5, 1),
    ( 9, 5, 1),
    (11, 5, 0),
    ( 2, 3, 0),
    ( 5, 0, 6),
    ( 6, 0, 5),
    ( 7, 0, 4),
])
def test_5r5b_constrain_red_ge(size, red, expected):
    constraints = 'red >= {}'.format(red)
    assert collection_5r5b.count_sets(size, constraints) == expected

# 5 red, 5 blue, constrain red (in)
@pytest.mark.parametrize('size,red,expected', [
    (10, [5], 1),
    ( 9, [5], 1),
    ( 8, [5], 1),
    (10, [4], 0),
    ( 6, [1], 1),
    ( 5, [0], 1),
    ( 0, [1], 0),
    (10, [5, 1], 1),
    ( 9, [5, 2], 1),
])
def test_5r5b_constrain_red_in(size, red, expected):
    constraints = 'red in {}'.format(red)
    assert collection_5r5b.count_sets(size, constraints) == expected

# 5 red, 5 blue, constrain red (not in)
@pytest.mark.parametrize('size,red,expected', [
    (10, [5], 0),
    ( 9, [5], 1),
    ( 1, [1], 1),
    ( 6, [3], 4),
    ( 5, [1, 2], 4),
])
def test_5r5b_constrain_red_not_in(size, red, expected):
    constraints = 'red not in {}'.format(red)
    assert collection_5r5b.count_sets(size, constraints) == expected

# 5 red, 5 blue, constrain red (%, ==)
@pytest.mark.parametrize('size,mod,rem,expected', [
    (10, 2, 0, 0),
    (10, 2, 1, 1),
    ( 5, 2, 0, 3),
    ( 5, 2, 1, 3),
    ( 5, 3, 0, 2),
])
def test_5r5b_constrain_red_modulo_eq(size, mod, rem, expected):
    constraints = 'red % {} == {}'.format(mod, rem)
    assert collection_5r5b.count_sets(size, constraints) == expected

# 5 red, 5 blue, constrain red (%, <)
@pytest.mark.parametrize('size,mod,rem,expected', [
    ( 5, 2, 1, 3),
    ( 5, 2, 2, 6),
    ( 5, 3, 2, 4),
])
def test_5r5b_constrain_red_modulo_lt(size, mod, rem, expected):
    constraints = 'red % {} < {}'.format(mod, rem)
    assert collection_5r5b.count_sets(size, constraints) == expected

# ------------------------------------------------

# 5 red, 5 blue, constrain red (==) and blue (==)
@pytest.mark.parametrize('size,red,blue,expected', [
    (10, 5, 5, 1),
    ( 9, 4, 5, 1),
    ( 9, 5, 4, 1),
    ( 9, 5, 5, 0),
    ( 2, 1, 1, 1),
    ( 2, 0, 2, 1),
    ( 2, 2, 0, 1),
    ( 5, 1, 1, 0),
])
def test_5r5b_constrain_red_eq_blue_eq(size, red, blue, expected):
    constraints = 'red == {} and blue == {}'.format(red, blue)
    assert collection_5r5b.count_sets(size, constraints) == expected

# 5 red, 5 blue, ? yellow, constrain red (==), blue (==), yellow (==) 
@pytest.mark.parametrize('size,red,blue,yellow,expected', [
    (10, 5, 5, 0, 1),
    (10, 5, 5, 1, 0),
    (11, 5, 5, 1, 1),
    (10, 4, 5, 1, 1),
    ( 9, 4, 5, 0, 1),
    ( 2, 0, 2, 0, 1),
    ( 2, 2, 0, 0, 1),
])
def test_5r5b_constrain_red_eq_blue_eq_plus_yellow_eq(size, red, blue, yellow, expected):
    constraints = 'red == {} and blue == {} and yellow == {}'.format(red, blue, yellow)
    assert collection_5r5b.count_sets(size, constraints) == expected

