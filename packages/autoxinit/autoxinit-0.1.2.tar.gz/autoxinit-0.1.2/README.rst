==========================
autoXinit - lazy importing
==========================

This package extends the the py-package 'automodinit' with the option also to import classes and functions inside a module.

If classes/functions have the same name as modules they will override them.
This is useful if the *'one class/function per file'* principle is used

**autoXinit** is listed in the Python Package Index. You can install it typing 'pip install autoxinit'.

- Fork the code on `github <https://github.com/radjkarl/autoXinit>`_

- Find the original `http://pypi.python.org/pypi/automodinit <http://pypi.python.org/pypi/automodinit>`_

To init your package with **autoXinit** add the following to your __init__.py::

    __all__ = []
    # Don't modify the line above, or this line!
    from autoxinit import autoxinit
    autoxinit(__name__, __file__, globals())
    del autoxinit

**autoXinit** also provides a **test** package. Importing this module via::

    from autoxinit import test

1. Execute the test environment
2. Imports all modules AND all included (dummy) functions/classes. If a function/class share the same same with its parent module calling the modules name leeds to the function/class.

File structure of the **test** package:

- testClass.py
    - class testClass
- testFunction.py
    - def testFunction
- testModule.py
    - class testModuleClass
    - def testModuleFunction

Instead of typing::

    from test.testClass import testClass
    from test.testFunction import testFunction

You can import your classes/functions directly via::

    from test import testClass
    from test import testFunction

As written before the imported names are only overridden if the name of a class/function is identical to the name of the module. That's why you can still access::

   from test import testModule
   from testModule import testModuleClass
   from testModule import testModuleFunction
