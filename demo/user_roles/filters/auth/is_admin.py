#!/usr/bin/env python
# -*- coding: utf-8 -*-


def post(req, api):
    if not req.body['role'] == 'admin':
        raise api.web.HTTPUnauthorized()