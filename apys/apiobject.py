from apys import config, log

class _ApiObject(object):
    """
    Api properties that will be avaliable on endpoints
    
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
        self.config = config.load(config_file) if config_file else config.load()

        # Log
        self._bcolors = log.bcolors if self.config['log']['color'] else log.nocolors

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

    def debug(self, msg, to='debug'):
        log.debug(self, msg, to)
        
    def error(self, msg, to='debug', ex=False):
        log.error(self, msg, to, ex)

def mount(config_file):
    return _ApiObject(config_file)