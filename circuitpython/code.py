# Matrix Arcade — Adafruit Matrix Portal M4 + 64x32 (product 4812)
# Tip the panel to move. Hold a tip to play.
# Buttons are on the BACK of the panel (middle = play, bottom = next).

import time

import board
import tiltkart as tk

try:
    import neopixel

    _PIX = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.25)
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


def _fmt(n):
    v = int(n)
    if v < -9:
        return "-9"
    if v > 9:
        return "9"
    return str(v)


def menu_loop(display, bitmap, lis, up, down, rest):
    index = 0
    was_up = False
    was_down = False
    tilt_wait = 0
    hold = 0
    tick = 0
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

        dx, dy, dz, mag = tk.motion_xyz(lis, rest)
        side = dy if abs(dy) >= abs(dx) else dx
        if tilt_wait > 0:
            tilt_wait -= 1
        elif side > 1.6:
            index = (index + 1) % len(GAMES)
            tilt_wait = 8
        elif side < -1.6:
            index = (index - 1) % len(GAMES)
            tilt_wait = 8
        if mag > 3.5:
            hold += 1
            if hold > 12:
                return index
        else:
            hold = 0

        if _PIX:
            if up_now or down_now:
                _PIX[0] = (0, 255, 80)
            elif tick & 8:
                _PIX[0] = (0, 0, 80)
            else:
                _PIX[0] = (80, 0, 40)

        if up_now:
            bg = tk.C_CYAN
        elif down_now:
            bg = tk.C_YELLOW
        elif tick & 16:
            bg = tk.C_SKY2
        else:
            bg = tk.C_SKY1
        tk.clear(bitmap, bg)
        tk.draw_text(bitmap, "PLAY", 22, 1, tk.C_YELLOW)
        tk.draw_text(bitmap, _fmt(dx), 2, 8, tk.C_CYAN)
        tk.draw_text(bitmap, _fmt(dy), 14, 8, tk.C_CYAN)
        tk.draw_text(bitmap, _fmt(dz), 26, 8, tk.C_CYAN)
        name = GAMES[index][0]
        tk.draw_text(bitmap, name, 16, 16, tk.C_WHITE)
        tk.draw_text(bitmap, "TIP", 24, 25, tk.C_HUD)
        display.refresh(minimum_frames_per_second=0)
        tick += 1
        time.sleep(0.03)


def main():
    display, bitmap = tk.setup_display()
    up, down = tk.setup_buttons()
    lis = tk.setup_accel()
    rest = tk.rest_xyz(lis)
    while True:
        choice = menu_loop(display, bitmap, lis, up, down, rest)
        load_game(GAMES[choice][1])(display, bitmap, lis, up, down)
        time.sleep(0.2)


main()
