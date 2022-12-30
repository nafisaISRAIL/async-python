import os
import aiohttp
import time
import pymorphy2
import aiofiles
from anyio import sleep, create_task_group, run
import asyncio
from async_timeout import timeout
from adapters import SANITIZERS, ArticleNotFound
from text_tools import calculate_jaundice_rate, split_by_words
from enums import ProcessingStatus

from contextlib import contextmanager
from contextlib import asynccontextmanager
import logging


logging.basicConfig(level=logging.DEBUG)


sanitizer = SANITIZERS["inosmi_ru"]


async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


def get_charge_words_from_file():
    with open("charged_dict/negative_words.txt") as f:
        negative_words = [line.rstrip("\n") for line in f]

    with open("charged_dict/positive_words.txt") as f:
        positive_words = [line.rstrip("\n") for line in f]

    return (negative_words, positive_words)


@asynccontextmanager
async def timeit():
    start = time.monotonic()
    try:
        yield
    finally:
        taken_time = "%.2f" % (time.monotonic() - start)
        logging.info(f"Time taken to analize the text: {taken_time}")


async def process_article(session, morph, charged_words, url, result):
    score = None
    words_count = None
    status = None
    data_fetched = False
    cleaned_body = ""
    try:
        async with timeout(3):
            html = await fetch(session, url)
            data_fetched = True
            status = ProcessingStatus.OK
            cleaned_body = sanitizer(html, plaintext=True)
    except asyncio.TimeoutError:
        status = ProcessingStatus.TIMEOUT
    except ArticleNotFound:
        status = ProcessingStatus.PARSING_ERROR
    except aiohttp.client_exceptions.ClientConnectorError:
        status = ProcessingStatus.FETCH_ERROR
    if data_fetched:
        try:
            async with timeit():
                async with timeout(5):
                    article_words = split_by_words(morph, cleaned_body)
                score = calculate_jaundice_rate(article_words, charged_words)
                words_count = len(article_words)
        except asyncio.TimeoutError:
            status = ProcessingStatus.TIMEOUT
    result.append({"url": url,"score": score, "words_count": words_count, "status": status.value})


async def articles_processor(urls):
    result = []
    async with aiohttp.ClientSession() as session:
        morph = pymorphy2.MorphAnalyzer()
        negative_charge_words, _ = get_charge_words_from_file()
        async with create_task_group() as tg:
            for article_url in urls:
                tg.start_soon(process_article, session, morph, negative_charge_words, article_url, result)
    return result
