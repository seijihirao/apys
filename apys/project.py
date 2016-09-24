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
        'log': False,
        'server': {
            'port': 80,
            'cors': False
        }
    })

    _writeConfigFile('dev', {
        'log': True,
        'server': {
            'port': 8888,
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
[Python](https://docs.python.org/3/)

## LIBRARIES
* [apys](https://github.com/seijihirao/apys) - Backend restful framework

---

## RUNNING

```
$ apys -s
```
"""