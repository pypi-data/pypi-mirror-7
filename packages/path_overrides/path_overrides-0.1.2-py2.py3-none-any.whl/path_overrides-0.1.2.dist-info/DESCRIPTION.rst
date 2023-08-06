Path Overrides
==============

Detects executables which 'override' other executables in the system PATH.

Install
-------

``path_overrides`` has been tested on recent OS X and Linux systems. It should work on any POSIX system.

To install, simply run::

    $ pip install --user path_overrides

or similar.  Installing the Python package ``blessings`` is recommended to provide colourised output, but is not required.

Use
---

Run ``path_overrides``. It will display a list of which executables shadow other (different) executables.

Motivation
----------

If I press the 'tab' key a couple of times on a recent Linux or OS X shell, I get a prompt looking something like::

    Display all 2228 possibilities? (y or n)

There are over 2000 commands all ready and waiting to be run at a single word being entered. And these don't all live in one place; they live in a (typically small) number of different locations, which are listed in the ``PATH`` environment variable. ``PATH`` is an ordered sequence of paths which are searched to find an executable which will be run. This works well for the most part, but as with all things where there isn't a single namespace, collisions happen. There could be a number of items all with the same name living in different paths all in ``PATH``. In normal use this isn't a problem; ``PATH`` is ordered, and each part of it is a unique no-collisions-possible directory. There is never non-determinism about which executable will 'win', and the ``which`` shell program will report on 'which' path has precedence.

However, unless you are in the habit of regularly running ``which`` before executing any command - or only ever run commands with absolute pathnames - there can be surprises; if someone places a executable earlier in the ``PATH`` than the one you would expect to be run, it will take precendence. ``path_overrides`` will report on any command which overrides a *different* command later in the ``PATH``. Note it's quite common to have symlinks from (e.g.) ``/usr/bin`` to programs in ``/bin``; since they represent 'the same command', ``path_overrides`` will ignore these.

Example
-------

This is a run of ``path_overrides`` on an OS X machine, currently working in a virtualenv. If ``blessings`` is installed, the output will be colourised.

::

    ben$ path_overrides 
    /Users/ben/.virtualenvs/path_overrides/bin/python overrides /usr/bin/python
    /Users/ben/.virtualenvs/path_overrides/bin/easy_install overrides /usr/bin/easy_install
    /Users/ben/.virtualenvs/path_overrides/bin/python2.7 (python) overrides /usr/bin/python2.7 (../../System/Library/Frameworks/Python.framework/Versions/2.7/bin/python2.7)
    /Users/ben/.virtualenvs/path_overrides/bin/easy_install-2.7 overrides /usr/bin/easy_install-2.7
    /Users/ben/.virtualenvs/path_overrides/bin/pip overrides /usr/local/bin/pip
    /Library/Frameworks/Python.framework/Versions/3.4/bin/2to3 (2to3-3.4) overrides /usr/bin/2to3
    /usr/bin/ndisasm overrides /usr/local/bin/ndisasm (../Cellar/nasm/2.11.02/bin/ndisasm)
    /usr/bin/2to3 overrides /usr/local/bin/2to3 (../../../Library/Frameworks/Python.framework/Versions/3.4/bin/2to3)
    /usr/bin/nasm overrides /usr/local/bin/nasm (../Cellar/nasm/2.11.02/bin/nasm)
    /usr/local/bin/libpng-config (../Cellar/libpng/1.6.10/bin/libpng-config) overrides /opt/X11/bin/libpng-config (libpng15-config)
    /usr/local/bin/fc-match (../Cellar/fontconfig/2.11.1/bin/fc-match) overrides /opt/X11/bin/fc-match
    /usr/local/bin/fc-list (../Cellar/fontconfig/2.11.1/bin/fc-list) overrides /opt/X11/bin/fc-list
    /usr/local/bin/fc-cat (../Cellar/fontconfig/2.11.1/bin/fc-cat) overrides /opt/X11/bin/fc-cat
    /usr/local/bin/fc-cache (../Cellar/fontconfig/2.11.1/bin/fc-cache) overrides /opt/X11/bin/fc-cache
    /usr/local/bin/fc-scan (../Cellar/fontconfig/2.11.1/bin/fc-scan) overrides /opt/X11/bin/fc-scan
    /usr/local/bin/freetype-config (../Cellar/freetype/2.5.3_1/bin/freetype-config) overrides /opt/X11/bin/freetype-config
    /usr/local/bin/fc-validate (../Cellar/fontconfig/2.11.1/bin/fc-validate) overrides /opt/X11/bin/fc-validate
    /usr/local/bin/fc-query (../Cellar/fontconfig/2.11.1/bin/fc-query) overrides /opt/X11/bin/fc-query
    /usr/local/bin/fc-pattern (../Cellar/fontconfig/2.11.1/bin/fc-pattern) overrides /opt/X11/bin/fc-pattern

@codedstructure 2014


