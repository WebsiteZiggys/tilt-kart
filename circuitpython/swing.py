# Swing — tilt-tennis for the 64x32 Matrix Portal.
# Tilt aims the racket. UP swings. Time it like a Wii remote.

import time

import tiltkart as tk

COURT_TOP = 8
NET_X = 31
YOU_X = 57
CPU_X = 5
RACKET = 5
WIN_POINTS = 4


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


def draw_racket(bitmap, x, y, swinging, facing):
    color = tk.C_CYAN if facing > 0 else tk.C_RED
    reach = 3 if swinging else 0
    for i in range(RACKET):
        py = int(y) - RACKET // 2 + i
        tk.plot(bitmap, x, py, color)
        tk.plot(bitmap, x + facing, py, tk.C_WHITE)
        if reach:
            tk.plot(bitmap, x + facing * reach, py, color)


def draw_ball(bitmap, x, y):
    bx, by = int(x), int(y)
    tk.plot(bitmap, bx, by, tk.C_YELLOW)
    tk.plot(bitmap, bx + 1, by, tk.C_WHITE)


def run(display, bitmap, lis, up, down):
    rest = tk.rest_axis(lis)
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
        you_y = clamp(you_y + steer * 1.4, COURT_TOP + 3, tk.HEIGHT - 3)

        if ended:
            draw_court(bitmap)
            tk.draw_text(bitmap, "WIN" if you_score > cpu_score else "OUT", 24, 12, tk.C_YELLOW)
            tk.draw_text(bitmap, "%d-%d" % (cpu_score, you_score), 22, 20, tk.C_HUD)
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
            swing = 10
            if serving and serve_turn == 1:
                ball_x, ball_y = YOU_X - 3, you_y
                ball_vx, ball_vy = -1.15, steer * 0.6
                serving = False

        target = ball_y if ball_vx < 0 or serving else 20
        cpu_y += clamp(target - cpu_y, -0.7, 0.7)
        cpu_y = clamp(cpu_y, COURT_TOP + 3, tk.HEIGHT - 3)
        if not serving and ball_vx < 0 and ball_x < 12 and cpu_swing == 0:
            if abs(ball_y - cpu_y) < 6:
                cpu_swing = 10

        if serving and serve_turn == -1 and pause == 0:
            ball_x, ball_y = CPU_X + 3, cpu_y
            ball_vx, ball_vy = 1.1, (you_y - cpu_y) * 0.04
            serving = False
            cpu_swing = 8

        if not serving:
            ball_x += ball_vx
            ball_y += ball_vy
            if ball_y < COURT_TOP + 1:
                ball_y = COURT_TOP + 1
                ball_vy *= -1
            if ball_y > tk.HEIGHT - 2:
                ball_y = tk.HEIGHT - 2
                ball_vy *= -1

            if ball_vx > 0 and ball_x >= YOU_X - 2:
                if swing > 0 and abs(ball_y - you_y) < 4.2:
                    ball_x = YOU_X - 3
                    ball_vx = -min(1.7, abs(ball_vx) + 0.12)
                    ball_vy += (ball_y - you_y) * 0.22 + steer * 0.35
                elif ball_x > 63:
                    cpu_score += 1
                    serving = True
                    serve_turn = 1 if (you_score + cpu_score) % 2 == 0 else -1
                    ball_vx = ball_vy = 0
                    pause = 22
            if ball_vx < 0 and ball_x <= CPU_X + 2:
                if cpu_swing > 0 and abs(ball_y - cpu_y) < 4.5:
                    ball_x = CPU_X + 3
                    ball_vx = min(1.65, abs(ball_vx) + 0.08)
                    ball_vy += (20 - cpu_y) * 0.05
                elif ball_x < 0:
                    you_score += 1
                    serving = True
                    serve_turn = 1 if (you_score + cpu_score) % 2 == 0 else -1
                    ball_vx = ball_vy = 0
                    pause = 22

        if you_score >= WIN_POINTS or cpu_score >= WIN_POINTS:
            ended = True

        was_up = up_now
        draw_court(bitmap)
        tk.draw_text(bitmap, "%d" % cpu_score, 10, 1, tk.C_RED)
        tk.draw_text(bitmap, "%d" % you_score, 50, 1, tk.C_CYAN)
        if serving and serve_turn == 1:
            tk.draw_text(bitmap, "UP", 26, 1, tk.C_YELLOW)
        draw_racket(bitmap, CPU_X, cpu_y, cpu_swing > 0, 1)
        draw_racket(bitmap, YOU_X, you_y, swing > 0, -1)
        if not serving or serve_turn == 1:
            draw_ball(bitmap, ball_x if not serving else YOU_X - 3, ball_y if not serving else you_y)
        display.refresh(minimum_frames_per_second=0)
        spent = time.monotonic() - now
        if spent < 0.03:
            time.sleep(0.03 - spent)
