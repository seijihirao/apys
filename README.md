# apys - v3.1
Wellcome to apys! A simple backend restful framework! 

## LANGUAGE
[Python >= 3.4.2](https://docs.python.org/3/)

## LIBRARIES
* [aiohttp](https://aiohttp.readthedocs.io/) - http client/server for asyncio

---

## INSTALLATION

1. Install python 3
    * Windows - [Link](https://www.python.org/download/releases/3.5/)
    * Ubuntu - `sudo apt-get install python`
    * Fedora - `sudo yum install python`
    * Arch - `sudo pacman -S python`
2. Install PIP - Python libraries manager
    * Windows - [Link](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pip)
    * Ubuntu - `sudo apt-get install pip`
    * Fedora - `sudo yum install pip`
    * Arch - `sudo pacman -S pip`
3. Install this framework using PIP
    * `pip install apys`
    
---


## INITIALIZING PROJECT

```
$ apys --init
```

---

## USING

### DIRECTORIES
    /config - json configuration files
    /endpoints - backend endpoints
    /filters - script files to execute before the endpoint  
    /utils - script files to execute when server starts

### CONFIG
Here are the configuration files used in the app.
They will be send to the endpoint via param `api.config`

There are 3 special file names:
* `prod.json` - The production configuration file 
* `dev.json` - The development configuration file
* `local.json` - The local configuration file (ignore in git)

You can also force it to use a configuration with the `--config` or `-c` option:
```
$ apys -s --config=my_config
```

>Note: If no config file is chosen, they will work as following: the api tries to load `local.json`, then `dev.json`, then `prod.json`

The current config special properties are the following:
```json
{
    "log": {
        "file": {
            "debug": "string or false //default=false. debug log file, false for sys.stdout", 
            "error": "string or false //default=false. debug error file, false for sys.stderr",
            "(...)": "string or false //optional. you can specify any other log file, but you will have to tell the `api.debug` function to use it"
        },
        "color": "bool //default=true"
    },
    "server": {
        "port": "int //default=8080",
        "cors": "string or false //default=false"
    },
    "utils": ["string //default=[]. list of utils in order to load"],
    "(...)": "(...) //you can add any other key and access it via `api.config['my_key']`"
}
```
You can also use environment variables
like `$PORT` (for `PORT` env var), and set a default value if no env var is found
like `$PORT|8080` or `$PORT|8080|int` (if type is needed)

### ENDPOINTS
This will be your main dev dir

All files added here will be an endpoint automatically

i.e.: the file `endpoints/hello/world.py` will generate an endpoint `/hello/world`

The file's code will be the following:
```python

filters = [
    'filter1',
    ['filter2', 'filter3']
]

def method(req, api):
    pass # process
``` 

Where `method` is the http request type:
* post
* get
* put
* delete
* head
* options
* default - executed when a request is made for any of the above, but it is not implemented 

`process` is what you wan the endpoint to do (your code) 

`filter1`, `filter2` and `filter3` are the *filters* scripts (without `.py`) executed before the endpoint is called

> If you put your filter inside an array the error they return will be returned only if ALL of them return some error 

`req` is *aiohttp*'s request, [documentation](http://aiohttp.readthedocs.io/en/stable/web_reference.html#request)

> `req`'s property `body` only works for json works as of now

`api` is the object that contains all api functionalities:
* config - Configuration dictionary used in the actual scope
* debug - function to log messages
* error - function to log errors

Also `api.web` contains `aiohttp.web`

### FILTERS

Code that will that will be called before every request.

`method`(req, api) - `method` being the type of http request
    
    The function that will be executed before every request to the function with the same name on the endpoint.
    Any result should be stored on the variable `req`, because it is the only local variable on the request.
    
always(req, api)
    
    The function that will be executed before any request.
    Note: this function will be executed before the other filters.

### UTILS

Python files special functionality.

It needs to be inside a dir and has some special files

## __init__.py

This file contains a function that will be called before initializing the api.

```python
def init(api):
    pass
```

    The function that will be executed on server startup
    Only one time.

> Useful for setting some api constants

## __cli__.py

This file contains a function that will add a commandline argument.

The util flags will be `--[util_name]` and `--[util_name_first_char]`

> util name is test, so flags should be `--test` and `-t`

```python
class CLI:
    def __init__(self, result):
        # See `parser.add_argument` doc for information on these
        self.action = 'store_true'
        self.default = False
        self.help = 'It makes everything shine'
        
        # store the result of user input
        self.result = result
    
    def start(self, api, endpoints):
        pass
 ```

## EXAMPLE

Look at the `demos/` for examples:

1. `hello_world`: a simple hello world app, to learn the basics
2. `calculator`: a simpler app that resembles more a normal product
3. `log_to_file`: an example of logging in files
4. `user_role`: an advanced example on filters
4. `unit_testing`: an advanced example on adding cli arguments

---

### STARTING THE SERVER

There are 2 ways to start the server

1. Execute `apys -s` from terminal on your root project folder (Recommended)

2. Call the method `start()` from module `apys.server`

---

## OBSERVATION

Both the framework and this page are in development, so, subjected to changes.

> Version previous to v0.1.0 vas called [pypolyback](https://github.com/seijihirao/pypolyback) and used python 2.
