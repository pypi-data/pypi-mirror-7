================================
 OpenSlides Topic Voting Plugin
================================

Overview
========

This plugin for OpenSlides features a structured voting on topics using the
Sainte-Laguë method.


Requirements
============

OpenSlides 1.6.x (http://openslides.org/)


Install
=======

This is only an example instruction to install the plugin on GNU/Linux. It
can also be installed as any other python package and on other platforms,
e. g. on Windows.

Change to a new directory::

    $ cd

    $ mkdir OpenSlides

    $ cd OpenSlides

Setup and activate a virtual environment and install OpenSlides and the
plugin in it::

    $ virtualenv .virtualenv

    $ source .virtualenv/bin/activate

    $ pip install "openslides>=1.6,<1.7" openslides-topicvoting

Start OpenSlides::

    $ openslides


License and authors
===================

This plugin is Free/Libre Open Source Software and distributed under the
MIT License, see LICENSE file. The authors are mentioned in the AUTHORS file.


Changelog
=========

Version 1.1.0 (2014-06-05)
--------------------------
* Updated to new plugin api and to other api changes of OpenSlides 1.6
  (slides, urls, views, widget and main menu entry).
* Added winners as list to result view and slide.
* Added list of all results for print.
* Added csv import.
* Changed several template files and updated some code styling stuff.


Version 1.0 (2014-01-04)
------------------------
* First release of this plugin.
