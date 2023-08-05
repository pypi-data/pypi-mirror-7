#!/usr/bin/env python
# encoding: utf-8
import sys
import os

# mod_wsgi restricts stdout, so switch it to stderr
sys.stdout = sys.stderr

# find out where this module lives, set the project path accordingly
project_path,script_path = os.path.split(
                               os.path.dirname( os.path.realpath( __file__ ) ))

# add the project and pybald paths to the sitedir
# TODO: make pybald installable so this is unnecesary
import site
site.addsitedir(project_path)
import project
site.addsitedir(project.toplevel)

from pybald.core.router import Router
from pybald.core.errors import ErrorMiddleware
# from pybald.core.sessions import SessionManager
# from pybald.core.users import UserManager
# from pybald.core.pybald_logger import PybaldLogger

# Load the project specified in the project file
my_project = __import__(project.package_name, globals(), locals(),
                                                            ['app','wsgi'], -1)
# add the project package name to the global symbol table
globals()[project.package_name] = my_project
__import__('{project}.app'.format(project=project.package_name),
                      globals(), locals(), ['urls','models','controllers'], -1)

from pybald.core.db_middleware import DbMiddleware

# load the error controller so that the ErrorMiddleware
# has somewhere to route the request if an error occurs
# from quiz_site.app.models.session import Session
# from quiz_site.app.models.user import User


# The main application pipeline
# Include all WSGI middleware here. The order of
# web transaction will flow from the bottom of this list
# to the top, and then back out. The pybald Router
# should usually be the first item listed.
# ----------------------------------
app = Router(routes=my_project.app.urls.map)
# app = UserManager(app, user_class=User)
# app = SessionManager(app, session_class=Session)
app = DbMiddleware(app)
app = ErrorMiddleware(app, error_controller=None)
# ----------------------------------
#    ↑↑↑                  ↓↓↓
#    ↑↑↑                  ↓↓↓
#   Request              Response


# apache / mod_wsgi looks for 'application'
application = app

# called directly enable the interactive debugger
# requires python paste be installed
def main():
    '''A simple server startup if module is called directly'''
    # port = 8080
    # host = '0.0.0.0'
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--host", default="0.0.0.0",
                      dest="host",
                      help="host ip to run")
    parser.add_option("-p", "--port",
                      dest="port", default=8080,
                      help="the port to run on.")
    (options, args) = parser.parse_args()
    try:
        import paste
        from paste import httpserver
        # use this for the interactive debugger
        from paste.evalexception import EvalException
        # add the static server component
        from static_serve import static_serve
        my_app = static_serve(app, path='public')
        httpserver.serve(my_app, host=options.host, port=options.port)
        sys.exit(1)
    except ImportError:
        pass

    from wsgiref.simple_server import make_server
    # add the static server component
    from static_serve import static_serve
    my_app = static_serve(app, path='public')
    httpd = make_server(options.host, options.port, my_app)
    print "Serving on port {0}...".format(options.port)
    httpd.serve_forever()
    sys.exit(1)


#use when moduled called directly, runs internal webserver
if __name__ == '__main__':
    main()
