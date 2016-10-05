"""
Powers the first number by the second
"""

def post(req, api):
    """
    Args:
        x - Number
        power - Number
    
    Return:
        result of the power
    """
    return req.param['x'] ** req.param['power']