import asyncio
import logging
import os
import sys

from aiohttp import web
import aiofiles

CHUNK_SIZE = 102400
SHOW_LOGS = os.getenv('SHOW_LOGS', False)
PHOTOS_DIR = os.getenv('PHOTOS_DIR', 'test_photos')
PAUSE_TIME = os.getenv('PAUSE_TIME', 1)

if SHOW_LOGS:
    logging.basicConfig(level=logging.DEBUG)


async def archivate(request):
    archive_hash = request.match_info['archive_hash']

    photos_dir = f'photos/{archive_hash}'

    if not os.path.exists(photos_dir):
        raise web.HTTPFound('/404/')

    headers = {
        'Content-Type': 'application/zip',
        'Content-Disposition': f'attachment; filename="{archive_hash}".zip',
    }

    response = web.StreamResponse(headers=headers)
    await response.prepare(request)

    zip_command = ['zip', '-r', '-', photos_dir]

    process = await asyncio.create_subprocess_exec(
        sys.executable,
        *zip_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        while True:
            data = await process.stdout.read(CHUNK_SIZE)
            if not data:
                logging.info('Complited to send the file.')
                break
            logging.info(f'Sending archive chunk {len(data)} ...')
            await response.write(data)
            await asyncio.sleep(PAUSE_TIME)
    except asyncio.CancelledError:
        logging.error('Download was interrupted.')
        logging.info(f'Killing the zip subprocess.')
        process.kill()
    finally:
        await response.write_eof()
    return response


async def handle_index_page(request):
    async with aiofiles.open('templates/index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


async def handle_404_page(request):
    async with aiofiles.open('templates/404.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archivate),
        web.get('/404/', handle_404_page),
    ])
    web.run_app(app)
