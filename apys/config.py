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
        obj = __get_env(json.loads(config.read()))
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


def __get_env(obj):
    """
    gets value from environment variable if `$` is preceded on value

    i.e.:

    ```
    {
        "key": "$API_KEY"
        "db_url": "$DB|localhost"
        "port": "$PORT|8080|int"
    }
    ```

     * `key` will now have the value of the `API_KEY` environment variable, or '$API_KEY' if env var does not exists
     * `db_url` will now have the value of the `DB` environment variable, or 'localhost' if env var does not exists
     * `port` will now have the value of the `PORT` environment variable, or 8080 if env var does not exists


    :param obj: object to format
    :return: formatted object
    """
    for key in obj:
        if type(obj[key]) == dict:
            obj[key] = __get_env(obj[key])
        elif type(obj[key]) == str and obj[key][0] == '$':
            env_var = obj[key][1:]

            # Case no default value
            if env_var.count('|') == 0:
                if env_var in os.environ:
                    obj[key] = os.environ[env_var]

            # Case default value
            if env_var.count('|') == 1:
                env_var, default_val = env_var.split('|')
                if env_var in os.environ:
                    obj[key] = os.environ[env_var]
                else:
                    obj[key] = default_val

            # Case default value with type
            if env_var.count('|') == 2:
                env_var, default_val, default_type = env_var.split('|')
                if env_var in os.environ:
                    obj[key] = os.environ[env_var]
                else:
                    obj[key] = eval(default_type)(default_val)
    return obj
