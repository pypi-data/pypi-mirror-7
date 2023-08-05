An SDL2 wrapper made with cffi. Faster on pypy.

Adapted from headers & wrapper functions from
libSDL2,
https://github.com/torch/sdl2-ffi,
https://bitbucket.org/duangle/pysdl-cffi, and
PySDL2.

My goal is to preserve a flat, faithful-to-C view of the SDL API, then make
it more Pythonic by removing the SDL_ prefix, renaming each SDL_FunctionName to
sdl.functionName, leaving the enum's capitalized. The wrapper will also
convert "out" parameters (most of the time (int *) or other pointer arguments
are passed) to returned tuples, and it will convert SDL_GetError() to an
exception.

It does not yet do all of these things.

This wrapper won't contain anything that doesn't directly translate to part of
the library's API. The goal is to be a dependency for something like pygame,
not a replacement.
