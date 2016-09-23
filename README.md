# APY - v0.1
Wellcome to APY! A simple backend restful framework! 

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
    * `pip install apy`
    
---


## INITIALIZATING PROJECT

```
$ apy --init
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

>Note: They really work as following: the api tries to load `local.json`, then `dev.json`, then `prod.json`. So in the oficial release you will only have `prod.json`

The current config special properties are the following:
```json
{
    "log": bool, //optional. default=False
    "server": {
        "port": int, //optional. default=8888
        "cors": string or False //optional. default=False
    },
    "mail": {
        "host": string,
        "port": int, //optional. default=25 or 587 for TLS 
        "tls": bool, //optional. default=False
        "username?": string, //optional. no default
        "password?": string //optional. no default
    }
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

> `req` has the `param` property to read the request body 

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

Look at the `demos/` for examples

---

### STARTING THE SERVER

There are 2 ways to start the server

1. Execute `apy -s` from terminal on your root project folder (Recomended)

2. Call the method `start()` from module `apy.server` (Only recomended if you need to do something before starting the server)

---

## OBSERVATION

Both the framework and this page are in development, so, subjected to changes.

>Version previous to v0.1.0 vas called [pypolyback](https://github.com/seijihirao/pypolyback) and used python 2.