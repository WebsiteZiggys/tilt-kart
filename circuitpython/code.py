# Matrix Arcade — tip the panel. A dot should roll with gravity.
# Hold a tip to play. If nothing is tilted, KART starts on its own.

import time

import board
import tiltkart as tk

try:
    import neopixel

    _PIX = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3)
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
    return str(v)


def _read(lis):
    if not lis:
        return None
    try:
        return lis.acceleration
    except Exception:
        return None


def menu_loop(display, bitmap, lis, up, down, rest):
    index = 0
    was_up = False
    was_down = False
    tilt_wait = 0
    hold = 0
    tick = 0
    started = time.monotonic()
    last_print = 0
    while True:
        up_now = not up.value
        down_now = not down.value
        if down_now and not was_down:
            index = (index + 1) % len(GAMES)
        if up_now and not was_up:
            return index
        was_up = up_now
        was_down = down_now

        acc = _read(lis)
        if acc:
            ax, ay, az = acc
        else:
            ax = ay = az = 0.0

        dx = ax - rest[0]
        dy = ay - rest[1]
        dz = az - rest[2]
        mag = (dx * dx + dy * dy + dz * dz) ** 0.5
        side = (ax, ay, az)[tk.STEER_AXIS] - rest[tk.STEER_AXIS]

        if tilt_wait > 0:
            tilt_wait -= 1
        elif side > 0.8:
            index = (index + 1) % len(GAMES)
            tilt_wait = 6
        elif side < -0.8:
            index = (index - 1) % len(GAMES)
            tilt_wait = 6
        if mag > 1.4:
            hold += 1
            if hold > 8:
                return index
        else:
            hold = 0

        # Always start something if the player cannot tilt or click
        if time.monotonic() - started > 3:
            return index

        if tick - last_print >= 10:
            print("acc", ax, ay, az, "mag", mag)
            last_print = tick

        if _PIX:
            _PIX[0] = (255, 80, 0) if tick & 4 else (0, 80, 255)

        bg = tk.C_SKY2 if tick & 8 else tk.C_SKY1
        if up_now:
            bg = tk.C_CYAN
        if down_now:
            bg = tk.C_YELLOW
        tk.clear(bitmap, bg)
        tk.draw_text(bitmap, "PLAY", 22, 1, tk.C_YELLOW)
        tk.draw_text(bitmap, _fmt(ax), 2, 8, tk.C_CYAN)
        tk.draw_text(bitmap, _fmt(ay), 14, 8, tk.C_CYAN)
        tk.draw_text(bitmap, _fmt(az), 26, 8, tk.C_CYAN)
        tk.draw_text(bitmap, GAMES[index][0], 16, 16, tk.C_WHITE)
        px = max(1, min(62, 32 + int(ax * 2.2)))
        py = max(9, min(30, 20 + int(ay * 2.2)))
        tk.plot(bitmap, px, py, tk.C_YELLOW)
        tk.plot(bitmap, px + 1, py, tk.C_YELLOW)
        tk.plot(bitmap, px, py + 1, tk.C_YELLOW)
        tk.plot(bitmap, px + 1, py + 1, tk.C_YELLOW)
        display.refresh(minimum_frames_per_second=0)
        tick += 1
        time.sleep(0.02)


def main():
    display, bitmap = tk.setup_display()
    up, down = tk.setup_buttons()
    lis = tk.setup_accel()
    tk.rest_axis(lis)
    acc = _read(lis)
    rest = acc if acc else (0.0, 0.0, 0.0)
    print("lis", lis, "axis", tk.STEER_AXIS, "rest", rest)
    while True:
        choice = menu_loop(display, bitmap, lis, up, down, rest)
        load_game(GAMES[choice][1])(display, bitmap, lis, up, down)
        time.sleep(0.2)


main()
