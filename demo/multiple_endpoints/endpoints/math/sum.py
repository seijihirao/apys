"""
Sums 2 numbers
"""

def post(req, api):
    """
    Args:
        x - Number
        y - Number
    
    Return:
        sum of both
    """
    return req.param['x'] + req.param['y']