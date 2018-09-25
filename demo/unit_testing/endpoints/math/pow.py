def post(req, api):
    """
    Powers the first number by the second

    Args:
        x - Number
        power - Number
    
    Return:
        result of the power
    """
    if 'x' not in req.body:
        raise api.web.HTTPUnprocessableEntity(reason='Query missing "x" argument')
    if 'power' not in req.body:
        raise api.web.HTTPUnprocessableEntity(reason='Query missing "power" argument')
    return req.body['x'] ** req.body['power']