Installation
------------

::

  pip install pythonwpy

::

wpy "expression" ≅ python -c "print(expression)"
-----------------------------------------------

Float Arithmetic
~~~~~~~~~~~~~~~~

::

  $ wpy "3 * 1.5" 
  4.5

::

Access imports directly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ wpy "math.exp(1)"
  2.71828182846

  $ wpy "random.random()"
  0.103173957713
  
  $ wpy "datetime.datetime.now?"
  Help on built-in function now:

  now(...)
        [tz] -> new datetime with tz's local day and time.


::

Lists are printed row by row
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ wpy "range(3)"
  0
  1
  2

  $ wpy "[range(3)]"
  [0, 1, 2]

::

wpy -x "foo(x)" will apply foo to each line of input
---------------------------------------------------

Multiply each line of input by 7.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ wpy "range(3)" | wpy -x "int(x)*7"
  0
  7
  14

::

Append ".txt" to each line of input
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ wpy "range(3)" | wpy -x "x + '.txt'"
  0.txt
  1.txt
  2.txt

::

Append ".txt" to every file in the directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ ls | wpy -x "'mv `%s` `%s.txt`' % (x,x)" | sh 
  # sharp quotes are swapped out for single quotes
  # single quotes handle spaces in filenames

::

Get only even numbers
~~~~~~~~~~~~~~~~~~~~~

::

  $ wpy "range(8)" | wpy -x "x if int(x)%2 == 0 else None"
  0
  2
  4
  6

::

wpy -fx "predicate(x)" filters rows satisfying a condition
---------------------------------------------------------

Get only odd numbers
~~~~~~~~~~~~~~~~~~~~

::

  $ wpy "range(8)" | wpy -fx "int(x)%2 == 1"
  1
  3
  5
  7

::

wpy -l will set l = list(sys.stdin)
-------------------------------------------

Reverse the input
~~~~~~~~~~~~~~~~~

::

  $ wpy "range(3)" | wpy -l "l[::-1]"
  2
  1
  0

::

Sum the input
~~~~~~~~~~~~~

::

  $ wpy "range(3)" | wpy -l "sum(int(x) for x in l)"
  3

::

Count the lines of input
~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ wpy "range(17)" | wpy -l "len(l)"
  17

::

If you haven't had enough yet, check out the `wiki <http://github.com/Russell91/pythonwpy/wiki>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
