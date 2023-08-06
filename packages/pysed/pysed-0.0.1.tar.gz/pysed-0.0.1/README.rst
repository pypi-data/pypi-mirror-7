Cli utility that parses and transforms text written in Python.


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

	$ pysed -s --print 'high-level' 'HIGH LEVEL' example.txt
	$ pysed -p example.txt

	Python is a widely used general-purpose, HIGH LEVEL programming language. Its
        design philosophy emphasizes code readability, and its syntax allows programmers to express
        concepts in fewer lines of code than would be possible in languages such as C. The
        language provides constructs intended to enable clear programs on both a small and large
        scale.


Replace text:

.. code-block:: bash


	$ cat example.txt

	Python is a widely used general-purpose, high-level programming language. Its 
	design philosophy emphasizes code readability, and its syntax allows programmers to express 
	concepts in fewer lines of code than would be possible in languages such as C. The 
	language provides constructs intended to enable clear programs on both a small and large 
	scale.


	$ pysed -s 'high-level' 'HIGH LEVEL' example.txt
	$ cat example.txt
	
	Python is a widely used general-purpose, HIGH LEVEL programming language. Its 
	design philosophy emphasizes code readability, and its syntax allows programmers to express 
	concepts in fewer lines of code than would be possible in languages such as C. The 
	language provides constructs intended to enable clear programs on both a small and large 
	scale.


Add text after the target:

.. code-block:: bash


	$ pysed -n 'C' '++' example.txt
	$ cat examples.txt

	Python is a widely used general-purpose, HIGH LEVEL programming language. Its 
	design philosophy emphasizes code readability, and its syntax allows programmers to express 
	concepts in fewer lines of code than would be possible in languages such as C++. The 
	language provides constructs intended to enable clear programs on both a small and large 
	scale.


Add text before target:

.. code-block:: bash


	$ pysed -b 'small' 'big, ' example.txt	
	$ cat example.txt

	Python is a widely used general-purpose, HIGH LEVEL programming language. Its 
	design philosophy emphasizes code readability, and its syntax allows programmers to express 
	concepts in fewer lines of code than would be possible in languages such as C++. The 
	language provides constructs intended to enable clear programs on both a big, small and large 
	scale.


Replace special character:

.. code-block:: bash

	
	$ pysed -s '\+\+' '#' example.txt	
	$ cat example.txt

	Python is a widely used general-purpose, HIGH LEVEL programming language. Its 
	design philosophy emphasizes code readability, and its syntax allows programmers to express 
	concepts in fewer lines of code than would be possible in languages such as C#. The 
	language provides constructs intended to enable clear programs on both a big, small and large 
	scale.
	

Remove text:

.. code-block:: bash


	$ pysed -s 'programming ' '' example.txt
        $ cat example.txt

	Python is a widely used general-purpose, HIGH LEVEL language. Its 
	design philosophy emphasizes code readability, and its syntax allows programmers to express 
	concepts in fewer lines of code than would be possible in languages such as C++. The 
	language provides constructs intended to enable clear programs on both a big, small and large 
	scale.





More features come....
