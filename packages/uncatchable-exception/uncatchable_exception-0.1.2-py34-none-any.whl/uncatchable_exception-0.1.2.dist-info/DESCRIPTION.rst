Uncatchable Exception
====================
.. image:: https://badge.fury.io/py/uncatchable-exception.png
   :target: http://badge.fury.io/py/uncatchable-exception
.. image:: https://pypip.in/d/uncatchable-exception/badge.png
   :target: https://crate.io/packages/uncatchable-exception/
.. image:: https://requires.io/github/bh/uncatchable-exception/requirements.png?branch=master
   :target: https://requires.io/github/bh/uncatchable-exception/requirements/?branch=master

Description
-----------

You will get an exception class which is not catchable when it was raised.

Installation
------------

Use ``pip`` to install:

.. code:: bash

    $ pip install uncatchable-exception --use-mirrors

Usage
-----

An example:

.. code:: python

    from uncatchable_exception import UncatchableException

    def raise_an_uncatchable_exception():
        raise UncatchableException('Harr Harr!')

    try:
        raise_an_uncatchable_exception()
    except:
        print("Uncatchable exception caught")


Yeah, the Python process is hanging, kill it with ``^C``


