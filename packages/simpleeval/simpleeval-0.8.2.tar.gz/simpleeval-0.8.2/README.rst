simpleeval (Simple Eval)
========================

A quick single file library for easily adding evaluatable expressions into python
projects.  Say you want to allow a user to set an alarm volume, which could depend
on the time of day, alarm level, how many previous alarms had gone off, and if there
is music playing at the time.

Or if you want to allow simple formulae in a web application, but don't want to
give full eval() access, or don't want to run in javascript on the client side.

It's deliberately very simple, just a single file you can dump into a project, or import
from pypi (pip or easy_install).

Internally, it's using the amazing python ``ast`` module to parse the expression, which
allows very fine control of what is and isn't allowed.  It should be completely safe in terms
of what operations can be performed by the expression.

The only issue I know to be aware of is that you can create an expression which
takes a long time to evaluate, or which evaluating requires an awful lot of memory,
which leaves the potential for DOS attacks.  There is basic protection against this,
and you can lock it down further if you desire. (see the `Operators` section below)

You should be aware of this when deploying in a public setting.

The defaults are pretty locked down and basic, and it's very easy to add whatever
extra specific functionality you need (your own functions, variable/name lookup, etc).

Basic Usage
-----------

To get very simple evaluating: ::

    from simpleeval import simple_eval

    simple_eval("21 + 21")

returns ``42``.

Expressions can be as complex and convoluted as you want: ::

    simple_eval("21 + 19 / 7 + (8 % 3) ** 9")

returns ``535.714285714``.

You can add your own functions in as well. ::

    simple_eval("square(11)", functions={"square": lambda x: x*x})

returns ``121``.

For more details of working with functions, read further down.

Note:
~~~~~
all further examples use ``>>>`` to designate python code, as if you are using the python interactive
prompt.

Operators
---------
You can add operators yourself, using the ``operators`` argument, but these are the defaults:

 +----+------------------------------------+
 | \+ | add two things. ``x + y``          |
 |    | ``1 + 1`` -> ``2``                 |
 +----+------------------------------------+
 | \- | subtract two things ``x - y``      |
 |    | ``100 - 1`` -> ``99``              |
 +----+------------------------------------+
 | \/ | divide one thing by another        |
 |    | ``x / y``                          |
 |    | ``100/10`` -> ``10``               |
 +----+------------------------------------+
 | \* | multiple one thing by another      |
 |    | ``x * y``                          |
 |    | ``10 * 10`` -> ``100``             |
 +----+------------------------------------+
 |\*\*| 'to the power of' ``x**y``         |
 |    | ``2 ** 10`` -> ``1024``            |
 +----+------------------------------------+
 | \% | modulus. (remainder)  ``x % y``    |
 |    | ``15 % 4`` -> ``3``                |
 +----+------------------------------------+
 | == | equals  ``x == y``                 |
 |    | ``15 == 4`` -> ``False``           |
 +----+------------------------------------+
 | <  | Less than. ``x < y``               |
 |    | ``1 < 4`` -> ``True``              |
 +----+------------------------------------+
 | >  | Greater than. ``x > y``            |
 |    | ``1 > 4`` -> ``False``             |
 +----+------------------------------------+
 | <= | Less than or Equal to. ``x <= y``  |
 |    | ``1 < 4`` -> ``True``              |
 +----+------------------------------------+
 | >= | Greater or Equal to ``x >= 21``    |
 |    | ``1 >= 4`` -> ``False``            |
 +----+------------------------------------+


The ``^`` operator is notably missing - not because it's hard, but because it is often mistaken for
a exponent operator, not the bitwise operation that it is in python.  It's trivial to add back in again
if you wish (using the class based evaluator explained below): ::

    >>> import ast
    >>> import operator

    >>> s = SimpleEval()
    >>> s.operators[ast.BitXor] = operator.xor

    >>> s.eval("2 ^ 10")
    8

Limited Power
~~~~~~~~~~~~~

Also note, the ``**`` operator has been locked down by default to have a maximum input value
of ``4000000``, which makes it somewhat harder to make expressions which go on for ever.  You
can change this limit by changing the ``simpleeval.POWER_MAX`` module level value to whatever
is an appropriate value for you (and the hardware that you're running on) or if you want to
completely remove all limitations, you can set the ``s.operators[ast.Pow] = operator.pow`` or make
your own function.

On my computer, ``9**9**5`` evaluates almost instantly, but ``9**9**6`` takes over 30 seconds.
Since ``9**7`` is ``4782969``, and so over the ``POWER_MAX`` limit, it throws a
``NumberTooHigh`` exception for you. (Otherwise it would go on for hours, or until the computer
runs out of memory)

String Safety
~~~~~~~~~~~~~

There are also limits on string length (100000 characters, ``MAX_STRING_LENGTH``).
This can be changed if you wish.

If Expressions
--------------

You can use python style ``if x then y else z`` type expressions: ::

    >>> simple_eval("'equal' if x == y else 'not equal'",
                    names={"x": 1, "y": 2})
    'not equal'

which, of course, can be nested: ::

    >>> simple_eval("'a' if 1 == 2 else 'b' if 2 == 3 else 'c'")
    'c'
    

Functions
---------

You can define functions which you'd like the expresssions to have access to: ::

    >>> simple_eval("double(21)", functions={"double": lambda x:x*2})
    42

You can define "real" functions to pass in rather than lambdas, of course too, and even re-name them so that expressions can be shorter ::

    >>> def double(x):
            return x * 2
    >>> simple_eval("d(100) + double(1)", functions={"d": double, "double":double})
    202

Names
-----
 
Sometimes it's useful to have variables available, which in python terminology are called 'names'. ::

    >>> simple_eval("a + b", names={"a": 11, "b": 100})
    111

You can also hand the handling of names over to a function, if you prefer: ::

    >>> def name_handler(node):
            return ord(node.id[0].lower(a))-96

    >>> simple_eval('a + b', names=name_handler)
    3

That was a bit of a silly example, but you could use this for pulling values from a database or file, say, or doing some kind of caching system.

Creating an Evaluator Class
---------------------------

Rather than creating a new evaluator each time, if you are doing a lot of evaluations,
you can create a SimpleEval object, and pass it expressions each time (which should be a bit quicker, and certainly more convienient for some use cases): ::

    s = SimpleEval()
    s.eval("1 + 1")
    # and so on...

You can assign / edit the various options of the ``SimpleEval`` object if you want to.
Either assign them during creation (like the ``simple_eval`` function) ::

    s = SimpleEval(functions={"boo": boo})

or edit them after creation: ::

    s.names['fortytwo'] = 42

this actually means you can modify names (or functions) with functions, if you really feel so inclined: ::

    s = SimpleEval()
    def set_val(name, value):
        s.names[name.value] = value.value
        return value.value

    s.functions = {'set': set_val}

    s.eval("set('age', 111)")

Say.  This would allow a certain level of 'scriptyness' if you had these evaluations happening as callbacks in a program.  Although you really are reaching the end of what this library is intended for at this stage.

Other...
--------

This is written using python 2.7, but should be trivial to convert to python3 with the 2to3 converter.  It totals around 100 lines of code, so it isn't a complex beast.

Please read the ``test_simpleeval.py`` file for other potential gotchas or details.  I'm very happy to accept pull requests, suggestions, or other issues.  Enjoy!

.. image:: https://coveralls.io/repos/danthedeckie/simpleeval/badge.png :target: https://coveralls.io/r/danthedeckie/simpleeval 
