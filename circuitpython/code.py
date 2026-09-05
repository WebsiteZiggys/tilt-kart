# Matrix Arcade — Adafruit Matrix Portal M4 + 64x32 (product 4812)
# Copy this folder to CIRCUITPY: code.py, tiltkart.py, stacker.py, swing.py
#
# Buttons are on the BACK of the panel, on the Portal PCB:
#   top = reset, middle = UP / play, bottom = DOWN / next.
# Tilt also works: tip to move, hold a tip to play.

import time

import board
import tiltkart as tk

try:
    import neopixel

    _PIX = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
except Exception:
    _PIX = None

GAMES = (
    ("KART", "tiltkart"),
    ("STACK", "stacker"),
    ("SWING", "swing"),
)


def load_game(module_name):
    if module_name == "tiltkart":
        return tk.run
    if module_name == "stacker":
        import stacker

        return stacker.run
    if module_name == "swing":
        import swing

        return swing.run
    return __import__(module_name).run


def menu_loop(display, bitmap, lis, up, down, rest=0.0):
    index = 0
    was_up = False
    was_down = False
    tilt_wait = 0
    hold = 0
    while True:
        up_now = not up.value
        down_now = not down.value

        if down_now and not was_down:
            index = (index + 1) % len(GAMES)
        if up_now and not was_up:
            time.sleep(0.1)
            return index
        was_up = up_now
        was_down = down_now

        if _PIX:
            if up_now:
                _PIX[0] = (0, 255, 255)
            elif down_now:
                _PIX[0] = (255, 220, 0)
            else:
                _PIX[0] = (40, 0, 0)

        steer = 0.0
        if lis:
            try:
                steer = tk.read_steer(lis, rest)
            except Exception:
                steer = 0.0
        if tilt_wait > 0:
            tilt_wait -= 1
        elif steer > 0.4:
            index = (index + 1) % len(GAMES)
            tilt_wait = 10
        elif steer < -0.4:
            index = (index - 1) % len(GAMES)
            tilt_wait = 10
        if abs(steer) > 0.8:
            hold += 1
            if hold > 16:
                return index
        else:
            hold = 0

        if up_now:
            tk.clear(bitmap, tk.C_CYAN)
        elif down_now:
            tk.clear(bitmap, tk.C_YELLOW)
        else:
            tk.clear(bitmap, tk.C_SKY1)
        tk.draw_text(bitmap, "PLAY", 22, 2, tk.C_YELLOW if not up_now else tk.C_SKY1)
        start = 0
        if index > 1:
            start = index - 1
        visible = GAMES[start : start + 3]
        for i, (name, _mod) in enumerate(visible):
            real = start + i
            y = 11 + i * 7
            color = tk.C_MAGENTA if real == index else tk.C_HUD
            if real == index:
                tk.draw_text(bitmap, ">", 8, y, tk.C_CYAN)
            tk.draw_text(bitmap, name, 16, y, color)
        tk.draw_text(bitmap, "TILT", 22, 26, tk.C_HUD)
        display.refresh(minimum_frames_per_second=0)
        time.sleep(0.02)


def main():
    display, bitmap = tk.setup_display()
    up, down = tk.setup_buttons()
    lis = tk.setup_accel()
    rest = tk.rest_axis(lis)
    while True:
        choice = menu_loop(display, bitmap, lis, up, down, rest)
        load_game(GAMES[choice][1])(display, bitmap, lis, up, down)
        time.sleep(0.2)


main()
