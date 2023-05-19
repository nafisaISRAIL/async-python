import argparse
import asyncio
import logging
import os
import socket
from tkinter import messagebox

import aiofiles
import anyio
from async_timeout import timeout
from dotenv import load_dotenv

import gui
from server_connection import (
    UserInterrupt,
    authenticate_user,
    get_connection,
    read_messages,
    register_user,
    submit_message
)

WATCH_CONNECTION_TIMEOUT = 15
PING_PONG_TIMEOUT = 10
DELAY_BETWEEN_PING_PONG = 10

main_logger = logging.getLogger("main_logger")
watchdog_logger = logging.getLogger("watchdog_logger")


def get_arguments(host, read_port, write_port, token, history):
    parser = argparse.ArgumentParser()
    add_argument = parser.add_argument

    add_argument("--host", type=str, help="Host for connecting to chat")
    add_argument(
        "--read-port",
        type=str,
        help="Port for connecting to chat for reading messages. Default: 5000",
    )
    add_argument(
        "--write-port",
        type=str,
        help="Port for connecting to chat for writing messages. Default: 5050",
    )
    add_argument(
        "--token", type=str, help="User token for authorisation in chat"
    )
    add_argument(
        "--history",
        type=str,
        help="Filepath for save chat messages. Default: history.txt",
    )

    parser.set_defaults(
        host=host,
        read_port=read_port,
        write_port=write_port,
        token=token,
        history=history,
    )
    args_namespace = parser.parse_args()
    args = vars(args_namespace)
    return (
        args["host"],
        args["read_port"],
        args["write_port"],
        args["token"],
        args["history"],
    )


async def ping_pong(reader, writer, watchdog_queue):
    while True:
        try:
            async with timeout(PING_PONG_TIMEOUT):
                writer.write("\n".encode())
                await writer.drain()

                await reader.readline()
            await asyncio.sleep(DELAY_BETWEEN_PING_PONG)
            watchdog_queue.put_nowait(
                "Connection is alive. Ping message sent")

        except socket.gaierror as exc:
            watchdog_queue.put_nowait(
                "socket.gaierror: no internet connection")
            raise ConnectionError() from exc


async def watch_for_connection(watchdog_queue):
    while True:
        try:
            async with timeout(WATCH_CONNECTION_TIMEOUT):
                message = await watchdog_queue.get()
                watchdog_logger.info(message)
        except asyncio.TimeoutError as err:
            watchdog_logger.info(
                f"{WATCH_CONNECTION_TIMEOUT}s is elapsed")
            raise ConnectionError() from err


async def display_saved_messages(filepath, saved_messages_queue):
    async with aiofiles.open(filepath, mode="w+") as file:
        async for line in file:
            saved_messages_queue.put_nowait(line)


async def send_message(reader, writer, sending_queue):
    while True:
        message = await sending_queue.get()
        await submit_message(reader, writer, message)


async def handle_connection(host, write_port, read_port, filepath,
                            token, sending_queue, messages_queue,
                            watchdog_queue, status_updates_queue):
    while True:
        try:
            async with get_connection(host, write_port,
                                      status_updates_queue) as streams:
                async with timeout(WATCH_CONNECTION_TIMEOUT):
                    token_is_valid, username = await authenticate_user(
                        *streams, token)

                    if not token_is_valid:
                        username = gui.msg_box(
                                "Token is invalid.",
                                "Please enter preferred nickname",
                            )
                        if username == "":
                            main_logger.info(
                                "The user didn't enter a username")
                            messagebox.showinfo(
                                "Invalid username",
                                "Empty string as a username is not allowed"
                            )
                            raise UserInterrupt()
                        if username is None:
                            main_logger.info(
                                "User canceled 'username' input")
                            raise UserInterrupt()
                        await register_user(*streams, username)
                    status_updates_queue.put_nowait(
                        gui.NicknameReceived(username))
                    async with anyio.create_task_group() as tg:
                        tg.start_soon(
                            read_messages,
                            host, read_port, filepath, messages_queue)
                        tg.start_soon(
                            send_message, *streams, sending_queue)
                        tg.start_soon(watch_for_connection, watchdog_queue)
                        tg.start_soon(ping_pong, *streams, watchdog_queue)
        except (
            ConnectionRefusedError,
            ConnectionResetError,
            ConnectionError,
            asyncio.TimeoutError,
        ):
            continue
        else:
            break


async def main():
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()
    host, read_port, write_port, token, filepath = get_arguments(
        os.getenv("MINECHAT_SERVER_HOST"),
        os.getenv("MINECHAT_SERVER_READ_PORT"),
        os.getenv("MINECHAT_SERVER_WRITE_PORT"),
        os.getenv("MINECHAT_TOKEN"),
        os.getenv("MINECHAT_HISTORY"),
    )
    messages_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()
    saved_messages_queue = asyncio.Queue()
    watchdog_queue = asyncio.Queue()
    try:
        async with anyio.create_task_group() as tg:
            tg.start_soon(
                gui.draw,
                messages_queue, sending_queue,
                status_updates_queue, saved_messages_queue)
            tg.start_soon(
                display_saved_messages,
                filepath, saved_messages_queue)
            tg.start_soon(
                handle_connection,
                host, write_port, read_port, filepath, token,
                sending_queue, messages_queue, watchdog_queue,
                status_updates_queue)
    except anyio.ExceptionGroup as exc:
        raise exc

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, gui.TkAppClosed, UserInterrupt):
        exit()
