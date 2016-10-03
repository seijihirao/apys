from aiohttp import web

from apys import apiobject, log, routes, config

def start():
    """
    Starts server
    """

    log.start()

    app = web.Application()
    global_api = apiobject.mount()

    routes.prepare(app, global_api, cors_url=config.value['server']['cors'])

    web.run_app(app, port=config.value['server']['port'])