import argparse
import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime

import aiofiles
from dotenv import find_dotenv, set_key

from gui import ReadConnectionStateChanged, SendingConnectionStateChanged

main_logger = logging.getLogger("main_logger")


class UserInterrupt(Exception):
    pass


async def read_messages(host, port, filepath, messages_queue):
    reader, writer = await asyncio.open_connection(host, port)
    while True:
        server_message = await reader.readline()
        if not server_message:
            break
        line = server_message.decode("utf-8")
        date = datetime.now().strftime("%y.%m.%d %H:%M")
        line = f"[{date}] " + line
        async with aiofiles.open(filepath, mode="a") as file:
            await file.write(line)
        messages_queue.put_nowait(line)
        await asyncio.sleep(1)



def format_text(message):
    return message.replace("\n", "").replace("\r", "")


async def submit_message(reader, writer, message):
    message = "{}\n\n".format(format_text(message))
    writer.write(message.encode())
    await writer.drain()


async def register_user(reader, writer, username):
    main_logger.info(f"Try register username {username}")
    
    # pass "hello" message
    await reader.readline()

    # leave empty message instead of enter token
    writer.write("{}\n".encode())
    await writer.drain()

    # pass nickname ask message
    for _ in range(2):
        await reader.readline()

    message = "{}\n".format(format_text(username))
    writer.write(message.encode())
    await writer.drain()

    data = await reader.readline()
    response = json.loads(data.decode())

    set_key(find_dotenv(), "MINECHAT_TOKEN", response["account_hash"])

    main_logger.info(
        f"User with username {format_text(username)} registered with token {response['account_hash']}"
    )


async def authenticate_user(reader, writer, token):
    if not token or token == "":
        return False, None
    await reader.readline()

    message = token + "\n"
    writer.write(message.encode())
    await writer.drain()

    data = await reader.readline()

    response = json.loads(data.decode())
    if not response:
        main_logger.info("Invalid token: {}".format(token))
        return False, None

    data = await reader.readline()
    main_logger.info("Received: {}".format(data.decode()))
    return True, response["nickname"]


async def open_connection(host, port, max_attempts=3):
    attempts = 0
    reader = None
    while not reader:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            msg = f"Connection established, port: {port}"
            main_logger.info(msg)
            return reader, writer
        except (
            ConnectionRefusedError,
            ConnectionResetError,
            ConnectionError,
        ):
            if attempts < int(max_attempts):
                msg = "No connection. Trying again..."
                main_logger.info(msg)
                attempts += 1
                await asyncio.sleep(3)
            else:
                msg = "No connection. Trying again in 3 sec..."
                main_logger.info(msg)
                await asyncio.sleep(3)
            continue



@asynccontextmanager
async def get_connection(host, port, status_queue):
    reader, writer = await open_connection(host, port)

    status_queue.put_nowait(ReadConnectionStateChanged.INITIATED)
    status_queue.put_nowait(SendingConnectionStateChanged.INITIATED)

    try:
        status_queue.put_nowait(ReadConnectionStateChanged.ESTABLISHED)
        status_queue.put_nowait(SendingConnectionStateChanged.ESTABLISHED)

        yield (reader, writer)
    finally:
        status_queue.put_nowait(ReadConnectionStateChanged.CLOSED)
        status_queue.put_nowait(SendingConnectionStateChanged.CLOSED)

        writer.close()
        await writer.wait_closed()