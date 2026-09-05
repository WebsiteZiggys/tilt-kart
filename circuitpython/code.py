# Tilt Kart — Matrix Portal M4 + 64x32 RGB matrix (Adafruit #4812)
# Copy this file to CIRCUITPY as code.py
#
# Tilt the panel to steer. BUTTON_UP = start / boost. BUTTON_DOWN = brake.
# If steering feels backwards, set STEER_FLIP = -1. If it barely responds,
# try STEER_AXIS = 0 or 1.

import math
import time
import random

import board
import digitalio
import displayio
import framebufferio
import rgbmatrix

try:
    import adafruit_lis3dh
except ImportError:
    adafruit_lis3dh = None

WIDTH = 64
HEIGHT = 32
HORIZON = 9
BIT_DEPTH = 3

STEER_AXIS = 1  # 0=X  1=Y  2=Z
STEER_FLIP = 1
STEER_DEADZONE = 0.12
STEER_SENS = 2.4

LAPS = 3
MAX_SPEED = 2.35
BOOST_SPEED = 3.15
ACCEL = 0.045
BRAKE = 0.09
DRAG = 0.012
OFFROAD_DRAG = 0.055
CENTRIFUGAL = 0.018

# (length along track, curve strength)
TRACK = (
    (55, 0.0),
    (38, 2.2),
    (28, 0.4),
    (42, -2.8),
    (22, 0.0),
    (36, 1.8),
    (30, -1.2),
    (40, 0.0),
    (34, 2.6),
    (26, -2.1),
    (48, 0.0),
)

# 3x5 caps, rows packed in 3 bits (MSB = left pixel)
FONT = {
    " ": 0,
    "A": (0b010, 0b101, 0b111, 0b101, 0b101),
    "B": (0b110, 0b101, 0b110, 0b101, 0b110),
    "C": (0b011, 0b100, 0b100, 0b100, 0b011),
    "D": (0b110, 0b101, 0b101, 0b101, 0b110),
    "E": (0b111, 0b100, 0b110, 0b100, 0b111),
    "F": (0b111, 0b100, 0b110, 0b100, 0b100),
    "G": (0b011, 0b100, 0b101, 0b101, 0b011),
    "I": (0b111, 0b010, 0b010, 0b010, 0b111),
    "K": (0b101, 0b101, 0b110, 0b101, 0b101),
    "L": (0b100, 0b100, 0b100, 0b100, 0b111),
    "N": (0b101, 0b111, 0b111, 0b101, 0b101),
    "O": (0b010, 0b101, 0b101, 0b101, 0b010),
    "P": (0b110, 0b101, 0b110, 0b100, 0b100),
    "R": (0b110, 0b101, 0b110, 0b101, 0b101),
    "S": (0b011, 0b100, 0b010, 0b001, 0b110),
    "T": (0b111, 0b010, 0b010, 0b010, 0b010),
    "W": (0b101, 0b101, 0b111, 0b111, 0b101),
    "Y": (0b101, 0b101, 0b010, 0b010, 0b010),
    "0": (0b111, 0b101, 0b101, 0b101, 0b111),
    "1": (0b010, 0b110, 0b010, 0b010, 0b111),
    "2": (0b111, 0b001, 0b111, 0b100, 0b111),
    "3": (0b111, 0b001, 0b111, 0b001, 0b111),
    "4": (0b101, 0b101, 0b111, 0b001, 0b001),
    "5": (0b111, 0b100, 0b111, 0b001, 0b111),
    "6": (0b111, 0b100, 0b111, 0b101, 0b111),
    "7": (0b111, 0b001, 0b001, 0b001, 0b001),
    "8": (0b111, 0b101, 0b111, 0b101, 0b111),
    "9": (0b111, 0b101, 0b111, 0b001, 0b111),
    "/": (0b001, 0b001, 0b010, 0b100, 0b100),
    "!": (0b010, 0b010, 0b010, 0b000, 0b010),
    "$": (0b010, 0b111, 0b110, 0b011, 0b111),
}

# palette indices
C_BLACK = 0
C_SKY1 = 1
C_SKY2 = 2
C_SKY3 = 3
C_SUN = 4
C_HILL = 5
C_GRASS_A = 6
C_GRASS_B = 7
C_RUMBLE_A = 8
C_RUMBLE_B = 9
C_ROAD = 10
C_ROAD_EDGE = 11
C_DASH = 12
C_FINISH = 13
C_HUD = 14
C_RED = 15
C_WHITE = 16
C_CYAN = 17
C_YELLOW = 18
C_MAGENTA = 19
C_ORANGE = 20
C_SHADOW = 21
C_BANANA = 22
C_COIN = 23


def setup_display():
    displayio.release_displays()
    matrix = rgbmatrix.RGBMatrix(
        width=WIDTH,
        height=HEIGHT,
        bit_depth=BIT_DEPTH,
        rgb_pins=[
            board.MTX_R1,
            board.MTX_G1,
            board.MTX_B1,
            board.MTX_R2,
            board.MTX_G2,
            board.MTX_B2,
        ],
        addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD],
        clock_pin=board.MTX_CLK,
        latch_pin=board.MTX_LAT,
        output_enable_pin=board.MTX_OE,
        doublebuffer=True,
    )
    display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)
    bitmap = displayio.Bitmap(WIDTH, HEIGHT, 32)
    palette = displayio.Palette(32)
    palette[C_BLACK] = 0x000000
    palette[C_SKY1] = 0x12002A
    palette[C_SKY2] = 0x2A1060
    palette[C_SKY3] = 0xFF6A20
    palette[C_SUN] = 0xFFD84A
    palette[C_HILL] = 0x1A0A28
    palette[C_GRASS_A] = 0x0A4A18
    palette[C_GRASS_B] = 0x167028
    palette[C_RUMBLE_A] = 0xE01020
    palette[C_RUMBLE_B] = 0xF0F0F0
    palette[C_ROAD] = 0x2A2A36
    palette[C_ROAD_EDGE] = 0x4A4A58
    palette[C_DASH] = 0xF0D020
    palette[C_FINISH] = 0xF8F8F8
    palette[C_HUD] = 0xF4F4FF
    palette[C_RED] = 0xFF2040
    palette[C_WHITE] = 0xFFFFFF
    palette[C_CYAN] = 0x20F0FF
    palette[C_YELLOW] = 0xFFE020
    palette[C_MAGENTA] = 0xFF40C8
    palette[C_ORANGE] = 0xFF8020
    palette[C_SHADOW] = 0x101018
    palette[C_BANANA] = 0xFFE040
    palette[C_COIN] = 0xFFC000
    tile = displayio.TileGrid(bitmap, pixel_shader=palette)
    group = displayio.Group()
    group.append(tile)
    display.root_group = group
    return display, bitmap


def setup_buttons():
    up = digitalio.DigitalInOut(board.BUTTON_UP)
    up.switch_to_input(pull=digitalio.Pull.UP)
    down = digitalio.DigitalInOut(board.BUTTON_DOWN)
    down.switch_to_input(pull=digitalio.Pull.UP)
    return up, down


def setup_accel():
    if adafruit_lis3dh is None:
        return None
    try:
        i2c = board.I2C()
        lis = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)
        lis.range = adafruit_lis3dh.RANGE_4_G
        return lis
    except Exception:
        return None


def build_track():
    starts = []
    z = 0.0
    for length, curve in TRACK:
        starts.append((z, length, curve))
        z += length
    return starts, z


SEGMENTS, TRACK_LEN = build_track()


def curve_at(z):
    z = z % TRACK_LEN
    for start, length, curve in SEGMENTS:
        if z < start + length:
            return curve
    return 0.0


def button_pressed(pin):
    return not pin.value


def read_steer(lis, rest):
    if lis is None:
        return 0.0
    try:
        accel = lis.acceleration
    except Exception:
        return 0.0
    value = accel[STEER_AXIS] - rest
    if abs(value) < STEER_DEADZONE:
        return 0.0
    return max(-1.0, min(1.0, value * STEER_FLIP * STEER_SENS * 0.35))


def rest_axis(lis):
    if lis is None:
        return 0.0
    total = 0.0
    count = 0
    for _ in range(6):
        try:
            total += lis.acceleration[STEER_AXIS]
            count += 1
        except Exception:
            pass
        time.sleep(0.02)
    return total / count if count else 0.0


def plot(bitmap, x, y, color):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        bitmap[x, y] = color


def fill_row(bitmap, y, color):
    for x in range(WIDTH):
        bitmap[x, y] = color


def draw_text(bitmap, text, x, y, color):
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        if glyph == 0:
            cx += 4
            continue
        for row in range(5):
            bits = glyph[row]
            for col in range(3):
                if bits & (0b100 >> col):
                    plot(bitmap, cx + col, y + row, color)
        cx += 4


def draw_sky(bitmap, t):
    for y in range(HORIZON + 1):
        if y < 3:
            color = C_SKY1
        elif y < 6:
            color = C_SKY2
        else:
            color = C_SKY3
        fill_row(bitmap, y, color)
    sun_x = 48 + int(math.sin(t * 0.15) * 2)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if dx * dx + dy * dy <= 4:
                plot(bitmap, sun_x + dx, 4 + dy, C_SUN)
    for x in range(WIDTH):
        hill = 2 + int(1.6 * math.sin(x * 0.22 + t * 0.05) + math.sin(x * 0.07))
        hy = HORIZON - hill
        for y in range(max(0, hy), HORIZON + 1):
            plot(bitmap, x, y, C_HILL)


def draw_road(bitmap, player_z, player_x, dt_stripe):
    for y in range(HEIGHT - 1, HORIZON, -1):
        span = HEIGHT - 1 - HORIZON
        near = (y - HORIZON) / span
        z_ahead = 4.0 + (1.0 - near) * (1.0 - near) * 90.0
        world_z = player_z + z_ahead
        curve = curve_at(world_z)
        half = 2.2 + near * 26.0
        center = 31.5 - player_x * half * 0.95 + curve * (1.0 - near) * 11.0
        stripe = int((world_z + dt_stripe) * 0.55) & 1
        grass = C_GRASS_A if stripe else C_GRASS_B
        rumble = C_RUMBLE_A if stripe else C_RUMBLE_B
        finish = (world_z % TRACK_LEN) < 3.2
        left = center - half
        right = center + half
        rumble_w = 1.2 + near * 2.4
        for x in range(WIDTH):
            if x < left - rumble_w or x > right + rumble_w:
                bitmap[x, y] = grass
            elif x < left or x > right:
                bitmap[x, y] = C_FINISH if finish and ((x + y) & 1) else rumble
            else:
                edge = (x < left + 1.1) or (x > right - 1.1)
                mid = abs(x - center) < (0.7 + near * 0.4)
                dash = stripe and mid and near > 0.18
                if finish:
                    bitmap[x, y] = C_WHITE if ((int(x) + int(world_z)) & 1) else C_BLACK
                elif dash:
                    bitmap[x, y] = C_DASH
                elif edge:
                    bitmap[x, y] = C_ROAD_EDGE
                else:
                    bitmap[x, y] = C_ROAD


def project_sprite(player_z, player_x, obj_z, obj_x):
    ahead = obj_z - player_z
    if ahead < 2 or ahead > 88:
        return None
    near = 1.0 - (ahead - 2.0) / 86.0
    if near < 0.08:
        return None
    half = 2.2 + near * 26.0
    curve = curve_at(obj_z)
    center = 31.5 - player_x * half * 0.95 + curve * (1.0 - near) * 11.0
    sx = int(center + obj_x * half * 0.92)
    sy = int(HORIZON + near * (HEIGHT - 1 - HORIZON))
    scale = 1 if near < 0.35 else (2 if near < 0.62 else 3)
    return sx, sy, scale, near


def draw_kart(bitmap, sx, sy, scale, body, accent, blink):
    if blink:
        body = C_WHITE
    offsets = (
        (0, -2, accent),
        (-1, -1, body),
        (0, -1, body),
        (1, -1, body),
        (-2, 0, C_YELLOW),
        (-1, 0, body),
        (0, 0, C_WHITE),
        (1, 0, body),
        (2, 0, C_YELLOW),
        (-2, 1, C_SHADOW),
        (0, 1, C_SHADOW),
        (2, 1, C_SHADOW),
    )
    for dx, dy, color in offsets:
        if scale == 1 and abs(dx) > 1:
            continue
        plot(bitmap, sx + dx, sy + dy, color)
        if scale >= 3 and dy >= 0:
            plot(bitmap, sx + dx, sy + dy + 1, color)


def draw_banana(bitmap, sx, sy, scale):
    plot(bitmap, sx, sy, C_BANANA)
    plot(bitmap, sx + 1, sy, C_YELLOW)
    if scale > 1:
        plot(bitmap, sx, sy + 1, C_YELLOW)


def draw_coin(bitmap, sx, sy, frame):
    plot(bitmap, sx, sy, C_COIN if frame else C_YELLOW)
    if frame:
        plot(bitmap, sx, sy - 1, C_YELLOW)


def draw_pad(bitmap, sx, sy):
    plot(bitmap, sx - 1, sy, C_MAGENTA)
    plot(bitmap, sx, sy, C_WHITE)
    plot(bitmap, sx + 1, sy, C_MAGENTA)


def player_kart(bitmap, boost, spin):
    sx, sy = 32, 28
    body = C_RED
    if boost:
        plot(bitmap, sx - 1, sy + 2, C_CYAN)
        plot(bitmap, sx + 1, sy + 2, C_CYAN)
        plot(bitmap, sx, sy + 2, C_WHITE)
    draw_kart(bitmap, sx, sy, 3, body, C_WHITE, spin)


def draw_hud(bitmap, lap, place, boost_left, coins):
    draw_text(bitmap, "L%d/%d" % (min(lap, LAPS), LAPS), 1, 1, C_HUD)
    draw_text(bitmap, "P%d" % place, 28, 1, C_CYAN)
    draw_text(bitmap, "$%d" % coins, 44, 1, C_COIN)
    if boost_left > 0:
        for x in range(int(boost_left * 10)):
            plot(bitmap, 1 + x, 7, C_MAGENTA)


def clear(bitmap, color=C_BLACK):
    for y in range(HEIGHT):
        fill_row(bitmap, y, color)


class Racer:
    def __init__(self, z, x, speed, body, is_player=False):
        self.z = z
        self.x = x
        self.speed = speed
        self.body = body
        self.is_player = is_player
        self.lap = 1
        self.spin = 0.0
        self.boost = 0.0
        self.finished = False
        self.place = 1


class Pickup:
    def __init__(self, kind, z, x):
        self.kind = kind
        self.z = z
        self.x = x
        self.alive = True


def make_pickups():
    items = []
    random.seed(7)
    z = 18.0
    while z < TRACK_LEN - 8:
        roll = random.random()
        lane = random.choice((-0.55, -0.2, 0.15, 0.5))
        if roll < 0.34:
            items.append(Pickup("coin", z, lane))
        elif roll < 0.58:
            items.append(Pickup("banana", z, lane))
        elif roll < 0.74:
            items.append(Pickup("pad", z, 0.0 if abs(lane) < 0.4 else lane))
        z += 16 + random.random() * 10
    return items


def race_place(player, cpus):
    def key(racer):
        return racer.lap * TRACK_LEN + racer.z

    pack = [player] + cpus
    ranked = sorted(pack, key=key, reverse=True)
    for i, racer in enumerate(ranked):
        racer.place = i + 1
    return player.place


def advance_racer(racer, steer, braking, track_curve):
    if racer.finished:
        racer.speed *= 0.96
        return
    if racer.spin > 0:
        racer.spin -= 0.05
        steer += math.sin(racer.spin * 14.0) * 0.7
        racer.speed *= 0.97
    if racer.boost > 0:
        racer.boost -= 0.04
        cap = BOOST_SPEED
        racer.speed += ACCEL * 1.8
    else:
        cap = MAX_SPEED
        racer.speed += ACCEL
    if braking:
        racer.speed -= BRAKE
    racer.speed -= DRAG * racer.speed
    racer.x += steer * (0.035 + racer.speed * 0.018)
    racer.x += track_curve * racer.speed * CENTRIFUGAL * 0.12
    off = abs(racer.x) > 0.92
    if off:
        racer.speed -= OFFROAD_DRAG
        racer.x = max(-1.18, min(1.18, racer.x))
    else:
        racer.x = max(-1.05, min(1.05, racer.x))
    racer.speed = max(0.35 if racer.is_player else 0.55, min(cap, racer.speed))
    prev = racer.z
    racer.z += racer.speed
    if racer.z >= TRACK_LEN:
        racer.z -= TRACK_LEN
        if prev > TRACK_LEN * 0.6:
            racer.lap += 1
            if racer.lap > LAPS:
                racer.finished = True
                racer.lap = LAPS


def hit_pickups(player, pickups, coins):
    for item in pickups:
        if not item.alive:
            continue
        dz = abs((item.z - player.z + TRACK_LEN) % TRACK_LEN)
        if dz > TRACK_LEN / 2:
            dz = TRACK_LEN - dz
        if dz > 2.4:
            continue
        if abs(item.x - player.x) > 0.22:
            continue
        item.alive = False
        if item.kind == "banana":
            player.spin = 1.2
            player.speed *= 0.45
        elif item.kind == "coin":
            coins += 1
        elif item.kind == "pad":
            player.boost = 1.15
            player.speed = min(BOOST_SPEED, player.speed + 0.7)
    return coins


def cpu_think(cpu, player):
    curve = curve_at(cpu.z + 10)
    target = -curve * 0.12 + math.sin(cpu.z * 0.07) * 0.18
    if abs(cpu.z - player.z) < 6 and abs(cpu.x - player.x) < 0.2:
        target += 0.28 if cpu.x < player.x else -0.28
    steer = max(-1.0, min(1.0, (target - cpu.x) * 1.6))
    return steer


def title_loop(display, bitmap, lis, up, rest):
    t = 0.0
    demo_z = 0.0
    while True:
        draw_sky(bitmap, t)
        draw_road(bitmap, demo_z, math.sin(t * 0.7) * 0.25, demo_z)
        player_kart(bitmap, False, False)
        draw_text(bitmap, "TILT", 23, 2, C_YELLOW)
        draw_text(bitmap, "KART", 23, 9, C_MAGENTA)
        if int(t * 2) & 1:
            draw_text(bitmap, "UP", 28, 16, C_HUD)
        display.refresh(minimum_frames_per_second=0)
        if button_pressed(up):
            time.sleep(0.15)
            return rest_axis(lis) if rest is None else rest
        demo_z += 1.1
        t += 0.12
        time.sleep(0.03)


def countdown(display, bitmap, player_z):
    for word, color in (("3", C_RED), ("2", C_YELLOW), ("1", C_CYAN), ("GO", C_WHITE)):
        draw_sky(bitmap, 0)
        draw_road(bitmap, player_z, 0.0, 0)
        player_kart(bitmap, False, False)
        ox = 29 if len(word) == 1 else 27
        draw_text(bitmap, word, ox, 12, color)
        display.refresh(minimum_frames_per_second=0)
        time.sleep(0.55)


def finish_screen(display, bitmap, player, coins):
    clear(bitmap)
    if player.place == 1:
        draw_text(bitmap, "WIN", 26, 8, C_YELLOW)
    else:
        draw_text(bitmap, "P%d" % player.place, 26, 8, C_CYAN)
    draw_text(bitmap, "$%d" % coins, 26, 16, C_COIN)
    draw_text(bitmap, "UP", 28, 24, C_HUD)
    display.refresh(minimum_frames_per_second=0)
    time.sleep(0.4)


def race_loop(display, bitmap, lis, up, down, rest):
    player = Racer(2.0, 0.0, 0.8, C_RED, True)
    cpus = [
        Racer(8.0, -0.25, 1.15, C_CYAN),
        Racer(14.0, 0.35, 1.05, C_ORANGE),
    ]
    pickups = make_pickups()
    coins = 0
    countdown(display, bitmap, player.z)

    while True:
        now = time.monotonic()
        steer = read_steer(lis, rest)
        braking = button_pressed(down)
        if button_pressed(up) and player.boost <= 0:
            player.boost = 0.85

        curve = curve_at(player.z)
        advance_racer(player, steer, braking, curve)
        for cpu in cpus:
            advance_racer(cpu, cpu_think(cpu, player), False, curve_at(cpu.z))
        coins = hit_pickups(player, pickups, coins)
        place = race_place(player, cpus)

        draw_sky(bitmap, player.z * 0.04)
        draw_road(bitmap, player.z, player.x, player.z)
        for item in pickups:
            if not item.alive:
                continue
            proj = project_sprite(player.z, player.x, item.z, item.x)
            if not proj:
                continue
            sx, sy, scale, _near = proj
            if item.kind == "banana":
                draw_banana(bitmap, sx, sy, scale)
            elif item.kind == "coin":
                draw_coin(bitmap, sx, sy, int(now * 8) & 1)
            else:
                draw_pad(bitmap, sx, sy)
        for cpu in cpus:
            cz = cpu.z
            if cpu.lap > player.lap:
                cz += TRACK_LEN
            elif cpu.lap < player.lap:
                cz -= TRACK_LEN
            proj = project_sprite(player.z, player.x, cz, cpu.x)
            if proj:
                sx, sy, scale, _near = proj
                draw_kart(bitmap, sx, sy, scale, cpu.body, C_WHITE, cpu.spin > 0)
        player_kart(bitmap, player.boost > 0, player.spin > 0.15)
        draw_hud(bitmap, player.lap, place, player.boost, coins)
        display.refresh(minimum_frames_per_second=0)

        if player.finished:
            finish_screen(display, bitmap, player, coins)
            while not button_pressed(up):
                time.sleep(0.02)
            time.sleep(0.2)
            return

        # keep the M4 breathing; skip extra sleep if the frame was already slow
        spent = time.monotonic() - now
        if spent < 0.028:
            time.sleep(0.028 - spent)


def main():
    display, bitmap = setup_display()
    up, down = setup_buttons()
    lis = setup_accel()
    rest = rest_axis(lis)
    while True:
        rest = title_loop(display, bitmap, lis, up, rest)
        race_loop(display, bitmap, lis, up, down, rest)


main()
