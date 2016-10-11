import json, os

def init():
    """
    Initiate project folders with sample config and readme
    """

    #folders
    dirs = [
        'config',
        'endpoints',
        'utils'
    ]
    _createDirs(dirs)

    #configs
    _writeConfigFile('prod', {
        'server': {
            'port': 80,
            'cors': False
        },
        'log': {
            'file': {
                'debug': '/var/logs/apys/debug.log',
                'debug': '/var/logs/apys/error.log'
            },
            'color': False
        }
    })

    _writeConfigFile('dev', {
        'server': {
            'port': 8080,
            'cors': "*"
        }
    })

    #readme
    with open('./README.md', 'w') as outfile:
        outfile.write(readme)
    
def _createDirs(directories):
    for directory in directories:
        if not os.path.exists('./' + directory):
            os.makedirs(directory)


def _writeConfigFile(file, obj):
    with open('./config/' + file + '.json', 'w') as outfile:
        json.dump(obj, outfile, indent=4)

readme = """# MY PROJECT

My project description

## LANGUAGE
[Python >= 3.4.2](https://docs.python.org/3/)

## LIBRARIES
* [apys](https://github.com/seijihirao/apys) - Backend restful framework

---

## RUNNING

```
$ apys -s
```

## TESTING

```
$ apys -t
```
"""