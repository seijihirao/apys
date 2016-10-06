"""
Append a story to our rpg
"""

def post(req, api):
    """
    Input:
        content: string
        
    Output:
        string
    """
    api.debug(req.params['content'])
    return 'Success'