Examples
========

Examples to demonstrate the features of batchOpenMPI follow.

Multi-ref example
-----------------

If the *multiRef* flag in enabled for a **batchOpenMPI.batchFunction** instances, then duplicate inputs searched for as to save computing resources.

.. literalinclude:: ../examples/ex2.py
   :lines: 5-
   :emphasize-lines: 4

Call expected example
---------------------

.. literalinclude:: ../examples/ex3.py
   :lines: 5-
   :emphasize-lines: 7

Dependency examples
----------------------------


.. literalinclude:: ../examples/ex4.py
   :lines: 5-

.. literalinclude:: ../examples/ex4b.py
   :lines: 5-

.. literalinclude:: ../examples/ex4c.py
   :lines: 5-

Downward dependency examples

.. literalinclude:: ../examples/ex5.py
   :lines: 5-

.. literalinclude:: ../examples/ex5b.py
   :lines: 5-

Individual working directory for each process
----------------------

.. literalinclude:: ../examples/ex7.py
   :lines: 5-
