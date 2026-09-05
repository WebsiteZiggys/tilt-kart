# Matrix Arcade

Games for the [Adafruit Matrix Portal Starter Kit](https://www.adafruit.com/product/4812) (ADABOX 016): **Matrix Portal M4 + 64×32 RGB LED matrix**.

The panel boots to a **PLAY** menu. Pick a game, play it, and you land back on the menu.

## Games

- **KART** — tilt-to-steer racer, crates, items, 7 laps
- **STACK** — drop the moving bar, stack as high as you can
- **SWING** — tilt-tennis: pick EASY / NORM / HARD, aim with tilt, swing with the button

This is original work. It does not use Nintendo characters or art.

## Load it onto the board

1. Put CircuitPython on the Portal ([setup guide](https://learn.adafruit.com/adafruit-matrixportal-m4/circuitpython-setup))
2. From the [library bundle](https://circuitpython.org/libraries) copy into `CIRCUITPY/lib/`:
   - `adafruit_lis3dh.mpy`
   - `adafruit_bus_device/`
   - `adafruit_register/`
3. Copy **all** of these onto `CIRCUITPY`:
   - `circuitpython/code.py`
   - `circuitpython/tiltkart.py`
   - `circuitpython/stacker.py`
   - `circuitpython/swing.py`
4. **DOWN** moves the cursor. **UP** starts the highlighted game.

If kart steering feels backwards, set `STEER_FLIP = -1` in `tiltkart.py`. If it barely responds, try `STEER_AXIS = 0`.

## Play in the browser

```bash
cd simulator
python3 -m http.server 4173
```

Open http://127.0.0.1:4173

- Menu: `↑` `↓` to pick, Enter / space / click to play
- Kart: `A` `D` or arrows steer, space uses an item, `S` brakes
- Stack: space or `↑` drops the bar
- Swing: `↓` picks a level, space / Enter plays; `↑` `↓` aim, space / click swings
- After Swing, Enter goes back to the level list; BACK leaves to the arcade menu

## Add another game

**On the board**

1. Create `circuitpython/mygame.py` with:

```python
def run(display, bitmap, lis, up, down):
    # draw on bitmap, then return to go back to the menu
    return
```

2. Open `circuitpython/code.py` and add a line to `GAMES`:

```python
GAMES = (
    ("KART", "tiltkart"),
    ("STACK", "stacker"),
    ("SWING", "swing"),
    ("MINE", "mygame"),
)
```

Keep the menu name to about 5 letters so it fits the 64×32 screen.

**In the browser**

1. Create `simulator/mygame.js` that exports `createMyGame(canvas, statusEl, onExit)` and calls `onExit()` when the player is done.
2. Register it in `simulator/games.js`:

```javascript
export const GAMES = [
  { name: "KART", create: createTiltKart },
  { name: "STACK", create: createStacker },
  { name: "SWING", create: createSwing },
  { name: "MINE", create: createMyGame },
];
```

## Kart

Seven laps. Tilt to steer. Flashing crates cycle a random item; UP / space fires it (boost, peel, bomb, blue). Rainbow pads are a ground boost. Three CPU karts start ahead.

## Stack

A bar slides back and forth. Drop it onto the stack. Anything hanging off is cut away. Miss and the run ends.

## Swing

Tilt-tennis. You stand on the right. First pick **EASY** (default), **NORM**, or **HARD**. Tilt aims the racket, UP / space swings. Time the hit when the ball reaches you.

- **EASY** — big racket, slow ball, CPU misses a lot, first to 3
- **NORM** — in between, first to 4
- **HARD** — small racket, fast ball, CPU almost always returns, first to 4

## Project layout

```
circuitpython/code.py      # menu + game list
circuitpython/tiltkart.py  # Kart
circuitpython/stacker.py   # Stack
circuitpython/swing.py     # Swing tennis
simulator/                 # same arcade in a browser
simulator/games.js         # browser game list
```
