pyfuncrun
=========

Run a python function in a module from command line and shift ``sys.argv``,
so function can parse ``sys.argv`` properly.

Install
---------

.. code-block:: bash

    $ pip install pyfuncrun

Usage
-----

.. code-block:: bash

    $ pyfuncrun <path.to.func> <func arguments> <arguments for func to parse in sys.argv>


Example
-------

func.py:

.. code-block:: python

    def print_sys_argv():
        print sys.argv


    def func_with_args(a, b):
        print ((a + b), sys.argv)


    def func_with_kwargs(a, b, c=1):
        print ((a + b + c), sys.argv)

Run:

.. code-block:: bash

    $ pyfuncrun func.print_sys_argv 1 2
    ['pyfuncrun', 1, 2]

    $ pyfuncrun func.func_with_args 1 2
    (3, ['pyfuncrun'])

    $ pyfuncrun func.func_with_kwargs 1 2 3 4
    (6, ['pyfuncrun', 4])
