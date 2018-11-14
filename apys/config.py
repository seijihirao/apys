import os
import json

from apys import settings


def load(scope=None):
    """
    loads chosen config file
    if scope is not define loads default (first try `local`, then `dev` and last `prod`)
    
    Args:
        scope: config file, without `.json`

    Returns:
        obj: formatted json config object
    """
    if not scope:
        scope = default()

    path = os.path.join(settings.DIR_CONFIG, '{}.json'.format(scope))

    if not os.path.exists(path):
        raise EnvironmentError('No config file found for {}'.format(scope))

    with open(path, 'r') as config:
        obj = json.loads(config.read())
        obj['scope'] = scope

        # Default Values

        __fill_default_value(obj, 'log', {})
        __fill_default_value(obj['log'], 'file', settings.DEFAULT_LOG)
        if type(obj['log']['file']) == str:
            obj['log']['file'] = {
                'debug': obj['log']['file'],
                'error': obj['log']['file']
            }
        __fill_default_value(obj['log'], 'color', settings.DEFAULT_COLOR)

        __fill_default_value(obj, 'server', {})
        __fill_default_value(obj['server'], 'port', settings.DEFAULT_PORT)
        __fill_default_value(obj['server'], 'cors', settings.DEFAULT_CORS)

        return obj


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
    

def __fill_default_value(obj, key, default_value):
    """
    Fill Default value if key does not exists on object

    Args:
        obj: object to fill with default_value
        key: key that will be filled if nonexistent
        default_value: default_value value to be filled
    """
    if key not in obj:
        obj[key] = default_value
