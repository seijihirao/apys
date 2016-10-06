"""
Add a new hero to our rpg
"""
def post(req, api):
    """
    This endpoint will not work on dev, 
    try running it with `apy -s --config=prod`

    Input:
        name: string
        class: string
        
    Output:
        string
    """
    try:
        api.debug(req.params['name'] + ' - ' + req.params['class'], to='hero')
        return 'Success'
    except Exception as ex:
        api.error('An error ocurred while adding hero: ' + req.params['name'] + ' - ' + req.params['class'], ex=ex)
        return 'Error'