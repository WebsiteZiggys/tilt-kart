# Stack — drop the moving bar. Overhang is cut. Miss and you're done.
# Add more games by dropping a file next to this and listing it in code.py.

import time

import tiltkart as tk


def run(display, bitmap, lis, up, down):
    layers = [(18, 28)]
    piece_x = 2.0
    piece_w = 28
    direction = 1
    speed = 0.55
    score = 0
    dropping = False
    was_up = True
    ended = False

    while True:
        now = time.monotonic()
        up_now = tk.button_pressed(up)
        if ended:
            tk.clear(bitmap)
            tk.draw_text(bitmap, "STACK", 20, 6, tk.C_YELLOW)
            tk.draw_text(bitmap, str(score), 28, 14, tk.C_CYAN)
            tk.draw_text(bitmap, "UP", 28, 22, tk.C_HUD)
            display.refresh(minimum_frames_per_second=0)
            if up_now and not was_up:
                time.sleep(0.15)
                return
            was_up = up_now
            time.sleep(0.03)
            continue

        if up_now and not was_up and not dropping:
            dropping = True
            base_x, base_w = layers[-1]
            left = max(int(piece_x), base_x)
            right = min(int(piece_x) + piece_w, base_x + base_w)
            overlap = right - left
            if overlap <= 1:
                ended = True
                was_up = up_now
                continue
            layers.append((left, overlap))
            piece_w = overlap
            piece_x = float(left)
            score += 1
            speed = min(1.7, speed + 0.12)
            dropping = False
            if 31 - len(layers) * 2 < 8:
                ended = True
        was_up = up_now

        piece_x += direction * speed
        if piece_x < 1:
            piece_x = 1
            direction = 1
        if piece_x + piece_w > 62:
            piece_x = 62 - piece_w
            direction = -1

        tk.clear(bitmap, tk.C_SKY1)
        tk.draw_text(bitmap, str(score), 1, 1, tk.C_HUD)
        for i, (lx, lw) in enumerate(layers):
            y = 30 - i * 2
            color = tk.RAINBOW[i % 6]
            for x in range(lx, lx + lw):
                tk.plot(bitmap, x, y, color)
                tk.plot(bitmap, x, y + 1, color)
        y = 30 - len(layers) * 2
        if y > 6:
            color = tk.C_WHITE
            for x in range(int(piece_x), int(piece_x) + piece_w):
                tk.plot(bitmap, x, y, color)
                tk.plot(bitmap, x, y + 1, tk.C_CYAN)
        display.refresh(minimum_frames_per_second=0)
        spent = time.monotonic() - now
        if spent < 0.03:
            time.sleep(0.03 - spent)
