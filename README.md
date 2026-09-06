# Rainbow sand

Tilt-only demo for the [Adafruit Matrix Portal Starter Kit](https://www.adafruit.com/product/4812) (ADABOX 016): **Matrix Portal M4 + 64×32 RGB LED matrix**.

No buttons. Rainbow grains pile up, slip, and pour wherever gravity points.

On the real panel, tilt the Matrix Portal. If the accelerometer is missing, gravity slowly spins on its own.

## Load it onto the board

1. Put CircuitPython on the Portal ([setup guide](https://learn.adafruit.com/adafruit-matrixportal-m4/circuitpython-setup))
2. From the [library bundle](https://circuitpython.org/libraries) copy into `CIRCUITPY/lib/`:
   - `adafruit_lis3dh.mpy`
   - `adafruit_bus_device/`
   - `adafruit_register/`
3. Copy these onto `CIRCUITPY`:
   - `circuitpython/code.py`
   - `circuitpython/tiltkart.py`

## Play in the browser

```bash
cd simulator
python3 -m http.server 4173
```

Open http://127.0.0.1:4173

Move the pointer over the panel (or tilt a phone). No keys. No clicks required.

## Project layout

```
circuitpython/code.py      # rainbow sand
circuitpython/tiltkart.py  # display + accelerometer helpers
simulator/sand.js          # same sand in the browser
```

Kart, Stack, and Swing still live in the repo if you want the old arcade back.
