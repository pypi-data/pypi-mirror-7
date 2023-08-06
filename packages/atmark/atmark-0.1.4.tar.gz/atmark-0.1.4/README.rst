The Atmark
##########

.. _description:

The Atmark -- Awk+sed for humans.

Do this: ::

    # Rename a files in current directory (file-name -> file_name.jpg)
    $ ls | @ replace - _ "mv # @.jpg" | sh

Except this: ::

    # Rename a files in current directory (file-name -> file_name.jpg)
    $ ls | awk '{print $1 $1}' | sed s/"-"/"_"/ | awk '{print "mv", $2, $1, ".jpg"}' | sh


More deep: ::

    $ ls | @  replace   -   _   "mv # @.jpg" | sh
              -------   |   |   ------------
                |       |   |       \_ format string (# - link on first state,
                |       |   |                         @ - link on current state (after replace))
                |       |   |
                |       |    \_ second replace param (to replace)
                |       |
                |        \_ first replace param (what replace)
                |
                 \_ function name (replace)

More examples:

Change file's extension .html > .php ::

    # Atmark
    $ ls | @ split . head "mv # @.php"

    # Awk/Sed
    $ ls | awk '{printf "mv "$0; sub(/html/,"php"); print " "$0}' | sh


Print all but the first three columns ::

    # Atmark
    $ ls -la | @ split_ drop 3 join_

    # Awk/Sed
    $ ls -la | awk '{for(i=1;i<4;i++) $i="";print}'


Kill process by name ::

    # Atmark
    $ ps aux | @ grep sysmond$ index 2 "kill @" | sh 

    # Awk/Sed
    $ ps aux | grep [s]ysmond | awk '{print "kill "$2}' | sh


And more, more, more.

.. _badges:

.. image:: https://secure.travis-ci.org/klen/atmark.png?branch=develop
    :target: http://travis-ci.org/klen/atmark
    :alt: Build Status

.. image:: https://coveralls.io/repos/klen/atmark/badge.png?branch=develop
    :target: https://coveralls.io/r/klen/atmark?branch=develop

.. image:: https://pypip.in/d/atmark/badge.png
    :target: https://pypi.python.org/pypi/atmark

.. image:: https://badge.fury.io/py/atmark.png
    :target: http://badge.fury.io/py/atmark

.. _documentation:

.. **Docs are available at https://atmark.readthedocs.org/. Pull requests
.. with documentation enhancements and/or fixes are awesome and most welcome.**

.. _contents:

.. contents::

.. _requirements:

Requirements
=============

- python >= 2.6

.. _installation:

Installation
=============

**The Atmark** should be installed using pip: ::

    pip install atmark

.. _usage:

Usage
=====

::

    $ @ --help

    Atmark (@) -- is a command line utility for parsing text input and generating output.

    You can pipe data within a Atmark (@) statement using standard unix style pipes ("|").
    Provide for Atmark function composition and let them work for you.

    Example. Replace "_" with "-" in files in current dir and change the files extensions to jpg:

        $ ls | @ replace _ -  split . "mv # @.jpg"

    It is mean:

        $ ls > replace($LINE, "_", "-") > split($RESULT, ".") > format($RESULT, "mv $LINE $RESULT.jpg")

    You can use "@ --debug ARGS" for debug Armark commands.

    ===================================================================================
    LIST OF THE BUILT IN FUNCTIONS

    format PATTERN -- format and print a string.

        Symbol '#' in PATTERN represents the line of the input (before pipe "|").
        Symbol '@' in PATTERN represents the current value in process of composition of fuctions.

        Synonyms: You can drop `format` function name. This lines are equalent:

            $ ls | @ upper format "@.BAK"
            $ ls | @ upper "@.BAK" 

    capitalize/c -- capitalize the string. 

    drop N -- drop N elements from list/string. 

    filter/if -- filter results by value has length 

    grep/g REGEXP -- filter results by REGEXP 

    head/h -- extract the first element/character of a list/string 

    index/ix/i N -- get the N-th element/character from list/string. 

    join/j SEPARATOR -- concatenate a list/string with intervening occurrences of SEPARATOR 

    join_/j_ -- same as join but SEPARATOR set as ' ' 

    last -- get last element/character of incoming list/string. 

    length/len -- return length of list/string. 

    lower/l -- make the string is lowercase 

    replace/r FROM TO -- replace in a string/list FROM to TO. 

    reverse -- reverse list/string. 

    rstrip/rs PATTERN -- return the string with trailing PATTERN removed. 

    sort -- sort list/string. 

    split/sp SEPARATOR -- return a list of the substrings of the string splited by SEPARATOR 

    split_/sp_ -- same as split by splited a string by whitespace characters 

    strip/s PATTERN -- return the string with leading and trailing PATTERN removed. 

    tail/t -- extract the elements after the head of a list 

    take N -- take N elements from list/string. 

    upper/u -- make the string is uppercase 


.. _bugtracker:

Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/atmark/issues

.. _contributing:

Contributing
============

Development of starter happens at github: https://github.com/klen/atmark


Contributors
=============

* klen_ (Kirill Klenov)

.. _license:

License
========

Licensed under a `BSD license`_.

.. _links:

.. _BSD license: http://www.linfo.org/bsdlicense.html
.. _klen: http://klen.github.com/


