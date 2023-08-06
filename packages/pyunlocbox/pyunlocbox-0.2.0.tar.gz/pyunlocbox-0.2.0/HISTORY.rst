.. :changelog:

=======
History
=======

0.2.0 (2014-08-04)
------------------

Second usable version, available on GitHub and released on PyPI.
Still experimental.

New features :

* Douglas-Rachford splitting algorithm
* Projection on the L2-ball for tight and non tight frames
* Compressed sensing tutorial using L2-ball, L2-norm and Douglas-Rachford
* Automatic solver selection

Infrastructure :

* Unit tests for all functions and solvers
* Continuous integration testing on Python 2.6, 2.7, 3.2, 3.3 and 3.4

0.1.0 (2014-06-08)
------------------

First usable version, available on GitHub and released on PyPI.
Still experimental.

Features :

* Forward-backward splitting algorithm
* L1-norm function (eval and prox)
* L2-norm function (eval, grad and prox)
* Least square problem tutorial using L2-norm and forward-backward
* Compressed sensing tutorial using L1-norm, L2-norm and forward-backward

Infrastructure :

* Sphinx generated documentation using Numpy style docstrings
* Documentation hosted on Read the Docs
* Code hosted on GitHub
* Package hosted on PyPI
* Code checked by flake8
* Docstring and tutorial examples checked by doctest (as a test suite)
* Unit tests for functions module (as a test suite)
* All test suites executed in Python 2.6, 2.7 and 3.2 virtualenvs by tox
* Distributed automatic testing on Travis CI continuous integration platform
