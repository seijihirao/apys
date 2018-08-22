def post(req, api):
    """
    Append a story to our rpg

    Input:
        content: string
        
    Output:
        string
    """
    api.debug(req.body['content'])
    return 'Success'