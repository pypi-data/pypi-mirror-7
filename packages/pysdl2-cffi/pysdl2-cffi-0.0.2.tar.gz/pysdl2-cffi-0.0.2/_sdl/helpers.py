# This file is mostly from pysdl-cffi.

from __future__ import (print_function, division, absolute_import)

from .cdefs import ffi as _ffi
from .dso import _LIB # XXX should probably use the error-checking ones

################################################################################

def SDL_Init(*args):
    result = _LIB.SDL_Init(*args)
    _LIB.SDL_ClearError()
    return result

def SDL_GetError():
    return _ffi.string(_LIB.SDL_GetError())

def SDL_PollEvent():
    event = _ffi.new('SDL_Event *')
    if not _LIB.SDL_PollEvent(event):
        return None
    return event

def SDL_GetWindowSize(window):
    w = _ffi.new('int *')
    h = _ffi.new('int *')
    _LIB.SDL_GetWindowSize(window, w, h)
    return w[0], h[0]

def SDL_GetMouseState():
    x = _ffi.new('int *')
    y = _ffi.new('int *')
    state = _LIB.SDL_GetMouseState(x, y)
    return state, x[0], y[0]

def SDL_GetCurrentDisplayMode(displayIndex):
    mode = _ffi.new('SDL_DisplayMode *')
    result = _LIB.SDL_GetCurrentDisplayMode(displayIndex, mode)
    if result == 0:
        return mode

def SDL_GetDisplayMode(displayIndex, modeIndex):
    mode = _ffi.new('SDL_DisplayMode *')
    result = _LIB.SDL_GetDisplayMode(displayIndex, modeIndex, mode)
    if result == 0:
        return mode

def SDL_GetDesktopDisplayMode(displayIndex):
    mode = _ffi.new('SDL_DisplayMode *')
    result = _LIB.SDL_GetDesktopDisplayMode(displayIndex, mode)
    if result == 0:
        return mode

def SDL_GetDisplayBounds(displayIndex):
    rect = _ffi.new('SDL_Rect *')
    result = _LIB.SDL_GetDisplayBounds(displayIndex, rect)
    if result == 0:
        return (rect.x, rect.y, rect.w, rect.h)

def SDL_GL_GetAttribute(attr):
    value = _ffi.new('int *')
    _LIB.SDL_GL_GetAttribute(attr, value)
    return value[0]

def SDL_GetClipboardText():
    if not SDL_HasClipboardText():
        return None
    text = _LIB.SDL_GetClipboardText()
    if text == _ffi.NULL:
        return None
    result = _ffi.string(text)
    #SDL_free(text)
    return result

def SDL_JoystickName(joystick):
    name = _LIB.SDL_JoystickName(joystick)
    if name == _ffi.NULL:
        return None
    return _ffi.string(name)
