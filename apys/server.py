import sys
import os
import importlib
import importlib.util
import asyncio
import contextlib
from multiprocessing import Process, Event, Manager


from aiohttp import web

from apys import apiobject, routes, config, settings


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


def cli_start(util_name, args_config=None, arg=None):
    """
    Starts cli util on a process and server on another

    :param util_name: util dir name
    :param args_config: config file name got from cli args
    :param arg: argument used on cli
    :return:
    """
    if os.path.exists(os.path.join('.', settings.DIR_UTILS)):
        if (
                (os.path.isdir(os.path.join('.', settings.DIR_UTILS, util_name))) and
                (os.path.exists(os.path.join('.', settings.DIR_UTILS, util_name, '__cli__.py')))
        ):
            spec = importlib.util.spec_from_file_location(
                util_name,
                os.path.join('.', settings.DIR_UTILS, util_name, '__cli__.py'))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            cli = module.CLI(arg)

            # Getting config file
            if args_config:
                config_file = args_config
            elif hasattr(cli, 'config'):
                config_file = cli.config
            else:
                config_file = None

            process = {
                'dict': Manager().dict(),
                'event': Event()
            }

            def start_server(server_config_file, multiprocess):
                with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):  # disable logs
                    start(server_config_file, multiprocess)

            server_process = Process(target=start_server, args=(config_file, process))
            server_process.start()
            process['event'].wait()

            # execute async function
            loop = asyncio.new_event_loop()
            loop.run_until_complete(cli.start(process['dict']['api'], process['dict']['endpoints']))

            server_process.terminate()
