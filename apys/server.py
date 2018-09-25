import sys

from aiohttp import web

from apys import apiobject, routes, config


def start(config_file=None, process={'event': False, 'dict': {}}):
    """
    Starts server

    Args:
        config_file: default to 'prod'
        disable_log: True to disable access logs
        process: multiprocessing object
            process['event']: Event object (used to wait)
            process['dict']: Manager.dict object
    """

    # Preparing environment
    app = web.Application()
    global_api = apiobject.ApiObject(config_file)
    process['dict']['api'] = global_api

    # Setting log files
    if global_api.config['log']['file']:
        f_out = open(global_api.config['log']['file']['debug'], 'a')
        sys.stdout = f_out

        f_err = open(global_api.config['log']['file']['error'], 'a')
        sys.stderr = f_err

    # Preparing routes
    process['dict']['endpoints'] = routes.prepare(app, global_api, cors_url=global_api.config['server']['cors'])

    # Start logging
    start_str = 'Using [' + global_api.bcolors.HEADER + '{}' + global_api.bcolors.ENDC + '] configuration\n'
    if config_file:
        global_api.debug(start_str.format(config_file))
    else:
        global_api.debug(start_str.format(config.default()))

    if process['event']:
        process['event'].set()

    # Running server
    web.run_app(app, port=global_api.config['server']['port'])
