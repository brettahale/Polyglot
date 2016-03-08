""" Element Manager Module """

from polyglot.element_manager import http
from polyglot.element_manager import api
from polyglot.element_manager import isy
from polyglot.element_manager import frontend
import logging

_LOGGER = logging.getLogger(__name__)


class ElementManager(object):
    """ Element Manager for Polyglot """

    def __init__(self, pglot):
        self.pglot = pglot
        self.http = http
        self.api = api
        self.isy = isy
        self.frontend = frontend

    def load_config(self):
        """ get config data from config manager """
        return self.pglot.config['elements']

    def set_config(self, config):
        """ set the config for elements """
        for elem_name, elem_config in config.items():
            element = getattr(self, elem_name)
            element.set_config(elem_config)
        self.pglot.update_config()

    @property
    def config(self):
        """ get config data from elements """
        return {'http': self.http.get_config(),
                'api': self.api.get_config(),
                'isy': self.isy.get_config(),
                'frontend': self.frontend.get_config()}

    def load(self):
        """ load all elements """
        _LOGGER.info("Loading Elements")
        self.http.load(self.pglot, self.load_config().get('http', {}))
        self.api.load(self.pglot, self.load_config().get('api', {}))
        self.isy.load(self.pglot, self.load_config().get('isy', {}))
        self.frontend.load(self.pglot, self.load_config().get('frontend', {}))

    def unload(self):
        """ unload all elements """
        self.frontend.unload()
        self.isy.unload()
        self.api.unload()
        self.http.unload()
        _LOGGER.info("Unloaded Elements")
