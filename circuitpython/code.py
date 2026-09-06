# Simple 2D racer.
# BACK of the panel, on the Portal next to USB-C:
#   top = reset (ignore)  middle = left  bottom = right
# Tip also steers.

import time

import board
import tiltkart as tk

try:
    import neopixel

    PIX = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.35)
except Exception:
    PIX = None


def main():
    display, bitmap = tk.setup_display()
    up, down = tk.setup_buttons()
    lis = tk.setup_accel()
    rest = tk.rest_axis(lis)
    x = 32.0
    z = 0
    while True:
        up_now = not up.value
        down_now = not down.value
        steer = tk.read_steer(lis, rest)
        if up_now:
            x -= 2.2
        if down_now:
            x += 2.2
        x += steer * 2.4
        if x < 6:
            x = 6
        if x > 57:
            x = 57

        if PIX:
            if up_now:
                PIX[0] = (0, 255, 255)
            elif down_now:
                PIX[0] = (255, 220, 0)
            else:
                PIX[0] = (0, 0, 40)

        if up_now:
            tk.clear(bitmap, tk.C_CYAN)
        elif down_now:
            tk.clear(bitmap, tk.C_YELLOW)
        else:
            tk.clear(bitmap, tk.C_GRASS_A)
        for y in range(8, 32):
            for px in range(10, 54):
                bitmap[px, y] = tk.C_ROAD
            bitmap[10, y] = tk.C_RUMBLE_A if ((y + z) & 2) else tk.C_WHITE
            bitmap[53, y] = tk.C_RUMBLE_A if ((y + z) & 2) else tk.C_WHITE
            if ((y + z) & 3) == 0:
                bitmap[31, y] = tk.C_YELLOW
                bitmap[32, y] = tk.C_YELLOW
        tk.draw_text(bitmap, "KART", 22, 1, tk.C_SKY1 if (up_now or down_now) else tk.C_YELLOW)

        cx = int(x)
        for dy in range(4):
            for dx in range(-3, 4):
                tk.plot(bitmap, cx + dx, 26 + dy, tk.C_RED)
        tk.plot(bitmap, cx, 27, tk.C_WHITE)

        display.refresh(minimum_frames_per_second=0)
        z += 1
        time.sleep(0.02)


main()
