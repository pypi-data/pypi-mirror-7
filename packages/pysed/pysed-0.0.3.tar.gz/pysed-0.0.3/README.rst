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


	usage: pysed [-h] [-v] [-p] [-s] [-b] [-n]

	Utility that parses and transforms text

	optional arguments:
	  -h, --help		show this help message and exit
	  -v, --version		print version and exit
	  -p, --print		print text
	  -s,			find and replace text
	  -b,			add text before target
	  -n,			add text after the target


Pysed Examples
--------------

See changes before save:

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

	$ pysed -s --print '\n ' ' ' text.txt

	This is my cat, whose name is Betty.
	This is my dog, whose name is Frank.
	This is my fish,
	whose name is George.
	This is my goat, whose name is Adam.


	$ pysed -s --print '\n ' ' ' text.txt > text2.txt
	$ cat text2.txt

	This is my cat, whose name is Betty.
        This is my dog, whose name is Frank.
        This is my fish,
        whose name is George.
        This is my goat, whose name is Adam.


	$ pysed -p example.txt

        Python is a widely used general-purpose, high-level programming language.
        Its design philosophy emphasizes code readability, and its syntax allows
        programmers to express concepts in fewer lines of code than would be possible
        in languages such as C. The language provides constructs intended to enable
        clear programs on both a small and large scale.


	$ pysed -s --print 'high-level' 'HIGH LEVEL' example.txt

	Python is a widely used general-purpose, HIGH LEVEL programming language. 
	Its design philosophy emphasizes code readability, and its syntax allows 
	programmers to express concepts in fewer lines of code than would be possible
	in languages such as C. The language provides constructs intended to enable
	clear programs on both a small and large scale.


Replace text:

.. code-block:: bash


	$ cat example.txt

        Python is a widely used general-purpose, high-level programming language. 
        Its design philosophy emphasizes code readability, and its syntax allows 
        programmers to express concepts in fewer lines of code than would be possible 
        in languages such as C. The language provides constructs intended to enable
	clear programs on both a small and large scale.	


	$ pysed -s 'high-level' 'HIGH LEVEL' example.txt
	$ cat example.txt
	
        Python is a widely used general-purpose, HIGH LEVEL programming language. 
        Its design philosophy emphasizes code readability, and its syntax allows 
        programmers to express concepts in fewer lines of code than would be possible 
        in languages such as C. The language provides constructs intended to enable
	clear programs on both a small and large scale.



Add text after the target:

.. code-block:: bash


	$ pysed -n 'C' '++' example.txt
	$ cat examples.txt

        Python is a widely used general-purpose, HIGH LEVEL programming language. 
        Its design philosophy emphasizes code readability, and its syntax allows 
        programmers to express concepts in fewer lines of code than would be possible 
        in languages such as C++. The language provides constructs intended to enable
	clear programs on both a small and large scale.



Add text before target:

.. code-block:: bash


	$ pysed -b 'small' 'big, ' example.txt	
	$ cat example.txt

        Python is a widely used general-purpose, HIGH LEVEL programming language.
        Its design philosophy emphasizes code readability, and its syntax allows
        programmers to express concepts in fewer lines of code than would be possible
        in languages such as C++. The language provides constructs intended to enable
	clear programs on both a big, small and large scale.



Replace special character:

.. code-block:: bash

	
	$ pysed -s '\+\+' '#' example.txt	
	$ cat example.txt

        Python is a widely used general-purpose, HIGH LEVEL programming language.
        Its design philosophy emphasizes code readability, and its syntax allows
        programmers to express concepts in fewer lines of code than would be possible
        in languages such as C#. The language provides constructs intended to enable
	clear programs on both a big, small and large scale.

	

Remove text:

.. code-block:: bash


	$ pysed -s 'programming ' '' example.txt
        $ cat example.txt

        Python is a widely used general-purpose, HIGH LEVEL language.
        Its design philosophy emphasizes code readability, and its syntax allows
        programmers to express concepts in fewer lines of code than would be possible
        in languages such as C#. The language provides constructs intended to enable
	clear programs on both a big, small and large scale.




More features come....
