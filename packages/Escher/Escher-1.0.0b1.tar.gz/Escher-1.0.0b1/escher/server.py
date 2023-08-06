# -*- coding: utf-8 -*-

from escher.ko_server import koHandler
from escher.plots import Builder

import os, subprocess
from os.path import join
import tornado.ioloop
from tornado.web import RequestHandler, asynchronous, HTTPError, Application
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
import tornado.escape
from tornado.options import define, options, parse_command_line
import json
import re
from jinja2 import Environment, PackageLoader
from mimetypes import guess_type

# set up jinja2 template location
env = Environment(loader=PackageLoader('escher', 'templates'))

# set directory to server
directory = os.path.abspath(os.path.dirname(__file__)).strip(os.pathsep)
directory = re.sub(r'escher$', '', directory)
NO_CACHE = True
PORT = 7778
PUBLIC = False

def run(port=PORT, public=PUBLIC):
    global PORT
    global PUBLIC
    PORT = port
    PUBLIC = public
    print 'serving directory %s on port %d' % (directory, PORT)
    application.listen(port, None if public else "localhost")
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print "bye!"

def stop():
    tornado.ioloop.IOLoop.instance().stop()

class BaseHandler(RequestHandler):
    def serve_path(self, path):
        # make sure the path exists
        if not os.path.isfile(path):
            raise HTTPError(404)
        # serve it
        with open(path, "rb") as file:
            data = file.read()
        # set the mimetype
        self.set_header("Content-Type", guess_type(path, strict=False)[0])
        self.serve(data)
        
    def serve(self, data):
        if (NO_CACHE):
            self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.write(data)
        self.finish()

class IndexHandler(BaseHandler):
    def get(self):
        template = env.get_template('index.html')
        data = template.render()
        self.set_header("Content-Type", "text/html")
        self.serve(data)
  
class BuilderHandler(BaseHandler):
    @asynchronous
    @gen.engine
    def get(self, dev_path, offline_path, kind, path):
        # builder vs. viewer & dev vs. not dev
        js_source = ('dev' if (dev_path is not None) else
                     ('local' if (offline_path is not None) else
                      'web'))
        enable_editing = (kind=='builder')
        
        # Builder options
        builder_kwargs = {}
        for a in ['starting_reaction', 'model_name', 'map_name', 'map_json']:
            args = self.get_arguments(a)
            if len(args)==1:
                builder_kwargs[a] = args[0]

        # make the builder
        builder = Builder(safe=True, **builder_kwargs)
            
        # display options
        display_kwargs = {'minified_js': True,
                          'scroll_behavior': 'pan',
                          'menu': 'all'}
        # keyword
        for a in ['menu', 'scroll_behavior', 'minified_js']:
            args = self.get_arguments(a)
            if len(args)==1:
                display_kwargs[a] = args[0]

        # get the html
        html = builder._get_html(js_source=js_source, enable_editing=enable_editing,
                                 enable_keys=True, html_wrapper=True, fill_screen=True,
                                 height='100%', **display_kwargs)
        
        self.set_header("Content-Type", "text/html")
        self.serve(html)
        
class LibHandler(BaseHandler):
    def get(self, path):
        full_path = join(directory, 'escher', 'lib', path)
        if os.path.isfile(full_path):
            path = full_path
        else:
            raise HTTPError(404)
        self.serve_path(path)

class StaticHandler(BaseHandler):
    def get(self, path):
        path = join(directory, 'escher', path)
        print 'getting path %s' % path
        self.serve_path(path)
        
settings = {"debug": "False"}

application = Application([
    (r".*/knockout-map/(.*)", koHandler),
    (r".*/lib/(.*)", LibHandler),
    (r".*/(fonts/.*)", LibHandler),
    (r".*/(js/.*)", StaticHandler),
    (r".*/(css/.*)", StaticHandler),
    (r".*/(resources/.*)", StaticHandler),
    (r"/(dev/)?(offline/)?(builder|viewer)(.*)", BuilderHandler),
    (r".*/(map_spec.json)", StaticHandler),
    (r".*/(escher[^/]+js)", LibHandler),
    (r"/", IndexHandler),
], **settings)
 
if __name__ == "__main__":
    # define port
    define("port", default=PORT, type=int, help="Port to serve on.")
    define("public", default=PUBLIC, type=bool,
           help=("If False, listen only on localhost. If True, listen on "
                 "all available addresses."))
    parse_command_line()
    run(port=options.port, public=options.public)
