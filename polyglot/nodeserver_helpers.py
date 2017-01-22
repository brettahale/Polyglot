""" Helper functions for managing Node Servers. """
import json
import logging
import os
import sys

_LOGGER = logging.getLogger(__name__)
try:
    SOURCE_DIR = os.path.dirname(__file__)
except NameError:  # We are running as a binary.
    import sys
    SOURCE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
SERVER_LIB = os.path.abspath(os.path.join(SOURCE_DIR, 'node_servers'))
SERVER_LIB_EXTERNAL = None


def available_servers():
    ''' list all available elements '''
    paths = dirs_in(SERVER_LIB) + dirs_in(SERVER_LIB_EXTERNAL)
    out = {}
    for path in paths:
        try:
            def_file = os.path.join(path, 'server.json')
            definition = json.loads(open(def_file).read())
            name = definition['name']
            platform = [val for val in path.split(os.path.sep)
                        if val != ''][-1]
        except (IOError, ValueError, KeyError, TypeError):
            _LOGGER.error("Error reading server.json for %s", path)
        else:
            out[platform] = {'path': path, 'name': name}
    return out


def get_path(platform):
    """ Find Node Server Platform path """
    for lib in [SERVER_LIB, SERVER_LIB_EXTERNAL]:
        if platform in dirs_in(lib, False):
            path = os.path.join(lib, platform)
            return path

    raise ValueError(
        "Could not find node server: {}".format(platform))


def dirs_in(path, include_path=True):
    '''
    Returns a list of directories in a path.

    :param path: The path to search.
    '''
    if path is None:
        return []
    out = []
    for obj in os.listdir(path):
        if not ignore_dir(path, obj):
            if include_path:
                out.append(os.path.join(path, obj))
            else:
                out.append(obj)
    return out


def ignore_dir(path, dir_name):
    """ Deterermine if a directory should be ignored. """
    return dir_name.startswith('.')  \
        or not os.path.isdir(os.path.join(path, dir_name)) \
        or dir_name == "CVS"
