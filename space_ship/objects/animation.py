import asyncio
from itertools import cycle
import random
import time

from .explosion import explode
from .fire import fire
from .obstacles import Obstacle
from .utils import draw_frame, get_frame_size, show_gameover_frame
from .stars import sleep

from game_scenario import PHRASES
from game_scenario import get_garbage_delay_tics
from global_objects import (
    COROUNINES,
    OBSTRACLES,
    OBSTRACLES_IN_LAST_COLLISION,
    GAME_IS_OVER,
    YEAR,
    CAN_SHOOT
)

from physics import update_speed


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-SHIP ANIMATION-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-
SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


async def animate_ship(canvas, row, column, frames, gameover_frame):
    global GAME_IS_OVER
    preview_frame = ''
    prev_y, prev_x = (row, column)
    row_speed = column_speed = 0
    height, width = canvas.getmaxyx()

    for frame in cycle(frames):
        for obstacle in OBSTRACLES:
                if obstacle.has_collision(row, column):
                    COROUNINES.append(show_gameover_frame(canvas, gameover_frame))
                    GAME_IS_OVER = True
                    return
        draw_frame(canvas, prev_y, prev_x, preview_frame, negative=True)
        draw_frame(canvas, row, column, frame)

        preview_frame = frame
        prev_y, prev_x = (row, column)
        frame_y, frame_x = get_frame_size(preview_frame)
        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction, columns_direction)

        row += row_speed
        column += column_speed

        if space_pressed and CAN_SHOOT:
            COROUNINES.append(fire(canvas, row, column))

        if row < 0 or row + frame_y > height:
            row = prev_y
        if column < 0 or column + frame_x > width:
            column = prev_x
        await asyncio.sleep(0)


# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-GARBAGE ANIMATION-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-

async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom.
       Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)
    row = 0
    rows_size, columns_size = get_frame_size(garbage_frame)

    obstacle = Obstacle(row, column, rows_size, columns_size)
    OBSTRACLES.append(obstacle)

    try:
        while row < rows_number:
            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            obstacle.row += speed
            row += speed

            # Stop drawing garbage and obstacle frame if it was hit:
            # remove that coroutines from corresponding lists and show explosion
            if obstacle in OBSTRACLES_IN_LAST_COLLISION:
                OBSTRACLES_IN_LAST_COLLISION.remove(obstacle)
                await explode(
                    canvas, row + (rows_size // 2), column + (columns_size // 2)
                )
                return
    finally:
        OBSTRACLES.remove(obstacle)


async def fill_orbit_with_garbage(canvas, canvas_width, garbage_frames):
    frame_by_numbers = {key: frame for key, frame in enumerate(garbage_frames)}
    while True:
        sleep_time = get_garbage_delay_tics(YEAR)
        if sleep_time:
            await sleep(sleep_time)
            frame_number = random.randint(0, len(garbage_frames) - 1)
            garbage_frame = frame_by_numbers[frame_number]
            _, columns = get_frame_size(garbage_frame)
            position = random.randint(columns, canvas_width - columns)

            coroutine_garbage = fly_garbage(canvas, position, garbage_frame)
            COROUNINES.append(coroutine_garbage)
        await sleep()

# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-YEAR INFORMATION ANIMATION-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*--*-*-*-*-*-*-*-*-


async def display_year(canvas, height, width, game_started_time):
    global YEAR
    global CAN_SHOOT
    ratio = 2
    y_main_message_position = height - 5
    y_description_position = height - 3
    while True:
        if YEAR >= 2000:
            CAN_SHOOT = True

        if GAME_IS_OVER:
            return

        time_now = time.monotonic()
        diff = round(time_now - game_started_time, 1)

        if diff % ratio == 0.0:
            YEAR += 1

        message = f"The current year is - {YEAR}"
        x_position = width - 30
        canvas.derwin(y_main_message_position, x_position).addstr(message)

        canvas.derwin(y_description_position, x_position).addstr(PHRASES.get(YEAR, ''))
        await asyncio.sleep(0)
