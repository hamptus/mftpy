from wsgiref.util import request_uri, application_uri, shift_path_info
from wsgiref.simple_server import make_server
import datetime
from urlparse import parse_qs
from paste import httpserver
from webob import Request, Response
from mbr import Mbr


class RequestHandler(object):

    template = None

    def __init__(self):
        #self.environ = environ
        #self.start_response = start_response
        self.response = Response()
        self.response.status = 200
        self.response.content_type = 'text/html'
        self.response.body = '<html><body>It works!</body></html>'

    def __call__(self, environ, start_response):
        self.request = Request(environ)
        self.start_response = start_response
        if self.request.method == 'GET':
            return self.get()
    
    def get(self):
        return self.response(self.request.environ, self.start_response)

class MbrHandler(RequestHandler):
    def get(self):
        mbr = Mbr(open('/dev/sda', 'rb').read(512))
        self.response.body = "<html><body>"
        self.response.body += mbr.partition1.get_type()
        self.response.body += "</body></html>"
        return self.response(self.request.environ, self.start_response)

urls = {
    '/mbr/': MbrHandler,
    '/': MbrHandler,
    '/static/', StaticHandler,
}
class UrlRouter(object):
    def __call__(self, environ, start_response):
        request = Request(environ)
        handler = urls[request.path]
        return handler().__call__(environ, start_response)
        

httpserver.serve(UrlRouter(), host='127.0.0.1', port=8080)

