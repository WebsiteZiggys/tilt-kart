import { PALETTE, PixelBuffer, HEIGHT } from "./game.js";
import { paintLeds } from "./leds.js";

const COURT_TOP = 8;
const NET_X = 31;
const YOU_X = 57;
const CPU_X = 5;
const RACKET = 5;
const WIN_POINTS = 4;

function clamp(value, lo, hi) {
  return Math.max(lo, Math.min(hi, value));
}

export function createSwing(canvas, statusEl, onExit) {
  const buf = new PixelBuffer();
  let alive = true;
  let youScore = 0;
  let cpuScore = 0;
  let youY = 20;
  let cpuY = 20;
  let ballX = 54;
  let ballY = 20;
  let ballVx = 0;
  let ballVy = 0;
  let serving = true;
  let serveTurn = 1;
  let swing = 0;
  let cpuSwing = 0;
  let pause = 0;
  let ended = false;
  let wasUse = true;
  let tilt = 0;
  const keys = new Set();

  function teardown() {
    alive = false;
    window.removeEventListener("keydown", onKey);
    window.removeEventListener("keyup", onKeyUp);
    window.removeEventListener("click", onClick);
    window.removeEventListener("deviceorientation", onOrient);
  }

  function onKey(event) {
    keys.add(event.key.toLowerCase());
    if (["ArrowUp", "ArrowDown", " "].includes(event.key)) event.preventDefault();
    if (event.key === "Enter" && ended) {
      teardown();
      if (onExit) onExit();
    }
  }

  function onKeyUp(event) {
    keys.delete(event.key.toLowerCase());
  }

  function onClick() {
    if (ended) {
      teardown();
      if (onExit) onExit();
      return;
    }
    keys.add("click");
    setTimeout(() => keys.delete("click"), 80);
  }

  function onOrient(event) {
    if (typeof event.beta !== "number" && typeof event.gamma !== "number") return;
    tilt = clamp((event.beta || 0) / 18, -1, 1);
  }

  function using() {
    return keys.has(" ") || keys.has("click");
  }

  function aim() {
    let steer = tilt;
    if (keys.has("arrowup") || keys.has("w")) steer -= 0.85;
    if (keys.has("arrowdown") || keys.has("s")) steer += 0.85;
    return clamp(steer, -1, 1);
  }

  function drawCourt() {
    buf.clear(PALETTE.SKY1);
    for (let y = COURT_TOP; y < HEIGHT; y++) {
      for (let x = 0; x < 64; x++) {
        buf.plot(x, y, (x + y) & 2 ? PALETTE.GRASS_B : PALETTE.GRASS_A);
      }
    }
    for (let x = 0; x < 64; x++) {
      buf.plot(x, COURT_TOP, PALETTE.WHITE);
      buf.plot(x, HEIGHT - 1, PALETTE.WHITE);
    }
    for (let y = COURT_TOP; y < HEIGHT; y++) {
      buf.plot(0, y, PALETTE.WHITE);
      buf.plot(63, y, PALETTE.WHITE);
      if (y & 1) {
        buf.plot(NET_X, y, PALETTE.WHITE);
        buf.plot(NET_X + 1, y, PALETTE.HUD);
      }
    }
  }

  function drawRacket(x, y, swinging, facing, color) {
    const reach = swinging ? 3 : 0;
    for (let i = 0; i < RACKET; i++) {
      const py = Math.round(y) - Math.floor(RACKET / 2) + i;
      buf.plot(x, py, color);
      buf.plot(x + facing, py, PALETTE.WHITE);
      if (reach) buf.plot(x + facing * reach, py, color);
    }
  }

  function frame() {
    if (!alive) return;
    const steer = aim();
    const use = using();
    youY = clamp(youY + steer * 1.4, COURT_TOP + 3, HEIGHT - 3);

    if (ended) {
      drawCourt();
      buf.text(youScore > cpuScore ? "WIN" : "OUT", 24, 12, PALETTE.YELLOW);
      buf.text(`${cpuScore}-${youScore}`, 22, 20, PALETTE.HUD);
      statusEl.textContent = "Enter for menu";
      paintLeds(canvas, buf.pixels);
      requestAnimationFrame(frame);
      return;
    }

    if (pause > 0) pause -= 1;
    if (swing > 0) swing -= 1;
    if (cpuSwing > 0) cpuSwing -= 1;

    if (use && !wasUse && swing === 0 && pause === 0) {
      swing = 10;
      if (serving && serveTurn === 1) {
        ballX = YOU_X - 3;
        ballY = youY;
        ballVx = -1.15;
        ballVy = steer * 0.6;
        serving = false;
      }
    }
    wasUse = use;

    const target = ballVx < 0 || serving ? ballY : 20;
    cpuY += clamp(target - cpuY, -0.7, 0.7);
    cpuY = clamp(cpuY, COURT_TOP + 3, HEIGHT - 3);
    if (!serving && ballVx < 0 && ballX < 12 && cpuSwing === 0 && Math.abs(ballY - cpuY) < 6) {
      cpuSwing = 10;
    }

    if (serving && serveTurn === -1 && pause === 0) {
      ballX = CPU_X + 3;
      ballY = cpuY;
      ballVx = 1.1;
      ballVy = (youY - cpuY) * 0.04;
      serving = false;
      cpuSwing = 8;
    }

    if (!serving) {
      ballX += ballVx;
      ballY += ballVy;
      if (ballY < COURT_TOP + 1) {
        ballY = COURT_TOP + 1;
        ballVy *= -1;
      }
      if (ballY > HEIGHT - 2) {
        ballY = HEIGHT - 2;
        ballVy *= -1;
      }
      if (ballVx > 0 && ballX >= YOU_X - 2) {
        if (swing > 0 && Math.abs(ballY - youY) < 4.2) {
          ballX = YOU_X - 3;
          ballVx = -Math.min(1.7, Math.abs(ballVx) + 0.12);
          ballVy += (ballY - youY) * 0.22 + steer * 0.35;
        } else if (ballX > 63) {
          cpuScore += 1;
          serving = true;
          serveTurn = (youScore + cpuScore) % 2 === 0 ? 1 : -1;
          ballVx = 0;
          ballVy = 0;
          pause = 22;
        }
      }
      if (ballVx < 0 && ballX <= CPU_X + 2) {
        if (cpuSwing > 0 && Math.abs(ballY - cpuY) < 4.5) {
          ballX = CPU_X + 3;
          ballVx = Math.min(1.65, Math.abs(ballVx) + 0.08);
          ballVy += (20 - cpuY) * 0.05;
        } else if (ballX < 0) {
          youScore += 1;
          serving = true;
          serveTurn = (youScore + cpuScore) % 2 === 0 ? 1 : -1;
          ballVx = 0;
          ballVy = 0;
          pause = 22;
        }
      }
    }

    if (youScore >= WIN_POINTS || cpuScore >= WIN_POINTS) ended = true;

    drawCourt();
    buf.text(String(cpuScore), 10, 1, PALETTE.RED);
    buf.text(String(youScore), 50, 1, PALETTE.CYAN);
    if (serving && serveTurn === 1) buf.text("UP", 26, 1, PALETTE.YELLOW);
    drawRacket(CPU_X, cpuY, cpuSwing > 0, 1, PALETTE.RED);
    drawRacket(YOU_X, youY, swing > 0, -1, PALETTE.CYAN);
    if (!serving || serveTurn === 1) {
      const bx = serving ? YOU_X - 3 : ballX;
      const by = serving ? youY : ballY;
      buf.plot(Math.floor(bx), Math.floor(by), PALETTE.YELLOW);
      buf.plot(Math.floor(bx) + 1, Math.floor(by), PALETTE.WHITE);
    }
    statusEl.textContent = serving
      ? "Tilt aims · space / ↑ serves and swings"
      : `CPU ${cpuScore}  YOU ${youScore} · swing when it comes`;
    paintLeds(canvas, buf.pixels);
    requestAnimationFrame(frame);
  }

  window.addEventListener("keydown", onKey);
  window.addEventListener("keyup", onKeyUp);
  window.addEventListener("click", onClick);
  window.addEventListener("deviceorientation", onOrient);
  requestAnimationFrame(frame);
  return { stop: teardown };
}
