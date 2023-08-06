Changelog
=========

2.4.0 - September 1, 2014
-------------------------

- Use pyramid_sqlalchemy instead of s4u.sqlalchemy.


2.3.2 - May 2, 2014
-------------------

- Fix error in image scaling: open source image in read-mode, not write mode.


2.3.1 - April 30, 2014
----------------------

- Swallow errors when trying to delete a missing file.


2.3.0 - December 20, 2013
-------------------------

- Add support for Python 3


2.2.0 - December 5, 2013
------------------------

- Add API to initialise filesystem paths.


2.1.0 - November 29, 2013
-------------------------

- Add a `delete` method to the Image class.

- Add a `replace_content` method to the Image class, which can be used to
  modify the image.

- Fix URL for pyramid documentation.

- Use `tempfile.gettempdir()
  <http://docs.python.org//library/tempfile#tempfile.gettempdir>`_ to get the
  temporary directory for tests instead of hardcoding ``/tmp/``.


2.0.1 - January 8, 2013
-----------------------

- First public release.


2.0 - September 14, 2012
------------------------

- Add a new URL column to images and extend API to support remote images.

- Use Pillow instead of PIL.


2.0a3 - August 3, 2012
----------------------

- Fix bug in image scale generation which ignored the whitespace option.
  Thanks to Jason for catching this.

2.0a2 - August 3, 2012
----------------------

- Fix error in storing image scale parameters.


2.0a1 - August 3, 2012
----------------------

- Add option to remove whitespace surrounding an image.


1.4 - February 28, 2012
-----------------------

- Add support for hosting images via a separate URL.


1.3 - November 30, 2011
-----------------------

- Add a better index for index for the image scale table.


1.2 - October 14, 2011
----------------------

- Add support for s4u.upgrade: add an upgrade step to create the image
  directories.

- Only use 16 top-level directories; 256 was a bit too much.


1.1 - September 28, 2011
------------------------

- Move minimal image data to s4u.image.testing to promote reuse by other
  packages.

- Register a static view for Pyramid to serve image data.


1.0 - August 8, 2011
--------------------

- First version.
