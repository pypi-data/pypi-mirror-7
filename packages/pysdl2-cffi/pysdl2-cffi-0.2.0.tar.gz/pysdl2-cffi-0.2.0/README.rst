An SDL2 wrapper made with cffi. Faster on pypy.

Adapted from headers & wrapper functions from
libSDL2,
https://github.com/torch/sdl2-ffi,
https://bitbucket.org/duangle/pysdl-cffi, and
PySDL2.

The goal is to provide a flat, consistent, faithful-to-C binding with some
more-Pythonic renaming and conveniences.

This wrapper won't contain anything that doesn't directly translate to part of
the library's API. The goal is to be a dependency for something like pygame,
not a replacement.
