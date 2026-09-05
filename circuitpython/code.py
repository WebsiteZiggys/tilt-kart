# Matrix Arcade — Adafruit Matrix Portal M4 + 64x32 (product 4812)
# Tip the panel (change its angle). Hold a tip to play.

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
    v = int(round(n))
    if v < -9:
        return "-9"
    if v > 9:
        return "9"
    if v < 0:
        return str(v)
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

        if lis:
            try:
                ax, ay, az = lis.acceleration
            except Exception:
                ax = ay = az = 0.0
                lis = None
        else:
            ax = ay = az = 0.0

        dx = ax - rest[0]
        dy = ay - rest[1]
        dz = az - rest[2]
        mag = (dx * dx + dy * dy + dz * dz) ** 0.5
        side = dy if abs(dy) >= abs(dx) else dx

        if tilt_wait > 0:
            tilt_wait -= 1
        elif side > 1.0:
            index = (index + 1) % len(GAMES)
            tilt_wait = 7
        elif side < -1.0:
            index = (index - 1) % len(GAMES)
            tilt_wait = 7
        if mag > 2.0:
            hold += 1
            if hold > 10:
                return index
        else:
            hold = 0

        if _PIX:
            _PIX[0] = (0, 255, 80) if (up_now or down_now) else ((0, 0, 90) if tick & 8 else (90, 0, 40))

        bg = tk.C_CYAN if up_now else tk.C_YELLOW if down_now else (tk.C_SKY2 if tick & 16 else tk.C_SKY1)
        tk.clear(bitmap, bg)
        tk.draw_text(bitmap, "PLAY", 22, 1, tk.C_YELLOW)
        if lis:
            tk.draw_text(bitmap, _fmt(ax), 2, 8, tk.C_CYAN)
            tk.draw_text(bitmap, _fmt(ay), 14, 8, tk.C_CYAN)
            tk.draw_text(bitmap, _fmt(az), 26, 8, tk.C_CYAN)
        else:
            tk.draw_text(bitmap, "NO", 2, 8, tk.C_RED)
        tk.draw_text(bitmap, GAMES[index][0], 16, 16, tk.C_WHITE)
        tk.draw_text(bitmap, "TIP", 24, 25, tk.C_HUD)
        display.refresh(minimum_frames_per_second=0)
        tick += 1
        time.sleep(0.03)


def main():
    display, bitmap = tk.setup_display()
    up, down = tk.setup_buttons()
    lis = tk.setup_accel()
    rest = tk.rest_xyz(lis) if lis else (0.0, 0.0, 0.0)
    while True:
        choice = menu_loop(display, bitmap, lis, up, down, rest)
        load_game(GAMES[choice][1])(display, bitmap, lis, up, down)
        time.sleep(0.2)


main()
