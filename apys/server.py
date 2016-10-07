import sys

from aiohttp import web

from apys import apiobject, log, routes, config

def start(config_file):
    """
    Starts server
    """

    # Preparing environment
    app = web.Application()
    global_api = apiobject.mount(config_file)
    
    # Setting log files
    if global_api.config['log']['file']:
        f_out = open(global_api.config['log']['file']['debug'], 'a')
        sys.stdout = f_out

        f_err = open(global_api.config['log']['file']['error'], 'a')
        sys.stderr = f_err

    # Preparing routes
    routes.prepare(app, global_api, cors_url=global_api.config['server']['cors'])

    # Start logging
    start_str = 'Using [' + global_api._bcolors.HEADER + '{}' + global_api._bcolors.ENDC + '] configuration\n'
    if config_file:
        global_api.debug(start_str.format(config_file))
    else:
        global_api.debug(start_str.format(config.default()))

    # Running server
    web.run_app(app, port=global_api.config['server']['port'])