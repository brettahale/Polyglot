"""
Polyglot

Server for translating communication between the ISY994 controller and
third-party Node Servers.
"""
# pylint: disable=no-name-in-module,import-error
# flake8: noqa

from . import utils
from . import nodeserver_api
import version
import os

__version__ = version.PGVERSION
SOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
