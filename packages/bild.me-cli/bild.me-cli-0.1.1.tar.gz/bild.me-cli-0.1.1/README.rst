bild.me-cli
===========

|Build| |PyPI version|

CLI tool for bild.me.


* GitHub: https://github.com/mozillazg/bild.me-cli
* Free software: MIT license
* PyPI: https://pypi.python.org/pypi/bild.me-cli
* Python version: 2.6, 2.7, pypy, 3.3, 3.4


Installation
------------

To install bild.me-cli, simply:

.. code-block:: bash

    $ pip install bild.me-cli


Usage
------

.. code-block:: console

    $ bild -f test1.png test2.png
    test1.png: [==================================================>]
    http://s1.bild.me/bilder/260513/4053120test1.png
    test2.png: [==================================================>]
    http://s1.bild.me/bilder/260513/1932235test2.png

    $ bild -q -f test1.png test2.png
    http://s1.bild.me/bilder/260513/3599206test2.png
    http://s1.bild.me/bilder/260513/8204314test1.png

    $ bild -qf *.png
    http://s1.bild.me/bilder/260513/3041575test2.png
    http://s1.bild.me/bilder/260513/6296743test1.png

    $ bild -h
    usage: bild [-h] [-V] [-l] [-q] -f FILE [FILE ...]

    CLI tool for bild.me.

    optional arguments:
      -h, --help            show this help message and exit
      -V, --version         show program's version number and exit
      -l, --list            list all result
      -q, --quiet           decrease verbosity
      -f FILE [FILE ...], -F FILE [FILE ...], --file FILE [FILE ...]
                            picture file path, support Unix shell-style wildcards


.. |Build| image:: https://api.travis-ci.org/mozillazg/bild.me-cli.png?branch=master
   :target: https://travis-ci.org/mozillazg/bild.me-cli
.. |PyPI version| image:: https://pypip.in/v/bild.me-cli/badge.png
   :target: https://crate.io/packages/bild.me-cli
