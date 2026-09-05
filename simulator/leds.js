import { WIDTH, HEIGHT, PALETTE } from "./game.js";

export function paintLeds(canvas, pixels) {
  const ctx = canvas.getContext("2d");
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
      const color = pixels[y * WIDTH + x];
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
