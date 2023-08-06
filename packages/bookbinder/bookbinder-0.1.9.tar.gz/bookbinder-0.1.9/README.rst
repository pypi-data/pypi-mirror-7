Book Binder
===========

Book Binder is an ePub generation tool. It generates an ePub book from
Google Documents and/or markdown files located in a Google Drive folder.
When the content of your book is ready at a Google Drive folder (either
as Google Documents or as markdown files) you can use Book Binder to
convert that folder into an ePub. Book Binder requires a metadata file
(in form of a Google Spreadsheet) to be able to successfully populate
the ePub metadata.

Warning
-------
This project is not mature enough and requires a lot of testing. Use it
at your own risk.

Installation
------------

::

  pip install bookbinder

Usage
-----

::

  bookbinder FOLDER-ID

Where ``FOLDER-ID`` is the ID of your Google Drive folder. Once you
authenticate, it will start downloading, processing and packing of the
files. For help, and usage information, type ``bookbinder -h``.

To use Book Binder more effectively, see the project documentation.
Formatting of metadata, use of multiple folders and HTML templates
makes your life easier once you get the grip of it.

Documentation
-------------
Book Binder User Guider is located at http://canpolat.viewdocs.io/bookbinder.
It covers typical usage scenarios and some advanced topics.

License
-------
Copyright (c) 2014 Eren Inan Canpolat

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
