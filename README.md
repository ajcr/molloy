# Molloy

Molloy computes the number of possible collections of items that satisfy one or more constraints.

How many choices of 5 items from :cake::pizza::doughnut::pizza::green_apple::cake::green_apple: contain at least one slice of pizza?

``` python
>>> food = Molloy(['cake', 'pizza', 'donut', 'pizza', 'apple', 'cake', 'apple'])
>>> food.count_collections(5, 'pizza >= 1')
8
```

The answer is 8.

This module provides an extension to Python's `Counter` class as the foundation for solving these combinatorial problems, and provides a simple way to express the constraints that a collection should meet.

## Getting started

### Prerequisites

Molloy is written to be used with Python 3, but *may* work with Python 2.

The only external dependency is [NumPy](http://www.numpy.org/) (and [PyTest](https://docs.pytest.org/en/latest/) for testing). The dependency on NumPy *might* go away in future, or another dependency could be substituted (e.g. SymPy) as more features are added and I get better at figuring out how to solve various combinatorial problems.

### Installing

Clone the repo (e.g. `git clone https://github.com/ajcr/molloy.git`), change to the directory (e.g. `cd molloy`) and then `python setup.py install` should do the trick.

## Examples

### Counting collections

Suppose we are faced with the following problem:

> There are 8 red marbles, 14 blue marbles and 11 yellow marbles. How many collections of 13 marbles can be chosen such that fewer than 5 red marbles are used, and at least 3 blue and at least 3 yellow marbles are used?

This is a slightly tedious counting problem that can be solved in many different ways; normally we'd have to implement our chosen way in Python by ourself. Molloy rids us of this chore:

``` python
>>> from molloy import Molloy
>>> marbles = Molloy({'red': 8, 'blue': 14, 'yellow': 11})
```
We've just defined our starting collection of marbles by passing a dictionary of counts. This should look very familiar if you've ever used Python's `collections.Counter` class.

Now we can use the `count_collections()` method to solve the problem:
``` python
>>> marbles.count_collections(13, 'red < 5 and blue >= 3 and yellow >= 3')
30
```
So there are 30 ways to choose a collection of 13 marbles meeting the constraints.

Notice that the constraint is given as a string. Molloy parses the string as a Python expression and translates it into a computation to solve the problem. This allows for a versatile and concise way of giving the problem to the program.

Let's try a slightly more ambitious exercise (cf. Section 5 [here](https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-042j-mathematics-for-computer-science-fall-2005/readings/ln11.pdf)):

> We've made a huge fruit salad. How many ways can we serve a bowl of 6 pieces of fruit such that:
>  - the number of apples is even, *and*
>  - the number of oranges is at most 4, *and*
>  - the number of pears in at most 1, *and*
>  - the number of bananas must be a multiple of 5?
>
> ...And how many ways for 100 pieces of fruit given the same requirements?

``` python
>>> constraints = """apple % 2 == 0 and 
                     orange <= 4    and
                     pear in (0, 1) and 
                     banana % 5 == 0"""
>>> Molloy().count_collections(6, constraints)
7
>>> Molloy().count_collections(100, constraints)
101
```
As well as using inequalities, we can express 'is a multiple of' by using Python's modulo `%` operator. We can also specify the values an item can take using a collection (e.g. `'pear in (0, 1)'`).

Notice that we used an 'empty' initial collection here. If an item mentioned in a constraint is not in the current collection, Molloy will assume it can use as many copies of that item as necessary.


### Counting sequences

Coming soon!

### Counting partitions

Coming later.

## Miscellaneous

Currently Molloy is in the 'proof of concept' stage. Internally, the counts are computed by creating polynomials for each item, multiplying these polynomials and extracting the appropriate coefficient. There are more advanced and efficient ways to compute solutions to these and other problems and it is my aim to implement alternative approaches as the library grows and I learn more about combinatorial techniques in general.

I named the project 'Molloy' after remembering the [sucking-stones sequence](http://www.samuel-beckett.net/molloy1.html) from that novel.


