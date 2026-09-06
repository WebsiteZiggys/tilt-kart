import { PALETTE, PixelBuffer } from "./game.js";
import { paintLeds } from "./leds.js";

const W = 64;
const H = 32;
const COLORS = [
  PALETTE.RB0,
  PALETTE.RB1,
  PALETTE.RB2,
  PALETTE.RB3,
  PALETTE.RB4,
  PALETTE.RB5,
  PALETTE.CYAN,
  PALETTE.MAGENTA,
  PALETTE.YELLOW,
  PALETTE.ORANGE,
];

function dir(g) {
  if (g > 1.6) return 1;
  if (g < -1.6) return -1;
  return 0;
}

function step(grid, sx, sy) {
  const xs = sx > 0 ? [...Array(W).keys()].reverse() : [...Array(W).keys()];
  const ys = sy > 0 ? [...Array(H).keys()].reverse() : [...Array(H).keys()];
  for (const y of ys) {
    const row = y * W;
    for (const x of xs) {
      const color = grid[row + x];
      if (!color) continue;
      const nx = x + sx;
      const ny = y + sy;
      if (nx >= 0 && nx < W && ny >= 0 && ny < H && !grid[ny * W + nx]) {
        grid[row + x] = 0;
        grid[ny * W + nx] = color;
        continue;
      }
      for (const [px, py] of [
        [-sy, sx],
        [sy, -sx],
      ]) {
        const tx = x + sx + px;
        const ty = y + sy + py;
        if (tx >= 0 && tx < W && ty >= 0 && ty < H && !grid[ty * W + tx]) {
          grid[row + x] = 0;
          grid[ty * W + tx] = color;
          break;
        }
      }
    }
  }
}

function spawn(grid, sx, sy, color) {
  let spots;
  if (sy > 0) spots = Array.from({ length: 48 }, (_, i) => [i + 8, 0]);
  else if (sy < 0) spots = Array.from({ length: 48 }, (_, i) => [i + 8, H - 1]);
  else if (sx > 0) spots = Array.from({ length: 24 }, (_, i) => [0, i + 4]);
  else spots = Array.from({ length: 24 }, (_, i) => [W - 1, i + 4]);
  for (const [x, y] of spots) {
    const i = y * W + x;
    if (!grid[i] && Math.random() < 0.08) {
      grid[i] = color;
      return;
    }
  }
}

export function createSand(canvas, statusEl, onExit) {
  const buf = new PixelBuffer();
  const grid = new Array(W * H).fill(0);
  let alive = true;
  let tick = 0;
  let gx = 0;
  let gy = 8;
  const start = performance.now();

  for (let n = 0; n < 260; n++) {
    const x = 6 + Math.floor(Math.random() * (W - 12));
    const y = 2 + Math.floor(Math.random() * (H - 5));
    const i = y * W + x;
    if (!grid[i]) grid[i] = COLORS[n % COLORS.length];
  }

  function onMove(event) {
    const rect = canvas.getBoundingClientRect();
    const px = (("clientX" in event ? event.clientX : event.touches[0].clientX) - rect.left) / rect.width;
    const py = (("clientY" in event ? event.clientY : event.touches[0].clientY) - rect.top) / rect.height;
    gx = (px - 0.5) * 20;
    gy = (py - 0.5) * 20;
  }

  function onOrient(event) {
    if (typeof event.gamma !== "number" && typeof event.beta !== "number") return;
    gx = (event.gamma || 0) / 4;
    gy = (event.beta || 0) / 4;
  }

  function frame() {
    if (!alive) return;
    let sx = dir(gx);
    let sy = dir(gy);
    if (sx === 0 && sy === 0) {
      const t = (performance.now() - start) / 1000;
      sx = dir(Math.sin(t * 0.7) * 8);
      sy = dir(Math.cos(t * 0.7) * 8);
      if (sx === 0 && sy === 0) sy = 1;
    }
    step(grid, sx, sy);
    if (tick & 1) spawn(grid, sx, sy, COLORS[tick % COLORS.length]);
    buf.clear(PALETTE.BLACK);
    for (let i = 0; i < grid.length; i++) {
      if (grid[i]) buf.plot(i % W, Math.floor(i / W), grid[i]);
    }
    if (statusEl) statusEl.textContent = "Move the pointer or tilt the phone — no buttons";
    paintLeds(canvas, buf.pixels);
    tick += 1;
    requestAnimationFrame(frame);
  }

  canvas.addEventListener("pointermove", onMove);
  canvas.addEventListener("touchmove", onMove, { passive: true });
  window.addEventListener("deviceorientation", onOrient);
  requestAnimationFrame(frame);

  return {
    stop() {
      alive = false;
      canvas.removeEventListener("pointermove", onMove);
      canvas.removeEventListener("touchmove", onMove);
      window.removeEventListener("deviceorientation", onOrient);
      if (onExit) onExit();
    },
  };
}
