=============
codevalidator
=============

Simple source code validator with file reformatting option (remove trailing WS, pretty print XML, ..).

For Python code formatting it can either use autopep8_ or the builtin copy of PythonTidy.

Requirements
------------

* Python 2.7+
* lxml_ (for XML formatting)
* pep8_ (for Python checking)
* autopep8_ (for Python formatting)
* pyflakes_ (for static Python code checking)
* Jalopy_ (for Java code formatting)
* coffeelint (for CoffeeScript validation)
* PHP_CodeSniffer (for PHP style checking)
* Puppet (for Puppet manifest validation)
* sqlparse
* jshint (for JavaScript checking)
* PyYAML (for YAML checking)

On Ubuntu you can install most packages easily::

    sudo apt-get install python-lxml pep8 pyflakes nodejs npm
    sudo npm install -g jshint

Installation
------------

There are at least two ways of installing codevalidator:

* Alternative 1: Use the codevalidator source tree directly (i.e. clone the GIT repo and put codevalidator.py in your ``PATH``)::

    git clone https://github.com/hjacobs/codevalidator.git
    sudo ln -s codevalidator/codevalidator.py /usr/local/bin/codevalidator.py

* Alternative 2: Install codevalidator from PyPI using PIP::

    sudo pip install codevalidator

Getting Started
---------------

Validating test files with builtin default configuration::

    ./codevalidator.py test/*

Fixing test files (removing trailing whitespace, XML format)::

    ./codevalidator.py -f test/*

Using custom configuration file::

    ./codevalidator.py -c test/config.json test/*

Validate and fix a whole directory tree::

    ./codevalidator.py -c myconfig.json -rf /path/to/mydirectory

Validate a single PHP file and print detailed error messages (needs PHP_CodeSniffer with PSR standards installed!)::

    ./codevalidator.py -v test/test.php

Running in very verbose (debug) mode to see what is validated::

    ./codevalidator.py -vvrc test/config.json test

Using the filter mode to "fix" stdin and write to stdout::

    echo 'print 1' | ./codevalidator.py --fix --filter foobar.py && echo success

If you are annoyed by the .XX.pre-cvfix backup files you can disable them either on the command line (``--no-backup``) or in the config file.

Advanced Usages
---------------

You can use the ``--fix --filter`` combination to directly filter your current buffer in VIM::

    :%!codevalidator.py --fix --filter %

The ``--fix --filter`` was also designed to be used with `GIT filters`_.

To apply a formatting rule once without changing you configuration file, you can use the ``-a`` option. Formatting a Python file once with the ``pythontidy`` rule looks like::

    ./codevalidator.py -a pythontidy myfile.py


Known Issues
------------

* PythonTidy cannot parse `dict comprehensions`_. As a workaround you can use list comprehensions and wrap it with ``dict``.

.. _lxml:                 http://lxml.de/
.. _pep8:                 https://pypi.python.org/pypi/pep8
.. _autopep8:             https://pypi.python.org/pypi/autopep8
.. _pyflakes:             https://pypi.python.org/pypi/pyflakes
.. _Jalopy:               http://www.triemax.com/products/jalopy/
.. _dict comprehensions:  http://www.python.org/dev/peps/pep-0274/
.. _GIT filters:          https://www.kernel.org/pub/software/scm/git/docs/gitattributes.html
