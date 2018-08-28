"""
Start the server with `apys -s`
"""

filters = [
    'hello_world'
]

def get(req, api):
    """
    Go to your browser and open `localhost:8888/hello/world`
    It should display a page with the message `HELLO WORLD!!! Success on local, in method get!`
    
    
    Input:
        message: string
    Output:
        string
    """


    message = req.query['message']

    result = req.hello_world_message
    result += ' - your message was: '
    result += message if message else 'None'
    
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
    
    message = req.body['message']

    return {
        'request': message,
        'result': req.hello_world_message
    }