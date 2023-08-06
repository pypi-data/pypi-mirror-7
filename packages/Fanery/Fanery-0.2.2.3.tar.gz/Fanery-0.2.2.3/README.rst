Fanery
======

Application development framework.


Project Goals
-------------

  * Strong security by default.
  * Focus on being developer-oriented.
  * Promote funcional pythonic style.
  * Promote continuous testing+profiling.


Why Fanery
----------

Fanery is an opinionated development framework build around a few simple concepts:

  * Strong cryptography must be transparent and enabled by default.
  * Encryption must not rely on cryptographic keys generated client side.
  * Encryption must only rely on unbroken high-quality ciphers/algorithms/implementations.
  * Session security must not rely on SessionIDs, bizare URLs, secure cookies, secret tokens, magic keys or any other piece of information that can be guessed or stolen during transmission.
  * Capture and re-transmission of encrypted messages must be pointless.
  * The framework must protect transparently against brute-force and authenticated sessions abuse.
  * The framework must handle transparently input serialization to harmless/built-in only object types.
  * The framework must not depend on strict/pre-defined configuration style/format and/or directory structure.
  * The framework must not tie to a particular storage or UI technology.
  * The framework must provide the facilities for easy testing, debugging and profiling.
  * The framework must not rely on components that inhibit elastic/horizontal scalability.

A lot of discussions happens around `JavaScript Cryptography Considered Harmfull <https://news.ycombinator.com/item?id=7903720>`_ so a bit of clarification is needed to understand why and how Fanery use it:

  * HTTPS cannot be replaced by JavaScript Cryptography, however SSL/TLS is no help against the majority of common attacks, that's why Fanery use "scrypt + NaCl + One-Time Pad" (both server and client side) together with SSL to achieve protection against many of those threats.

Install
-------

1. First make sure to install successfully the following C libraries::

    pip install PyNaCl
    pip install cxor
    pip install ujson
    pip install scrypt
    pip install bjoern
    pip install bsdiff4
    pip install ciso8601
    pip install python-libuuid
    pip install msgpack-python

2. Then install Fanery and run test files::

    pip install Fanery
    python tests/test_term.py
    python tests/test_service.py

3. The following libraries offer great help during debug, profiling and testing::

    pip install ipdb
    pip install linesman objgraph
    pip install multi-mechanize

Contribute
----------

- Issue Tracker: https://bitbucket.org/mcaramma/fanery/issues
- Source Code: https://bitbucket.org/mcaramma/fanery/src

License
-------

The project is licensed under the ISC license.

Documentation
-------------

.. image:: https://readthedocs.org/projects/fanery/badge/?version=latest
    :target: https://fanery.readthedocs.org
    :alt: Fanery Documentation
