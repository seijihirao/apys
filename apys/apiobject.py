import aiohttp
import aiohttp.web

from apys import config, log


class ApiObject:
    """
    Api properties that will be available on endpoints
    
    Properties:
        vars: dictionary api custom variables
        config: current config object
        supported_methods: supported http rest methods
        debug: function to log message
        error: function to log error
        (will be added endpoint required util modules)
    """

    def __init__(self, config_file):
        # Config file
        self.config_file = config_file
        self.config = config.load(config_file) if config_file else config.load()

        # Log
        self.bcolors = log.BColors if self.config['log']['color'] else log.NoColors

        # Supported methods
        self.supported_methods = [
            'get', 
            'post',
            'put',
            'delete',
            'head',
            'options',
            'default'
        ]

        # Shared variable
        self.vars = {}

        self.web = aiohttp.web

    def debug(self, msg, to='debug'):
        log.debug(self, msg, to)
        
    def error(self, msg, to='debug', ex=False):
        log.error(self, msg, to, ex)

    def __reduce__(self):
        return ApiObject, (self.config_file, )

