from aiohttp import web
from processor import articles_processor

async def handle(request):
    urls = request.rel_url.query.get("urls", []).split(",")
    if len(urls) > 10:
        return web.json_response({"error": "too many urls in request, should be 10 or less"}, status=400)
    res = await articles_processor(urls)
    return web.json_response(res)

app = web.Application()
app.add_routes([web.get('/', handle)])

if __name__ == '__main__':
    web.run_app(app)