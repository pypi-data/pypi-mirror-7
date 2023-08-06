.. image:: https://badge.fury.io/py/pysed.png
    :target: http://badge.fury.io/py/pysed
.. image:: https://pypip.in/d/pysed/badge.png
    :target: https://pypi.python.org/pypi/pysed
.. image:: https://pypip.in/license/pysed/badge.png
    :target: https://pypi.python.org/pypi/pysed



Cli utility that parses and transforms text written in Python.


[CHANGELOG] : https://github.com/dslackw/pysed/blob/master/CHANGELOG


Installation
------------

.. code-block:: bash

	$ pip install pysed

	uninstall

	$ pip uninstall pysed



Command Line Tool Usage
-----------------------

.. code-block:: bash


	usage: pysed [-h] [-v] [-p] [-s] [-i]

	Utility that parses and transforms text

	optional arguments:
	  -h, --help		show this help message and exit
	  -v, --version		print version and exit
	  -p, --print		print text
	  -s, m /		replace text
	  -i, m /		insert text


Pysed Examples
--------------

See changes before modification with options -p --print:


Print text file:

(NOTE: Windows users avoid using quotes '')


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

Remove new lines:

.. code-block:: bash

	$ pysed -s --print '\n ' ' ' text.txt

	This is my cat, whose name is Betty.
	This is my dog, whose name is Frank.
	This is my fish,
	whose name is George.
	This is my goat, whose name is Adam.

Redirect results to another file:

.. code-block:: bash

	$ pysed -s --print '\n ' ' ' text.txt > text2.txt
	$ cat text2.txt

	This is my cat, whose name is Betty.
        This is my dog, whose name is Frank.
        This is my fish,
        whose name is George.
        This is my goat, whose name is Adam.

Replace text:

.. code-block:: bash

	$ pysed -s --print 'This' 'THIS' text.txt
	
	THIS is my cat,
	 whose name is Betty.
	THIS is my dog,
	 whose name is Frank.
	THIS is my fish,
	whose name is George.
	THIS is my goat,
	 whose name is Adam.

Replace max:

.. code-block:: bash

	$ pysed -s --print m2/'This' 'THIS' text.txt

        THIS is my cat,
         whose name is Betty.
        THIS is my dog,
         whose name is Frank.
        This is my fish,
        whose name is George.
        This is my goat,
         whose name is Adam.

Insert text:

.. code-block:: bash

	$ pysed -i --print 'whose ' 'sur' text.txt

        THIS is my cat,
         whose surname is Betty.
        THIS is my dog,
         whose surname is Frank.
        This is my fish,
        whose surname is George.
        This is my goat,
         whose surname is Adam.	

Insert max:

.. code-block:: bash

	$ pysed -i --print m2/'whose ' 'sur' text.txt

        THIS is my cat,
         whose surname is Betty.
        THIS is my dog,
         whose surname is Frank.
        This is my fish,
        whose name is George.
        This is my goat, 
         whose name is Adam.	


More features come....
