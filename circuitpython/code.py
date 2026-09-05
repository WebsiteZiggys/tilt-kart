# Matrix Arcade — red, yellow, cyan, then the race.

import time

import tiltkart as tk


def flash(display, bitmap, color, seconds):
    tk.clear(bitmap, color)
    display.refresh(minimum_frames_per_second=0)
    time.sleep(seconds)


def main():
    display, bitmap = tk.setup_display()
    up, down = tk.setup_buttons()
    lis = tk.setup_accel()
    flash(display, bitmap, tk.C_RED, 0.5)
    flash(display, bitmap, tk.C_YELLOW, 0.5)
    flash(display, bitmap, tk.C_CYAN, 0.5)
    while True:
        tk.run(display, bitmap, lis, up, down)
        time.sleep(0.2)


main()

