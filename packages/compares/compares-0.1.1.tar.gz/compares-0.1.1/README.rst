========
Compares
========

``Compares`` is a module that defines a single decorator, ``compares.via``\ ,
which removes some boilerplate around defining ``__eq__``\ , ``__ne__`` and
``__repr__`` for object comparisons and display.

It takes advantage of the fact that there is often a set of relevant attributes
(fields) which should be used to compare instances.

It is inspired by `twisted.python.util.FancyEqMixin
<https://twistedmatrix.com/documents/current/api/twisted.python.util.FancyEqMixin.html>`_\ .
