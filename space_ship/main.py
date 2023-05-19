import time
import curses
import random

from objects.stars import blink
from objects.animation import animate_ship, fill_orbit_with_garbage, display_year

from objects.obstacles import show_obstacles
from objects.utils import get_frames_from_files, get_frame_from_file
from global_objects import COROUNINES, OBSTRACLES


SYMBOLS = ['*', ':', '+', '.']
TIC_TIMEOUT = 0.1


def draw(canvas):

    height, width = canvas.getmaxyx()
    curses.curs_set(False)
    canvas.nodelay(True)

    ship_frames = get_frames_from_files(
        (
            'frames/rocket/rocket_frame_1.txt',
            'frames/rocket/rocket_frame_2.txt'
        )
    )

    garbage_frames = get_frames_from_files(
        (
            'frames/garbage/trash_small.txt',
            'frames/garbage/trash_large.txt',
            'frames/garbage/duck.txt'
        )
    )

    gameover_frame = get_frame_from_file("frames/game_over.txt")

    coroutine_ship = animate_ship(canvas, height / 2, width / 2, ship_frames, gameover_frame)
    coroutine_garbages = fill_orbit_with_garbage(canvas, width, garbage_frames)

    # coroutine_obstacles = show_obstacles(canvas, OBSTRACLES)
    # COROUNINES.append(coroutine_obstacles)
    COROUNINES.append(coroutine_ship)
    COROUNINES.append(coroutine_garbages)


    started_time = time.monotonic()
    COROUNINES.append(display_year(canvas, height, width, started_time))

    border_size = 1

    for _ in range(100):
        symbol = random.choice(SYMBOLS)
        y_coord = random.randint(1, height - border_size)
        x_coord = random.randint(1, width - border_size)
        coroutine = blink(
            canvas, y_coord, x_coord, symbol, random.randint(1, 5))
        COROUNINES.append(coroutine)
    while COROUNINES:
        for coroutine in COROUNINES.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                COROUNINES.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.wrapper(draw)
