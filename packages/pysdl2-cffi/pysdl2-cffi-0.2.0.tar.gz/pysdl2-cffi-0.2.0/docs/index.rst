.. pysdl2-cffi documentation master file, created by
   sphinx-quickstart on Tue May 27 14:33:52 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pysdl2-cffi's documentation!
=======================================

pysdl2-cffi is a new wrapper for SDL2 written using cffi, featuring:

- A cffi + dlopen interface to the underlying SDL2 libraries.
- Automatically generated, consistent helper functions for SDL2, SDL_image,
  SDL_mixer, and SDL_ttf that hide most allocation and dereferencing.
- Useful docstrings on every function, including the C function signature and
  (for SDL2 only) the library's original doxygen documentation reformatted as
  Sphinx restructured text.
- A small collection of libSDL2's original example / test programs converted
  to Python using Eric S. Raymond's ctopy.

This library is developed on Linux and OS X; not yet tested on Windows.

This library is licensed under the GPLv2.

Contents:

.. toctree::
   :maxdepth: 2

   intro
   SDL
   SDL_image
   SDL_mixer
   SDL_ttf


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

