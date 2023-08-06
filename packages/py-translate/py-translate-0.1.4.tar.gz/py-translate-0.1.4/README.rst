py-translate
=============

.. image:: https://travis-ci.org/jjangsangy/py-translate.svg?branch=master
    :target: https://travis-ci.org/jjangsangy/py-translate

.. image:: https://badge.fury.io/gh/jjangsangy%2Fpy-translate.png
    :target: http://badge.fury.io/gh/jjangsangy%2Fpy-translate

.. image:: https://badge.fury.io/py/py-translate.png
    :target: http://badge.fury.io/py/py-translate

py-translate is a CLI Tool for Google Translate written in Python!

.. image:: img/alice.gif
    :alt: alice
    :align: center

:Author: Sang Han, 2014
:License: Apache Software License v2
:Version: 0.1.4

The end goal is a simple application for translating text in the terminal.
Text can be generated interactively or programmatically
in the shell enviornment. Through command line arguments,
file descriptors or pipes generating translated output
that can be piped to a file or displayed on the terminal.

Features
---------
- Simple command line parsing!
- Written in pure Python!
- Backwards compatable with Python 2.7
- Supports all language from Google Translate API
- The power of Unix pipes and filters
- Native UTF-8 Support

Installation
------------

From PyPI with pip (easy)
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ pip install py-translate


From Source at Github
~~~~~~~~~~~~~~~~~~~~~

* Clone the repository

.. code-block:: bash

    $ git clone https://github.com/jjangsangy/py-translate.git

* Install with setup.py

.. code-block:: bash

    $ python setup.py install

Usage
-----
* Default will translate from english to target language

.. code-block:: bash

    # Translate Hello World in Chinese
    $ echo 'Hello World!' | translate zh-TW
    你好世界！

.. image:: img/helloworld.gif
    :alt: Hello
    :align: center

* Just as easily specify a source language by providing it as first
  argument

.. code-block:: bash

   # Translate Hello from French to English
   $ echo 'Bonjour, comment allez-vous!' | translate fr en
   Hello, how are you?

Documentation
-------------

Documentation is available at https://py-translate.readthedocs.org/
