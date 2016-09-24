"""
Start the server with `apys -s`
"""

utils = [
    'hello'
]

def get(req, api):
    """
    Go to your browser and open `localhost:8888/hello/world`
    It should display a page with the message `HELLO WORLD!!! Success on local, in method get!`
    
    Output:
        string
    """
    
    result = api.hello.insert_hello(req.message)
    
    return result

def post(req, api):
    """
    Make a post request to `localhost:8888/hello/world`
    With the body `{"message": "my_message"}
    It should return `{"request": "my_message", "result":"HELLO WORLD!!! Success on local, in method post!"}`
    
    Input:
        message: string
        
    Output:
        message: string
        result: string
    """
    
    message = req.param['message']

    return {
        'request': message,
        'result': api.hello.insert_hello(req.message)
    }