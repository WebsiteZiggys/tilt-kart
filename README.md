# Tilt Kart

A tilt-to-steer kart racer for the [Adafruit Matrix Portal Starter Kit](https://www.adafruit.com/product/4812) (ADABOX 016): **Matrix Portal M4 + 64×32 RGB LED matrix**.

This is an original game. It plays like a tiny arcade racer, not Mario Kart, and it does not use Nintendo characters or art.

**On the real panel:** tilt left/right to steer, `BUTTON_UP` to start/boost, `BUTTON_DOWN` to brake.

**In the browser:** same race, keyboard controls, so you can try it before copying files to the board.

## What you need

- Adafruit Matrix Portal M4 plugged into the 64×32 matrix
- USB-C cable (data, not charge-only)
- CircuitPython on the Portal ([install guide](https://learn.adafruit.com/adafruit-matrixportal-m4/circuitpython-setup))
- From the [Adafruit CircuitPython library bundle](https://circuitpython.org/libraries):
  - `adafruit_lis3dh.mpy`
  - `adafruit_bus_device/`
  - `adafruit_register/`

`rgbmatrix`, `framebufferio`, and `displayio` are already built into the Matrix Portal CircuitPython build.

## Load it onto the board

1. Plug in the Portal. A `CIRCUITPY` drive should appear.
2. Copy the three libraries above into `CIRCUITPY/lib/`.
3. Copy [`circuitpython/code.py`](circuitpython/code.py) to `CIRCUITPY/code.py`.
4. Hold the panel like a landscape picture and tilt it. Press the **UP** button to start.

If steering feels backwards, open `code.py` and set:

```python
STEER_FLIP = -1
```

If it barely responds, try `STEER_AXIS = 0` instead of `1`.

Power the matrix from the included 5V supply once you are done programming. USB-C can run the Portal, but a full-bright 64×32 panel is happier on the barrel jack / 5V supply.

## Play in the browser

```bash
cd simulator
python3 -m http.server 4173
```

Open http://127.0.0.1:4173

- `Enter` or click: start / race again
- `←` `→` or `A` `D`: steer
- `Space` or `↑`: boost
- `↓` or `S`: brake
- On a phone, tilt works after the browser allows device orientation

## How it plays

Three laps on a fake-3D night course. Stay on the asphalt — grass is slow. Yellow coins score. Yellow bananas spin you out. Rainbow strips on the road are boosts: drive through them. Two CPU karts race with you.

The Portal’s LIS3DH accelerometer (I2C address `0x19`) is the steering wheel. That is the same sensor Adafruit uses for the digital-sand demos.

## Project layout

```
circuitpython/code.py   # drop this on CIRCUITPY
simulator/              # 64x32 LED preview in a browser
```
