def post(req, api):
    """
    Powers the first number by the second

    Args:
        x - Number
        power - Number
    
    Return:
        result of the power
    """
    print(req)
    return req.body['x'] ** req.body['power']