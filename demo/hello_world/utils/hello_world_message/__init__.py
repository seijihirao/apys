#!/usr/bin/env python
# -*- coding: utf-8 -*-

def init(api):
    """
    This will run when the server starts

    Args:
        api - api object
    """
    api.hello_world_message = api.config['test'] # get 'test' value from config json
    api.debug('App started')