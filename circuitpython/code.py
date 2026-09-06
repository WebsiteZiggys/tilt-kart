# Rainbow sand — no buttons. Tilt the panel and the grains pour.
# If the accelerometer is missing, gravity slowly spins on its own.

import math
import random
import time

import tiltkart as tk

W = 64
H = 32
COLORS = (
    tk.C_RB0,
    tk.C_RB1,
    tk.C_RB2,
    tk.C_RB3,
    tk.C_RB4,
    tk.C_RB5,
    tk.C_CYAN,
    tk.C_MAGENTA,
    tk.C_YELLOW,
    tk.C_ORANGE,
)


def _dir(g):
    if g > 1.6:
        return 1
    if g < -1.6:
        return -1
    return 0


def _step(grid, sx, sy):
    xs = range(W - 1, -1, -1) if sx > 0 else range(W)
    ys = range(H - 1, -1, -1) if sy > 0 else range(H)
    for y in ys:
        row = y * W
        for x in xs:
            color = grid[row + x]
            if color == 0:
                continue
            nx = x + sx
            ny = y + sy
            dest = ny * W + nx
            if 0 <= nx < W and 0 <= ny < H and grid[dest] == 0:
                grid[row + x] = 0
                grid[dest] = color
                continue
            for px, py in ((-sy, sx), (sy, -sx)):
                tx = x + sx + px
                ty = y + sy + py
                if 0 <= tx < W and 0 <= ty < H and grid[ty * W + tx] == 0:
                    grid[row + x] = 0
                    grid[ty * W + tx] = color
                    break


def _spawn(grid, sx, sy, color):
    if sy > 0:
        spots = ((x, 0) for x in range(8, 56))
    elif sy < 0:
        spots = ((x, H - 1) for x in range(8, 56))
    elif sx > 0:
        spots = ((0, y) for y in range(4, 28))
    else:
        spots = ((W - 1, y) for y in range(4, 28))
    for x, y in spots:
        i = y * W + x
        if grid[i] == 0 and random.random() < 0.08:
            grid[i] = color
            return


def main():
    display, bitmap = tk.setup_display()
    lis = tk.setup_accel()
    grid = bytearray(W * H)
    for _ in range(260):
        x = random.randint(6, W - 7)
        y = random.randint(2, H - 3)
        i = y * W + x
        if grid[i] == 0:
            grid[i] = COLORS[random.randrange(len(COLORS))]
    tick = 0
    while True:
        if lis:
            try:
                ax, ay, _az = lis.acceleration
            except Exception:
                ax, ay = 0.0, 9.0
        else:
            now = time.monotonic()
            ax = math.sin(now * 0.7) * 8.0
            ay = math.cos(now * 0.7) * 8.0
        sx = _dir(ax)
        sy = _dir(ay)
        if sx == 0 and sy == 0:
            sy = 1
        _step(grid, sx, sy)
        if tick & 1:
            _spawn(grid, sx, sy, COLORS[tick % len(COLORS)])
        tk.clear(bitmap, tk.C_BLACK)
        for i, color in enumerate(grid):
            if color:
                bitmap[i % W, i // W] = color
        display.refresh(minimum_frames_per_second=0)
        tick += 1


main()
