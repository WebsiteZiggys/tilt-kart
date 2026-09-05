# Matrix Arcade — Adafruit Matrix Portal M4 + 64x32 (product 4812)
# Copy this folder to CIRCUITPY: code.py, tiltkart.py, stacker.py, swing.py
#
# DOWN = next game. UP = play. After a game you come back here.
# To add a game: make games/mygame.py with run(display, bitmap, lis, up, down)
# then add ("NAME", "mygame") to GAMES below.

import time

import tiltkart as tk

# name on the 64x32 menu, module to import when selected
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
    module = __import__(module_name)
    return module.run


def menu_loop(display, bitmap, lis, up, down, rest):
    index = 0
    was_up = True
    was_down = True
    t = 0
    while True:
        down_now = tk.button_pressed(down)
        up_now = tk.button_pressed(up)
        if down_now and not was_down:
            index = (index + 1) % len(GAMES)
        if up_now and not was_up:
            time.sleep(0.12)
            return index
        was_up = up_now
        was_down = down_now

        steer = 0.0
        if lis:
            try:
                steer = tk.read_steer(lis, rest)
            except Exception:
                steer = 0.0
        if steer > 0.55:
            index = min(len(GAMES) - 1, index + 1)
            time.sleep(0.16)
        elif steer < -0.55:
            index = max(0, index - 1)
            time.sleep(0.16)

        tk.clear(bitmap, tk.C_SKY1)
        tk.draw_text(bitmap, "PLAY", 22, 2, tk.C_YELLOW)
        start = 0
        if index > 1:
            start = index - 1
        visible = GAMES[start : start + 3]
        for i, (name, _mod) in enumerate(visible):
            real = start + i
            y = 11 + i * 7
            color = tk.C_CYAN if real == index else tk.C_HUD
            if real == index:
                tk.draw_text(bitmap, ">", 8, y, tk.C_MAGENTA)
            tk.draw_text(bitmap, name, 16, y, color)
        if int(t * 2) & 1:
            tk.draw_text(bitmap, "UP", 50, 26, tk.C_HUD)
        display.refresh(minimum_frames_per_second=0)
        t += 0.08
        time.sleep(0.03)


def main():
    display, bitmap = tk.setup_display()
    up, down = tk.setup_buttons()
    lis = tk.setup_accel()
    rest = tk.rest_axis(lis)
    while True:
        choice = menu_loop(display, bitmap, lis, up, down, rest)
        name, module_name = GAMES[choice]
        run = load_game(module_name)
        run(display, bitmap, lis, up, down)
        time.sleep(0.2)


main()
