import os
import sys
import imp
import json
import re
import inspect

from collections import OrderedDict

from aiohttp import web
import aiohttp_cors

from apys import log, settings

#
# CONSTANTS
#

ATTR_FILTERS = settings.DIR_FILTERS
ATTR_UTILS = settings.DIR_UTILS

#
# Functions
#

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
                expose_headers='*',
                allow_headers='*'
            )
        })

    file_paths = []
    
    #read all endpoint files
    for root, subdirs, files in os.walk(os.path.join('.', settings.DIR_ENDPOINTS)):
        for file in files:
            if os.path.splitext(file)[1] == '.py':
                file_paths += [{
                    'url': os.path.splitext(os.path.relpath(os.path.join(root, file), settings.DIR_ENDPOINTS))[0],
                    'file': os.path.join(root, file)
                }]
    
    routes = []
    
    utils = {}
    filters = {}
    
    api.debug('')
    if cors_url:
        api.debug('================== Resources ==================== {}cors-enabled=\'{}\'{}'.format(api._bcolors.WARNING, cors_url, api._bcolors.ENDC))
    else:
        api.debug('================== Resources ====================')

    api.debug('')
    
    ##
    # ADDING UTILS TO API PARAM
    #
    if os.path.exists(os.path.join('.', settings.DIR_UTILS)):
        for subdir in os.listdir(os.path.join('.', settings.DIR_UTILS)):
            if((os.path.isdir(os.path.join('.', settings.DIR_UTILS, subdir))) and
                (os.path.exists(os.path.join('.', settings.DIR_UTILS, subdir, '__init__.py')))):
                util = subdir
                if util not in utils:
                    utils[util] = imp.load_source(util, os.path.join('.', settings.DIR_UTILS, util, '__init__.py'))
                    setattr(api, util, utils[util])
                
                    # calls util init function 
                    if hasattr(utils[util], 'init'):
                        utils[util].init(api)

    # populate routes
    for file_path in file_paths:

        file_module = imp.load_source(file_path['url'].replace('/', '-'), file_path['file'])

        supported_methods = api.supported_methods

        handler_props = {
            'api': api
        }

        loaded_methods = []
        loaded_filters = {}
        
        ##
        # ADDING FILTER TO LIST
        #
        if hasattr(file_module, ATTR_FILTERS):
            for filt in file_module.filters:
                if not filt in filters:
                    filters[filt] = imp.load_source(filt, '{}.py'.format(os.path.join(settings.DIR_FILTERS, *(filt.split('.')))))

                    #calls util init function 
                    if hasattr(filters[filt], 'init'):
                        filters[filt].init(api)

                loaded_filters[filt] = filters[filt]

        ##
        # ADDING METHOD FUNCTIONS
        #
        def createFunc(endpoint, method):

            ##
            # This is what gets executed when you call the endpoint
            #
            async def func(req):
                req.vars = {}
                try:
                    if req.has_body:
                        req.body = await req.json()
                        req.body = __translateJson(req.body)
                    else:
                        req.body = {}
                except Exception as ex:
                    api.error('Error while getting json data', ex=ex)
                
                if hasattr(endpoint, ATTR_FILTERS):
                    for filt in endpoint.filters:
                        # Calls 'any' filt function
                        if hasattr(filters[filt], 'any'):
                            filters[filt].any(req, handler_props['api'])
                        # Calls current method filt function
                        if hasattr(filters[filt], method):
                            getattr(filters[filt], method)(req, handler_props['api'])

                # Calls current method function
                
                func = getattr(endpoint, method)
                if inspect.iscoroutinefunction(func):
                    return web.json_response(await func(req, handler_props['api']))
                else:
                    return web.json_response(func(req, handler_props['api']))

            return func

        # Adds route resource

        if cors_url:
            resource = cors.add(app.router.add_resource('/{}'.format(file_path['url'])))
        else: 
            resource = app.router.add_resource('/{}'.format(file_path['url']))
        for method in supported_methods:
            if hasattr(file_module, method):

                loaded_methods += [method] # Log purpose
                # Adds route
                if cors_url:
                    cors.add(resource.add_route(method.upper(), createFunc(file_module, method)))
                else:
                    resource.add_route(method.upper(), createFunc(file_module, method))
        
        # Logging loaded endpoints
        for method in loaded_methods:
            str_loaded_methods = '{}{}{}'.format(api._bcolors.OKGREEN, method, api._bcolors.ENDC)

            str_loaded_filters = ''
            for filt in loaded_filters:
                if hasattr(loaded_filters[filt], 'any'):
                    str_loaded_filters += '{}{}{}'.format(api._bcolors.OKBLUE, filt, api._bcolors.ENDC)
                    str_loaded_filters += ', '
                if hasattr(loaded_filters[filt], method):
                    str_loaded_filters += '{}{}{}'.format(api._bcolors.OKGREEN, filt, api._bcolors.ENDC)
                    str_loaded_filters += ', '
            str_loaded_filters = str_loaded_filters[0:-2]
            
            api.debug('Endpoint Loaded: [{}{}{}] ({}) <- {{{}}}'.format(api._bcolors.OKGREEN, file_path['url'], api._bcolors.ENDC, str_loaded_methods, str_loaded_filters))
    
    api.debug('')

    # Logging loades utils
    for util in utils:
        api.debug('Util Loaded: [{}{}{}]'.format(api._bcolors.OKBLUE, util, api._bcolors.ENDC))
    
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