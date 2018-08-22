def post(req, api):
    """
    Add a new hero to our rpg

    This endpoint will not work on dev, 
    try running it with `apy -s --config=prod`

    Input:
        name: string
        class: string
        
    Output:
        string
    """
    try:
        api.debug(req.body['name'] + ' - ' + req.body['class'], to='hero')
        return 'Success'
    except Exception as ex:
        api.error('An error ocurred while adding hero: ' + req.body['name'] + ' - ' + req.body['class'], ex=ex)
        return 'Error'