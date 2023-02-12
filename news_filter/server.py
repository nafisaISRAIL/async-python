from aiohttp import web


from processor import analize_articles


async def handle(request):
    urls = request.rel_url.query.get("urls")
    if not urls:
        return web.json_response({})
    urls = urls.split(",")
    if len(urls) > 10:
        return web.json_response(
            {
                "error": "too many urls in request, should be 10 or less"
            },
            status=400
        )
    analized_articles = await analize_articles(urls)
    return web.json_response(analized_articles)


def main():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    web.run_app(app)


if __name__ == '__main__':
    main()
