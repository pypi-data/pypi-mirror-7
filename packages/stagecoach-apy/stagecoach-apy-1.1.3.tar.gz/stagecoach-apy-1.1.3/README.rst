apy
===

.. image:: https://travis-ci.org/stagecoachio/apy.png?branch=master
    :target: https://travis-ci.org/stagecoachio/apy

.. image:: https://coveralls.io/repos/stagecoachio/apy/badge.png?branch=master
    :target: https://coveralls.io/r/stagecoachio/apy?branch=master

.. image:: https://pypip.in/d/stagecoach-apy/badge.png
    :target: https://pypi.python.org/pypi/stagecoach-apy/
    :alt: Downloads
    
.. image:: https://pypip.in/v/stagecoach-apy/badge.png
    :target: https://pypi.python.org/pypi/stagecoach-apy/
    :alt: Latest Version

apy is a powerful Python framework designed with a clear and single purpose: **To serve as a REST API.** So, apy *do one thing and do it well*.

It makes real-world web application development and deployment more fun, more predictable, and more productive.

Most existing Python Frameworks are extremely verbose and uncomfortable for a Python coders who need a simple and elegant toolkit to create full-featured API REST applications.

They can provide most of the API REST capabilities that you can need, but because they are multipropose, sometimes overarchitectures your API REST application, 
and requires an extra amount of work to perform the simplest of tasks. So, when you uses a multipropose framework, 
you might been not following the python principle "Simple is better than complex.".

*Things shouldn't be this way. Not in Python.*

**apy has an exceptional performance**, integrates the Tornado asynchronous networking library. *Powered by Facebook*. (You can easy-configure other wsgi adapter)

By using non-blocking network I/O, can scale to tens of thousands of open connections, making it ideal for long polling,
and other applications that require a long-lived connection to each user.

-------

**We believe development must be an enjoyable and creative experience to be truly fulfilling.**

**Happy developers make the best code.**


Installation
------------

To install *apy*, simply:

.. code-block:: bash

    $ pip install stagecoach_apy


Documentation
-------------

Documentation is available at http://apy.readthedocs.org/


Compatibility
-------------

apy is fully tested with a *travis* continuous integration on:

- python 2.6
- python 2.7
- pypy
- python 3.2
- python 3.3
- python 3.4

-------

*apy is open-sourced software licensed under the MIT license*
