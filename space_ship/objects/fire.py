import asyncio
from global_objects import OBSTRACLES, OBSTRACLES_IN_LAST_COLLISION


async def fire(
    canvas, start_row, start_column,
        rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row = start_row - 1
    column = start_column + 2

    while 0 < row:
        for obstacle in OBSTRACLES:
            if obstacle.has_collision(row, column):
                OBSTRACLES_IN_LAST_COLLISION.append(obstacle)
                return

        canvas.addstr(round(row), round(column), "|")
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), " ")
        row -= 1
