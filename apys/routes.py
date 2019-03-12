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

    filters = {}

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

        def add_filters(cur_filter):
            if cur_filter not in filters:
                filter_spec = importlib.util.spec_from_file_location(
                    cur_filter,
                    '{}.py'.format(os.path.join(settings.DIR_FILTERS, *(cur_filter.split('.')))))

                filters[cur_filter] = importlib.util.module_from_spec(filter_spec)
                filter_spec.loader.exec_module(filters[cur_filter])

                # calls util init function
                if hasattr(filters[cur_filter], 'init'):
                    filters[cur_filter].init(api)

                loaded_filters[cur_filter] = filters[cur_filter]

        if hasattr(file_module, ATTR_FILTERS):
            for filt in file_module.filters:

                if type(filt) == str:
                    add_filters(filt)
                elif type(filt) == list:
                    for f in filt:
                        add_filters(f)


        ##
        # ADDING METHOD FUNCTIONS
        #
        def create_func(endpoint, cur_method):

            def exec_filter(req, cur_filter):
                # Calls 'always' filt function
                if hasattr(filters[cur_filter], 'always'):
                    filters[cur_filter].always(req, handler_props['api'])
                # Calls current method filt function
                if hasattr(filters[cur_filter], cur_method):
                    getattr(filters[cur_filter], cur_method)(req, handler_props['api'])

            ##
            # This is what gets executed when you call the endpoint
            #
            async def func(req):
                req.vars = {}
                try:
                    if req.has_body:
                        if req.content_type == 'application/json':
                            req.body = await req.json()
                        elif req.content_type == 'multipart/form-data' or \
                                req.content_type == 'application/x-www-form-urlencoded':
                            req.body = dict(await req.post())
                        else:
                            req.body = {}

                        req.body = __translate_json(req.body)
                    else:
                        req.body = {}
                except Exception as ex:
                    str_err = 'Error while getting json data'
                    api.error(str_err, ex=ex)
                    raise handler_props['api'].web.HTTPInternalServerError(reason=str_err)
                
                if hasattr(endpoint, ATTR_FILTERS):
                    for cur_filter in endpoint.filters:
                        if type(cur_filter) == str:
                            exec_filter(req, cur_filter)
                        elif type(cur_filter) == list:
                            exception = None
                            for f in cur_filter:
                                exception = None

                                try:
                                    exec_filter(req, f)
                                except Exception as ex:
                                    exception = ex

                                if exception is None:
                                    break

                            if exception is not None:
                                raise exception

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
                if hasattr(loaded_filters[filt], 'always'):
                    str_loaded_filters += '{}{}{}'.format(api.bcolors.OKBLUE, filt, api.bcolors.ENDC)
                    str_loaded_filters += ', '
                if hasattr(loaded_filters[filt], method):
                    str_loaded_filters += '{}{}{}'.format(api.bcolors.OKGREEN, filt, api.bcolors.ENDC)
                    str_loaded_filters += ', '
            str_loaded_filters = str_loaded_filters[0:-2]
            
            api.debug('Endpoint Loaded: [{}{}{}] ({}) <- {{{}}}'.format(
                api.bcolors.OKGREEN, file_path['url'], api.bcolors.ENDC, str_loaded_methods, str_loaded_filters))
    
    api.debug('')
    return file_paths


def __translate_json(obj):
    """
    Gets a dictionary and formats its keys,
    following the rules:

        {'var.0': 'value0', 'var.1': 'value1'}
        will be
        {'var': ['value0', 'value1']}

    And 
    
        {'var.key0': 'value0', 'var.key1': 'value1'}
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
        dot_count = key.count('.')
        if dot_count:
            keys = key.split('.')
            cur_translated_obj = translated_obj
            for cur_key in keys:
                if dot_count:
                    # Keeps iterating and adding nested objects
                    if cur_key not in cur_translated_obj:
                        cur_translated_obj[cur_key] = {}
                    cur_translated_obj = cur_translated_obj[cur_key]
                else:
                    # Last one should have value
                    cur_translated_obj[cur_key] = obj[key]
                dot_count -= 1
        else:
            translated_obj[key] = obj[key]

    return __dict_to_list(translated_obj)


def __dict_to_list(obj):
    """
    Converts a dictionary to a list recursively

        {'0':'value0', '1':'value1'}
        will be
        ['value0', 'value1']

    Args:
        obj - dictionary object to be converted

    Returns:
        list if conversion was possible
    """

    # Only converts a dictionary
    if type(obj) != dict or obj == {}:
        return obj

    # Recursively converts
    for key in obj:
        if type(obj[key]) == dict:
            obj[key] = __dict_to_list(obj[key])

    # Checks if it really can be converted to a list
    for key in obj:
        if not key.isdigit():
            return obj

    return list(OrderedDict(obj).values())  # needs an ordered dict to return list in order
