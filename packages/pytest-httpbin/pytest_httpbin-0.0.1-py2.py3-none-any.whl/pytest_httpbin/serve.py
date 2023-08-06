import os
import sys
import threading
import ssl
import tempfile
from wsgiref.simple_server import WSGIServer, make_server
from six import BytesIO
from six.moves.urllib.parse import urljoin

CERT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'certs')


class SecureWSGIServer(WSGIServer):

    def finish_request(self, request, client_address):
        """
        Negotiates SSL and then mimics BaseServer behavior.
        """
        ssock = ssl.wrap_socket(
            request,
            keyfile=os.path.join(CERT_DIR, 'key.pem'),
            certfile=os.path.join(CERT_DIR, 'cert.pem'),
            server_side=True
        )
        self.RequestHandlerClass(ssock, client_address, self)
        # WSGIRequestHandler seems to close the socket for us.
        # Thanks, WSGIRequestHandler!!


class Server(threading.Thread):
    """
    HTTP server running a WSGI application in its own thread.
    """

    def __init__(self, host='127.0.0.1', port=0, application=None, **kwargs):
        self.app = application
        self._server = make_server(host, port, self.app, **kwargs)
        self.host = self._server.server_address[0]
        self.port = self._server.server_address[1]
        self.protocol = 'http'

        super(Server, self).__init__(
            name=self.__class__,
            target=self._server.serve_forever)

    def __del__(self):
        self.stop()

    def __add__(self, other):
        return self.url + other

    def stop(self):
        self._server.shutdown()

    @property
    def url(self):
        return '{0}://{1}:{2}'.format(self.protocol, self.host, self.port)

    def join(self, url, allow_fragments=True):
        return urljoin(self.url, url, allow_fragments=allow_fragments)


class SecureServer(Server):
    def __init__(self, host='127.0.0.1', port=0, application=None, **kwargs):
        kwargs['server_class'] = SecureWSGIServer
        super(SecureServer, self).__init__(host, port, application, **kwargs)
        self.protocol = 'https'
