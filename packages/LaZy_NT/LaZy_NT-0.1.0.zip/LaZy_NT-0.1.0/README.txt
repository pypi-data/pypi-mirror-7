===========
LaZy_NT
===========

LaZy_NT is a forensic analysis and data recovery framework designed to carve
files from raw disk images. It uses file signatures and other techniques to
recover as much of the original data as possible.

The feature that sets this software apart from more well-known file carving
utilties is  that it was designed to detect and carve files that have been
compressed by the NTFS file system. NTFS supports compression of individual
files, folders or entire volumes using the proprietary 'LZNT1' algorithm, from
which this package derives its name. While processing a disk image, if NTFS
compression is detected, LaZy_NT will decompress the data stream on the fly to
ensure that the correct file data is recovered.

In addition to standard file carving, LaZy_NT provides a rudimentary bulk
ASCII extraction capability to support forensic investigation. When enabled,
this mode will decompress and extract all ASCII text data and evaluate it to
identify email addresses, URLs, and other personal or forensically interesting
information.

LaZy_NT operates normally on files and volumes which have not been compressed,
and on images of non-NTFS file systems. However under those circumstances the
recovery performance may not be as good as a combination of more well known
file carving and bulk extraction utilities.

Usage
=====

The simplest way to invoke the pre-made application is to call the ``run()``
method of the ``App`` class within the ``app`` module. The following example
demonstrates how this canbe implemented as a simple launcher script::

    #!python
    from LaZy_NT import app
    ...
    # Obtain command line arguments, e.g. via argparse, to pass to App() as
    # keyword arguments. Otherwise defaults from `config` will be used.
    ...
    application = app.App()
    application.run()

Alternatively, the API exposed by LaZy_NT can be used to build a more
customized file recovery application, without using the ``app`` module
at all.

Installation
============
``LaZy_NT`` is available on PyPI and installable via ``pip``::

    python -m pip install LaZy_NT

The following optional dependencies enhance LaZy_NT by adding metadata
extraction for files after they've been carved::

    hachoir-core, hachoir-parser, hacoir-metadata
    openxmllib
    pyPdf
    Pillow (or PIL)

All optional dependencies will be installed automatically if ``LaZy_NT``
is installed through ``pip``.

Documentation
=============
Documentation for ``LaZy_NT`` was generated using ``pdoc``.

Acknowledgements
================
I would like to recognize Richard Russon and Yuval Fledel, authors of the
'NTFS Documentation' manual associated with the Linux NTFS filesystem driver.
Without their detailed explanation of the LZNT1 algorithm, this project would
not have been possible.

I would also like to recognize Simson L. Garfinkel, designer of the well known
'Bulk Extractor' utility. While I have not viewed or used any of his source
code or documentation in this project, the use of his utility was what inspired
me to add ASCII extraction capabilities to this project.