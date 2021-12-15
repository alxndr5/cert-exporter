import asyncio
from aiohttp import web

class Server:
    def __init__(self, metrics):
        self.app = web.Application()
        self.app.add_routes([
            web.get('/', Server.root),
            web.get('/metrics', Server.metrics),
            web.get('/startup', Server.startup),
            web.get('/readines', Server.readiness),
            web.get('/liveness', Server.liveness)
            ])
        self.app['metrics'] = metrics

    def start(self):
        web.run_app(self.app, port=9000)

    async def root(request):
        return web.Response(body=b"CertExporter")

    async def metrics(request):
        body = bytes()

        for line in request.app['metrics'].get():
            body += bytes(line + "\n", encoding='utf8')

        return web.Response(body=body)

    async def startup(request):
        return web.Response(body=b"ok")
    
    async def liveness(request):
        return web.Response(body=b"ok")
    
    async def readiness(request):
        return web.Response(body=b"ok")
