#!/usr/bin/env python
# encoding: utf-8

import unittest

from functools import wraps
from pybald.core.templates import render as render_view

from webob import Request, Response
from webob import exc
import re
from pybald.util import camel_to_underscore
from routes import redirect_to
import project
import hashlib
import base64
import json
import random

controller_pattern = re.compile(r'(\w+)Controller')

# a no-op placeholder
noop_func = lambda *pargs, **kargs: None


def get_template_name(instance, method_name):
    # this code defines the template id to match against
    # template path = controller name + '/' + action name (except in the case
    # of) index if the template is specified as part of the processed object
    # return that, short circuiting any other template name processing
    # This form may removed later, considered a candidate for deprecation
    t = getattr(instance, 'template_id', None)
    if t:
        return t
    # build a default template name if one isn't explicitly set
    try:
        template_root_name = camel_to_underscore(
                  controller_pattern.search(instance.__class__.__name__
                                       ).group(1))
    except AttributeError:
        template_root_name = ''
    return "/".join(filter(lambda x: x != '', [template_root_name, method_name]))


# action / method decorator
def action(method):
    '''
    Decorates methods that are WSGI apps to turn them into pybald-style actions.

    :param method: A method to turn into a pybald-style action.

    This decorator is usually used to take the method of a controller instance
    and add some syntactic sugar around it to allow the method to use WebOb
    Request and Response objects. It will work with any method that
    implements the WSGI spec.

    It allows actions to work with WebOb request / response objects and handles
    default behaviors, such as displaying the view when nothing is returned,
    or setting up a plain text Response if a string is returned. It also
    assigns instance variables from the ``pybald.extension`` environ variables
    that can be set from other parts of the WSGI pipeline.

    This decorator is optional but recommended for making working
    with requests and responses easier.
    '''
    # the default template name is the controller class + method name
    # the method name is pulled during decoration and stored for use
    # in template lookups
    template_name = method.__name__
    # special case where 'call' or 'index' use the base class name
    # for the template otherwise use the base name
    if template_name in ('index', '__call__'):
        template_name = ''

    @wraps(method)
    def action_wrapper(self, environ, start_response):
        req = Request(environ)
        # add any url variables as members of the controller
        for varname, value in req.urlvars.items():
            # Set the controller object to contain the url variables
            # parsed from the dispatcher / router
            setattr(self, varname, value)

        # add the pybald extension dict to the controller
        # object
        for key, value in req.environ.setdefault('pybald.extension', {}).items():
            setattr(self, key, value)

        # TODO: fixme this is a hack
        setattr(self, 'request', req)
        setattr(self, 'request_url', req.url)

        # set pre/post/view to a no-op if they don't exist
        pre = getattr(self, '_pre', noop_func)
        post = getattr(self, '_post', noop_func)

        # set the template_id for this request
        self.template_id = get_template_name(self, template_name)

        # The response is either the controllers _pre code, whatever
        # is returned from the controller
        # or the view. So pre has precedence over
        # the return which has precedence over the view
        resp = (pre(req) or
                 method(self, req) or
                 render_view(template=self.template_id,
                             data=self.__dict__ or {}))
        # if the response is currently a string
        # wrap it in a response object
        if isinstance(resp, basestring):
            resp = Response(body=resp, charset="utf-8")
        # run the controllers post code
        post(req, resp)
        return resp(environ, start_response)
    return action_wrapper


def caching_pre(keys, method_name, prefix=''):
    '''Decorator for pybald _pre to return cached responses if available.'''
    if keys is None:
        keys = []

    def pre_wrapper(pre):
        def replacement(self, req):
            val = ":".join([prefix] + [str(getattr(self, k, '')) for
                        k in keys] + [method_name])
            self.cache_key = base64.urlsafe_b64encode(hashlib.md5(val).digest())
            resp = project.mc.get(self.cache_key)
            if resp:
                return resp
            return pre(req)
        return replacement
    return pre_wrapper


def caching_post(time=0):
    '''Decorator for pybald _post to cache/store responses.'''
    def post_wrapper(post):
        def replacement(self, req, resp):
            post(req, resp)
            # only cache 2XX or 4XX responses
            if (200 <= resp.status_code < 300) or (400 <= resp.status_code < 500):
                if 'X-Cache' not in resp.headers:
                    resp.headerlist.append(('X-Cache', 'MISS'))
                    project.mc.set(self.cache_key, resp, time)
                else:
                    resp.headers['X-Cache'] = 'HIT'
        return replacement
    return post_wrapper

# regenerate a content_cache_prefix on every reload so that content will
# be force loaded after any full application restart
# This provides a way to cache static content for the duration of the
# application lifespan.
content_cache_prefix = hex(random.randrange(0, 2 ** 32 - 1))


# memcache for actions
def action_cached(prefix=content_cache_prefix, keys=None, time=0):
    '''
    Wrap actions and return pre-generated responses when appropriate.
    '''
    if keys is None:
        keys = []

    def cached_wrapper(my_action_method):
        @wraps(my_action_method)
        def replacement(self, environ, start_response):
            # bind newly wrapped methods to self
            self._pre = caching_pre(keys,
                                    my_action_method.__name__,
                                    prefix=prefix)(self._pre
                                        ).__get__(self, self.__class__)
            self._post = caching_post(time)(self._post
                                        ).__get__(self, self.__class__)
            return my_action_method(self, environ, start_response)
        # don't enable caching if requested
        if project.DISABLE_STATIC_CONTENT_CACHE:
            return my_action_method
        return replacement
    return cached_wrapper


class BaseController(object):
    '''Base controller that includes the view and a default index method.'''

    def _pre(self, req):
        pass

    def _post(self, req, resp):
        pass

    def _redirect_to(self, *pargs, **kargs):
        '''Redirect the controller'''
        return redirect_to(*pargs, **kargs)

    def _not_found(self, text=None):
        '''Raise the 404 http_client_error exception.'''
        raise exc.HTTPNotFound(text)

    def _status(self, code):
        '''Raise an http_client_error exception using a specific code'''
        raise exc.status_map[int(code)]

    def _JSON(self, data, status=200):
        '''Return JSON object with the proper-ish headers.'''
        res = Response(body=json.dumps(data),
            status=status,
            # wonky Cache-Control headers to stop IE6 from caching content
            cache_control="max-age=0,no-cache,no-store,post-check=0,pre-check=0",
            expires="Mon, 26 Jul 1997 05:00:00 GMT",
            content_type="application/json",
            charset='UTF-8'
            )
        return res

    def _view(self, data=None):
        '''
        This method is a shim between the old view rendering code and the new
        template rendering methods. It should not be used and is present only
        to maintain backward compatibility.

        This is targeted for deprecation.
        '''
        if data is None:
            data = self.__dict__ or {}
        template_name = data.pop('template_id', None) or getattr(self, 'template_id', None)
        return render_view(template=template_name,
                             data=data)

class BaseControllerTests(unittest.TestCase):
    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()
