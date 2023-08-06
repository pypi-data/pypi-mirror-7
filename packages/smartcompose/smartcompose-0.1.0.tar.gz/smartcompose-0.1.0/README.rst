``smartcompose``: Easy delegation with composition
==================================================

Decorate a class with ``@delegate(attribute_name, method_names)``
to delegate the methods in ``method_names`` to the attribute ``attribute_name``:

.. code:: python

    In [1]: from smartcompose import delegate

    In [2]: @delegate('_n', ('__add__', '__mul__'))
       ...: class NumberWrapper:
       ...:     def __init__(self, n):
       ...:         self._n = n
       ...:             

    In [3]: n = NumberWrapper(10)    

    In [4]: n + 2
    Out[4]: 12    

    In [5]: n * 3
    Out[5]: 30


For now, only compatible with Python 3.

::

    pip install smartcompose
