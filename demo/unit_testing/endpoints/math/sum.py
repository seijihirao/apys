def post(req, api):
    """
    Sums 2 numbers

    Args:
        x - Number
        y - Number
    
    Return:
        sum of both
    """
    if 'x' not in req.body:
        raise api.web.HTTPUnprocessableEntity(reason='Query missing "x" argument')
    if 'y' not in req.body:
        raise api.web.HTTPUnprocessableEntity(reason='Query missing "y" argument')
    return req.body['x'] + req.body['y']