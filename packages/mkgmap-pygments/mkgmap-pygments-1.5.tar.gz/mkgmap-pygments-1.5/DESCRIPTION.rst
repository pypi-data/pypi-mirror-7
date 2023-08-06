A pygments lexer for mkgmap style files
=======================================

This package installs a new lexer for pygmentize to syntax highlight
mkgmap_ style files.  You can then use pygmentize (or the API) with the
lexer 'mkgmap' to highlight style files.

.. _mkgmap: http://www.mkgmap.org.uk

Installing this package will install pygments if it not already
installed::

  pip install mkgmap-pygments

Usage
-----

To just display a file to the terminal::

  pygmentize -l mkgmap lines

To create a complete html file::

  pygmentize -l mkgmap -f html -Ofull=true -o output.html lines


Style
=====

The package also includes a pygments style named `mkgmap`.

You might prefer it to the default style as it will be used in
the mkgmap manual and website.

To create a complete html file using the mkgmap style::

  pygmentize -l mkgmap -f html -Ofull=true,style=mkgmap -o output.html lines
