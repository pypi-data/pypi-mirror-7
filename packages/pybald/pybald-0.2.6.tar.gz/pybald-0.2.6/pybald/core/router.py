#!/usr/bin/env python
# encoding: utf-8

import unittest
import re
from webob import Request, Response, exc
from routes import Mapper, request_config, URLGenerator
# handle Mako's top level lookup
from mako import exceptions
import project
from pybald.util import camel_to_underscore
import logging
console = logging.getLogger(__name__)

# load the controllers from the project defined path
# change this to passed in value to the Router. That way it can
# be project specific
# Load the project specified in the project file
my_project = __import__(project.package_name, globals(), locals(),
                                                            ['app'], -1)
# add the project package name to the global symbol table
# to avoid any double imports
globals()[project.package_name] = my_project
# import all controllers
__import__('{project}.app'.format(project=project.package_name),
                      globals(), locals(), ['controllers'], -1)


class Router(object):
    # class method match patterns
    has_underscore = re.compile(r'^\_')
    controller_pattern = re.compile(r'(\w+)_controller')

    # add controllers=None to the call sig and use that for controller
    # loading
    def __init__(self, application=None, routes=None):
        '''
        Create a Router object, the core of the pybald framework.

        :param application:  WSGI application/middleware that is to be
                             *wrapped* by the router in the web app pipeline.

        :param routes: A routing function that takes a mapper (for parsing and
                       matching urls).

        '''
        if routes is None:
            raise Exception("Route mapping is required. Please pass in a "
                            "routing function to the router as and arg to "
                            "Router init. "
                            "The routing function takes a routes mapper "
                            "object and uses it to contruct url mappings. "
                            "See pybald docs for more details.")

        self.controllers = {}
        # initialize Router
        # explicit turns off route memory and 'index' for
        # default action
        self.map = Mapper(explicit=False)
        routes(self.map)
        # debug print the whole URL map
        console.debug(str(self.map))
        self.load()

    def load(self):
        '''
        Loads controllers from PROJECT.app.controllers. It does some text
        munging to change the camel-case class names into
        underscore-separated url like names. (HomeController)

        All controller candidates are loaded into a hash to look up
        the matched "controller" urlvar against.

        The _controller suffix is removed from the module name for the url
        route mapping table (so controller="home" matches home_controller).

        against and the routes regex is initialized with a list of controller
        names.

        Called only once at the start of a pybald application.
        '''

        controller_names = []
        for controller in my_project.app.controllers.__all__:
            controller_name = camel_to_underscore(controller)
            try:
                controller_path_name = self.controller_pattern.search(
                                                    controller_name).group(1)
            except AttributeError:
                controller_path_name = controller_name
            controller_names.append(controller_path_name)
            # self.controllers holds paths to map to modules and controller
            # names
            self.controllers[controller_path_name] = getattr(my_project.app.controllers,
                                                                    controller)

        # register the controller module names
        # with the mapper, creates the internal regular
        # expressions
        self.map.create_regs(controller_names)

    def __repr__(self):
        return "<Pybald Router Object>"

    def get_handler(self, urlvars=None):
        controller_name = urlvars["controller"]
        action_name = urlvars["action"]

        #methods starting with underscore can't be used as actions
        if self.has_underscore.match(action_name):
            raise exc.HTTPNotFound("Invalid Action")

        for key, value in urlvars.items():
            console.debug(u'''{0}: {1}'''.format(key, value))

        try:
            # create controller instance from controllers dictionary
            # using routes 'controller' returned from the match
            controller = self.controllers[controller_name]()
            handler = getattr(controller, action_name)
        # only catch the KeyError/AttributeError for the controller/action
        # search
        except (KeyError, AttributeError):
            raise exc.HTTPNotFound("Missing Controller or Action")

        return controller, handler

    def __call__(self, environ, start_response):
        '''
        A Router instance is a WSGI app. It accepts the standard WSGI call
        signature of ``environ``, ``start_response``.

        The Router has a few jobs. First it uses the Routes package to
        compare the requested path to available url patterns that have
        been loaded and passed to the Router upon init.

        Router is the most *framework-like* component of Pybald. In addition to
        dispatching urls to controllers, it also allows 'method override'
        behavior allowing other HTTP methods to be invoked such as ``put`` and
        ``delete`` from web clients that don't support them natively.
        '''
        req = Request(environ)
        req.errors = 'ignore'
        #method override
        #===============
        # for REST architecture, this allows a POST parameter of _method
        # to be used to override POST with alternate HTTP verbs (PUT, DELETE)
        if req.POST:
            override_method = req.POST.pop('_method', None)
            if override_method is not None:
                environ['REQUEST_METHOD'] = override_method.upper()
                console.debug("Changing request method to {0}".format(
                                                        environ["REQUEST_METHOD"]))

        results = self.map.routematch(environ=environ)
        if results:
            match, route = results[0], results[1]
        else:
            match = route = None

        url = URLGenerator(self.map, environ)
        config = request_config()

        # Your mapper object
        config.mapper = self.map
        # The dict from m.match for this URL request
        config.mapper_dict = match
        config.host = req.host
        config.protocol = req.scheme
        # host_port
        # defines the redirect method. In this case it generates a
        # Webob Response object with the location and status headers
        # set
        config.redirect = lambda url: Response(location=url, status=302)

        environ['wsgiorg.routing_args'] = ((url), match)
        environ['routes.route'] = route
        environ['routes.url'] = url
        environ['pybald.router'] = self

        # Add pybald extension
        # the pybald.extension is a dictionary that can be used to copy state
        # into a running controller (usually handled by the @action decorator)
        environ.setdefault('pybald.extension', {})["url_for"] = url

        # debug print messages
        console.debug(''.join(['=' * 20, ' ', req.path_qs, ' ', '=' * 20]))
        console.debug('Method: {0}'.format(req.method))

        # use routes to match the url to a path
        # urlvars will contain controller + other non query string
        # URL data. Middleware above this can override and set urlvars
        # and the router will use those values.
        # TODO: allow individual variable overrides?
        urlvars = environ.get('urlvars', match) or {}

        # lifted from Routes middleware, handles 'redirect'
        # routes (map.redirect)
        if route and route.redirect:
            route_name = '_redirect_{0}'.format(id(route))
            location = url(route_name, **match)
            return Response(location=location,
                            status=route.redirect_status
                            )(environ, start_response)

        req.urlvars = urlvars
        environ['urlvars'] = urlvars

        if urlvars:
            controller, handler = self.get_handler(urlvars)
        # No URL vars means nothing matched in the mapper function
        else:
            raise exc.HTTPNotFound("No URL match")

        try:
            # call the action we determined from the mapper
            return handler(environ, start_response)
        # This is a mako 'missing template' exception
        except exceptions.TopLevelLookupException:
            raise exc.HTTPNotFound("Missing Template")
        # except Exception as e:
        # All other program errors get re-raised
        # e.g. a 500 server error
        # raise e


class routerTests(unittest.TestCase):
    def setUp(self):
        pass

    def testMap(self):
        router = Router()

    def testRoute(self):
        pass

    def testLoad(self):
        pass

if __name__ == '__main__':
    unittest.main()
