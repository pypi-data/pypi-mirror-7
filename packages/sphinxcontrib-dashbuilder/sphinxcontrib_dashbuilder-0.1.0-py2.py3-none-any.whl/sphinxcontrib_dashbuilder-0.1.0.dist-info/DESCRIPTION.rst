`sphinxcontrib_dashbuilder` generate a 'Documentation Set' intended to be used with the `dash API browser` from a Sphinx documentation.

You can read the 'Documentation Set' style document by using `dash API browser`.

* For Mac OS X users: dash_
* For Windows or Linux users: Zeal_

This extension has been inspired by doc2dash_

.. _dash: http://kapeli.com/dash
.. _Zeal: http://zealdocs.org/
.. _doc2dash: https://pypi.python.org/pypi/doc2dash

Features
==========

Implemented:

* Generate a 'Documentation Set' for dash API browser.


Not Implemented yet:

* Keyword indexing with Sphinx i18n translated documentation.
* Disable sidebar
* Table of contents support http://kapeli.com/docsets#tableofcontents


Install
========

::

   $ pip install sphinxcontrib-dashbuilder


If you wanto to use unrelease version, you can install from repository::

   $ pip install -e hg+https://bitbucket.org/shimizukawa/sphinxcontrib-dashbuilder


Configuration
================

conf.py configuration values:

:dash_name:
   (optional) name for docset explicitly. default is same as `project`.
:dash_icon_file:
   (optional) PNG file path for docset icon.
:dash_translator_class:
   (optional) A string with the fully-qualified name of a
   Dash Translator class, that is, a subclass of Sphinx' DashTranslator,
   that is used to translate document trees to HTML for Dash.
   Default is None (use the builtin translator).


conf.py example::

   extensions = ['sphinxcontrib.dashbuilder']

   dash_name = 'Python_3'
   dash_icon_file = '_static/python.png'


Run
======

run::

   $ sphinx-build -b dash [source] [outdir]

and you get dash documentation set under '_build/dash/' directory.


