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
    return req.params['x'] ** req.params['power']