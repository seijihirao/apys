import os
import sys
import imp
import json

from aiohttp import web
import aiohttp_cors

from apys import log

def prepare(app, api, cors_url=False):
    """
    Mount routers and add them to aiohttp application 
    
    Returns:
        application (cyclone.web.Application): cyclone application with endpoint routers mounted 
    """

    cors = aiohttp_cors.setup(app)

    file_paths = []
    
    #read all endpoint files
    for root, subdirs, files in os.walk('./endpoints'):
        for file in files:
            if os.path.splitext(file)[1] == '.py':
                file_paths += [{
                    'url': os.path.splitext(os.path.relpath(os.path.join(root, file), 'endpoints/'))[0],
                    'file': os.path.join(root, file)
                }]
    
    routes = []
    
    utils = {}
    
    api.debug('')
    api.debug('================== Resources ====================')
    
    #populate routes
    for file_path in file_paths:
        
        # api.debug('Loading endpoint: [' + api._bcolors.HEADER + file_path['url'] + api._bcolors.ENDC + ']')
        
        file_module = imp.load_source(file_path['url'].replace('/', '-'), file_path['file'])

        supported_methods = api.supported_methods

        handler_props = {
            '_params': None,
            
            'api': api
        }
        

        handler_props['pypoly_utils_any'] = []
        ##
        # ADDING UTILS TO API PARAM
        #
        if hasattr(file_module, 'utils'):
            for util in file_module.utils:
                if not util in utils:
                    utils[util] = imp.load_source(util, os.path.join('utils', util + '.py'))
                setattr(handler_props['api'], util, utils[util])
                
                #calls util init function 
                if hasattr(utils[util], 'init'):
                    utils[util].init(api)

        ##
        # ADDING METHOD FUNCTIONS
        #
        def createFunc(endpoint, method):
            async def func(req):

                if req.has_body:
                    req.params = await req.json()
                else:
                    req.params = {}
                
                if hasattr(endpoint, 'utils'):
                    for util in endpoint.utils:
                        # Calls 'any' util function
                        if hasattr(utils[util], 'any'):
                            utils[util].any(req, handler_props['api'])
                        # Calls current method util function
                        if hasattr(utils[util], method):
                            getattr(utils[util], method)(req, handler_props['api'])

                # Calls current method function
                return web.json_response(getattr(endpoint, method)(req, handler_props['api']))

            return func

        # Adds route resource

        resource = cors.add(app.router.add_resource('/' + file_path['url']))
        loaded_methods = []
        for method in supported_methods:
            if hasattr(file_module, method):

                loaded_methods += [method] # Log purpose
                # Adds route
                if cors_url:
                    cors.add(resource.add_route(method.upper(), createFunc(file_module, method)), {
                        cors_url: aiohttp_cors.ResourceOptions()
                    })
                else:
                    resource.add_route(method.upper(), createFunc(file_module, method))
        
        # Logging loaded endpoints
        str_loaded_methods = '('
        for method in loaded_methods:
            str_loaded_methods += api._bcolors.OKGREEN + method + api._bcolors.ENDC
            str_loaded_methods += ', '
        str_loaded_methods = str_loaded_methods[0:-2]
        str_loaded_methods += ')'
        api.debug('Endpoint Loaded: [' + api._bcolors.OKGREEN + file_path['url'] + api._bcolors.ENDC + '] ' + str_loaded_methods)
    
    # Logging loades utils
    for root, subdirs, files in os.walk('./utils'):
        for file in files:
            if os.path.splitext(file)[1] == '.py':
                util = os.path.splitext(file)[0]
                if util in utils:
                    api.debug('Util Loaded: [' + api._bcolors.OKBLUE + util + api._bcolors.ENDC + ']')
                else:
                    api.debug('Util not Loaded: [' + api._bcolors.WARNING + util + api._bcolors.ENDC + ']')
    
    api.debug('')
    return app