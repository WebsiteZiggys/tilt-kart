# Matrix Arcade — start the race.

import time

import tiltkart as tk


def main():
    display, bitmap = tk.setup_display()
    up, down = tk.setup_buttons()
    lis = tk.setup_accel()
    while True:
        tk.run(display, bitmap, lis, up, down)
        time.sleep(0.2)


main()
