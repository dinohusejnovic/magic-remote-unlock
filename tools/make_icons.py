#!/usr/bin/env python3
"""Generate the app icons (a simple remote with a pointer dot). No dependencies."""
import math, struct, sys, zlib

def png(path, size):
    S = 4  # supersampling
    n = size * S
    bg, body, accent = (20, 23, 28), (232, 234, 237), (207, 6, 82)
    def px(x, y):
        u, v = x / n, y / n
        # remote body: rounded vertical rectangle
        cx, w, top, bot, r = 0.5, 0.17, 0.12, 0.88, 0.08
        dx, dy = abs(u - cx), 0
        if v < top + r: dy = top + r - v
        elif v > bot - r: dy = v - (bot - r)
        inside = dx <= w and top <= v <= bot and (dx - (w - r) <= 0 or dy == 0 or
                 math.hypot(max(dx - (w - r), 0), dy) <= r)
        if math.hypot(u - cx, v - 0.36) <= 0.075: return accent
        if math.hypot(u - cx, v - 0.62) <= 0.04: return bg
        return body if inside else bg
    rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            acc = [0, 0, 0]
            for sy in range(S):
                for sx in range(S):
                    c = px(x * S + sx, y * S + sy)
                    for i in range(3): acc[i] += c[i]
            row += bytes(a // (S * S) for a in acc)
        rows.append(bytes(row))
    def chunk(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    data = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(b''.join(rows), 9)) + chunk(b'IEND', b''))
    open(path, 'wb').write(data)

for size, path in ((80, 'package/app/assets/icon80.png'), (130, 'package/app/assets/icon130.png'),
                   (160, 'assets/icon160.png')):
    png(path, size)
