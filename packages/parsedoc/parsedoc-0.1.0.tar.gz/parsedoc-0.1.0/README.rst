===============================
Parsedoc
===============================

.. image:: https://badge.fury.io/py/parsedoc.png
    :target: http://badge.fury.io/py/parsedoc

.. image:: https://travis-ci.org/thomwiggers/parsedoc.png?branch=master
        :target: https://travis-ci.org/thomwiggers/parsedoc

.. image:: https://pypip.in/format/parsedoc/badge.svg
        :target: https://pypi.python.org/pypi/parsedoc/
        :alt: Download format

.. image:: https://pypip.in/license/parsedoc/badge.svg
        :target: https://pypi.python.org/pypi/parsedoc/
        :alt: License

.. image:: https://pypip.in/py_versions/parsedoc/badge.svg
        :target: https://pypi.python.org/pypi/parsedoc/
        :alt: Supported Python versions

.. image:: https://pypip.in/implementation/parsedoc/badge.svg
        :target: https://pypi.python.org/pypi/parsedoc/
        :alt: Supported Python implementations

Parses PHP doc blocks into markdown

Usage
-----

See ``parsedoc --help``.

Features
--------

* Parse PHP files into markdown
* Able to recursively do this for a folder
* Create index files per folder
* Allows to only include certain annotations
* Allows to not write files without comments

Requirements
------------

- Python >= 2.7 or >= 3.3
- Also tested using PyPy
- docopt

Installation
------------

``pip install .`` or ``python setup.py install``.

Licence
-------


    Copyright (C) 2014  Thom Wiggers

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

See the bundled `LICENCE
<https://github.com/thomwiggers/parsedoc/blob/master/LICENCE>`_ file for more
details.
