// Add a game: write simulator/mygame.js that exports createMyGame(canvas, status, onExit)
// then add { name: "MINE", create: createMyGame } here.
// CircuitPython twin: circuitpython/mygame.py with run(display, bitmap, lis, up, down)
// and ("MINE", "mygame") in circuitpython/code.py GAMES.

import { createTiltKart } from "./game.js";
import { createStacker } from "./stacker.js";
import { createSwing } from "./swing.js";

export const GAMES = [
  { name: "KART", create: createTiltKart },
  { name: "STACK", create: createStacker },
  { name: "SWING", create: createSwing },
];
