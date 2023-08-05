==========
Deba bōchō
==========

Slice up PDFs like a pro::

    % python bocho.py my-fancy-file.pdf --pages 1 3 5 6 10 --angle 30 --zoom 1.6
    my-fancy-file-bocho-630x290.png

``bocho`` takes a PDF file and creates a "stacked page" preview from a selection of pages.

It accepts a bunch of options for customising the output (pass the ``-h`` flag for details).

Installation
============

Requires ImageMagick and the contents of ``requirements.txt``, e.g::

    % sudo apt-get install imagemagick
    % pip install -r requirements.txt

On OS X, it's a bit more complicated::

    % brew install ghostscript
    % brew install imagemagick
    % ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install --allow-external pyPdf --allow-unverified pyPdf -r requirements.txt


TODO
====

- implement rotation properly ✓
- allow a "zoom" option ✓
- optional drop-shadows (and make the basic edge separators optional also)
- automatic spacing as an option as well as fixed pixel spacing
- horizontal and vertical spacing (currently only horizontal)
- horizontal and vertical offsets ✓
- optional right-to-left stacking ✓
- handle non-A4 aspect ratio input documents ✓
- optionally apply transforms:

  - affine ✓ (basic, subtle, non-configurable)
  - perspective

- ensure sliced PNGs are large enough when custom width / height are specified
- fix x and y spacing calculation to account for any applied transformations
- if an angle is specified, apply the offsets after rotation, not before
- allow transforms to be configurable (probably with presets defined in an
  ``.ini`` file)
- docs
