# Matrix Arcade — skip the menu and start the race.
# You should see RED, then YELLOW, then CYAN, then a bar slide, then the road.

import time

import tiltkart as tk

GAMES = (
    ("KART", "tiltkart"),
    ("STACK", "stacker"),
    ("SWING", "swing"),
)


def flash(display, bitmap, color, seconds):
    tk.clear(bitmap, color)
    display.refresh(minimum_frames_per_second=0)
    time.sleep(seconds)


def slide_bar(display, bitmap):
    for x in range(0, 64, 3):
        tk.clear(bitmap, tk.C_SKY1)
        for y in range(32):
            tk.plot(bitmap, x, y, tk.C_YELLOW)
            if x + 1 < 64:
                tk.plot(bitmap, x + 1, y, tk.C_YELLOW)
        display.refresh(minimum_frames_per_second=0)


def main():
    display, bitmap = tk.setup_display()
    up, down = tk.setup_buttons()
    lis = tk.setup_accel()
    flash(display, bitmap, tk.C_RED, 0.45)
    flash(display, bitmap, tk.C_YELLOW, 0.45)
    flash(display, bitmap, tk.C_CYAN, 0.45)
    slide_bar(display, bitmap)
    while True:
        tk.run(display, bitmap, lis, up, down)
        time.sleep(0.2)


main()
