#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BC3 Compressor/Decompressor
# Version 0.1
# Copyright © 2018 MasterVermilli0n / AboodXD

# decompress_.py
# A BC3/DXT5 decompressor in Python based on libtxc_dxtn.

################################################################
################################################################


def ToSigned8(v):
    if v > 255:
        return -1

    elif v < 0:
        return 0

    elif v > 127:
        return v - 256

    return v


def ToUnsigned8(v):
    if v > 127:
        return 127

    elif v < -128:
        return 128

    elif v < 0:
        return v + 256

    return v


def EXP5TO8R(packedcol):
    return (((packedcol) >> 8) & 0xf8) | (((packedcol) >> 13) & 0x07)


def EXP6TO8G(packedcol):
    return (((packedcol) >> 3) & 0xfc) | (((packedcol) >>  9) & 0x03)


def EXP5TO8B(packedcol):
    return (((packedcol) << 3) & 0xf8) | (((packedcol) >>  2) & 0x07)


def EXP4TO8(col):
    return col | col << 4


def dxt135_decode_imageblock(pixdata, img_block_src, i, j, dxt_type):
    color0 = pixdata[img_block_src] | (pixdata[img_block_src + 1] << 8)
    color1 = pixdata[img_block_src + 2] | (pixdata[img_block_src + 3] << 8)
    bits = pixdata[img_block_src + 4] | (pixdata[img_block_src + 5] << 8) |      \
        (pixdata[img_block_src + 6] << 16) | (pixdata[img_block_src + 7] << 24)

    bit_pos = 2 * (j * 4 + i)
    code = (bits >> bit_pos) & 3

    ACOMP = 255
    if code == 0:
        RCOMP = EXP5TO8R(color0)
        GCOMP = EXP6TO8G(color0)
        BCOMP = EXP5TO8B(color0)

    elif code == 1:
        RCOMP = EXP5TO8R(color1)
        GCOMP = EXP6TO8G(color1)
        BCOMP = EXP5TO8B(color1)

    elif code == 2:
        if color0 > color1:
            RCOMP = ((EXP5TO8R(color0) * 2 + EXP5TO8R(color1)) // 3)
            GCOMP = ((EXP6TO8G(color0) * 2 + EXP6TO8G(color1)) // 3)
            BCOMP = ((EXP5TO8B(color0) * 2 + EXP5TO8B(color1)) // 3)

        else:
            RCOMP = ((EXP5TO8R(color0) + EXP5TO8R(color1)) // 2)
            GCOMP = ((EXP6TO8G(color0) + EXP6TO8G(color1)) // 2)
            BCOMP = ((EXP5TO8B(color0) + EXP5TO8B(color1)) // 2)

    elif code == 3:
        if dxt_type > 1 or color0 > color1:
            RCOMP = ((EXP5TO8R(color0) + EXP5TO8R(color1) * 2) // 3)
            GCOMP = ((EXP6TO8G(color0) + EXP6TO8G(color1) * 2) // 3)
            BCOMP = ((EXP5TO8B(color0) + EXP5TO8B(color1) * 2) // 3)

        else:
            RCOMP = 0
            GCOMP = 0
            BCOMP = 0

            if dxt_type == 1:
                ACOMP = 0

    return ACOMP, RCOMP, GCOMP, BCOMP


def dxt5_decode_alphablock(pixdata, blksrc, i, j):
    alpha0 = pixdata[blksrc]
    alpha1 = pixdata[blksrc + 1]

    bits = (pixdata[blksrc] | (pixdata[blksrc + 1] << 8) |                    \
            (pixdata[blksrc + 2] << 16) | (pixdata[blksrc + 3] << 24) |       \
            (pixdata[blksrc + 4] << 32) | (pixdata[blksrc + 5] << 40) |       \
            (pixdata[blksrc + 6] << 48) | (pixdata[blksrc + 7] << 56)) >> 16

    for y in range(4):
        for x in range(4):
            if (x, y) == (i, j):
                code = bits & 0x07
                break

            bits >>= 3

    if code == 0:
        ACOMP = alpha0

    elif code == 1:
        ACOMP = alpha1

    elif alpha0 > alpha1:
        ACOMP = (alpha0 * (8 - code) + (alpha1 * (code - 1))) // 7

    elif code < 6:
        ACOMP = (alpha0 * (6 - code) + (alpha1 * (code - 1))) // 5

    elif code == 6:
        ACOMP = 0

    else:
        ACOMP = 255

    return ACOMP


def dxt5_decode_alphablock_signed(pixdata, blksrc, i, j):
    alpha0 = pixdata[blksrc]
    alpha1 = pixdata[blksrc + 1]

    bits = (pixdata[blksrc] | (pixdata[blksrc + 1] << 8) |                    \
            (pixdata[blksrc + 2] << 16) | (pixdata[blksrc + 3] << 24) |       \
            (pixdata[blksrc + 4] << 32) | (pixdata[blksrc + 5] << 40) |       \
            (pixdata[blksrc + 6] << 48) | (pixdata[blksrc + 7] << 56)) >> 16

    for y in range(4):
        for x in range(4):
            if (x, y) == (i, j):
                code = bits & 0x07
                break

            bits >>= 3

    if code == 0:
        ACOMP = alpha0

    elif code == 1:
        ACOMP = alpha1

    elif ToSigned8(alpha0) > ToSigned8(alpha1):
        ACOMP = ToUnsigned8((ToSigned8(alpha0) * (8 - code) + (ToSigned8(alpha1) * (code - 1))) // 7)

    elif code < 6:
        ACOMP = ToUnsigned8((ToSigned8(alpha0) * (6 - code) + (ToSigned8(alpha1) * (code - 1))) // 5)

    elif code == 6:
        ACOMP = 0x80

    else:
        ACOMP = 0x7f

    return ACOMP


def fetch_2d_texel_rgba_dxt1(srcRowStride, pixdata, i, j):
    blksrc = ((srcRowStride + 3) // 4 * (j // 4) + (i // 4)) * 8
    ACOMP, RCOMP, GCOMP, BCOMP = dxt135_decode_imageblock(pixdata, blksrc, i & 3, j & 3, 1)

    return RCOMP, GCOMP, BCOMP, ACOMP


def fetch_2d_texel_rgba_dxt3(srcRowStride, pixdata, i, j):
    blksrc = ((srcRowStride + 3) // 4 * (j // 4) + (i // 4)) * 16
    ACOMP, RCOMP, GCOMP, BCOMP = dxt135_decode_imageblock(pixdata, blksrc + 8, i & 3, j & 3, 2)

    anibble = (pixdata[blksrc + ((j & 3) * 4 + (i & 3)) // 2] >> (4 * (i & 1))) & 0xf
    ACOMP = EXP4TO8(anibble)

    return RCOMP, GCOMP, BCOMP, ACOMP


def fetch_2d_texel_rgba_dxt5(srcRowStride, pixdata, i, j):
    blksrc = ((srcRowStride + 3) // 4 * (j // 4) + (i // 4)) * 16

    ACOMP = dxt5_decode_alphablock(pixdata, blksrc, i & 3, j & 3)
    _, RCOMP, GCOMP, BCOMP = dxt135_decode_imageblock(pixdata, blksrc + 8, i & 3, j & 3, 2)

    return RCOMP, GCOMP, BCOMP, ACOMP


def fetch_2d_texel_r_bc4(srcRowStride, pixdata, i, j):
    blksrc = ((srcRowStride + 3) // 4 * (j // 4) + (i // 4)) * 8
    RCOMP = dxt5_decode_alphablock(pixdata, blksrc, i & 3, j & 3)

    return RCOMP


def fetch_2d_texel_r_bc4_snorm(srcRowStride, pixdata, i, j):
    blksrc = ((srcRowStride + 3) // 4 * (j // 4) + (i // 4)) * 8
    RCOMP = dxt5_decode_alphablock_signed(pixdata, blksrc, i & 3, j & 3)

    return RCOMP


def fetch_2d_texel_rg_bc5(srcRowStride, pixdata, i, j):
    blksrc = ((srcRowStride + 3) // 4 * (j // 4) + (i // 4)) * 16

    RCOMP = dxt5_decode_alphablock(pixdata, blksrc, i & 3, j & 3)
    GCOMP = dxt5_decode_alphablock(pixdata, blksrc + 8, i & 3, j & 3)

    return RCOMP, GCOMP


def fetch_2d_texel_rg_bc5_snorm(srcRowStride, pixdata, i, j):
    blksrc = ((srcRowStride + 3) // 4 * (j // 4) + (i // 4)) * 16

    RCOMP = dxt5_decode_alphablock_signed(pixdata, blksrc, i & 3, j & 3)
    GCOMP = dxt5_decode_alphablock_signed(pixdata, blksrc + 8, i & 3, j & 3)

    return RCOMP, GCOMP




def _color_palette(data, offset, dxt_type):
    color0 = data[offset] | (data[offset + 1] << 8)
    color1 = data[offset + 2] | (data[offset + 3] << 8)
    c0 = (
        EXP5TO8R(color0), EXP6TO8G(color0), EXP5TO8B(color0),
    )
    c1 = (
        EXP5TO8R(color1), EXP6TO8G(color1), EXP5TO8B(color1),
    )
    if color0 > color1:
        c2 = tuple((2 * a + b) // 3 for a, b in zip(c0, c1))
        c3 = tuple((a + 2 * b) // 3 for a, b in zip(c0, c1))
    else:
        c2 = tuple((a + b) // 2 for a, b in zip(c0, c1))
        c3 = (
            tuple((a + 2 * b) // 3 for a, b in zip(c0, c1))
            if dxt_type > 1 else (0, 0, 0)
        )
    return (c0, c1, c2, c3), color0, color1


def _alpha_palette(data, offset, signed=False):
    alpha0 = data[offset]
    alpha1 = data[offset + 1]
    values = [alpha0, alpha1]
    if signed:
        s0 = ToSigned8(alpha0)
        s1 = ToSigned8(alpha1)
        if s0 > s1:
            values.extend(
                ToUnsigned8((s0 * (8 - code) + s1 * (code - 1)) // 7)
                for code in range(2, 8)
            )
        else:
            values.extend(
                ToUnsigned8((s0 * (6 - code) + s1 * (code - 1)) // 5)
                for code in range(2, 6)
            )
            values.extend((0x80, 0x7F))
    elif alpha0 > alpha1:
        values.extend(
            (alpha0 * (8 - code) + alpha1 * (code - 1)) // 7
            for code in range(2, 8)
        )
    else:
        values.extend(
            (alpha0 * (6 - code) + alpha1 * (code - 1)) // 5
            for code in range(2, 6)
        )
        values.extend((0, 255))
    return values


def _alpha_code(data, offset, pixel_index):
    bits = int.from_bytes(data[offset + 2:offset + 8], "little")
    return (bits >> (pixel_index * 3)) & 7


def _write_color_block(output, width, height, block_x, block_y, data,
                       block_offset, dxt_type, alpha_values=None,
                       explicit_alpha=False):
    colors, color0, color1 = _color_palette(data, block_offset, dxt_type)
    color_bits = int.from_bytes(data[block_offset + 4:block_offset + 8], "little")
    for py in range(4):
        y = block_y * 4 + py
        if y >= height:
            break
        for px in range(4):
            x = block_x * 4 + px
            if x >= width:
                break
            pixel_index = py * 4 + px
            code = (color_bits >> (pixel_index * 2)) & 3
            r, g, b = colors[code]
            if explicit_alpha:
                alpha_byte = data[block_offset - 8 + pixel_index // 2]
                a = EXP4TO8(alpha_byte >> (4 * (pixel_index & 1)) & 0xF)
            elif alpha_values is None:
                a = 0 if code == 3 and color0 <= color1 and dxt_type == 1 else 255
            else:
                a = alpha_values[_alpha_code(data, block_offset - 8, pixel_index)]
            pos = (y * width + x) * 4
            output[pos:pos + 4] = bytes((r, g, b, a))


def _decode_dxt1_blocked(data, width, height):
    output = bytearray(width * height * 4)
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4
    for by in range(blocks_y):
        for bx in range(blocks_x):
            _write_color_block(
                output, width, height, bx, by, data,
                (by * blocks_x + bx) * 8, 1,
            )
    return bytes(output)


def _decode_dxt3_blocked(data, width, height):
    output = bytearray(width * height * 4)
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4
    for by in range(blocks_y):
        for bx in range(blocks_x):
            _write_color_block(
                output, width, height, bx, by, data,
                (by * blocks_x + bx) * 16 + 8, 2,
                explicit_alpha=True,
            )
    return bytes(output)


def _decode_dxt5_blocked(data, width, height):
    output = bytearray(width * height * 4)
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4
    for by in range(blocks_y):
        for bx in range(blocks_x):
            block = (by * blocks_x + bx) * 16
            _write_color_block(
                output, width, height, bx, by, data, block + 8, 2,
                alpha_values=_alpha_palette(data, block),
            )
    return bytes(output)


def _decode_bc4_blocked(data, width, height, snorm):
    output = bytearray(width * height * 4)
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4
    for by in range(blocks_y):
        for bx in range(blocks_x):
            block = (by * blocks_x + bx) * 8
            palette = _alpha_palette(data, block, bool(snorm))
            for py in range(4):
                y = by * 4 + py
                if y >= height:
                    break
                for px in range(4):
                    x = bx * 4 + px
                    if x >= width:
                        break
                    value = palette[_alpha_code(data, block, py * 4 + px)]
                    if snorm:
                        value = ToSigned8(value) + 128
                    pos = (y * width + x) * 4
                    output[pos:pos + 4] = bytes((value, value, value, 255))
    return bytes(output)


def _decode_bc5_blocked(data, width, height, snorm):
    output = bytearray(width * height * 4)
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4
    for by in range(blocks_y):
        for bx in range(blocks_x):
            block = (by * blocks_x + bx) * 16
            red = _alpha_palette(data, block, bool(snorm))
            green = _alpha_palette(data, block + 8, bool(snorm))
            for py in range(4):
                y = by * 4 + py
                if y >= height:
                    break
                for px in range(4):
                    x = bx * 4 + px
                    if x >= width:
                        break
                    pixel_index = py * 4 + px
                    r = red[_alpha_code(data, block, pixel_index)]
                    g = green[_alpha_code(data, block + 8, pixel_index)]
                    if snorm:
                        r = ToSigned8(r) + 128
                        g = ToSigned8(g) + 128
                    pos = (y * width + x) * 4
                    output[pos:pos + 4] = bytes((r, g, 0, 255))
    return bytes(output)


def decompressDXT1(data, width, height):
    return _decode_dxt1_blocked(data, width, height)


def decompressDXT3(data, width, height):
    return _decode_dxt3_blocked(data, width, height)


def decompressDXT5(data, width, height):
    return _decode_dxt5_blocked(data, width, height)


def decompressBC4(data, width, height, SNORM):
    return _decode_bc4_blocked(data, width, height, SNORM)


def decompressBC5(data, width, height, SNORM):
    return _decode_bc5_blocked(data, width, height, SNORM)
