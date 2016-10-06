# apys - v0.3
Wellcome to apys! A simple backend restful framework! 

## LANGUAGE
[Python >= 3.4.2](https://docs.python.org/3/)

## LIBRARIES
* [aiohttp](https://aiohttp.readthedocs.io/) - http client/server for asyncio

---

## INSTALATION
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


## INITIALIZATING PROJECT

```
$ apys --init
```

---

## USING

### DIRECTORIES
    /config - json configuration files
    /endpoints - backend endpoints
    /utils - helper script files  

### CONFIG
Here are the configuration files used in the app.
They will be send to the endpoint via param `api.config`

There are 3 special filenames:
* `prod.json` - The oficial configuration file 
* `dev.json` - The development configuration file
* `local.json` - The local configuration file (ignore in git)

You can also force it to use a configuration with the `--config` or `-c` option:
```
$ apys -s --config=my_config
```

>Note: If no config file is choosen, they will work as following: the api tries to load `local.json`, then `dev.json`, then `prod.json`

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
        "port": "int //default=8888",
        "cors": "string or false //default=false"
    },
    "(...)": "(...) //you can add any other key and access it via `api.config['my_key']`"
}
```

### ENDPOINTS
This will be your main dev dir

All files added here will be an endpoint automatically

i.e.: the file `endpoints/hello/world.py` will generate an endpoint `/hello/world`

The file's code will be the following:
```python

utils = [
    '[util1]',
    '[util2]'
]

def [method](req, api):
    [process]
``` 

Where `[method]` is the http request type:
* post
* get
* put
* delete
* head
* options
* default - executed when a request is made for any of the above, but it is not implemented 

`[process]` is what you wan the endpoint to do (your code) 

`[util1]` and `[util2]` are the *utils* scripts (without `.py`)

`req` is *aiohttp*'s request, [documentation](http://aiohttp.readthedocs.io/en/stable/web_reference.html#request)

> `req` has the `params` property to read the request body 

`api` is the object that contains all api functionalities:
* config - Configuration dictionary used in the actual scope
* debug - function to log messages
* error - function to log errors

### UTILS

Python files with reusable code, to be called on endpoints.

It will be a normal cod, but with some special funcions:

init(api)

    The function that will be executed on server startup
    Only one time.
    
`[method]`(req, api) - `[method]` being the type of http request
    
    The function that will be called before every request to the function with the same name on the endpoint.
    Any result should be stored on the variable `req`, because it is the only local variable on the request.
    
any(req, api)
    
    The function that will be executed before any request.
    Note: thids function will be executed before the later.

## EXAMPLE

Look at the `demos/` for examples:

1. `hello_world`: a simple hello world app, to learn the basics
2. `multiple_endpoints`: a simpler app that resembles more a final product
3. `log_to_file`: an example of logging in files

---

### STARTING THE SERVER

There are 2 ways to start the server

1. Execute `apys -s` from terminal on your root project folder (Recomended)

2. Call the method `start()` from module `apys.server` (Only recomended if you need to do something before starting the server)

---

## OBSERVATION

Both the framework and this page are in development, so, subjected to changes.

>Version previous to v0.1.0 vas called [pypolyback](https://github.com/seijihirao/pypolyback) and used python 2.