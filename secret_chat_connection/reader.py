import asyncio
import aiofiles
import argparse
from datetime import datetime


async def main(host, port, filepath):
    reader, writer = await asyncio.open_connection(host, port)
    while True:
        line = await reader.readline()
        if not line:
            break
        line = line.decode("utf-8")
        if line:
            date = datetime.now().strftime("%y.%m.%d %H:%M")
            line = f"[{date}] " + line
            async with aiofiles.open(filepath, mode="a") as file:
                await file.write(line)
                print(line)
    writer.close()


parent_parser = argparse.ArgumentParser(prog="listen-minechat")
parent_parser.add_argument("--host", type=str, default="minechat.dvmn.org", help="Connection host.")
parent_parser.add_argument("--port", type=int, default=5000, help="Connection port.")
parent_parser.add_argument("--history", type=str, default="history.txt", help="Store file location.")

args = parent_parser.parse_args()
asyncio.run(main(args.host, args.port, args.history))
