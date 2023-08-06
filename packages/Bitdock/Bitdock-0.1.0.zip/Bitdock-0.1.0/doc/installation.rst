..
    :copyright: Copyright (c) 2014 ftrack

.. _installation:

************
Installation
************

.. highlight:: bash

Installation is simple with `pip <http://www.pip-installer.org/>`_::

    $ pip install bitdock

Building from source
====================

You can also build manually from the source for more control. First obtain a
copy of the source by either downloading the
`zipball <https://bitbucket.org/ftrack/bitdock/get/master.zip>`_ or
cloning the public repository::

    git clone git@bitbucket.org:ftrack/bitdock.git

Then you can build and install the package into your current Python
site-packages folder::

    python setup.py install

Alternatively, just build locally and manage yourself::

    python setup.py build

Building documentation from source
----------------------------------

To build the documentation from source::

    python setup.py build_sphinx

Then view in your browser::

    file:///path/to/bitdock/build/doc/html/index.html

Dependencies
============

* `Python <http://python.org>`_ >= 2.6, < 3
* `CherryPy <http://www.cherrypy.org/>`_ >= 3.2, < 4
* `requests <http://docs.python-requests.org>`_ >= 2.2, < 3'

Additional For testing
----------------------

* `Pytest <http://pytest.org>`_  >= 2.3.5, < 3
