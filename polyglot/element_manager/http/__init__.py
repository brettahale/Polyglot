'''
Polyglot HTTP server

| Public Functions:
| AbstractHandler Class
| register(handlers, subdomain=None, parent_dir=None)

:ivar AUTH_USER: The required HTTP user
:ivar AUTH_PASS: The required HTTP password
:ivar SERVER: The Tornado web server applicaiton.
'''
from basic_auth import basic_auth
import logging
import os
import threading
import tornado.web
import tornado.ioloop

DEFAULT_CONFIG = {'port': 8080, 'username': 'admin', 'password': 'admin'}
AUTH_USER = None
AUTH_PASS = None
PORT = None
SERVER = None
_THREAD = None
_LOGGER = logging.getLogger(__name__)


def load(pglot, user_config):
    ''' setup the http server '''
    # pylint: disable=global-statement, unused-argument
    global SERVER, _THREAD

    # set configuration
    config = DEFAULT_CONFIG
    config.update(user_config)
    set_config(config)

    # create server
    SERVER = tornado.web.Application([], {})
    SERVER.listen(PORT)


    # run server on a thread
    _THREAD = threading.Thread(target=run_server)
    _THREAD.daemon = True
    _THREAD.start()
    _LOGGER.info('Started HTTP server on port %d', PORT)

    _LOGGER.info('Loaded HTTP element')


def unload():
    ''' stops the http server '''
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_callback(lambda x: x.stop(), ioloop)
    _LOGGER.info('Unloaded HTTP element')


def get_config():
    """ Returns the element's configuration. """
    return {'password': AUTH_PASS, 'username': AUTH_USER, 'port': PORT}


def set_config(config):
    """ Updates the current configuration. """
    # pylint: disable=global-statement, unused-argument
    global AUTH_USER, AUTH_PASS, PORT

    # pull config settings
    PORT = config['port']
    AUTH_USER = config['username']
    AUTH_PASS = config['password']


def register(handlers=None, subdomain=None, parent_dir=None, urls=None):
    '''
    Register additional handlers to the server.

    :param handlers: List of handler classes to register.
    :param subdomain: The desired subdomain
    :param parent_dir: The directory under which all the handlers should be
                       placed
    :param urls: List of lists like [['path', Handler]].
                 Overwrites handlers input.
    '''
    # parse input
    if subdomain is None:
        subdomain = "[A-Za-z0-9.]*"
    else:
        subdomain = r'{}\.[A-Za-z0-9.]*'.format(subdomain)

    if parent_dir is None:
        parent_dir = ''
    else:
        parent_dir = '/{}'.format(parent_dir)

    # create proper URLSpec handlers and callback
    if not urls:
        def doc_url(handler):
            """ reads the url regexp from the handler's docstring. """
            docs = handler.__doc__
            pieces = docs.strip().split('\n\n')[0].split('\n')
            return ''.join([piece.strip() for piece in pieces])
        handlers = [tornado.web.URLSpec('{}{}'.format(parent_dir,
                                                      doc_url(handler)),
                                        handler)
                    for handler in handlers]
    else:
        handlers = urls

    def add_handler_callback(server, subdmn, hndls):
        """ add handler to server """
        server.add_handlers(subdmn, hndls)

    # schedule handler addition to next IOLoop iteration
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_callback(add_handler_callback, SERVER, subdomain, handlers)


def run_server():
    ''' run the tornado web server '''
    tornado.ioloop.IOLoop.instance().start()


def authenticate(username, password):
    '''
    Authenticate the credentials.

    :param username: Supplied username
    :param password: Supplied password
    '''
    if AUTH_USER is None:
        return True
    return username == AUTH_USER and password == AUTH_PASS


@basic_auth(authenticate)
class AbstractHandler(tornado.web.RequestHandler):
    ''' An abstract request handler with authentication '''
    def get(self):
        ''' Get handler '''
        self.write('Polyglot is Running')
        self.finish()

    def data_received(self, chunk):
        ''' Overwriting abstract method. '''
        pass


@basic_auth(authenticate)
class AuthStaticFileHandler(tornado.web.StaticFileHandler):
    """ Static file handler with authentication. """

    def data_received(self, chunk):
        """ Overwriting abstract method. """
        pass
