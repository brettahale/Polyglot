''' The configuration management module for Polyglot '''

import base64
from collections import defaultdict
import copy
import json
import logging
import os
import stat
import time

_LOGGER = logging.getLogger(__name__)


class ConfigManager(defaultdict):
    """
    Configuration Manager class

    :param config_dir: The configuration directory to use
    """

    def __init__(self, config_dir):
        super(ConfigManager, self).__init__(dict)
        self._dir = config_dir
        self._file = os.path.join(self._dir, 'configuration.json')
        self._writing = False
        self.read()

    def __del__(self):
        """ Update configuration file before erasing configuration """
        self.write()

    def encode(self):
        """ Encode passwords and return an encoded copy """
        encoded = copy.deepcopy(dict(self))
        encoded['elements']['http']['password'] = \
            base64.b64encode(encoded['elements']['http']['password'])
        encoded['elements']['isy']['password'] = \
            base64.b64encode(encoded['elements']['isy']['password'])
        return encoded

    def decode(self, encoded):
        """ Decode passwords and return decoded """
        try:
            encoded['elements']['http']['password'] = \
                base64.b64decode(encoded['elements']['http']['password'])
            encoded['elements']['isy']['password'] = \
                base64.b64decode(encoded['elements']['isy']['password'])
        except TypeError:
            pass
        return encoded

    def update(self, *args, **kwargs):
        """ Update the configuration with values in dictionary """
        super(ConfigManager, self).update(*args, **kwargs)
        self.write()

    def read(self):
        """ Reads configuration file """
        if os.path.isfile(self._file):
            encoded = json.load(open(self._file, 'r'))
            decoded = self.decode(encoded)
            self.update(decoded)
            _LOGGER.debug('Read configuration file')

    def write(self):
        """ Writes configuration file """
        # wait for file to unlock. Timeout after 5 seconds
        for _ in range(5):
            if not self._writing:
                self._writing = True
                break
            time.sleep(1)
        else:
            _LOGGER.error('Could not write to configuration file. It is busy.')
            return

        # dump JSON to config file and unlock
        encoded = self.encode()
        json.dump(encoded, open(self._file, 'w'), sort_keys=True, indent=4,
                  separators=(',', ': '))
        os.chmod(self._file, stat.S_IRUSR | stat.S_IWUSR)
        self._writing = False
        _LOGGER.debug('Wrote configuration file')

    def make_path(self, *args):
        """ make a path to a file in the config directory """
        return os.path.join(self._dir, *args)

    def nodeserver_sandbox(self, url_base):
        """ make and return a sandbox directory for a node server. """
        sandbox = self.make_path(url_base)

        if not os.path.isdir(sandbox):
            os.mkdir(sandbox)

        return sandbox
