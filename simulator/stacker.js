import { PALETTE, PixelBuffer } from "./game.js";
import { paintLeds } from "./leds.js";

export function createStacker(canvas, statusEl, onExit) {
  const buf = new PixelBuffer();
  let alive = true;
  let layers = [{ x: 18, w: 28 }];
  let pieceX = 2;
  let pieceW = 28;
  let dir = 1;
  let speed = 0.55;
  let score = 0;
  let ended = false;
  let wasUse = true;

  function teardown() {
    alive = false;
    window.removeEventListener("keydown", onKey);
    window.removeEventListener("keyup", onKeyUp);
    window.removeEventListener("click", onClick);
  }

  const keys = new Set();

  function onKey(event) {
    keys.add(event.key.toLowerCase());
    if (event.key === "Enter" && ended) {
      teardown();
      if (onExit) onExit();
    }
    if (["ArrowUp", " ", "w"].includes(event.key)) event.preventDefault();
  }

  function onKeyUp(event) {
    keys.delete(event.key.toLowerCase());
  }

  function onClick() {
    if (ended) {
      teardown();
      if (onExit) onExit();
    }
  }

  function using() {
    return keys.has(" ") || keys.has("arrowup") || keys.has("w");
  }

  function drop() {
    const base = layers[layers.length - 1];
    const left = Math.max(Math.floor(pieceX), base.x);
    const right = Math.min(Math.floor(pieceX) + pieceW, base.x + base.w);
    const overlap = right - left;
    if (overlap <= 1) {
      ended = true;
      return;
    }
    layers.push({ x: left, w: overlap });
    pieceW = overlap;
    pieceX = left;
    score += 1;
    speed = Math.min(1.7, speed + 0.12);
    if (31 - layers.length * 2 < 8) ended = true;
  }

  function frame() {
    if (!alive) return;
    const use = using();
    if (ended) {
      buf.clear(PALETTE.SKY1);
      buf.text("STACK", 20, 6, PALETTE.YELLOW);
      buf.text(String(score), 28, 14, PALETTE.CYAN);
      buf.text("UP", 28, 22, PALETTE.HUD);
      statusEl.textContent = `Stack ${score} · Enter for menu`;
      paintLeds(canvas, buf.pixels);
      requestAnimationFrame(frame);
      return;
    }
    if (use && !wasUse) drop();
    wasUse = use;
    pieceX += dir * speed;
    if (pieceX < 1) {
      pieceX = 1;
      dir = 1;
    }
    if (pieceX + pieceW > 62) {
      pieceX = 62 - pieceW;
      dir = -1;
    }

    buf.clear(PALETTE.SKY1);
    buf.text(String(score), 1, 1, PALETTE.HUD);
    const rainbow = [PALETTE.RB0, PALETTE.RB1, PALETTE.RB2, PALETTE.RB3, PALETTE.RB4, PALETTE.RB5];
    layers.forEach((layer, i) => {
      const y = 30 - i * 2;
      const color = rainbow[i % 6];
      for (let x = layer.x; x < layer.x + layer.w; x++) {
        buf.plot(x, y, color);
        buf.plot(x, y + 1, color);
      }
    });
    const y = 30 - layers.length * 2;
    if (y > 6) {
      for (let x = Math.floor(pieceX); x < Math.floor(pieceX) + pieceW; x++) {
        buf.plot(x, y, PALETTE.WHITE);
        buf.plot(x, y + 1, PALETTE.CYAN);
      }
    }
    statusEl.textContent = "Space / ↑ drops the bar";
    paintLeds(canvas, buf.pixels);
    requestAnimationFrame(frame);
  }

  window.addEventListener("keydown", onKey);
  window.addEventListener("keyup", onKeyUp);
  window.addEventListener("click", onClick);
  requestAnimationFrame(frame);
  return { stop: teardown };
}
