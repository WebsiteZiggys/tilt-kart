# Swing — tilt-tennis. Pick a level, tilt to aim, UP to swing.
# L1 is easy: big racket, slow ball, CPU misses.

import random
import time

import tiltkart as tk

COURT_TOP = 8
NET_X = 31
YOU_X = 57
CPU_X = 5

# name, racket, hit window, swing frames, serve speed, max speed,
# cpu track speed, cpu hit window, cpu return chance, points to win, reach
LEVELS = (
    ("EASY", 9, 8.0, 20, 0.58, 0.88, 0.22, 2.6, 0.42, 3, 6),
    ("NORM", 6, 5.6, 13, 0.82, 1.25, 0.45, 3.6, 0.78, 4, 4),
    ("HARD", 5, 4.0, 9, 1.12, 1.7, 0.78, 4.6, 1.0, 4, 3),
)
LEVEL_NAMES = ("EASY", "NORM", "HARD", "BACK")


def clamp(value, lo, hi):
    return lo if value < lo else hi if value > hi else value


def draw_court(bitmap):
    tk.clear(bitmap, tk.C_SKY1)
    for y in range(COURT_TOP, tk.HEIGHT):
        for x in range(tk.WIDTH):
            bitmap[x, y] = tk.C_GRASS_A if ((x + y) & 2) == 0 else tk.C_GRASS_B
    for x in range(tk.WIDTH):
        tk.plot(bitmap, x, COURT_TOP, tk.C_WHITE)
        tk.plot(bitmap, x, tk.HEIGHT - 1, tk.C_WHITE)
    for y in range(COURT_TOP, tk.HEIGHT):
        tk.plot(bitmap, 0, y, tk.C_WHITE)
        tk.plot(bitmap, 63, y, tk.C_WHITE)
        if y & 1:
            tk.plot(bitmap, NET_X, y, tk.C_WHITE)
            tk.plot(bitmap, NET_X + 1, y, tk.C_HUD)


def draw_racket(bitmap, x, y, swinging, facing, size, color):
    reach = 4 if swinging else 0
    half = size // 2
    for i in range(size):
        py = int(y) - half + i
        tk.plot(bitmap, x, py, color)
        tk.plot(bitmap, x + facing, py, tk.C_WHITE)
        if reach:
            tk.plot(bitmap, x + facing * reach, py, color)


def draw_ball(bitmap, x, y):
    bx, by = int(x), int(y)
    tk.plot(bitmap, bx, by, tk.C_YELLOW)
    tk.plot(bitmap, bx + 1, by, tk.C_WHITE)


def pick_level(display, bitmap, up, down):
    index = 0
    was_up = True
    was_down = True
    while True:
        up_now = tk.button_pressed(up)
        down_now = tk.button_pressed(down)
        if down_now and not was_down:
            index = (index + 1) % 4
        if up_now and not was_up:
            time.sleep(0.12)
            return None if index == 3 else index
        was_up = up_now
        was_down = down_now
        tk.clear(bitmap, tk.C_SKY1)
        tk.draw_text(bitmap, "SWING", 20, 2, tk.C_YELLOW)
        for i, name in enumerate(LEVEL_NAMES):
            y = 9 + i * 6
            color = tk.C_CYAN if i == index else tk.C_HUD
            if i == index:
                tk.draw_text(bitmap, ">", 6, y, tk.C_MAGENTA)
            tk.draw_text(bitmap, name, 16, y, color)
        display.refresh(minimum_frames_per_second=0)
        time.sleep(0.03)


def play_match(display, bitmap, lis, up, down, rest, level):
    name, racket, hit, swing_len, serve_spd, max_spd, cpu_spd, cpu_hit, cpu_return, win_at, reach = LEVELS[level]
    you_score = 0
    cpu_score = 0
    you_y = 20.0
    cpu_y = 20.0
    ball_x, ball_y = 54.0, 20.0
    ball_vx, ball_vy = 0.0, 0.0
    serving = True
    serve_turn = 1
    swing = 0
    cpu_swing = 0
    pause = 0
    was_up = True
    ended = False
    prev_steer = 0.0

    while True:
        now = time.monotonic()
        up_now = tk.button_pressed(up)
        steer = tk.read_steer(lis, rest)
        flick = abs(steer - prev_steer) > 0.85
        prev_steer = steer
        if not serving and ball_vx > 0 and level == 0:
            you_y += clamp(ball_y - you_y, -0.35, 0.35)
        you_y = clamp(you_y + steer * 1.6, COURT_TOP + 4, tk.HEIGHT - 4)

        if ended:
            draw_court(bitmap)
            tk.draw_text(bitmap, "WIN" if you_score > cpu_score else "OUT", 24, 10, tk.C_YELLOW)
            tk.draw_text(bitmap, name, 22, 17, tk.C_CYAN)
            tk.draw_text(bitmap, "%d-%d" % (cpu_score, you_score), 22, 24, tk.C_HUD)
            display.refresh(minimum_frames_per_second=0)
            if up_now and not was_up:
                time.sleep(0.15)
                return
            was_up = up_now
            time.sleep(0.03)
            continue

        if pause > 0:
            pause -= 1
        if swing > 0:
            swing -= 1
        if cpu_swing > 0:
            cpu_swing -= 1

        want_swing = pause == 0 and ((up_now and not was_up) or flick)
        if want_swing and swing == 0:
            swing = swing_len
            if serving and serve_turn == 1:
                ball_x, ball_y = YOU_X - 3, you_y
                ball_vx, ball_vy = -serve_spd, steer * 0.35
                serving = False

        target = ball_y if ball_vx < 0 or serving else 20
        cpu_y += clamp(target - cpu_y, -cpu_spd, cpu_spd)
        cpu_y = clamp(cpu_y, COURT_TOP + 4, tk.HEIGHT - 4)
        if not serving and ball_vx < 0 and ball_x < 14 and cpu_swing == 0:
            if abs(ball_y - cpu_y) < 5.5 and random.random() < cpu_return:
                cpu_swing = 8

        if serving and serve_turn == -1 and pause == 0:
            ball_x, ball_y = CPU_X + 3, cpu_y
            ball_vx, ball_vy = serve_spd * 0.85, (you_y - cpu_y) * 0.03
            serving = False
            cpu_swing = 8

        if not serving:
            ball_x += ball_vx
            ball_y += ball_vy
            ball_vy *= 0.995
            if ball_y < COURT_TOP + 1:
                ball_y = COURT_TOP + 1
                ball_vy *= -0.9
            if ball_y > tk.HEIGHT - 2:
                ball_y = tk.HEIGHT - 2
                ball_vy *= -0.9

            if ball_vx > 0 and ball_x >= YOU_X - reach:
                close = abs(ball_y - you_y) < hit
                if swing > 0 and close:
                    ball_x = YOU_X - 3
                    ball_vx = -min(max_spd, abs(ball_vx) + 0.06)
                    ball_vy += (ball_y - you_y) * 0.12 + steer * 0.22
                    ball_vy = clamp(ball_vy, -0.7, 0.7)
                elif ball_x > 63:
                    cpu_score += 1
                    serving = True
                    serve_turn = 1 if (you_score + cpu_score) % 2 == 0 else -1
                    ball_vx = ball_vy = 0
                    pause = 28
            if ball_vx < 0 and ball_x <= CPU_X + 2:
                if cpu_swing > 0 and abs(ball_y - cpu_y) < cpu_hit:
                    ball_x = CPU_X + 3
                    ball_vx = min(max_spd * 0.9, abs(ball_vx) + 0.04)
                    ball_vy += (20 - cpu_y) * 0.04
                    ball_vy = clamp(ball_vy, -0.55, 0.55)
                elif ball_x < 0:
                    you_score += 1
                    serving = True
                    serve_turn = 1 if (you_score + cpu_score) % 2 == 0 else -1
                    ball_vx = ball_vy = 0
                    pause = 28

        if you_score >= win_at or cpu_score >= win_at:
            ended = True

        was_up = up_now
        draw_court(bitmap)
        tk.draw_text(bitmap, "%d" % cpu_score, 10, 1, tk.C_RED)
        tk.draw_text(bitmap, "%d" % you_score, 50, 1, tk.C_CYAN)
        tk.draw_text(bitmap, name, 24, 1, tk.C_YELLOW if serving and serve_turn == 1 else tk.C_HUD)
        draw_racket(bitmap, CPU_X, cpu_y, cpu_swing > 0, 1, 5, tk.C_RED)
        draw_racket(bitmap, YOU_X, you_y, swing > 0, -1, racket, tk.C_CYAN)
        if not serving or serve_turn == 1:
            draw_ball(bitmap, ball_x if not serving else YOU_X - 3, ball_y if not serving else you_y)
        display.refresh(minimum_frames_per_second=0)
        spent = time.monotonic() - now
        if spent < 0.03:
            time.sleep(0.03 - spent)


def run(display, bitmap, lis, up, down):
    rest = tk.rest_axis(lis)
    while True:
        choice = pick_level(display, bitmap, up, down)
        if choice is None:
            return
        play_match(display, bitmap, lis, up, down, rest, choice)
