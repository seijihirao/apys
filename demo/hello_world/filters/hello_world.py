#!/usr/bin/env python
# -*- coding: utf-8 -*-

def get(req, api):
    """
    This special function will run everytime a GET request is made

    Args:
        req - request object
        api - api object
    """
    if('message' not in req.query):
        raise api.web.HTTPUnprocessableEntity(reason='Query missing "message" argument')
    req.hello_world_message += 'get!'
    api.debug('Get request success')
    
def post(req, api):
    """
    This special function will run everytime a POST request is made

    Args:
        req - request object
        api - api object
    """
    if('message' not in req.body):
        raise api.web.HTTPUnprocessableEntity(reason='Body missing "message" argument')
    req.hello_world_message += 'post!'
    api.debug('Post request success')

def any(req, api):
    """
    This special function will run everytime any request is made

    Args:
        req - request object
        api - api object
    """
    req.hello_world_message = api.hello_world_message + ', in method '
    api.debug('Any request success')