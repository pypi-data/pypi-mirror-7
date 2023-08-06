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

* Strong criptography must be transparent and enabled by default.

* Encryption must only rely on unbroken high-quality ciphers/algorithms/implementations.

* Encryption must rely exclusively on cryptographic keys generated server side.

* Session security must not rely on SessionIDs, bizare URLs, secure cookies, secret tokens, magic keys o
r any other piece of information that can be guessed or stolen during transmission.

* Capture and re-transmission of encrypted messages must be pointless.

* The framework must protect transparently against brute-force and authenticated sessions abuse.

* The framework must handle transparently input serialization to harmless/built-in only object types.

* The framework must not depend on strict/pre-defined configuration style/format and/or directory struct
ure.

* The framework must not tie to a particular storage or UI technology.

* The framework must provide the facilities for easy testing/debugging and profiling.

* The framework must not rely on components that inhibit elastic/horizontal scalability.

* The framework must work seamessly in multi-thread/multi-process or event-driven environments.

A lot of discussions happens around "JavaScript criptography considered harmfull" so a bit of clarificat
ion is needed to understand why and how Fanery use it:

* HTTPS cannot be replaced by JavaScript criptography, however SSL/TLS is no help against the majority o
f common attacks, that's why Fanery use "scrypt + NaCl + One-Time Pad" (both server and client side) to
achieve protection against many of those threats using JavaScript criptography together with HTTPS and n
ot as a replacement.

Install howto
-------------

1. First make sure to install successfully the following C libraries

    ```
    pip install PyNaCl cxor ujson scrypt bsdiff4 ciso8601 python-libuuid msgpack-python
    ```

2. Then install Fanery and run test files

    ```
    pip install Fanery
    ```

    ```
    python tests/test_service.py
    ```

3. Enable debugging/profiling facilities installing the following packages
    ```
    pip install ipdb xtraceback profilehooks line-profiler memory-profiler linesman objgraph
    ```
