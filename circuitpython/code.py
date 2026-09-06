# Simple 2D racer — fast enough to see motion on the real panel.
# Tip left/right to move the red kart.

import time

import tiltkart as tk


def main():
    display, bitmap = tk.setup_display()
    up, down = tk.setup_buttons()
    lis = tk.setup_accel()
    rest = tk.rest_axis(lis)
    x = 32.0
    z = 0
    while True:
        steer = tk.read_steer(lis, rest)
        if not up.value:
            x = 32.0
        x += steer * 2.4
        if x < 6:
            x = 6
        if x > 57:
            x = 57

        tk.clear(bitmap, tk.C_GRASS_A)
        for y in range(8, 32):
            for px in range(10, 54):
                bitmap[px, y] = tk.C_ROAD
            bitmap[10, y] = tk.C_RUMBLE_A if ((y + z) & 2) else tk.C_WHITE
            bitmap[53, y] = tk.C_RUMBLE_A if ((y + z) & 2) else tk.C_WHITE
            if ((y + z) & 3) == 0:
                bitmap[31, y] = tk.C_YELLOW
                bitmap[32, y] = tk.C_YELLOW
        tk.draw_text(bitmap, "KART", 22, 1, tk.C_YELLOW)

        cx = int(x)
        for dy in range(4):
            for dx in range(-3, 4):
                tk.plot(bitmap, cx + dx, 26 + dy, tk.C_RED)
        tk.plot(bitmap, cx, 27, tk.C_WHITE)
        tk.plot(bitmap, cx - 3, 29, tk.C_YELLOW)
        tk.plot(bitmap, cx + 3, 29, tk.C_YELLOW)

        display.refresh(minimum_frames_per_second=0)
        z += 1
        time.sleep(0.02)


main()
