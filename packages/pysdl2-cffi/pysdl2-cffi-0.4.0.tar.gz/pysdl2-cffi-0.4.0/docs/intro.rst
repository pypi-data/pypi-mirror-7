pysdl2-cffi
===========

The pysdl2-cffi package is a wrapper for libSDL2 (http://www.libsdl.org/)
and its related libraries SDL_image, SDL_mixer, and SDL_ttf, built
using cffi. This package wraps each function in automatically
generated helper functions by following some simple rules, exposing
them under the ``sdl`` namespace without the ``SDL_`` etc.  prefixes.

The Binding Rules
-----------------

- Functions and constants are exposed under the ``sdl``,
  ``sdl.image``, ``sdl.mixer``, and ``sdl.ttf`` namespaces.
- Functions are renamed by removing the ``SDL_`` prefix and lower casing the
  first letter of the function. ``SDL_CreateWindow`` becomes
  ``sdl.createWindow``, ``IMG_LoadTexture`` becomes ``sdl.image.loadTexture``.
- Constants (or anything that has two capital letters after the prefix) are
  renamed by removing the prefix only.  ``SDL_INIT_VIDEO`` becomes
  ``sdl.INIT_VIDEO``, ``MIX_INIT_MP3`` becomes ``sdl.mixer.INIT_MP3``.
- (The original names are available in the ``lib`` submodule of each of the
  ``_sdl``, ``_sdl_image``, ``_sdl_mixer``, ``_sdl_ttf`` modules)
- Functions with primitive-typed out parameters return a tuple of the return
  value (if any) and the value of each out parameter.

    C::

        uint32_t SDL_GetMouseState(int *, int *);

    pysdl2-cffi::

        buttons, x, y = sdl.getMouseState()

        # It is also possible to pass the correct C type to the function:
        x_pointer = sdl.ffi.new('int *')
        y_pointer = sdl.ffi.new('int *')
        buttons, x, y = sdl.getMouseState(x_pointer, y_pointer)
        x[0] == x and y[0] == y

- Structs are exposed as classes that can automatically allocate non-opaque
  structures. For example, SDL_Rect can be allocated by pysdl2-cffi,
  but SDL_Window can only be allocated by calling ``sdl.createWindow()``.
  Structs are exposed without their prefix in the same way as other
  declarations::

    rect = sdl.Rect()
    rect.x = 4
    rect.y = 3
    rect.w = 42
    rect.h = 64

- Structs can accept any valid ffi initializer as their arguments. This also
  works when a function would otherwise require a struct::

    rect = sdl.Rect((4, 3, 42, 64))
    rect2 = sdl.Rect(dict(x=4, y=3, w=42, h=64))

    intersection = sdl.Rect()   # we need to be able to see the result
    intersects = sdl.intersectRect((4,3,42,64), (40,60,10,10), intersection)

- Any function that takes a particular struct as its first argument is also
  a method on the relevant helper class::

    intersects = rect.intersectRect((40,60,10,10), intersection)

- The binding does not try to hook resource management to garbage collection.
  Users should release textures, windows, and so on using the appropriate SDL
  functions or risk leaking resources.

Error Handling
--------------

Most functions in the ``sdl``, ``sdl.image``, and ``sdl.ttf`` libraries check their return
value for errors. If there was an error then an exception ``sdl.SDLError()`` is
thrown. The exception's ``.message`` property holds SDL's own error message as
reported by ``sdl.getError()``::

    >>> sdl.image.load('/tmp/i_dont_exist.png')
    SDLError: Couldn't open /tmp/i_dont_exist.png

The ``sdl.mixer`` library does not currently convert errors to exceptions.

Bugs
----

- Some functions that are probably useless in Python, like string manipulation
  or logging functions, are wrapped anyway. They may be removed later.
