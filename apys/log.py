#!/usr/bin/env python
# -*- coding: utf-8 -*-

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class nocolors:
    HEADER = ''
    OKBLUE = ''
    OKGREEN = ''
    WARNING = ''
    FAIL = ''
    ENDC = ''
    BOLD = ''
    UNDERLINE = ''
    
def debug(api, message, to):
    """
    Publish a message to the global log publisher.
    
    Args:
        api: api object, implicity passed
        message: the log message
        to='default': where to write message (defined on config)
    """
    if api.config['log']['file']:
        with open(api.config['log']['file'][to], 'a') as f:
            print(message, file=f)
    else:
        print(message)
    
def error(api, message, to, ex):
    """
    Publish an error to the global log publisher.
    
    Args:
        api: api object, implicity passed
        message: the error message
        to='default': where to write message (defined on config)
        ex: the exception type (default=Exception)
    """
    if ex:
        message += '\n' + str(ex)

    message = api._bcolors.FAIL + message + api._bcolors.ENDC

    if api.config['log']['file']:
        with open(api.config['log']['file'][to], 'a') as f:
            print(message, file=f)
    else:
        print(message)