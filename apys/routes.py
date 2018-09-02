import os
import importlib
import importlib.util
import re
import inspect

from collections import OrderedDict

from aiohttp import web
import aiohttp_cors

from apys import settings

#
# CONSTANTS
#


ATTR_FILTERS = settings.DIR_FILTERS
ATTR_UTILS = settings.DIR_UTILS

#
# Functions
#


def prepare(app, api, cors_url=''):
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
    
    # read all endpoint files
    for root, subdirs, files in os.walk(os.path.join('.', settings.DIR_ENDPOINTS)):
        for file in files:
            if os.path.splitext(file)[1] == '.py':
                file_paths += [{
                    'url': os.path.splitext(os.path.relpath(os.path.join(root, file), settings.DIR_ENDPOINTS))[0],
                    'file': os.path.join(root, file)
                }]
    
    utils = {}
    filters = {}
    
    api.debug('')
    if cors_url:
        api.debug('================== Resources ==================== {}cors-enabled=\'{}\'{}'.format(
            api.bcolors.WARNING, cors_url, api.bcolors.ENDC))
    else:
        api.debug('================== Resources ====================')

    api.debug('')
    
    ##
    # ADDING UTILS TO API PARAM
    #
    if os.path.exists(os.path.join('.', settings.DIR_UTILS)):
        for subdir in os.listdir(os.path.join('.', settings.DIR_UTILS)):
            if(
                (os.path.isdir(os.path.join('.', settings.DIR_UTILS, subdir))) and
                (os.path.exists(os.path.join('.', settings.DIR_UTILS, subdir, '__init__.py')))
            ):

                util = subdir
                if util not in utils:
                    spec = importlib.util.spec_from_file_location(
                        util,
                        os.path.join('.', settings.DIR_UTILS, util, '__init__.py'))

                    utils[util] = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(utils[util])

                    setattr(api, util, utils[util])
                
                    # calls util init function 
                    if hasattr(utils[util], 'init'):
                        utils[util].init(api)

    # populate routes
    for file_path in file_paths:

        spec = importlib.util.spec_from_file_location(file_path['url'].replace('/', '-'), file_path['file'])
        file_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(file_module)

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
                if filt not in filters:
                    spec = importlib.util.spec_from_file_location(
                        filt,
                        '{}.py'.format(os.path.join(settings.DIR_FILTERS, *(filt.split('.')))))

                    filters[filt] = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(filters[filt])

                    # calls util init function
                    if hasattr(filters[filt], 'init'):
                        filters[filt].init(api)

                loaded_filters[filt] = filters[filt]

        ##
        # ADDING METHOD FUNCTIONS
        #
        def create_func(endpoint, cur_method):

            ##
            # This is what gets executed when you call the endpoint
            #
            async def func(req):
                req.vars = {}
                try:
                    if req.has_body:
                        req.body = await req.json()
                        req.body = __translate_json(req.body)
                    else:
                        req.body = {}
                except Exception as ex:
                    api.error('Error while getting json data', ex=ex)
                
                if hasattr(endpoint, ATTR_FILTERS):
                    for cur_filter in endpoint.filters:
                        # Calls 'any' filt function
                        if hasattr(filters[cur_filter], 'any'):
                            filters[cur_filter].any(req, handler_props['api'])
                        # Calls current method filt function
                        if hasattr(filters[cur_filter], cur_method):
                            getattr(filters[cur_filter], cur_method)(req, handler_props['api'])

                # Calls current method function
                
                method_function = getattr(endpoint, cur_method)
                if inspect.iscoroutinefunction(method_function):
                    return web.json_response(await method_function(req, handler_props['api']))
                else:
                    return web.json_response(method_function(req, handler_props['api']))

            return func

        # Adds route resource

        if cors_url:
            # noinspection PyUnboundLocalVariable
            resource = cors.add(app.router.add_resource('/{}'.format(file_path['url'])))
        else: 
            resource = app.router.add_resource('/{}'.format(file_path['url']))
        for method in supported_methods:
            if hasattr(file_module, method):

                loaded_methods += [method]  # Log purpose
                # Adds route
                if cors_url:
                    cors.add(resource.add_route(method.upper(), create_func(file_module, method)))
                else:
                    resource.add_route(method.upper(), create_func(file_module, method))
        
        # Logging loaded endpoints
        for method in loaded_methods:
            str_loaded_methods = '{}{}{}'.format(api.bcolors.OKGREEN, method, api.bcolors.ENDC)

            str_loaded_filters = ''
            for filt in loaded_filters:
                if hasattr(loaded_filters[filt], 'any'):
                    str_loaded_filters += '{}{}{}'.format(api.bcolors.OKBLUE, filt, api.bcolors.ENDC)
                    str_loaded_filters += ', '
                if hasattr(loaded_filters[filt], method):
                    str_loaded_filters += '{}{}{}'.format(api.bcolors.OKGREEN, filt, api.bcolors.ENDC)
                    str_loaded_filters += ', '
            str_loaded_filters = str_loaded_filters[0:-2]
            
            api.debug('Endpoint Loaded: [{}{}{}] ({}) <- {{{}}}'.format(
                api.bcolors.OKGREEN, file_path['url'], api.bcolors.ENDC, str_loaded_methods, str_loaded_filters))
    
    api.debug('')

    # Logging loads utils
    for util in utils:
        api.debug('Util Loaded: [{}{}{}]'.format(api.bcolors.OKBLUE, util, api.bcolors.ENDC))
    
    api.debug('')
    return app


def __translate_json(obj):
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
            if main not in translated_obj:
                translated_obj[main] = {}
            translated_obj[main][sub] = __translate_json(obj[key])
            
        else:
            translated_obj[key] = __translate_json(obj[key])
    
    for key in translated_obj:
        translated_obj[key] = __dict_to_list(translated_obj[key])

    return translated_obj


def __dict_to_list(obj):
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
    
    return list(OrderedDict(obj).values())  # needs an ordered dict to return list in order
