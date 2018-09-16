#!/usr/bin/env python
# -*- coding: utf-8 -*-


def post(req, api):
    """
    Verify if post body has 'role' attribute
    """
    if 'role' not in req.body:
        raise api.web.HTTPUnprocessableEntity(reason='Body missing "role" argument')
