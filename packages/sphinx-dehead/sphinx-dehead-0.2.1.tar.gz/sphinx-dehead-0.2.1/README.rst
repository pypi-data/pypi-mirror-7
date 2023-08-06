sphinx-dehead
=============

- **Author:** Sean Wallitsch
- **Email:** sean@grenadehop.com
- **License:** MIT
- **Status:** Development
- **Python Versions:** 2.6-2.7

A script to extract the first found `<div class='section'>` from an HTML
document, then save that extracted element to it's own HTML file. Useful when
including an HTML file in another document, when you don't need all the header
junk.

Developed for including Sphinx built HTML documentation in an Octopress blog.

Usage
-----

sphinx-dehead takes a glob style input parameter, and an optional output
directory.

For example, this will dehead every HTML file in the current directory, and
save it to the default output directory, `dehead_output/`

.. code-block:: console

    $ sphinx-dehead './*.html'

While this will save it in the sibling `_docs` directory:

.. code-block:: console

    $ sphinx-dehead './*.html' -d ../_docs/

Installation
------------

sphinx-dehead can be installed with pip:

.. code-block:: console

    $ pip install sphinx-dehead

or by cloning the repository, and from the root directory calling:

.. code-block:: console

    $ python setup.py install

License
-------

    The MIT License (MIT)

    sphinx-dehead
    Copyright (c) 2014 By Sean Wallitsch

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
