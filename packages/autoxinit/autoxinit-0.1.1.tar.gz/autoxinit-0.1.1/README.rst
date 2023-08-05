==========================
AutoXinit - lazy importing
==========================

This package extends the the py-package 'automodinit' with the option also to import classes and functions inside a module.

If classes/functions have the same name as modules they will override them.
This is useful if the *'one class/function per file'* principle is used

**autoXInit** is listed in the Python Package Index. You can install it typing 'pip install autoxinit'.

- Fork the code on `github <http://pypi.python.org/pypi/automodinit>`_

- Find the original `http://pypi.python.org/pypi/automodinit <http://pypi.python.org/pypi/automodinit>`_

To init your package with AutoXinit daa the following to your __init__.py::

    __all__ = []
    # Don't modify the line above, or this line!
    from autoxinit import autoxinit
    autoxinit(__name__, __file__, globals())
    del autoxinit

AutoXinit also provides a **test** package. Importing this moule...

1. Execute the test environment
2. Imports all modules AND all included (dummy) functions/classes. If a function/class share the same same with its parent module calling the modules name leeds to the function/class.
