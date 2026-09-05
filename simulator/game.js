const WIDTH = 64;
const HEIGHT = 32;
const HORIZON = 9;
const LAPS = 7;
const MAX_SPEED = 2.05;
const BOOST_SPEED = 2.85;
const ACCEL = 0.038;
const BRAKE = 0.1;
const DRAG = 0.016;
const OFFROAD_DRAG = 0.09;
const CENTRIFUGAL = 0.032;
const PAD_SPAWN_MIN = 4.0;
const PAD_SPAWN_MAX = 8.5;
const CRATE_SPAWN_MIN = 3.4;
const CRATE_SPAWN_MAX = 6.8;
const ROULETTE_TIME = 1.05;

const TRACK = [
  [70, 0.0],
  [48, 2.8],
  [32, 0.8],
  [52, -3.3],
  [26, 0.2],
  [44, 2.6],
  [38, -2.4],
  [30, 0.4],
  [46, 3.1],
  [34, -2.8],
  [40, 1.6],
  [50, -3.2],
  [62, 0.0],
];

const PALETTE = {
  BLACK: "#000000",
  SKY1: "#12002a",
  SKY2: "#2a1060",
  SKY3: "#ff6a20",
  SUN: "#ffd84a",
  HILL: "#1a0a28",
  GRASS_A: "#0a4a18",
  GRASS_B: "#167028",
  RUMBLE_A: "#e01020",
  RUMBLE_B: "#f0f0f0",
  ROAD: "#2a2a36",
  ROAD_EDGE: "#4a4a58",
  DASH: "#f0d020",
  FINISH: "#f8f8f8",
  HUD: "#f4f4ff",
  RED: "#ff2040",
  WHITE: "#ffffff",
  CYAN: "#20f0ff",
  YELLOW: "#ffe020",
  MAGENTA: "#ff40c8",
  ORANGE: "#ff8020",
  SHADOW: "#101018",
  BANANA: "#ffe040",
  COIN: "#ffc000",
  RB0: "#ff2030",
  RB1: "#ff8010",
  RB2: "#ffe020",
  RB3: "#20e048",
  RB4: "#2090ff",
  RB5: "#c040ff",
};

const RAINBOW = [PALETTE.RB0, PALETTE.RB1, PALETTE.RB2, PALETTE.RB3, PALETTE.RB4, PALETTE.RB5];
const PAD_HALF_Z = 5.8;
const PAD_HALF_X = 0.42;

const FONT = {
  " ": 0,
  A: [0b010, 0b101, 0b111, 0b101, 0b101],
  B: [0b110, 0b101, 0b110, 0b101, 0b110],
  C: [0b011, 0b100, 0b100, 0b100, 0b011],
  D: [0b110, 0b101, 0b101, 0b101, 0b110],
  E: [0b111, 0b100, 0b110, 0b100, 0b111],
  G: [0b011, 0b100, 0b101, 0b101, 0b011],
  I: [0b111, 0b010, 0b010, 0b010, 0b111],
  K: [0b101, 0b101, 0b110, 0b101, 0b101],
  L: [0b100, 0b100, 0b100, 0b100, 0b111],
  N: [0b101, 0b111, 0b111, 0b101, 0b101],
  O: [0b010, 0b101, 0b101, 0b101, 0b010],
  P: [0b110, 0b101, 0b110, 0b100, 0b100],
  R: [0b110, 0b101, 0b110, 0b101, 0b101],
  S: [0b011, 0b100, 0b010, 0b001, 0b110],
  T: [0b111, 0b010, 0b010, 0b010, 0b010],
  W: [0b101, 0b101, 0b111, 0b111, 0b101],
  Y: [0b101, 0b101, 0b010, 0b010, 0b010],
  0: [0b111, 0b101, 0b101, 0b101, 0b111],
  1: [0b010, 0b110, 0b010, 0b010, 0b111],
  2: [0b111, 0b001, 0b111, 0b100, 0b111],
  3: [0b111, 0b001, 0b111, 0b001, 0b111],
  4: [0b101, 0b101, 0b111, 0b001, 0b001],
  5: [0b111, 0b100, 0b111, 0b001, 0b111],
  6: [0b111, 0b100, 0b111, 0b101, 0b111],
  7: [0b111, 0b001, 0b001, 0b001, 0b001],
  8: [0b111, 0b101, 0b111, 0b101, 0b111],
  9: [0b111, 0b101, 0b111, 0b001, 0b111],
  "/": [0b001, 0b001, 0b010, 0b100, 0b100],
  "!": [0b010, 0b010, 0b010, 0b000, 0b010],
  $: [0b010, 0b111, 0b110, 0b011, 0b111],
  "?": [0b111, 0b001, 0b011, 0b000, 0b010],
};

function buildTrack() {
  const starts = [];
  let z = 0;
  for (const [length, curve] of TRACK) {
    starts.push({ start: z, length, curve });
    z += length;
  }
  return { segments: starts, length: z };
}

const { segments: SEGMENTS, length: TRACK_LEN } = buildTrack();

function curveAt(z) {
  z = ((z % TRACK_LEN) + TRACK_LEN) % TRACK_LEN;
  for (const seg of SEGMENTS) {
    if (z < seg.start + seg.length) return seg.curve;
  }
  return 0;
}

class PixelBuffer {
  constructor() {
    this.pixels = new Array(WIDTH * HEIGHT).fill(PALETTE.BLACK);
  }

  clear(color = PALETTE.BLACK) {
    this.pixels.fill(color);
  }

  plot(x, y, color) {
    if (x < 0 || y < 0 || x >= WIDTH || y >= HEIGHT) return;
    this.pixels[y * WIDTH + x] = color;
  }

  fillRow(y, color) {
    const row = y * WIDTH;
    for (let x = 0; x < WIDTH; x++) this.pixels[row + x] = color;
  }

  text(str, x, y, color) {
    let cx = x;
    for (const ch of str) {
      const glyph = FONT[ch] ?? FONT[" "];
      if (glyph === 0) {
        cx += 4;
        continue;
      }
      for (let row = 0; row < 5; row++) {
        const bits = glyph[row];
        for (let col = 0; col < 3; col++) {
          if (bits & (0b100 >> col)) this.plot(cx + col, y + row, color);
        }
      }
      cx += 4;
    }
  }
}

function drawSky(buf, t) {
  for (let y = 0; y <= HORIZON; y++) {
    const color = y < 3 ? PALETTE.SKY1 : y < 6 ? PALETTE.SKY2 : PALETTE.SKY3;
    buf.fillRow(y, color);
  }
  const sunX = 48 + Math.round(Math.sin(t * 0.15) * 2);
  for (let dy = -2; dy <= 2; dy++) {
    for (let dx = -2; dx <= 2; dx++) {
      if (dx * dx + dy * dy <= 4) buf.plot(sunX + dx, 4 + dy, PALETTE.SUN);
    }
  }
  for (let x = 0; x < WIDTH; x++) {
    const hill = 2 + Math.round(1.6 * Math.sin(x * 0.22 + t * 0.05) + Math.sin(x * 0.07));
    const hy = HORIZON - hill;
    for (let y = Math.max(0, hy); y <= HORIZON; y++) buf.plot(x, y, PALETTE.HILL);
  }
}

function wrapDist(a, b) {
  let d = Math.abs((a - b + TRACK_LEN) % TRACK_LEN);
  if (d > TRACK_LEN / 2) d = TRACK_LEN - d;
  return d;
}

function pickupAt(worldZ, pickups, kind, halfZ) {
  if (!pickups) return null;
  for (const item of pickups) {
    if (item.kind !== kind || !item.alive) continue;
    if (wrapDist(worldZ, item.z) < halfZ) return item;
  }
  return null;
}

function padAt(worldZ, pickups) {
  return pickupAt(worldZ, pickups, "pad", PAD_HALF_Z);
}

function crateAt(worldZ, pickups) {
  return pickupAt(worldZ, pickups, "crate", 3.2);
}

function crateColor(worldZ, x) {
  return [PALETTE.WHITE, PALETTE.YELLOW, PALETTE.CYAN, PALETTE.MAGENTA][Math.abs(Math.floor(worldZ * 2 + x)) % 4];
}

function rainbowColor(worldZ, x, center) {
  return RAINBOW[Math.abs(Math.floor(worldZ * 1.3 + (x - center) * 0.5)) % 6];
}

function drawRoad(buf, playerZ, playerX, pickups = null) {
  for (let y = HEIGHT - 1; y > HORIZON; y--) {
    const span = HEIGHT - 1 - HORIZON;
    const near = (y - HORIZON) / span;
    const zAhead = 4 + (1 - near) * (1 - near) * 90;
    const worldZ = playerZ + zAhead;
    const curve = curveAt(worldZ);
    const half = 2.2 + near * 26;
    const center = 31.5 - playerX * half * 0.95 + curve * (1 - near) * 11;
    const stripe = (Math.floor((worldZ) * 0.55) & 1) === 1;
    const grass = stripe ? PALETTE.GRASS_B : PALETTE.GRASS_A;
    const rumble = stripe ? PALETTE.RUMBLE_B : PALETTE.RUMBLE_A;
    const finish = ((worldZ % TRACK_LEN) + TRACK_LEN) % TRACK_LEN < 3.2;
    const left = center - half;
    const right = center + half;
    const rumbleW = 1.2 + near * 2.4;
    const pad = padAt(worldZ, pickups);
    const crate = crateAt(worldZ, pickups);
    const row = y * WIDTH;
    for (let x = 0; x < WIDTH; x++) {
      if (x < left - rumbleW || x > right + rumbleW) {
        buf.pixels[row + x] = grass;
      } else if (x < left || x > right) {
        buf.pixels[row + x] = finish && ((x + y) & 1) ? PALETTE.FINISH : rumble;
      } else {
        const lane = half ? (x - center) / half : 0;
        const onPad = pad && Math.abs(lane - pad.x) < PAD_HALF_X;
        const onCrate = crate && Math.abs(lane - crate.x) < 0.28;
        const edge = x < left + 1.1 || x > right - 1.1;
        const mid = Math.abs(x - center) < 0.7 + near * 0.4;
        const dash = stripe && mid && near > 0.18;
        if (finish) {
          buf.pixels[row + x] = (Math.floor(x) + Math.floor(worldZ)) & 1 ? PALETTE.WHITE : PALETTE.BLACK;
        } else if (onPad) {
          const rim = Math.abs(Math.abs(lane - pad.x) - PAD_HALF_X) < 0.07;
          buf.pixels[row + x] = rim ? PALETTE.WHITE : rainbowColor(worldZ, x, center);
        } else if (onCrate) {
          buf.pixels[row + x] = (Math.floor(x) + Math.floor(worldZ)) & 1 ? PALETTE.BLACK : crateColor(worldZ, x);
        } else if (dash) {
          buf.pixels[row + x] = PALETTE.DASH;
        } else if (edge) {
          buf.pixels[row + x] = PALETTE.ROAD_EDGE;
        } else {
          buf.pixels[row + x] = PALETTE.ROAD;
        }
      }
    }
  }
}

function projectSprite(playerZ, playerX, objZ, objX) {
  const ahead = objZ - playerZ;
  if (ahead < 2 || ahead > 88) return null;
  const near = 1 - (ahead - 2) / 86;
  if (near < 0.08) return null;
  const half = 2.2 + near * 26;
  const curve = curveAt(objZ);
  const center = 31.5 - playerX * half * 0.95 + curve * (1 - near) * 11;
  return {
    sx: Math.round(center + objX * half * 0.92),
    sy: Math.round(HORIZON + near * (HEIGHT - 1 - HORIZON)),
    scale: near < 0.35 ? 1 : near < 0.62 ? 2 : 3,
  };
}

function drawKart(buf, sx, sy, scale, body, blink) {
  const color = blink ? PALETTE.WHITE : body;
  const offsets = [
    [0, -2, PALETTE.WHITE],
    [-1, -1, color],
    [0, -1, color],
    [1, -1, color],
    [-2, 0, PALETTE.YELLOW],
    [-1, 0, color],
    [0, 0, PALETTE.WHITE],
    [1, 0, color],
    [2, 0, PALETTE.YELLOW],
    [-2, 1, PALETTE.SHADOW],
    [0, 1, PALETTE.SHADOW],
    [2, 1, PALETTE.SHADOW],
  ];
  for (const [dx, dy, c] of offsets) {
    if (scale === 1 && Math.abs(dx) > 1) continue;
    buf.plot(sx + dx, sy + dy, c);
    if (scale >= 3 && dy >= 0) buf.plot(sx + dx, sy + dy + 1, c);
  }
}

function drawBanana(buf, sx, sy, scale) {
  buf.plot(sx, sy, PALETTE.BANANA);
  buf.plot(sx + 1, sy, PALETTE.YELLOW);
  if (scale > 1) buf.plot(sx, sy + 1, PALETTE.YELLOW);
}

function drawCoin(buf, sx, sy, frame) {
  buf.plot(sx, sy, frame ? PALETTE.COIN : PALETTE.YELLOW);
  if (frame) buf.plot(sx, sy - 1, PALETTE.YELLOW);
}

function drawPad(buf, sx, sy, scale, worldZ) {
  const span = 1 + scale;
  for (let dx = -span; dx <= span; dx++) {
    buf.plot(sx + dx, sy, rainbowColor(worldZ, sx + dx, sx));
    if (scale > 1) buf.plot(sx + dx, sy + 1, rainbowColor(worldZ + 1, sx + dx, sx));
  }
}

function drawPlayerKart(buf, boost, spin) {
  if (boost) {
    buf.plot(31, 30, PALETTE.CYAN);
    buf.plot(33, 30, PALETTE.CYAN);
    buf.plot(32, 30, PALETTE.WHITE);
  }
  drawKart(buf, 32, 28, 3, PALETTE.RED, spin);
}

class Racer {
  constructor(z, x, speed, body, isPlayer = false) {
    this.z = z;
    this.x = x;
    this.speed = speed;
    this.body = body;
    this.isPlayer = isPlayer;
    this.lap = 1;
    this.spin = 0;
    this.boost = 0;
    this.finished = false;
    this.place = 1;
    this.held = null;
    this.roulette = 0;
    this.pending = null;
    this.flash = 0;
  }
}

class Shot {
  constructor(kind, z, x, target) {
    this.kind = kind;
    this.z = z;
    this.x = x;
    this.target = target;
    this.alive = true;
  }
}

class Pickup {
  constructor(kind, z, x) {
    this.kind = kind;
    this.z = z;
    this.x = x;
    this.alive = true;
  }
}

function makePickups() {
  const items = [];
  let z = 12;
  const lanes = [-0.62, -0.35, -0.1, 0.2, 0.48, 0.68];
  while (z < TRACK_LEN - 8) {
    const roll = Math.random();
    const lane = lanes[Math.floor(Math.random() * lanes.length)];
    if (roll < 0.2) items.push(new Pickup("coin", z, lane));
    else if (roll < 0.78) items.push(new Pickup("banana", z, lane));
    z += 9 + Math.random() * 7;
  }
  return items;
}

function liveKind(pickups, kind) {
  return pickups.find((item) => item.kind === kind && item.alive) || null;
}

function expireKind(pickups, player, kind) {
  for (const item of pickups) {
    if (item.kind !== kind || !item.alive) continue;
    const ahead = (item.z - player.z + TRACK_LEN) % TRACK_LEN;
    if (ahead > 88) item.alive = false;
  }
}

function spawnAhead(pickups, player, kind, now, nextAt, lo, hi) {
  expireKind(pickups, player, kind);
  if (liveKind(pickups, kind) || now < nextAt) return nextAt;
  const ahead = 18 + Math.random() * 36;
  const lanes = [-0.58, -0.28, 0, 0.28, 0.58];
  pickups.push(new Pickup(kind, (player.z + ahead) % TRACK_LEN, lanes[Math.floor(Math.random() * lanes.length)]));
  return now + lo + Math.random() * (hi - lo);
}

function rollItem() {
  const pick = Math.random();
  if (pick < 0.34) return "boost";
  if (pick < 0.62) return "peel";
  if (pick < 0.82) return "bomb";
  return "blue";
}

function raceKey(racer) {
  return racer.lap * TRACK_LEN + racer.z;
}

function explode(racer) {
  racer.spin = 2;
  racer.speed *= 0.12;
  racer.boost = 0;
  racer.flash = 1.1;
}

function blueTarget(player, cpus) {
  const pack = [player, ...cpus].sort((a, b) => raceKey(b) - raceKey(a));
  if (pack[0] !== player) return pack[0];
  return pack[1] || null;
}

function bombTarget(player, cpus) {
  let best = null;
  let bestD = 9999;
  const here = raceKey(player);
  for (const other of cpus) {
    const d = Math.abs(raceKey(other) - here);
    if (d < bestD) {
      best = other;
      bestD = d;
    }
  }
  return best;
}

function tickRoulette(player, dt) {
  if (player.roulette <= 0) return;
  player.roulette -= dt;
  if (player.roulette <= 0) {
    player.held = player.pending;
    player.pending = null;
    player.roulette = 0;
  }
}

function useItem(player, cpus, pickups, shots) {
  if (player.roulette > 0 || !player.held) return;
  const item = player.held;
  player.held = null;
  if (item === "boost") {
    player.boost = 1.2;
    player.speed = Math.min(BOOST_SPEED, player.speed + 0.75);
  } else if (item === "peel") {
    pickups.push(new Pickup("banana", (player.z - 6 + TRACK_LEN) % TRACK_LEN, player.x));
  } else if (item === "blue") {
    const target = blueTarget(player, cpus);
    if (target) shots.push(new Shot("blue", player.z, player.x, target));
  } else if (item === "bomb") {
    const target = bombTarget(player, cpus);
    if (target) shots.push(new Shot("bomb", player.z, target.x, target));
  }
}

function advanceShots(shots) {
  for (const shot of shots) {
    if (!shot.alive || !shot.target) {
      shot.alive = false;
      continue;
    }
    shot.x += (shot.target.x - shot.x) * 0.28;
    shot.z = (shot.z + 6.2) % TRACK_LEN;
    if (wrapDist(shot.z, shot.target.z) < 6.5) {
      explode(shot.target);
      shot.alive = false;
    }
  }
}

function itemIconColor(name, frame) {
  if (name === "boost") return PALETTE.CYAN;
  if (name === "peel") return PALETTE.BANANA;
  if (name === "blue") return PALETTE.RB4;
  if (name === "bomb") return PALETTE.ORANGE;
  return [PALETTE.WHITE, PALETTE.YELLOW, PALETTE.CYAN, PALETTE.MAGENTA, PALETTE.RB4, PALETTE.BANANA][frame % 6];
}

function drawItemIcon(buf, name, frame) {
  const color = itemIconColor(name, frame);
  for (let dy = 0; dy < 5; dy++) {
    for (let dx = 0; dx < 5; dx++) {
      const edge = dx === 0 || dy === 0 || dx === 4 || dy === 4;
      buf.plot(58 + dx, 1 + dy, edge ? PALETTE.WHITE : color);
    }
  }
}

function racePlace(player, cpus) {
  const pack = [player, ...cpus].sort((a, b) => raceKey(b) - raceKey(a));
  pack.forEach((racer, i) => {
    racer.place = i + 1;
  });
  return player.place;
}

function advanceRacer(racer, steer, braking, trackCurve) {
  if (racer.finished) {
    racer.speed *= 0.96;
    return;
  }
  if (racer.flash > 0) racer.flash -= 0.05;
  if (racer.spin > 0) {
    racer.spin -= 0.05;
    steer += Math.sin(racer.spin * 14) * 0.7;
    racer.speed *= 0.97;
  }
  const cap = racer.boost > 0 ? BOOST_SPEED : MAX_SPEED;
  if (racer.boost > 0) {
    racer.boost -= 0.04;
    racer.speed += ACCEL * 1.8;
  } else {
    racer.speed += ACCEL;
  }
  if (braking) racer.speed -= BRAKE;
  racer.speed -= DRAG * racer.speed;
  racer.x += steer * (0.035 + racer.speed * 0.018);
  racer.x += trackCurve * racer.speed * CENTRIFUGAL * 0.12;
  if (Math.abs(racer.x) > 0.92) {
    racer.speed -= OFFROAD_DRAG;
    racer.x = Math.max(-1.18, Math.min(1.18, racer.x));
  } else {
    racer.x = Math.max(-1.05, Math.min(1.05, racer.x));
  }
  racer.speed = Math.max(racer.isPlayer ? 0.35 : 0.55, Math.min(cap, racer.speed));
  const prev = racer.z;
  racer.z += racer.speed;
  if (racer.z >= TRACK_LEN) {
    racer.z -= TRACK_LEN;
    if (prev > TRACK_LEN * 0.6) {
      racer.lap += 1;
      if (racer.lap > LAPS) {
        racer.finished = true;
        racer.lap = LAPS;
      }
    }
  }
}

function hitOne(racer, item, coins, isPlayer) {
  if (item.kind === "banana") {
    racer.spin = 1.65;
    racer.speed *= 0.32;
    racer.boost = 0;
    return [coins, true];
  }
  if (!isPlayer) return [coins, false];
  if (item.kind === "coin") return [coins + 1, true];
  if (item.kind === "pad") {
    racer.boost = 1.15;
    racer.speed = Math.min(BOOST_SPEED, racer.speed + 0.7);
    return [coins, true];
  }
  if (item.kind === "crate") {
    if (racer.held || racer.roulette > 0) return [coins, false];
    racer.roulette = ROULETTE_TIME;
    racer.pending = rollItem();
    racer.held = null;
    return [coins, true];
  }
  return [coins, false];
}

function hitPickups(player, cpus, pickups, coins) {
  const pack = [[player, true], ...cpus.map((cpu) => [cpu, false])];
  for (const item of pickups) {
    if (!item.alive) continue;
    for (const [racer, isPlayer] of pack) {
      const dz = wrapDist(item.z, racer.z);
      const reachZ = item.kind === "pad" ? PAD_HALF_Z : item.kind === "crate" ? 3 : 2.4;
      const reachX = item.kind === "pad" ? PAD_HALF_X : item.kind === "crate" ? 0.3 : 0.22;
      if (dz > reachZ || Math.abs(item.x - racer.x) > reachX) continue;
      const [nextCoins, used] = hitOne(racer, item, coins, isPlayer);
      coins = nextCoins;
      if (used) {
        item.alive = false;
        break;
      }
    }
  }
  return coins;
}

function cpuThink(cpu, player) {
  const curve = curveAt(cpu.z + 12);
  let target = -curve * 0.16 + Math.sin(cpu.z * 0.05) * 0.1;
  if (Math.abs(cpu.z - player.z) < 7 && Math.abs(cpu.x - player.x) < 0.18) {
    target += cpu.x < player.x ? 0.32 : -0.32;
  }
  return Math.max(-1, Math.min(1, (target - cpu.x) * 2));
}

export function createGame(canvas, statusEl) {
  const ctx = canvas.getContext("2d");
  const buf = new PixelBuffer();
  const keys = new Set();
  let tilt = 0;
  let mode = "title";
  let player;
  let cpus;
  let pickups;
  let shots;
  let coins = 0;
  let demoZ = 0;
  let time = 0;
  let countdownAt = 0;
  let countdownWord = "3";
  let nextPadAt = 0;
  let nextCrateAt = 0;
  let lastNow = performance.now();
  let physAcc = 0;
  let useArmed = true;
  const STEP = 0.03;

  function resetRace() {
    player = new Racer(2, 0, 0.65, PALETTE.RED, true);
    cpus = [
      new Racer(10, -0.22, 1.32, PALETTE.CYAN),
      new Racer(16, 0.3, 1.24, PALETTE.ORANGE),
      new Racer(22, -0.4, 1.18, PALETTE.MAGENTA),
    ];
    pickups = makePickups();
    shots = [];
    coins = 0;
    nextPadAt = performance.now() / 1000 + 3 + Math.random() * 2;
    nextCrateAt = performance.now() / 1000 + 1.6 + Math.random() * 1.4;
    useArmed = true;
    mode = "countdown";
    countdownAt = performance.now();
    countdownWord = "3";
  }

  function inputSteer() {
    let steer = tilt;
    if (keys.has("arrowleft") || keys.has("a")) steer -= 1;
    if (keys.has("arrowright") || keys.has("d")) steer += 1;
    return Math.max(-1, Math.min(1, steer));
  }

  function braking() {
    return keys.has("arrowdown") || keys.has("s");
  }

  function useHeldDown() {
    return keys.has(" ") || keys.has("arrowup") || keys.has("w") || keys.has("e");
  }

  function renderTitle() {
    const demoPads = [new Pickup("crate", 28, 0), new Pickup("pad", 70, -0.2)];
    drawSky(buf, time);
    drawRoad(buf, demoZ, Math.sin(time * 0.7) * 0.25, demoPads);
    drawPlayerKart(buf, false, false);
    buf.text("TILT", 23, 2, PALETTE.YELLOW);
    buf.text("KART", 23, 9, PALETTE.MAGENTA);
    if (Math.floor(time * 2) & 1) buf.text("GO", 28, 16, PALETTE.HUD);
    statusEl.textContent = "Enter or click to race · hit crates · space uses the item";
  }

  function renderCountdown() {
    const elapsed = performance.now() - countdownAt;
    countdownWord = elapsed < 550 ? "3" : elapsed < 1100 ? "2" : elapsed < 1650 ? "1" : "GO";
    drawSky(buf, 0);
    drawRoad(buf, player.z, 0);
    drawPlayerKart(buf, false, false);
    buf.text(countdownWord, countdownWord.length === 1 ? 29 : 27, 12, PALETTE.WHITE);
    if (elapsed > 2100) mode = "race";
    statusEl.textContent = "Get ready";
  }

  function stepRace() {
    const now = performance.now() / 1000;
    const steer = inputSteer();
    const using = useHeldDown();
    if (using && useArmed) useItem(player, cpus, pickups, shots);
    useArmed = !using;
    nextPadAt = spawnAhead(pickups, player, "pad", now, nextPadAt, PAD_SPAWN_MIN, PAD_SPAWN_MAX);
    nextCrateAt = spawnAhead(pickups, player, "crate", now, nextCrateAt, CRATE_SPAWN_MIN, CRATE_SPAWN_MAX);
    tickRoulette(player, STEP);
    advanceShots(shots);
    advanceRacer(player, steer, braking(), curveAt(player.z));
    for (const cpu of cpus) advanceRacer(cpu, cpuThink(cpu, player), false, curveAt(cpu.z));
    coins = hitPickups(player, cpus, pickups, coins);
    racePlace(player, cpus);
    if (player.finished) mode = "finish";
  }

  function renderRace() {

    drawSky(buf, player.z * 0.04);
    drawRoad(buf, player.z, player.x, pickups);
    for (const item of pickups) {
      if (!item.alive) continue;
      const proj = projectSprite(player.z, player.x, item.z, item.x);
      if (!proj) continue;
      if (item.kind === "banana") drawBanana(buf, proj.sx, proj.sy, proj.scale);
      else if (item.kind === "coin") drawCoin(buf, proj.sx, proj.sy, Math.floor(time * 8) & 1);
      else if (item.kind === "pad" && proj.scale === 1) drawPad(buf, proj.sx, proj.sy, proj.scale, item.z);
    }
    for (const shot of shots) {
      if (!shot.alive) continue;
      const proj = projectSprite(player.z, player.x, shot.z, shot.x);
      if (proj) {
        buf.plot(proj.sx, proj.sy, shot.kind === "blue" ? PALETTE.RB4 : PALETTE.ORANGE);
        buf.plot(proj.sx, proj.sy - 1, PALETTE.WHITE);
      }
    }
    for (const cpu of cpus) {
      let cz = cpu.z;
      if (cpu.lap > player.lap) cz += TRACK_LEN;
      else if (cpu.lap < player.lap) cz -= TRACK_LEN;
      const proj = projectSprite(player.z, player.x, cz, cpu.x);
      if (proj) drawKart(buf, proj.sx, proj.sy, proj.scale, cpu.body, cpu.spin > 0 || cpu.flash > 0);
    }
    drawPlayerKart(buf, player.boost > 0, player.spin > 0.15 || player.flash > 0);
    buf.text(`L${Math.min(player.lap, LAPS)}/${LAPS}`, 1, 1, PALETTE.HUD);
    buf.text(`P${player.place}`, 28, 1, PALETTE.CYAN);
    const frame = Math.floor(time * 12);
    if (player.roulette > 0) drawItemIcon(buf, null, frame);
    else if (player.held) drawItemIcon(buf, player.held, frame);
    else buf.text(`$${coins}`, 44, 1, PALETTE.COIN);
    if (player.boost > 0) {
      for (let x = 0; x < Math.floor(player.boost * 10); x++) buf.plot(1 + x, 7, PALETTE.MAGENTA);
    }
    const itemName = player.roulette > 0 ? "cycling..." : player.held || "no item";
    statusEl.textContent = `Lap ${player.lap}/${LAPS} · P${player.place} · ${itemName} · space to use`;
  }

  function renderFinish() {
    buf.clear(PALETTE.BLACK);
    if (player.place === 1) buf.text("WIN", 26, 8, PALETTE.YELLOW);
    else buf.text(`P${player.place}`, 26, 8, PALETTE.CYAN);
    buf.text(`$${coins}`, 26, 16, PALETTE.COIN);
    buf.text("GO", 28, 24, PALETTE.HUD);
    statusEl.textContent = "Enter to race again";
  }

  function paint() {
    const rect = canvas.getBoundingClientRect();
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const w = Math.floor(rect.width * dpr);
    const h = Math.floor(rect.height * dpr);
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
    }
    ctx.fillStyle = "#07080c";
    ctx.fillRect(0, 0, w, h);
    const gap = Math.min(w / WIDTH, h / HEIGHT);
    const ox = (w - gap * WIDTH) / 2;
    const oy = (h - gap * HEIGHT) / 2;
    const r = gap * 0.34;
    for (let y = 0; y < HEIGHT; y++) {
      for (let x = 0; x < WIDTH; x++) {
        const color = buf.pixels[y * WIDTH + x];
        const cx = ox + x * gap + gap / 2;
        const cy = oy + y * gap + gap / 2;
        ctx.beginPath();
        ctx.fillStyle = color;
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.fill();
        if (color !== PALETTE.BLACK && color !== PALETTE.SKY1) {
          ctx.globalAlpha = 0.22;
          ctx.beginPath();
          ctx.arc(cx, cy, r * 1.8, 0, Math.PI * 2);
          ctx.fill();
          ctx.globalAlpha = 1;
        }
      }
    }
  }

  function frame(now) {
    const dt = Math.min(0.08, (now - lastNow) / 1000);
    lastNow = now;
    time = now / 1000;
    physAcc += dt;
    while (physAcc >= STEP) {
      physAcc -= STEP;
      if (mode === "title") demoZ += 1.1;
      else if (mode === "race") stepRace();
    }
    if (mode === "title") renderTitle();
    else if (mode === "countdown") renderCountdown();
    else if (mode === "race") renderRace();
    else renderFinish();
    paint();
    requestAnimationFrame(frame);
  }

  function startOrRestart() {
    if (mode === "title" || mode === "finish") resetRace();
    else if (mode === "race") useItem(player, cpus, pickups, shots);
  }

  window.addEventListener("keydown", (event) => {
    keys.add(event.key.toLowerCase());
    if (event.key === "Enter") startOrRestart();
    if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", " "].includes(event.key)) {
      event.preventDefault();
    }
  });
  window.addEventListener("keyup", (event) => keys.delete(event.key.toLowerCase()));
  window.addEventListener("click", startOrRestart);

  window.addEventListener("deviceorientation", (event) => {
    if (typeof event.gamma !== "number") return;
    tilt = Math.max(-1, Math.min(1, event.gamma / 22));
  });

  requestAnimationFrame(frame);
  return { startOrRestart };
}
