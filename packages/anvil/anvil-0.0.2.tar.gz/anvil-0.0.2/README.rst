Anvil
=====

.. image:: https://pypip.in/version/anvil/badge.png
    :target: https://pypi.python.org/pypi/anvil/
    :alt: Latest Version

.. image:: https://travis-ci.org/dghubble/anvil.png
    :target: https://travis-ci.org/dghubble/anvil
    :alt: Continuous Integration Testing

.. image:: https://pypip.in/download/anvil/badge.png
    :target: https://pypi.python.org/pypi/anvil/
    :alt: Downloads

.. image:: https://pypip.in/license/anvil/badge.png
    :target: https://pypi.python.org/pypi/anvil/
    :alt: License

Anvil generates new project structures from any Jinja template to create projects, apps, packages, plugins, adapters, and more. It provides a simple
API so you can use its functionality to back your own initialization tools
too.

Install
-------

Install Anvil via `pip <https://pip.pypa.io/en/latest/>`_

.. code-block:: bash

    $ pip install anvil

If you want to remove the package later

.. code-block:: bash

    $ pip uninstall anvil

Usage
-----

.. code-block:: bash

    $ anvil
    usage: anvil [-h] [--version]  ...

    Generates project structures from Jinja templates

    optional arguments:
      --version   show version information
      -h, --help  show this help message and exit

    Available subcommands:

        init      initialize structure from a template
        version   show version information

    For subcomamnd help, run `anvil <subcommand> -h`

Documentation
-------------

Documentation is available `here <http://anvil.readthedocs.org/en/latest/>`_.


Contributing
------------

To get the source from Github

.. code-block:: bash

    $ git clone git@github.com:dghubble/anvil.git
    $ cd anvil
    $ pip install -r requirements.txt
    $ python setup.py develop

If you want to remove the development install

.. code-block:: bash

    $ cd anvil
    $ python setup.py develop --uninstall


Testing
-------

.. code-block:: bash

    $ nosetests
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.168s

    OK


Questions, Comments, Contact
----------------------------

If you'd like to contact me, feel free to Tweet to `@dghubble <https://twitter.com/dghubble>`_ or email dghubble@gmail.com.


License
-------

`MIT License <LICENSE>`_ 
