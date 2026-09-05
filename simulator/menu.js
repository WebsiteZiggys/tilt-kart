import { PALETTE, PixelBuffer } from "./game.js";
import { paintLeds } from "./leds.js";
import { GAMES } from "./games.js";

export function createMenu(canvas, statusEl) {
  const buf = new PixelBuffer();
  let selected = 0;
  let running = true;
  let time = 0;

  function play() {
    if (!running) return;
    running = false;
    const game = GAMES[selected];
    game.create(canvas, statusEl, () => {
      running = true;
      requestAnimationFrame(loop);
    });
  }

  function onKeyDown(event) {
    if (["ArrowUp", "ArrowDown", "Enter", " "].includes(event.key)) event.preventDefault();
    if (!running) return;
    if (event.key === "ArrowDown" || event.key === "s" || event.key === "S") {
      selected = (selected + 1) % GAMES.length;
    } else if (event.key === "ArrowUp" || event.key === "w" || event.key === "W") {
      selected = (selected - 1 + GAMES.length) % GAMES.length;
    } else if (event.key === "Enter" || event.key === " ") {
      play();
    }
  }

  function onClick() {
    if (running) play();
  }

  function loop(now) {
    if (!running) return;
    time = now / 1000;

    buf.clear(PALETTE.SKY1);
    buf.text("PLAY", 22, 2, PALETTE.YELLOW);
    let start = 0;
    if (selected > 1) start = selected - 1;
    const visible = GAMES.slice(start, start + 3);
    visible.forEach((game, i) => {
      const real = start + i;
      const y = 11 + i * 7;
      const color = real === selected ? PALETTE.CYAN : PALETTE.HUD;
      if (real === selected) buf.text(">", 8, y, PALETTE.MAGENTA);
      buf.text(game.name, 16, y, color);
    });
    if (Math.floor(time * 2) & 1) buf.text("UP", 50, 26, PALETTE.HUD);
    statusEl.textContent = "↑ ↓ pick a game · Enter / space / click plays";
    paintLeds(canvas, buf.pixels);
    requestAnimationFrame(loop);
  }

  window.addEventListener("keydown", onKeyDown);
  window.addEventListener("click", onClick);
  requestAnimationFrame(loop);
}
