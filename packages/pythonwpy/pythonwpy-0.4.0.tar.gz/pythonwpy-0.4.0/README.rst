Installation
------------

::

  pip install pythonwpy

::

wpy 'expression' ≅ python -c 'print(expression)'
-----------------------------------------------

Float Arithmetic
~~~~~~~~~~~~~~~~

::

  $ wpy '3 * 1.5' 
  4.5

::

Access imports directly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ wpy 'math.exp(1)'
  2.71828182846

  $ wpy 'random.random()'
  0.103173957713
  
  $ wpy 'datetime.datetime.now?'
  Help on built-in function now:

  now(...)
        [tz] -> new datetime with tz's local day and time.


::

Lists are printed row by row
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ wpy 'range(3)'
  0
  1
  2

  $ wpy '[range(3)]'
  [0, 1, 2]

::

wpy -x 'foo(x)' will apply foo to each line of input
---------------------------------------------------

Multiply each line of input by 7.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ wpy 'range(3)' | wpy -x 'int(x)*7'
  0
  7
  14

::

Append ".txt" to each line of input
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ wpy 'range(3)' | wpy -x 'x + ".txt"'
  0.txt
  1.txt
  2.txt

::

Append ".txt" to every file in the directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ ls | wpy -x '"mv `%s` `%s.txt`" % (x,x)' | sh 
  # sharp quotes are swapped out for single quotes
  # single quotes handle spaces in filenames

::

Get only even numbers
~~~~~~~~~~~~~~~~~~~~~

::

  $ wpy 'range(8)' | wpy -x 'x if int(x)%2 == 0 else None'
  0
  2
  4
  6

::

wpy -fx 'predicate(x)' filters rows satisfying a condition
---------------------------------------------------------

Get only odd numbers
~~~~~~~~~~~~~~~~~~~~

::

  $ wpy 'range(8)' | wpy -fx 'int(x)%2 == 1'
  1
  3
  5
  7

::

Get words starting with "and"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ cat /usr/share/dict/words | wpy -fx 're.match(r"and", x)' | head -5
  and
  andante
  andante's
  andantes
  andiron

::

Get verbs starting with ba
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ cat /usr/share/dict/words | wpy -fx 're.match(r"ba.*ing$", x)' | head -5
  baaing
  babbling
  babying
  babysitting
  backbiting

::

Get long palindromes
~~~~~~~~~~~~~~~~~~~~

::

  $ cat /usr/share/dict/words | wpy -fx 'x==x[::-1] and len(x) >= 5' | head -5
  civic
  deified
  kayak
  level
  ma'am

::

wpy -l will set l = list(sys.stdin)
-------------------------------------------

Reverse the input
~~~~~~~~~~~~~~~~~

::

  $ wpy 'range(3)' | wpy -l 'l[::-1]'
  2
  1
  0

::

Sum the input
~~~~~~~~~~~~~

::

  $ wpy 'range(3)' | wpy -l 'sum(int(x) for x in l)'
  3

::

Count the lines of input
~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ wpy 'range(17)' | wpy -l 'len(l)'
  17

::

Count words beginning with each letter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ cat /usr/share/dict/words | wpy -x 'x[0].lower()' | wpy -l 'collections.Counter(l).most_common(5)'
  ('s', 11327)
  ('c', 9521)
  ('p', 7659)
  ('b', 6068)
  ('m', 5922)

::

If you haven't had enough yet, check out the `wiki <http://github.com/Russell91/pythonwpy/wiki>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
