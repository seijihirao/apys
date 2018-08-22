#!/usr/bin/env python
# -*- coding: utf-8 -*-

properties = {}

def init(api):
    """
    This will run when the server starts

    Args:
        api - api object
    """
    api.hello_world_message = api.config['test'] # get 'test' value from config json
    api.debug('App started')

def get(req, api):
    """
    This special function will run everytime a GET request is made

    Args:
        req - request object
        api - api object
    """
    req.hello_world_message += 'get!'
    api.debug('Get request success')
    
def post(req, api):
    """
    This special function will run everytime a GET request is made

    Args:
        req - request object
        api - api object
    """
    req.hello_world_message += 'post!'
    api.debug('Post request success')

def any(req, api):
    """
    This special function will run everytime a GET request is made

    Args:
        req - request object
        api - api object
    """
    req.hello_world_message = api.hello_world_message + ', in method '
    api.debug('Any request success')

def insert_hello(hello_world_message):
    """
    This is a custom function, and will be called only by you.
    It inserts the "Hello World""

    Args:
        hello_world_message
    
    Return:
        new hello_world_message
    """
    return 'HELLO WORLD!!! ' + hello_world_message