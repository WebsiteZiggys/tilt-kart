const WIDTH = 64;
const HEIGHT = 32;
const HORIZON = 9;
const LAPS = 3;
const MAX_SPEED = 2.35;
const BOOST_SPEED = 3.15;
const ACCEL = 0.045;
const BRAKE = 0.09;
const DRAG = 0.012;
const OFFROAD_DRAG = 0.055;
const CENTRIFUGAL = 0.018;

const TRACK = [
  [55, 0.0],
  [38, 2.2],
  [28, 0.4],
  [42, -2.8],
  [22, 0.0],
  [36, 1.8],
  [30, -1.2],
  [40, 0.0],
  [34, 2.6],
  [26, -2.1],
  [48, 0.0],
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
};

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

function drawRoad(buf, playerZ, playerX) {
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
    const row = y * WIDTH;
    for (let x = 0; x < WIDTH; x++) {
      if (x < left - rumbleW || x > right + rumbleW) {
        buf.pixels[row + x] = grass;
      } else if (x < left || x > right) {
        buf.pixels[row + x] = finish && ((x + y) & 1) ? PALETTE.FINISH : rumble;
      } else {
        const edge = x < left + 1.1 || x > right - 1.1;
        const mid = Math.abs(x - center) < 0.7 + near * 0.4;
        const dash = stripe && mid && near > 0.18;
        if (finish) {
          buf.pixels[row + x] = (Math.floor(x) + Math.floor(worldZ)) & 1 ? PALETTE.WHITE : PALETTE.BLACK;
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

function drawPad(buf, sx, sy) {
  buf.plot(sx - 1, sy, PALETTE.MAGENTA);
  buf.plot(sx, sy, PALETTE.WHITE);
  buf.plot(sx + 1, sy, PALETTE.MAGENTA);
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
  let z = 18;
  let seed = 7;
  const rand = () => {
    seed = (seed * 16807) % 2147483647;
    return (seed - 1) / 2147483646;
  };
  const lanes = [-0.55, -0.2, 0.15, 0.5];
  while (z < TRACK_LEN - 8) {
    const roll = rand();
    const lane = lanes[Math.floor(rand() * lanes.length)];
    if (roll < 0.34) items.push(new Pickup("coin", z, lane));
    else if (roll < 0.58) items.push(new Pickup("banana", z, lane));
    else if (roll < 0.74) items.push(new Pickup("pad", z, Math.abs(lane) < 0.4 ? 0 : lane));
    z += 16 + rand() * 10;
  }
  return items;
}

function racePlace(player, cpus) {
  const pack = [player, ...cpus].sort(
    (a, b) => b.lap * TRACK_LEN + b.z - (a.lap * TRACK_LEN + a.z)
  );
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

function hitPickups(player, pickups, coins) {
  for (const item of pickups) {
    if (!item.alive) continue;
    let dz = Math.abs((item.z - player.z + TRACK_LEN) % TRACK_LEN);
    if (dz > TRACK_LEN / 2) dz = TRACK_LEN - dz;
    if (dz > 2.4 || Math.abs(item.x - player.x) > 0.22) continue;
    item.alive = false;
    if (item.kind === "banana") {
      player.spin = 1.2;
      player.speed *= 0.45;
    } else if (item.kind === "coin") {
      coins += 1;
    } else if (item.kind === "pad") {
      player.boost = 1.15;
      player.speed = Math.min(BOOST_SPEED, player.speed + 0.7);
    }
  }
  return coins;
}

function cpuThink(cpu, player) {
  const curve = curveAt(cpu.z + 10);
  let target = -curve * 0.12 + Math.sin(cpu.z * 0.07) * 0.18;
  if (Math.abs(cpu.z - player.z) < 6 && Math.abs(cpu.x - player.x) < 0.2) {
    target += cpu.x < player.x ? 0.28 : -0.28;
  }
  return Math.max(-1, Math.min(1, (target - cpu.x) * 1.6));
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
  let coins = 0;
  let demoZ = 0;
  let time = 0;
  let countdownAt = 0;
  let countdownWord = "3";
  let lastNow = performance.now();
  let physAcc = 0;
  const STEP = 0.03;

  function resetRace() {
    player = new Racer(2, 0, 0.8, PALETTE.RED, true);
    cpus = [new Racer(8, -0.25, 1.15, PALETTE.CYAN), new Racer(14, 0.35, 1.05, PALETTE.ORANGE)];
    pickups = makePickups();
    coins = 0;
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

  function boosting() {
    return keys.has(" ") || keys.has("arrowup") || keys.has("w");
  }

  function braking() {
    return keys.has("arrowdown") || keys.has("s");
  }

  function renderTitle() {
    drawSky(buf, time);
    drawRoad(buf, demoZ, Math.sin(time * 0.7) * 0.25);
    drawPlayerKart(buf, false, false);
    buf.text("TILT", 23, 2, PALETTE.YELLOW);
    buf.text("KART", 23, 9, PALETTE.MAGENTA);
    if (Math.floor(time * 2) & 1) buf.text("GO", 28, 16, PALETTE.HUD);
    statusEl.textContent = "Enter or click to race · arrows / A D steer · space boost";
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
    const steer = inputSteer();
    if (boosting() && player.boost <= 0) player.boost = 0.85;
    advanceRacer(player, steer, braking(), curveAt(player.z));
    for (const cpu of cpus) advanceRacer(cpu, cpuThink(cpu, player), false, curveAt(cpu.z));
    coins = hitPickups(player, pickups, coins);
    racePlace(player, cpus);
    if (player.finished) mode = "finish";
  }

  function renderRace() {

    drawSky(buf, player.z * 0.04);
    drawRoad(buf, player.z, player.x);
    for (const item of pickups) {
      if (!item.alive) continue;
      const proj = projectSprite(player.z, player.x, item.z, item.x);
      if (!proj) continue;
      if (item.kind === "banana") drawBanana(buf, proj.sx, proj.sy, proj.scale);
      else if (item.kind === "coin") drawCoin(buf, proj.sx, proj.sy, Math.floor(time * 8) & 1);
      else drawPad(buf, proj.sx, proj.sy);
    }
    for (const cpu of cpus) {
      let cz = cpu.z;
      if (cpu.lap > player.lap) cz += TRACK_LEN;
      else if (cpu.lap < player.lap) cz -= TRACK_LEN;
      const proj = projectSprite(player.z, player.x, cz, cpu.x);
      if (proj) drawKart(buf, proj.sx, proj.sy, proj.scale, cpu.body, cpu.spin > 0);
    }
    drawPlayerKart(buf, player.boost > 0, player.spin > 0.15);
    buf.text(`L${Math.min(player.lap, LAPS)}/${LAPS}`, 1, 1, PALETTE.HUD);
    buf.text(`P${player.place}`, 28, 1, PALETTE.CYAN);
    buf.text(`$${coins}`, 44, 1, PALETTE.COIN);
    if (player.boost > 0) {
      for (let x = 0; x < Math.floor(player.boost * 10); x++) buf.plot(1 + x, 7, PALETTE.MAGENTA);
    }
    statusEl.textContent = `Lap ${player.lap}/${LAPS} · P${player.place} · ${coins} coins`;
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
