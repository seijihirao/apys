import os
import json

def load(scope='default'):
    """
    loads choosen config file
    if scope is not define loads default (first try `local`, then `dev` and last `prod`)
    
    Args:
        scope: config file, without `.json`
    """
    
    if scope is 'default':
        for scope in ['local', 'dev', 'prod']:
            path = 'config/{}.json'.format(scope)
            if os.path.exists(path):
                config = load(scope)
                if config:
                    return config
                    
    else:
        path = 'config/{}.json'.format(scope)
        if os.path.exists(path):
            with open(path, 'r') as config:
                obj = json.loads(config.read())
                obj['scope'] = scope

                #Default Values

                _fillDefaultValue(obj, 'log', False)

                _fillDefaultValue(obj, 'server', {})
                _fillDefaultValue(obj['server'], 'port', 8888)
                _fillDefaultValue(obj['server'], 'cors', False)

                return obj
    raise EnvironmentError('No config file found')

def _fillDefaultValue(obj, key, default):
    """
    Fill Default value if key does not exists on object

    Args:
        obj: object to fill with default value
        key: key that will be filled if inexistent
        default: default value to be filled
    """
    if key not in obj:
        obj[key] = default

#shortcut to current config
value = load()