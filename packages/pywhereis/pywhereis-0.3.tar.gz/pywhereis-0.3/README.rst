Summary
=======
Locate a python object (package, module, function, class ...) source file.

Usage
=====

   ``pywhereis [-v] [-s] dotted_name...``

CMD line Examples
=================

- The ``pywhereis`` script accept a package, module, function or a class ::

    $ pywhereis shlex
    shlex: /usr/lib/python2.7/shlex.py
    $ pywhereis os.path.abspath
    os.path.abspath: /usr/lib/python2.7/posixpath.py  337

- You can pass more than one dotted-name to it ::

    $ pywhereis shlex inspect.ismodule
    shlex: /usr/lib/python2.7/shlex.py
    inspect.ismodule: /usr/lib/python2.7/inspect.py  51

- If the name is a function, class or method the result will contain the line
  number where the object is defined ::

    $ pywhereis unittest.TestCase.assertEqual
    unittest.TestCase.assertEqual: /usr/lib/python2.7/unittest.py  344

- It will **fail** localizing object that are not pure python ::

    $ pywhereis.py sys
    sys:

- For more info about why the localization fail you can use the verbose
  mode ::

    $ pywhereis -v sys
    sys: Error: <module 'sys' (built-in)> is not pure python.

- If it's run with -s, --site-packages option the script will check first in
  site-packages instead of the default which is to check in the current dir
  first ::

    $ cd ~ ; touch os.py
    $ pywhereis os
    os: /home/mouad/os.py
    $ pywhereis -s os
    os: /usr/lib/python2.7/os.py

  **Note:** Option only available for python3.2 and below !

- For python2.7 and above you can also do ::

    $ python2.7 -mwhereis subprocess.Popen
    subprocess.Popen: /usr/local/lib/python2.7/subprocess.py 33

  **Note:** The above will only work if pywhereis was installed in that python version.

- Of course you can still search in a different python version by running this
  script using that python ::

    $ python3.4 $(which pywhereis) html
    html: /usr/local/lib/python3.4/html/__init__.py


Code Examples
=============

This package come also with a python package ``whereis`` that can be used like
so ::

    >>> import whereis
    >>> whereis.resolve('sys')
    <module 'sys' (built-in)>
    >>> whereis.locate('os')
    '/usr/lib/python2.7/os.py'
