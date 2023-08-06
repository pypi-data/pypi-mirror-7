.. image:: https://badge.fury.io/py/pysed.png
    :target: http://badge.fury.io/py/pysed
.. image:: https://pypip.in/d/pysed/badge.png
    :target: https://pypi.python.org/pypi/pysed
.. image:: https://pypip.in/license/pysed/badge.png
    :target: https://pypi.python.org/pypi/pysed



CLI utility that parses and transforms text written in Python.


[CHANGELOG] : https://github.com/dslackw/pysed/blob/master/CHANGELOG


Installation
------------

.. code-block:: bash

    $ pip install pysed

    uninstall

    $ pip uninstall pysed
    

Usage Examples
--------------

How to use the module in your own python code:
[ modules: replace(), append() ]

.. code-block:: bash

    >>> import pysed

.. code-block:: bash

    >>> text = '''This is my cat,
    ...      whose name is Betty.
    ...     This is my dog,
    ...      whose name is Frank.
    ...     This is my fish,
    ...     whose name is George.
    ...     This is my goat,
    ...      whose name is Adam.'''
    >>>
    >>> result = pysed.replace(text, 'This', 'THIS', '', '')
    >>>
    >>> print result

        THIS is my cat,
         whose name is Betty.
        THIS is my dog,
         whose name is Frank.
        THIS is my fish,
        whose name is George.
        THIS is my goat,
         whose name is Adam.
    >>>
    >>> result = pysed.replace(text, 'This', 'THIS', 'max=2', 'red')
    >>>
    >>> print result

        THIS is my cat,
         whose name is Betty.
        THIS is my dog,
         whose name is Frank.
        This is my fish,
        whose name is George.
        This is my goat,
         whose name is Adam.
    >>>
    >>> result = pysed.append(text, 'This', '>', 'max=1', 'green')
    >>>
    >>> print result
    
        This> is my cat,
         whose name is Betty.
        This is my dog,
         whose name is Frank.
        This is my fish,
        whose name is George.
        This is my goat,
         whose name is Adam.



Command Line Tool Usage
-----------------------

.. code-block:: bash

    usage: pysed [-h] [-v] [-p] [-l] [-r] [-i]

    Utility that parses and transforms text

    optional arguments:
      -h, --help     : show this help message and exit
      -v, --version  : print version and exit
      -p, --print    : print text
                       e extract/, c chars/, s sum/
      -l, --lines    : print lines
                       'N', '[N-N]', 'step=N/*, all'
      -r, --replace  : replace text
                       m max=N/, u upper=*/, l lower=*/, /color
      -i, --insert   : insert text
                       m max=N/, /color

    N = Number, {Options}/, 'Pattern'
    color = red, green, blue, cyan, yellow, magenta


See changes before modification with options -p --print:


Print text file:

(NOTE: Windows users maybe avoid using quotes '')


.. code-block:: bash

    $ pysed --print text.txt

    This is my cat,
     whose name is Betty.
    This is my dog,
     whose name is Frank.
    This is my fish,
    whose name is George.
    This is my goat,
     whose name is Adam.

    $ pysed --print chars/'a' text.txt

    find 8 --> 'a'

    $ pysed --print chars/'is' text.txt

    find 13 --> 'is'

    $ pysed --print sum/'' text.txt

    7 lines
    118 characters
    32 words
    35 blanks

Print lines:

.. code-block:: bash

    $ pysed --lines '0,3,2,1,4,7,6,5' text.txt

    This is my cat,
     whose name is Frank.
    This is my dog,
     whose name is Betty.
    This is my fish,
     whose name is Adam.
    This is my goat,
    whose name is George.

    $ pysed --lines '2,7' text.txt

    This is my dog,
     whose name is Adam.

    $ pysed --lines '[3-5]' text.txt

     whose name is Frank.
    This is my fish,
    whose name is George.

    $ pysed --lines step=2/'*' text.txt

    This is my cat,
    This is my dog,
    This is my fish,
    This is my goat,

Extract text:

.. code-block:: bash

    $ pysed pysed -p extract/'is' text.txt

    is is is is is is is is is is is is is

Remove new lines:

.. code-block:: bash

    $ pysed -r --print '\n ' ' ' text.txt

    This is my cat, whose name is Betty.
    This is my dog, whose name is Frank.
    This is my fish,
    whose name is George.
    This is my goat, whose name is Adam.

Redirect results to another file:

.. code-block:: bash

    $ pysed -r --print '\n ' ' ' text.txt > text2.txt
    $ cat text2.txt

    This is my cat, whose name is Betty.
    This is my dog, whose name is Frank.
    This is my fish,
    whose name is George.
    This is my goat, whose name is Adam.

    $ pysed -p extract/'This' text.txt > text3.txt
    $ pysed --print text3.txt

    This This This This

    $ pysed --lines '0,2,4,6' text.txt > text4.txt
    $ pysed --print text4.txt

    This is my cat,
    This is my dog,
    This is my fish,
    This is my goat,

Replace text:

.. code-block:: bash

    $ pysed -r --print 'This' 'THIS' text.txt
    
    THIS is my cat,
     whose name is Betty.
    THIS is my dog,
     whose name is Frank.
    THIS is my fish,
    whose name is George.
    THIS is my goat,
     whose name is Adam.

    $ pysed -r --print '[a-z]' '_' text.txt

    T___ __ __ ___,
     _____ ____ __ B____.
    T___ __ __ ___,
     _____ ____ __ F____.
    T___ __ __ ____,
    _____ ____ __ G_____.
    T___ __ __ ____,
     _____ ____ __ A___.

    $ pysed -r --print '[a-k]' '' text.txt

    Ts s my t,
     wos nm s Btty.
    Ts s my o,
     wos nm s rn.
    Ts s my s,
    wos nm s Gor.
    Ts s my ot,
     wos nm s Am.

    $ pysed -r --print 'a' 'A'/green text.txt

    This is my cAt,
     whose nAme is Betty.
    This is my dog,
     whose nAme is FrAnk.
    This is my fish,
    whose nAme is George.
    This is my goAt,
     whose nAme is AdAm.

Replace max:

.. code-block:: bash

    $ pysed -r --print max=2/'This' 'THIS' text.txt

    THIS is my cat,
     whose name is Betty.
    THIS is my dog,
     whose name is Frank.
    This is my fish,
     whose name is George.
    This is my goat,
     whose name is Adam.

Convert text to uppercase:

.. code-block:: bash

    $ pysed -r --print upper/'This' 'this' text.txt

    THIS is my cat,
     whose name is Betty.
    THIS is my dog,
     whose name is Frank.
    THIS is my fish,
    whose name is George.
    THIS is my goat,
     whose name is Adam.

    $ pysed -r --print upper=*/'' '' text.txt
    
    THIS IS MY CAT,
     WHOSE NAME IS BETTY.
    THIS IS MY DOG,
     WHOSE NAME IS FRANK.
    THIS IS MY FISH,
    WHOSE NAME IS GEORGE.
    THIS IS MY GOAT,
     WHOSE NAME IS ADAM.

Convert text to lowercase:

.. code-block:: bash

    $ pysed -r --print lower/'T' 'T' text.txt

    this is my cat,
     whose name is Betty.
    this is my dog,
     whose name is Frank.
    this is my fish,
    whose name is George.
    this is my goat,
     whose name is Adam.

    $ pysed -r --print lower=*/'' '' text.txt

    this is my cat,
     whose name is betty.
    this is my dog,
     whose name is frank.
    this is my fish,
     whose name is george.
    this is my goat,
     whose name is adam 

Insert text:

.. code-block:: bash

    $ pysed -i --print 'whose ' 'sur' text.txt

    This is my cat,
     whose surname is Betty.
    This is my dog,
     whose surname is Frank.
    This is my fish,
     whose surname is George.
    This is my goat,
     whose surname is Adam. 

Insert max:

.. code-block:: bash

    $ pysed -i --print m=2/'whose ' 'sur' text.txt

    This is my cat,
     whose surname is Betty.
    This is my dog,
     whose surname is Frank.
    This is my fish,
     whose name is George.
    This is my goat, 
     whose name is Adam.    

Delete text:

.. code-block:: bash

    $ pysed -r --print 'my ' '' text.txt

    This is cat,
     whose name is Betty.
    This is dog,
     whose name is arank.
    This is fish,
    whose name is George.
    This is goat,
     whose name is Adam.


More features come....
