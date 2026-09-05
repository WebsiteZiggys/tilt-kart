# Tilt Kart — Matrix Portal M4 + 64x32 RGB matrix (Adafruit #4812)
# Copy this file to CIRCUITPY as code.py
#
# Tilt the panel to steer. BUTTON_UP = start / use item. BUTTON_DOWN = brake.
# Hit flashing crates for a random item, then press UP to use it.
# Rainbow pads are still a ground boost if you drive through them.
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
BIT_DEPTH = 1

STEER_AXIS = 1  # 0=X  1=Y  2=Z
STEER_FLIP = 1
STEER_DEADZONE = 0.12
STEER_SENS = 2.4

LAPS = 7
MAX_SPEED = 2.05
BOOST_SPEED = 2.85
ACCEL = 0.038
BRAKE = 0.1
DRAG = 0.016
OFFROAD_DRAG = 0.09
CENTRIFUGAL = 0.032
PAD_SPAWN_MIN = 4.0
PAD_SPAWN_MAX = 8.5
CRATE_SPAWN_MIN = 3.4
CRATE_SPAWN_MAX = 6.8
ROULETTE_TIME = 1.05
ITEM_NAMES = ("boost", "peel", "blue", "bomb")

# (length along track, curve strength)
TRACK = (
    (70, 0.0),
    (48, 2.8),
    (32, 0.8),
    (52, -3.3),
    (26, 0.2),
    (44, 2.6),
    (38, -2.4),
    (30, 0.4),
    (46, 3.1),
    (34, -2.8),
    (40, 1.6),
    (50, -3.2),
    (62, 0.0),
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
    "H": (0b101, 0b101, 0b111, 0b101, 0b101),
    "I": (0b111, 0b010, 0b010, 0b010, 0b111),
    "K": (0b101, 0b101, 0b110, 0b101, 0b101),
    "L": (0b100, 0b100, 0b100, 0b100, 0b111),
    "M": (0b101, 0b111, 0b111, 0b101, 0b101),
    "N": (0b101, 0b111, 0b111, 0b101, 0b101),
    "O": (0b010, 0b101, 0b101, 0b101, 0b010),
    "P": (0b110, 0b101, 0b110, 0b100, 0b100),
    "R": (0b110, 0b101, 0b110, 0b101, 0b101),
    "S": (0b011, 0b100, 0b010, 0b001, 0b110),
    "T": (0b111, 0b010, 0b010, 0b010, 0b010),
    "U": (0b101, 0b101, 0b101, 0b101, 0b111),
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
    "?": (0b111, 0b001, 0b011, 0b000, 0b010),
    ">": (0b100, 0b110, 0b111, 0b110, 0b100),
    "-": (0b000, 0b000, 0b111, 0b000, 0b000),
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
C_RB0 = 24
C_RB1 = 25
C_RB2 = 26
C_RB3 = 27
C_RB4 = 28
C_RB5 = 29

RAINBOW = (C_RB0, C_RB1, C_RB2, C_RB3, C_RB4, C_RB5)
PAD_HALF_Z = 5.8
PAD_HALF_X = 0.42


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
        doublebuffer=False,
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
    palette[C_RB0] = 0xFF2030
    palette[C_RB1] = 0xFF8010
    palette[C_RB2] = 0xFFE020
    palette[C_RB3] = 0x20E048
    palette[C_RB4] = 0x2090FF
    palette[C_RB5] = 0xC040FF
    tile = displayio.TileGrid(bitmap, pixel_shader=palette)
    group = displayio.Group()
    group.append(tile)
    display.root_group = group
    if hasattr(display, "show"):
        try:
            display.show(group)
        except Exception:
            pass
    return display, bitmap


def setup_buttons():
    up = digitalio.DigitalInOut(board.BUTTON_UP)
    up.switch_to_input(pull=digitalio.Pull.UP)
    down = digitalio.DigitalInOut(board.BUTTON_DOWN)
    down.switch_to_input(pull=digitalio.Pull.UP)
    return up, down


def _make_i2c():
    try:
        import bitbangio

        return bitbangio.I2C(board.SCL, board.SDA)
    except Exception:
        pass
    try:
        import busio

        return busio.I2C(board.SCL, board.SDA, frequency=100000)
    except Exception:
        pass
    try:
        return board.I2C()
    except Exception:
        return None


def setup_accel():
    if adafruit_lis3dh is None:
        return None
    i2c = _make_i2c()
    if i2c is None:
        return None
    for addr in (0x19, 0x18):
        try:
            lis = adafruit_lis3dh.LIS3DH_I2C(i2c, address=addr)
            lis.range = adafruit_lis3dh.RANGE_4_G
            _ = lis.acceleration
            return lis
        except Exception:
            pass
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
    global STEER_AXIS
    if lis is None:
        return 0.0
    xyz = rest_xyz(lis)
    absr = (abs(xyz[0]), abs(xyz[1]), abs(xyz[2]))
    # Gravity takes the largest axis. Steer on the flattest one.
    STEER_AXIS = absr.index(min(absr))
    return xyz[STEER_AXIS]


def rest_xyz(lis):
    if lis is None:
        return (0.0, 0.0, 0.0)
    acc = [0.0, 0.0, 0.0]
    count = 0
    for _ in range(6):
        try:
            a = lis.acceleration
            acc[0] += a[0]
            acc[1] += a[1]
            acc[2] += a[2]
            count += 1
        except Exception:
            pass
        time.sleep(0.02)
    if not count:
        return (0.0, 0.0, 0.0)
    return (acc[0] / count, acc[1] / count, acc[2] / count)


def motion_xyz(lis, rest):
    if lis is None:
        return 0.0, 0.0, 0.0, 0.0
    try:
        a = lis.acceleration
    except Exception:
        return 0.0, 0.0, 0.0, 0.0
    dx = a[0] - rest[0]
    dy = a[1] - rest[1]
    dz = a[2] - rest[2]
    return dx, dy, dz, (dx * dx + dy * dy + dz * dz) ** 0.5


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


def wrap_dist(a, b):
    d = abs((a - b + TRACK_LEN) % TRACK_LEN)
    if d > TRACK_LEN / 2:
        d = TRACK_LEN - d
    return d


def pickup_at(world_z, pickups, kind, half_z):
    if not pickups:
        return None
    for item in pickups:
        if item.kind != kind or not item.alive:
            continue
        if wrap_dist(world_z, item.z) < half_z:
            return item
    return None


def pad_at(world_z, pickups):
    return pickup_at(world_z, pickups, "pad", PAD_HALF_Z)


def crate_at(world_z, pickups):
    return pickup_at(world_z, pickups, "crate", 3.2)


def crate_color(world_z, x):
    return (C_WHITE, C_YELLOW, C_CYAN, C_MAGENTA)[int(world_z * 2 + x) % 4]


def rainbow_color(world_z, x, center):
    return RAINBOW[int(world_z * 1.3 + (x - center) * 0.5) % 6]


def draw_road(bitmap, player_z, player_x, dt_stripe, pickups=None):
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
        pad = pad_at(world_z, pickups)
        crate = crate_at(world_z, pickups)
        for x in range(WIDTH):
            if x < left - rumble_w or x > right + rumble_w:
                bitmap[x, y] = grass
            elif x < left or x > right:
                bitmap[x, y] = C_FINISH if finish and ((x + y) & 1) else rumble
            else:
                lane = (x - center) / half if half else 0
                on_pad = pad and abs(lane - pad.x) < PAD_HALF_X
                on_crate = crate and abs(lane - crate.x) < 0.28
                edge = (x < left + 1.1) or (x > right - 1.1)
                mid = abs(x - center) < (0.7 + near * 0.4)
                dash = stripe and mid and near > 0.18
                if finish:
                    bitmap[x, y] = C_WHITE if ((int(x) + int(world_z)) & 1) else C_BLACK
                elif on_pad:
                    rim = abs(abs(lane - pad.x) - PAD_HALF_X) < 0.07
                    bitmap[x, y] = C_WHITE if rim else rainbow_color(world_z, x, center)
                elif on_crate:
                    bitmap[x, y] = C_BLACK if ((int(x) + int(world_z)) & 1) else crate_color(world_z, x)
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


def draw_pad(bitmap, sx, sy, scale, world_z):
    span = 1 + scale
    for dx in range(-span, span + 1):
        plot(bitmap, sx + dx, sy, rainbow_color(world_z, sx + dx, sx))
        if scale > 1:
            plot(bitmap, sx + dx, sy + 1, rainbow_color(world_z + 1, sx + dx, sx))


def player_kart(bitmap, boost, spin):
    sx, sy = 32, 28
    body = C_RED
    if boost:
        plot(bitmap, sx - 1, sy + 2, C_CYAN)
        plot(bitmap, sx + 1, sy + 2, C_CYAN)
        plot(bitmap, sx, sy + 2, C_WHITE)
    draw_kart(bitmap, sx, sy, 3, body, C_WHITE, spin)


def item_icon_color(name, frame):
    if name == "boost":
        return C_CYAN
    if name == "peel":
        return C_BANANA
    if name == "blue":
        return C_RB4
    if name == "bomb":
        return C_ORANGE
    return (C_WHITE, C_YELLOW, C_CYAN, C_MAGENTA, C_RB4, C_BANANA)[frame % 6]


def draw_item_icon(bitmap, name, frame):
    color = item_icon_color(name, frame)
    for dy in range(5):
        for dx in range(5):
            edge = dx == 0 or dy == 0 or dx == 4 or dy == 4
            plot(bitmap, 58 + dx, 1 + dy, C_WHITE if edge else color)


def draw_hud(bitmap, lap, place, boost_left, coins, held, roulette, frame):
    draw_text(bitmap, "L%d/%d" % (min(lap, LAPS), LAPS), 1, 1, C_HUD)
    draw_text(bitmap, "P%d" % place, 28, 1, C_CYAN)
    if roulette > 0:
        draw_item_icon(bitmap, None, frame)
    elif held:
        draw_item_icon(bitmap, held, frame)
    else:
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
        self.held = None
        self.roulette = 0.0
        self.pending = None
        self.flash = 0.0


class Shot:
    def __init__(self, kind, z, x, target):
        self.kind = kind
        self.z = z
        self.x = x
        self.target = target
        self.alive = True


class Pickup:
    def __init__(self, kind, z, x):
        self.kind = kind
        self.z = z
        self.x = x
        self.alive = True


def make_pickups():
    items = []
    z = 12.0
    while z < TRACK_LEN - 8:
        roll = random.random()
        lane = random.choice((-0.62, -0.35, -0.1, 0.2, 0.48, 0.68))
        if roll < 0.2:
            items.append(Pickup("coin", z, lane))
        elif roll < 0.78:
            items.append(Pickup("banana", z, lane))
        z += 9 + random.random() * 7
    return items


def live_kind(pickups, kind):
    for item in pickups:
        if item.kind == kind and item.alive:
            return item
    return None


def expire_kind(pickups, player, kind):
    for item in pickups:
        if item.kind != kind or not item.alive:
            continue
        ahead = (item.z - player.z + TRACK_LEN) % TRACK_LEN
        if ahead > 88:
            item.alive = False


def spawn_ahead(pickups, player, kind, now, next_at, lo, hi):
    expire_kind(pickups, player, kind)
    if live_kind(pickups, kind) or now < next_at:
        return next_at
    ahead = 18 + random.random() * 36
    lane = random.choice((-0.58, -0.28, 0.0, 0.28, 0.58))
    pickups.append(Pickup(kind, (player.z + ahead) % TRACK_LEN, lane))
    return now + lo + random.random() * (hi - lo)


def roll_item():
    pick = random.random()
    if pick < 0.34:
        return "boost"
    if pick < 0.62:
        return "peel"
    if pick < 0.82:
        return "bomb"
    return "blue"


def race_key(racer):
    return racer.lap * TRACK_LEN + racer.z


def explode(racer):
    racer.spin = 2.0
    racer.speed *= 0.12
    racer.boost = 0.0
    racer.flash = 1.1


def blue_target(player, cpus):
    pack = sorted([player] + cpus, key=race_key, reverse=True)
    if pack[0] is not player:
        return pack[0]
    if len(pack) > 1:
        return pack[1]
    return None


def bomb_target(player, cpus):
    best = None
    best_d = 9999
    here = race_key(player)
    for other in cpus:
        d = abs(race_key(other) - here)
        if d < best_d:
            best = other
            best_d = d
    return best


def tick_roulette(player, dt):
    if player.roulette <= 0:
        return
    player.roulette -= dt
    if player.roulette <= 0:
        player.held = player.pending
        player.pending = None
        player.roulette = 0.0


def use_item(player, cpus, pickups, shots):
    if player.roulette > 0 or not player.held:
        return
    item = player.held
    player.held = None
    if item == "boost":
        player.boost = 1.2
        player.speed = min(BOOST_SPEED, player.speed + 0.75)
    elif item == "peel":
        pickups.append(Pickup("banana", (player.z - 6 + TRACK_LEN) % TRACK_LEN, player.x))
    elif item == "blue":
        target = blue_target(player, cpus)
        if target:
            shots.append(Shot("blue", player.z, player.x, target))
    elif item == "bomb":
        target = bomb_target(player, cpus)
        if target:
            shots.append(Shot("bomb", player.z, target.x, target))


def advance_shots(shots):
    for shot in shots:
        if not shot.alive or shot.target is None:
            shot.alive = False
            continue
        target = shot.target
        shot.x += (target.x - shot.x) * 0.28
        shot.z = (shot.z + 6.2) % TRACK_LEN
        if wrap_dist(shot.z, target.z) < 6.5:
            explode(target)
            shot.alive = False


def race_place(player, cpus):
    pack = [player] + cpus
    ranked = sorted(pack, key=race_key, reverse=True)
    for i, racer in enumerate(ranked):
        racer.place = i + 1
    return player.place


def advance_racer(racer, steer, braking, track_curve):
    if racer.finished:
        racer.speed *= 0.96
        return
    if racer.flash > 0:
        racer.flash -= 0.05
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


def hit_one(racer, item, coins, is_player):
    if item.kind == "banana":
        racer.spin = 1.65
        racer.speed *= 0.32
        racer.boost = 0.0
        return coins, True
    if not is_player:
        return coins, False
    if item.kind == "coin":
        return coins + 1, True
    if item.kind == "pad":
        racer.boost = 1.15
        racer.speed = min(BOOST_SPEED, racer.speed + 0.7)
        return coins, True
    if item.kind == "crate":
        if racer.held or racer.roulette > 0:
            return coins, False
        racer.roulette = ROULETTE_TIME
        racer.pending = roll_item()
        racer.held = None
        return coins, True
    return coins, False


def hit_pickups(player, cpus, pickups, coins):
    pack = [(player, True)] + [(cpu, False) for cpu in cpus]
    for item in pickups:
        if not item.alive:
            continue
        for racer, is_player in pack:
            dz = wrap_dist(item.z, racer.z)
            reach_z = PAD_HALF_Z if item.kind == "pad" else (3.0 if item.kind == "crate" else 2.4)
            reach_x = PAD_HALF_X if item.kind == "pad" else (0.3 if item.kind == "crate" else 0.22)
            if dz > reach_z or abs(item.x - racer.x) > reach_x:
                continue
            coins, used = hit_one(racer, item, coins, is_player)
            if used:
                item.alive = False
                break
    return coins


def cpu_think(cpu, player):
    curve = curve_at(cpu.z + 12)
    target = -curve * 0.16 + math.sin(cpu.z * 0.05) * 0.1
    if abs(cpu.z - player.z) < 7 and abs(cpu.x - player.x) < 0.18:
        target += 0.32 if cpu.x < player.x else -0.32
    steer = max(-1.0, min(1.0, (target - cpu.x) * 2.0))
    return steer


def title_loop(display, bitmap, lis, up, rest):
    t = 0.0
    demo_z = 0.0
    demo_pads = (Pickup("crate", 28.0, 0.0), Pickup("pad", 70.0, -0.2))
    while True:
        draw_sky(bitmap, t)
        draw_road(bitmap, demo_z, math.sin(t * 0.7) * 0.25, demo_z, demo_pads)
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
        time.sleep(0.28)


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
    player = Racer(2.0, 0.0, 0.65, C_RED, True)
    cpus = [
        Racer(10.0, -0.22, 1.32, C_CYAN),
        Racer(16.0, 0.3, 1.24, C_ORANGE),
        Racer(22.0, -0.4, 1.18, C_MAGENTA),
    ]
    pickups = make_pickups()
    shots = []
    coins = 0
    next_pad_at = time.monotonic() + 3.0 + random.random() * 2.0
    next_crate_at = time.monotonic() + 1.6 + random.random() * 1.4
    was_up = True
    countdown(display, bitmap, player.z)

    while True:
        now = time.monotonic()
        steer = read_steer(lis, rest)
        braking = button_pressed(down)
        up_now = button_pressed(up)
        if up_now and not was_up:
            use_item(player, cpus, pickups, shots)
        was_up = up_now
        next_pad_at = spawn_ahead(
            pickups, player, "pad", now, next_pad_at, PAD_SPAWN_MIN, PAD_SPAWN_MAX
        )
        next_crate_at = spawn_ahead(
            pickups, player, "crate", now, next_crate_at, CRATE_SPAWN_MIN, CRATE_SPAWN_MAX
        )
        tick_roulette(player, 0.03)
        advance_shots(shots)

        curve = curve_at(player.z)
        advance_racer(player, steer, braking, curve)
        for cpu in cpus:
            advance_racer(cpu, cpu_think(cpu, player), False, curve_at(cpu.z))
        coins = hit_pickups(player, cpus, pickups, coins)
        place = race_place(player, cpus)

        draw_sky(bitmap, player.z * 0.04)
        draw_road(bitmap, player.z, player.x, player.z, pickups)
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
            elif item.kind == "pad" and scale == 1:
                draw_pad(bitmap, sx, sy, scale, item.z)
        for shot in shots:
            if not shot.alive:
                continue
            proj = project_sprite(player.z, player.x, shot.z, shot.x)
            if proj:
                color = C_RB4 if shot.kind == "blue" else C_ORANGE
                plot(bitmap, proj[0], proj[1], color)
                plot(bitmap, proj[0], proj[1] - 1, C_WHITE)
        for cpu in cpus:
            cz = cpu.z
            if cpu.lap > player.lap:
                cz += TRACK_LEN
            elif cpu.lap < player.lap:
                cz -= TRACK_LEN
            proj = project_sprite(player.z, player.x, cz, cpu.x)
            if proj:
                sx, sy, scale, _near = proj
                draw_kart(bitmap, sx, sy, scale, cpu.body, C_WHITE, cpu.spin > 0 or cpu.flash > 0)
        player_kart(bitmap, player.boost > 0, player.spin > 0.15 or player.flash > 0)
        draw_hud(bitmap, player.lap, place, player.boost, coins, player.held, player.roulette, int(now * 12))
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


def run(display, bitmap, lis, up, down):
    rest = rest_axis(lis)
    race_loop(display, bitmap, lis, up, down, rest)
