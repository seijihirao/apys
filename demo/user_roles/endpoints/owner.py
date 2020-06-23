filters = [
    'check_params',
    'auth.is_owner'
]


def post(req, api):
    """
    return success if user has rights to access server
    user needs to have role owner or admin

    Input:
        role: string

    Output:
        result: string
    """

    return {
        'result': 'success'
    }
