def post(req, api):
    """
    Sums 2 numbers

    Args:
        x - Number
        y - Number
    
    Return:
        sum of both
    """
    return req.body['x'] + req.body['y']