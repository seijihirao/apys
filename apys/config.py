import os
import json

from apys import settings

def load(scope='default'):
    """
    loads choosen config file
    if scope is not define loads default (first try `local`, then `dev` and last `prod`)
    
    Args:
        scope: config file, without `.json`

    Returns:
        obj: formated json config object
    """
    if scope is 'default':
        config = load(default())
        if config:
            return config
                    
    else:
        path = os.path.join(settings.DIR_CONFIG, '{}.json'.format(scope))
        if os.path.exists(path):
            with open(path, 'r') as config:
                obj = json.loads(config.read())
                obj['scope'] = scope

                #Default Values

                __fillDefaultValue(obj, 'log', {})
                __fillDefaultValue(obj['log'], 'file', settings.DEFAULT_LOG)
                if type(obj['log']['file']) == str:
                    obj['log']['file'] = {
                        'debug': obj['log']['file'],
                        'error': obj['log']['file']
                    }
                __fillDefaultValue(obj['log'], 'color', settings.DEFAULT_COLOR)

                __fillDefaultValue(obj, 'server', {})
                __fillDefaultValue(obj['server'], 'port', settings.DEFAULT_PORT)
                __fillDefaultValue(obj['server'], 'cors', settings.DEFAULT_CORS)

                return obj

    raise EnvironmentError('No config file found for {}'.format(scope))

def default():
    """
    Gets default configuration file

    Returns:
        scope: config filename
    """
    for scope in [settings.DEFAULT_LOCAL_NAME, settings.DEFAULT_DEV_NAME, settings.DEFAULT_PROD_NAME]:
        path = os.path.join(settings.DIR_CONFIG, '{}.json'.format(scope))
        if os.path.exists(path):
            return scope
    

def __fillDefaultValue(obj, key, default):
    """
    Fill Default value if key does not exists on object

    Args:
        obj: object to fill with default value
        key: key that will be filled if inexistent
        default: default value to be filled
    """
    if key not in obj:
        obj[key] = default