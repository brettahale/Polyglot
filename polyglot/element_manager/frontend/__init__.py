''' Polyglot Frontend Interface '''
import logging
import os
from polyglot.element_manager import http

STATIC_DIR = \
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'www_static')
DEFAULT_CONFIG = {}
_LOGGER = logging.getLogger(__name__)


def load(pglot, user_config):
    ''' setup the frontend handlers '''
    urls = [
        (r"/static/(.*)", http.AuthStaticFileHandler, {"path": STATIC_DIR}),
        (r"/", IndexHandler)]
    http.register(urls=urls)

    _LOGGER.info('Loaded Frontend element')


def unload():
    ''' stops the http server '''
    _LOGGER.info('Unloaded Frontend element')


def get_config():
    """ Returns the element's configuration. """
    return {}


def set_config(config):
    """ Updates the current configuration. """
    # pylint: disable=global-statement
    pass


class IndexHandler(http.AbstractHandler):
    """ Handler for root requests. """

    def get(self):
        """ handle get requests. """
        #self.render(os.path.join(STATIC_DIR, 'index.html'))
        self.redirect('/static/index.html')
        #self.finish()

    def data_received(self, chunk):
        """ Overwriting abstract method. """
        pass
