#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# DXT1/3/5 Decompressor
# Version 0.1
# Copyright © 2018 MasterVermilli0n / AboodXD

################################################################
################################################################

import importlib

from . import decompress as _decompress


_native = None
_native_checked = False
_native_disabled = False


def _get_native():
    global _native, _native_checked
    if not _native_checked and not _native_disabled:
        _native_checked = True
        try:
            _native = importlib.import_module("berrybush_bcn_native")
        except Exception:
            _native = None
    return _native


def _native_or_python(name, data, width, height, *args):
    global _native, _native_disabled
    native = _get_native()
    if native is not None:
        try:
            result = getattr(native, name)(data, width, height, *args)
            expected = width * height * 4
            if isinstance(result, (bytes, bytearray)) and len(result) == expected:
                return bytes(result)
        except Exception:
            # A broken optional wheel must never make import/export fail.
            _native = None
            _native_disabled = True
    return getattr(_decompress, name)(data, width, height, *args)


def decompressDXT1(data, width, height):
    if not isinstance(data, bytes):
        try:
            data = bytes(data)

        except Exception:
            print("Couldn't decompress data")
            return b''

    csize = ((width + 3) // 4) * ((height + 3) // 4) * 8
    if len(data) < csize:
        print("Compressed data is incomplete")
        return b''

    data = data[:csize]
    return _native_or_python("decompressDXT1", data, width, height)


def decompressDXT3(data, width, height):
    if not isinstance(data, bytes):
        try:
            data = bytes(data)

        except Exception:
            print("Couldn't decompress data")
            return b''

    csize = ((width + 3) // 4) * ((height + 3) // 4) * 16
    if len(data) < csize:
        print("Compressed data is incomplete")
        return b''

    data = data[:csize]
    return _native_or_python("decompressDXT3", data, width, height)


def decompressDXT5(data, width, height):
    if not isinstance(data, bytes):
        try:
            data = bytes(data)

        except Exception:
            print("Couldn't decompress data")
            return b''

    csize = ((width + 3) // 4) * ((height + 3) // 4) * 16
    if len(data) < csize:
        print("Compressed data is incomplete")
        return b''

    data = data[:csize]
    return _native_or_python("decompressDXT5", data, width, height)


def decompressBC4(data, width, height, SNORM=0):
    if not isinstance(data, bytes):
        try:
            data = bytes(data)

        except Exception:
            print("Couldn't decompress data")
            return b''

    csize = ((width + 3) // 4) * ((height + 3) // 4) * 8
    if len(data) < csize:
        print("Compressed data is incomplete")
        return b''

    data = data[:csize]
    return _native_or_python("decompressBC4", data, width, height, SNORM)


def decompressBC5(data, width, height, SNORM=0):
    if not isinstance(data, bytes):
        try:
            data = bytes(data)

        except Exception:
            print("Couldn't decompress data")
            return b''

    csize = ((width + 3) // 4) * ((height + 3) // 4) * 16
    if len(data) < csize:
        print("Compressed data is incomplete")
        return b''

    data = data[:csize]
    return _native_or_python("decompressBC5", data, width, height, SNORM)


def nativeAvailable() -> bool:
    """Whether the optional validated native decoder is active."""
    return _get_native() is not None


def reloadNative() -> bool:
    """Re-scan for a wheel installed after addon startup."""
    global _native, _native_checked, _native_disabled
    _native = None
    _native_checked = False
    _native_disabled = False
    return nativeAvailable()
