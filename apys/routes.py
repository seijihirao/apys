import os
import sys
import imp
import json
import re
import inspect

from collections import OrderedDict

from aiohttp import web
import aiohttp_cors

from apys import log

def prepare(app, api, cors_url=False):
    """
    Mount routers and add them to aiohttp application 
    
    Returns:
        application (cyclone.web.Application): cyclone application with endpoint routers mounted 
    """
    
    if cors_url:
        cors = aiohttp_cors.setup(app, defaults={
            cors_url: aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*"
            )
        })

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
    api.debug('================== Resources ===================='  + ((api._bcolors.WARNING + ' cors-enabled=\'' + cors_url + '\'' + api._bcolors.ENDC) if cors_url else ''))
    
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

                try:
                    if req.has_body:
                        req.params = await req.json()
                        req.params = __translateJson(req.params)
                    else:
                        req.params = {}
                except Exception as ex:
                    api.error('Error while getting json data', ex=ex)
                
                if hasattr(endpoint, 'utils'):
                    for util in endpoint.utils:
                        # Calls 'any' util function
                        if hasattr(utils[util], 'any'):
                            utils[util].any(req, handler_props['api'])
                        # Calls current method util function
                        if hasattr(utils[util], method):
                            getattr(utils[util], method)(req, handler_props['api'])

                # Calls current method function
                
                func = getattr(endpoint, method)
                if inspect.iscoroutinefunction(func):
                    return web.json_response(await func(req, handler_props['api']))
                else:
                    return web.json_response(func(req, handler_props['api']))

            return func

        # Adds route resource

        if cors_url:
            resource = cors.add(app.router.add_resource('/' + file_path['url']))
        else: 
            resource = app.router.add_resource('/' + file_path['url'])
        loaded_methods = []
        for method in supported_methods:
            if hasattr(file_module, method):

                loaded_methods += [method] # Log purpose
                # Adds route
                if cors_url:
                    cors.add(resource.add_route(method.upper(), createFunc(file_module, method)))
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

def __translateJson(obj):
    """
    Gets a dictionary and formats its keys,
    following the rules:

        {'var[0]': 'value0', 'var[1]': 'value1'}
        will be
        {'var': ['value0', 'value1']}

    And 
    
        {'var[key0]': 'value0', 'var[key1]': 'value1'}
        will be
        {'var': {'key0':'value0', 'key1':'value1'}}

    Args:
        obj - dictionary object to be converted
    
    Returns:
        translated object
    """
    # Only translates a dictionary
    if type(obj) != dict:
        return obj

    translated_obj = {}
    for key in obj:
        if re.match(r'^(\w+)\[(\w+)\]$', key):
            main, sub = re.match(r'(\w+)\[(\w+)\]', key).groups()
            if not main in translated_obj: 
                translated_obj[main] = {}
            translated_obj[main][sub] = __translateJson(obj[key])
            
        else:
            translated_obj[key] = __translateJson(obj[key])       
    
    for key in translated_obj:
        translated_obj[key] = __DictToList(translated_obj[key])  

    return translated_obj

def __DictToList(obj):
    """
    Converts a dictionary to a list

        {'0':'value0', '1':'value1'}
        will be
        ['value0', 'value1']

    Args:
        obj - dictionary object to be converted
    
    Returns:
        list if conversion was possible 
    """
    # Only converts a dictionary
    if type(obj) != dict:
        return obj
    
    # Checks if it really can be converted to a list
    for key in obj:
        if not key.isdigit():
            return obj
    
    return list(OrderedDict(obj).values()) #needs an ordered dict to return list in order