#!/usr/bin/env python
# encoding: utf-8
# """
# ActionLogManager.py
#
# Created by mikepk on 2009-11-30.
# Copyright (c) 2009 Michael Kowalchik. All rights reserved.
# """

import sys
import os
import unittest

from webob import Request, Response
from app.models.LogEntry import LogEntry

class ActionLogManager:
    '''WSGI applications to handle creating a simple http action log. Tracks via Sessions.'''
    def __init__(self,application=None):
        if application:
            self.application = application
        else:
            # no pipeline so just generate a generic response
            self.applicaion = Response()

    def __call__(self,environ,start_response):
        req = Request(environ)
        # check if the browser has a cookie with a session_id
        # load the session from the session_id
        try:
            session_id = environ['session'].session_id
        except (KeyError, IOError):
            session_id = 0

        # for key in environ.keys():
        #     print '''%-30s %-30s''' % (key, environ[key])

        log = LogEntry()
        log.session_id = session_id
        try:
            log.request_uri = environ['PATH_INFO']
            log.ip_address = environ['REMOTE_ADDR']
            if req.params:
                log.form_vars = str(req.params)
            else:
                log.form_vars = ''

            log.save()
        except KeyError:
            pass
        resp = req.get_response(self.application)

        return resp(environ, start_response)

class ActionLogManagerTests(unittest.TestCase):
    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()