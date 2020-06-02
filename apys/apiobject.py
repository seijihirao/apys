import aiohttp
import aiohttp.web
import os
import importlib
import importlib.util

from apys import config, log, settings


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

    def __init__(self, config_file, has_log=True):
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

        ##
        # ADDING UTILS TO API PARAM
        #
        utils = {}
        if 'utils' in self.config:
            for util in self.config['utils']:
                if (
                        (os.path.isdir(os.path.join('.', settings.DIR_UTILS, util))) and
                        (os.path.exists(os.path.join('.', settings.DIR_UTILS, util, '__init__.py')))
                ):
                    if util not in utils:
                        spec = importlib.util.spec_from_file_location(
                            util,
                            os.path.join('.', settings.DIR_UTILS, util, '__init__.py'))

                        utils[util] = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(utils[util])

                        setattr(self, util, utils[util])

                        # calls util init function
                        if hasattr(utils[util], 'init'):
                            utils[util].init(self)

        if has_log:
            # Starts Logging Resources
            self.debug('')
            cors_url = self.config['server']['cors']
            if cors_url:
                self.debug('================== Resources ==================== {}cors-enabled=\'{}\'{}'.format(
                    self.bcolors.WARNING, cors_url, self.bcolors.ENDC))
            else:
                self.debug('================== Resources ====================')

            self.debug('')

            # Logging loaded utils
            for util in utils:
                self.debug('Util Loaded: [{}{}{}]'.format(self.bcolors.OKBLUE, util, self.bcolors.ENDC))

            self.debug('')

    def debug(self, msg, to='debug'):
        log.debug(self, msg, to)
        
    def error(self, msg, to='debug', ex=False):
        log.error(self, msg, to, ex)

    def __reduce__(self):
        return ApiObject, (self.config_file, False)
