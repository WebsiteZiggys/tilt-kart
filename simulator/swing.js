import { PALETTE, PixelBuffer, HEIGHT } from "./game.js";
import { paintLeds } from "./leds.js";

const COURT_TOP = 8;
const NET_X = 31;
const YOU_X = 57;
const CPU_X = 5;

const LEVELS = [
  { name: "EASY", racket: 9, hit: 8, swingLen: 20, serve: 0.58, max: 0.88, cpu: 0.22, cpuHit: 2.6, cpuReturn: 0.42, win: 3, reach: 6 },
  { name: "NORM", racket: 6, hit: 5.6, swingLen: 13, serve: 0.82, max: 1.25, cpu: 0.45, cpuHit: 3.6, cpuReturn: 0.78, win: 4, reach: 4 },
  { name: "HARD", racket: 5, hit: 4, swingLen: 9, serve: 1.12, max: 1.7, cpu: 0.78, cpuHit: 4.6, cpuReturn: 1, win: 4, reach: 3 },
];
const LEVEL_NAMES = ["EASY", "NORM", "HARD", "BACK"];

function clamp(value, lo, hi) {
  return Math.max(lo, Math.min(hi, value));
}

export function createSwing(canvas, statusEl, onExit) {
  const buf = new PixelBuffer();
  let alive = true;
  let screen = "pick";
  let levelIndex = 0;
  let level = LEVELS[0];
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
  let pendingSwing = false;
  let tilt = 0;
  const keys = new Set();

  function resetMatch() {
    youScore = 0;
    cpuScore = 0;
    youY = 20;
    cpuY = 20;
    ballX = 54;
    ballY = 20;
    ballVx = 0;
    ballVy = 0;
    serving = true;
    serveTurn = 1;
    swing = 0;
    cpuSwing = 0;
    pause = 0;
    ended = false;
    pendingSwing = false;
  }

  function teardown() {
    alive = false;
    window.removeEventListener("keydown", onKey);
    window.removeEventListener("keyup", onKeyUp);
    window.removeEventListener("click", onClick);
    window.removeEventListener("deviceorientation", onOrient);
  }

  function chooseLevel() {
    if (levelIndex === 3) {
      teardown();
      if (onExit) onExit();
      return;
    }
    level = LEVELS[levelIndex];
    resetMatch();
    screen = "play";
  }

  function onKey(event) {
    keys.add(event.key.toLowerCase());
    if (["ArrowUp", "ArrowDown", " ", "Enter"].includes(event.key)) event.preventDefault();
    if (event.repeat) return;
    if (screen === "pick") {
      if (event.key === "ArrowDown" || event.key === "s" || event.key === "S") {
        levelIndex = (levelIndex + 1) % 4;
      } else if (event.key === "Enter" || event.key === " ") {
        chooseLevel();
      }
    } else if (ended && (event.key === "Enter" || event.key === " ")) {
      screen = "pick";
    } else if (screen === "play" && (event.key === " " || event.key === "Enter")) {
      pendingSwing = true;
    }
  }

  function onKeyUp(event) {
    keys.delete(event.key.toLowerCase());
  }

  function onClick() {
    if (screen === "pick") {
      chooseLevel();
      return;
    }
    if (ended) {
      screen = "pick";
      return;
    }
    pendingSwing = true;
  }

  function onOrient(event) {
    if (typeof event.beta !== "number" && typeof event.gamma !== "number") return;
    tilt = clamp((event.beta || 0) / 18, -1, 1);
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

  function drawRacket(x, y, swinging, facing, size, color) {
    const reach = swinging ? 4 : 0;
    const half = Math.floor(size / 2);
    for (let i = 0; i < size; i++) {
      const py = Math.round(y) - half + i;
      buf.plot(x, py, color);
      buf.plot(x + facing, py, PALETTE.WHITE);
      if (reach) buf.plot(x + facing * reach, py, color);
    }
  }

  function frame() {
    if (!alive) return;
    const steer = aim();

    if (screen === "pick") {
      buf.clear(PALETTE.SKY1);
      buf.text("SWING", 20, 2, PALETTE.YELLOW);
      LEVEL_NAMES.forEach((name, i) => {
        const y = 9 + i * 6;
        if (i === levelIndex) buf.text(">", 6, y, PALETTE.MAGENTA);
        buf.text(name, 16, y, i === levelIndex ? PALETTE.CYAN : PALETTE.HUD);
      });
      statusEl.textContent = "↓ pick a level · space / Enter plays · BACK leaves";
      paintLeds(canvas, buf.pixels);
      requestAnimationFrame(frame);
      return;
    }

    youY = clamp(youY + steer * 1.6, COURT_TOP + 4, HEIGHT - 4);
    if (!serving && ballVx > 0 && level.name === "EASY") {
      youY += clamp(ballY - youY, -0.35, 0.35);
    }

    if (ended) {
      drawCourt();
      buf.text(youScore > cpuScore ? "WIN" : "OUT", 24, 10, PALETTE.YELLOW);
      buf.text(level.name, 22, 17, PALETTE.CYAN);
      buf.text(`${cpuScore}-${youScore}`, 22, 24, PALETTE.HUD);
      statusEl.textContent = "Enter / space for levels";
      paintLeds(canvas, buf.pixels);
      requestAnimationFrame(frame);
      return;
    }

    if (pause > 0) pause -= 1;
    if (swing > 0) swing -= 1;
    if (cpuSwing > 0) cpuSwing -= 1;

    if (pendingSwing && swing === 0 && pause === 0) {
      pendingSwing = false;
      swing = level.swingLen;
      if (serving && serveTurn === 1) {
        ballX = YOU_X - 3;
        ballY = youY;
        ballVx = -level.serve;
        ballVy = steer * 0.35;
        serving = false;
      }
    } else {
      pendingSwing = false;
    }

    const target = ballVx < 0 || serving ? ballY : 20;
    cpuY += clamp(target - cpuY, -level.cpu, level.cpu);
    cpuY = clamp(cpuY, COURT_TOP + 4, HEIGHT - 4);
    if (!serving && ballVx < 0 && ballX < 14 && cpuSwing === 0) {
      if (Math.abs(ballY - cpuY) < 5.5 && Math.random() < level.cpuReturn) cpuSwing = 8;
    }

    if (serving && serveTurn === -1 && pause === 0) {
      ballX = CPU_X + 3;
      ballY = cpuY;
      ballVx = level.serve * 0.85;
      ballVy = (youY - cpuY) * 0.03;
      serving = false;
      cpuSwing = 8;
    }

    if (!serving) {
      ballX += ballVx;
      ballY += ballVy;
      ballVy *= 0.995;
      if (ballY < COURT_TOP + 1) {
        ballY = COURT_TOP + 1;
        ballVy *= -0.9;
      }
      if (ballY > HEIGHT - 2) {
        ballY = HEIGHT - 2;
        ballVy *= -0.9;
      }
      if (ballVx > 0 && ballX >= YOU_X - level.reach) {
        if (swing > 0 && Math.abs(ballY - youY) < level.hit) {
          ballX = YOU_X - 3;
          ballVx = -Math.min(level.max, Math.abs(ballVx) + 0.06);
          ballVy += (ballY - youY) * 0.12 + steer * 0.22;
          ballVy = clamp(ballVy, -0.7, 0.7);
        } else if (ballX > 63) {
          cpuScore += 1;
          serving = true;
          serveTurn = (youScore + cpuScore) % 2 === 0 ? 1 : -1;
          ballVx = 0;
          ballVy = 0;
          pause = 28;
        }
      }
      if (ballVx < 0 && ballX <= CPU_X + 2) {
        if (cpuSwing > 0 && Math.abs(ballY - cpuY) < level.cpuHit) {
          ballX = CPU_X + 3;
          ballVx = Math.min(level.max * 0.9, Math.abs(ballVx) + 0.04);
          ballVy += (20 - cpuY) * 0.04;
          ballVy = clamp(ballVy, -0.55, 0.55);
        } else if (ballX < 0) {
          youScore += 1;
          serving = true;
          serveTurn = (youScore + cpuScore) % 2 === 0 ? 1 : -1;
          ballVx = 0;
          ballVy = 0;
          pause = 28;
        }
      }
    }

    if (youScore >= level.win || cpuScore >= level.win) ended = true;

    drawCourt();
    buf.text(String(cpuScore), 10, 1, PALETTE.RED);
    buf.text(String(youScore), 50, 1, PALETTE.CYAN);
    buf.text(level.name, 24, 1, serving && serveTurn === 1 ? PALETTE.YELLOW : PALETTE.HUD);
    drawRacket(CPU_X, cpuY, cpuSwing > 0, 1, 5, PALETTE.RED);
    drawRacket(YOU_X, youY, swing > 0, -1, level.racket, PALETTE.CYAN);
    if (!serving || serveTurn === 1) {
      const bx = serving ? YOU_X - 3 : ballX;
      const by = serving ? youY : ballY;
      buf.plot(Math.floor(bx), Math.floor(by), PALETTE.YELLOW);
      buf.plot(Math.floor(bx) + 1, Math.floor(by), PALETTE.WHITE);
    }
    statusEl.textContent = serving
      ? `${level.name} · tilt aims · space serves / swings`
      : `${level.name} · CPU ${cpuScore}  YOU ${youScore}`;
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
