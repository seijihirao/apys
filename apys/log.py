#!/usr/bin/env python
# -*- coding: utf-8 -*-


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class NoColors:
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
        api: api object, implicitly passed
        message: the log message
        to: where to write message (defined on config)
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
        api: api object, implicitly passed
        message: the error message
        to: where to write message (defined on config)
        ex: the exception type (default=Exception)
    """
    if ex:
        message = '\n{}\n{}\n'.format(message, str(ex))

    message = '{}{}{}'.format(api.bcolors.FAIL, message, api.bcolors.ENDC)

    if api.config['log']['file']:
        with open(api.config['log']['file'][to], 'a') as f:
            print(message, file=f)
    else:
        print(message)
