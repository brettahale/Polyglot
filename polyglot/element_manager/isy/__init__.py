''' Polyglot ISY Virtual Node API definition '''
# pylint: disable=no-name-in-module, import-error
import logging
from polyglot.element_manager import http
from . import incoming
import xml.etree.ElementTree as ET
import requests
import time
try:
    from urllib import quote, urlencode  # Python 2.x
except ImportError:
    from urllib.parse import quote, urlencode  # Python 3.x

DEFAULT_CONFIG = {'address': '192.168.10.100', 'https': False,
                  'password': 'admin', 'username': 'admin', 'port': 80, 'version':'4.2.3'}

ADDRESS = None
HTTPS = None
PASSWORD = None
PORT = None
USERNAME = None
VERSION = None
_LOGGER = logging.getLogger(__name__)

# [future] only accept incoming requests from the ISY


def load(pglot, user_config):
    ''' setup the http server '''
    # setup the configuration
    config = dict(DEFAULT_CONFIG)
    config.update(user_config)
    set_config(config)
    get_version()    


    # register addresses with server
    http.register(incoming.HANDLERS, parent_dir='ns')

    # Register Polyglot application
    incoming.PGLOT = pglot

    _LOGGER.info('Loaded ISY element')
    


def unload():
    ''' stops the http server '''
    _LOGGER.info('Unloaded ISY element')


def get_config():
    """ Returns the element's configuration. """
    return {'address': ADDRESS, 'https': HTTPS == 'https',
            'password': PASSWORD, 'username': USERNAME, 'port': PORT, 'version': VERSION}


def set_config(config):
    """ Updates the current configuration. """
    # pylint: disable=global-statement
    global ADDRESS, HTTPS, PASSWORD, PORT, USERNAME

    # pull config settings
    ADDRESS = config['address']
    HTTPS = 'https' if config['https'] else 'http'
    PASSWORD = config['password']
    PORT = config['port']
    USERNAME = config['username']


def add_node_prefix(ns_profnum, nid):
    '''
    Adds a node prefix to a node ID.

    :param nid: The nodes ID to which a prefix will be added.
    '''
    prefix = 'n{}_'.format(str(ns_profnum).zfill(3))
    return '{}{}'.format(prefix, nid)


def report_node_status(ns_profnum, node_address, driver_control, value, uom):
    '''
    Reports the node status to the ISY.

    :param ns_profnum: Node Server ID
    :param node_address: The Node Address
    :param driver_control: Driver control for the node
    :param value: The node's value
    :param uom: The units of measurement of the value
    '''
    node_address = add_node_prefix(ns_profnum, node_address)
    url = make_url(ns_profnum, ['nodes', node_address, 'report', 'status',
                                driver_control, value, uom])
    request(url)


def report_command(ns_profnum, node_address, command, value=None, uom=None,
                   **kwargs):
    '''
    Reports a command that has run on a node.

    :param ns_profnum: Node Server ID
    :param node_address: The Node Address
    :param command: The command that was run on the node
    :param optional value: The unnamed parameter the command ran with
    :param optional uom: The unit of measurement for the unnamed parameter
    :param optional <pN>.<uomN>: Named parameter (p) with specificed uom
    '''
    node_address = add_node_prefix(ns_profnum, node_address)
    url = make_url(ns_profnum, ['nodes', node_address, 'report', 'cmd',
                                command, value, uom],
                   kwargs)
    request(url)


def node_add(ns_profnum, node_address, node_def_id, primary, name):
    '''
    Adds a node to the ISY.

    :param ns_profnum: Node Server ID
    :param node_address: The Node Address
    :param node_def_id: The node definition ID
    :param primary: The address to the primary node
    :param name: The node name
    '''
    node_address = add_node_prefix(ns_profnum, node_address)
    primary = add_node_prefix(ns_profnum, primary)
    url = make_url(ns_profnum, ['nodes', node_address, 'add', node_def_id],
                   {'primary': primary, 'name': name})
    request(url)


def node_change(ns_profnum, node_address, node_def_id):
    '''
    Change node on the ISY.

    :param ns_profnum: Node Server ID
    :param node_address: The Node Address
    :param node_def_id: The node definition ID
    '''
    node_address = add_node_prefix(ns_profnum, node_address)
    url = make_url(ns_profnum, ['nodes', node_address, 'change', node_def_id])
    request(url)


def node_remove(ns_profnum, node_address):
    '''
    Remove node on the ISY.

    :param ns_profnum: Node Server ID
    :param node_address: The Node Address
    '''
    node_address = add_node_prefix(ns_profnum, node_address)
    url = make_url(ns_profnum, ['nodes', node_address, 'remove'])
    request(url)


def report_request_status(ns_profnum, request_id, success):
    '''
    Report the status of a request back to the ISY.

    :param request_id: The request ID from the controller.
    :param result: Boolean indicating the success of the command.
    '''
    status = 'success' if success else 'failed'
    url = make_url(ns_profnum,
                   ['report', 'request', request_id, status])
    request(url)

def get_version():
    global VERSION
    """
    Get the version of the ISY when requested by the nodeservers
    Set version information in config file for reference.
    """
    req = restcall('config')
    if req['text'] is not None:
        try:                   
            tree = ET.fromstring(req['text'])
            VERSION = tree.findall('app_version')[0].text
        except ET.ParseError:
            _LOGGER.error("No version information found on ISY.")
        _LOGGER.info("ISY: firmware version: %s", VERSION)
    return VERSION

def make_url(ns_profnum, path, path_args=None):
    '''
    Create a URL from the given path.

    :param path: List or subdirectories in path.
    :param path_args: Dictionary of arguments to add to the path.
    '''
    url = '{}://{}:{}/rest/ns/{}/'.format(HTTPS, ADDRESS, PORT, ns_profnum)
    url += '/'.join([quote(str(item)) for item in path if item is not None])

    if path_args is not None:
        url += '?{}'.format(urlencode(path_args))

    return url


def request(url):
    '''
    Requests a URL from the ISY.
    Returns True if success, False if failure

    :param url: URL to request.
    '''

    req = base_request(url)
    return (req['status_code'] == 200)

def restcall(api):
    '''
    Requests a REST API from the ISY. Returns response.

    :param api: API to request.
    '''

    url = '{}://{}:{}/rest/{}'.format(HTTPS, ADDRESS, PORT, api)
    return base_request(url)

def base_request(url):
    '''
    Requests a URL from the ISY, returns response.
    Returns a dictionary r containing:
        r.text:        response text     (string or None)
        r.status_code: HTTP status code  (integer or None)
        r.error_text:  error text        (string or None)

    :param url: URL to request.
    '''
    _LOGGER.debug('ISY: Request: %s', url)

    # make request
    ts = time.time()
    try:
        req = requests.get(url, auth=(USERNAME, PASSWORD),
                           timeout=30, verify=False)

    except requests.ConnectionError:
        elapsed = (time.time() - ts)
        _LOGGER.error('ISY:        (%5.2f) Connection Error: %s',
                      elapsed, url)
        return {'text':None, 'status_code': None,
                'error_text': 'Error',
                'elapsed': elapsed}

    except requests.HTTPError:
        elapsed = (time.time() - ts)
        _LOGGER.error('ISY:        (%5.2f) HTTP Error: %s',
                      elapsed, url)
        return {'text':None, 'status_code': None,
                'error_text': 'HTTPError',
                'elapsed': elapsed}

    except requests.URLRequired:
        elapsed = (time.time() - ts)
        _LOGGER.error('ISY:        (%5.2f) Valid URL Required: %s',
                      elapsed, url)
        return {'text':None, 'status_code': None,
                'error_text': 'URLRequired',
                'elapsed': elapsed}

    except requests.Timeout:
        elapsed = (time.time() - ts)
        _LOGGER.error('ISY:        (%5.2f) Timeout: %s',
                      elapsed, url)
        return {'text':None, 'status_code': None,
                'error_text': 'Timeout',
                'elapsed': elapsed}

    elapsed = (time.time() - ts)
    scode = req.status_code
    if scode == 200:
        _LOGGER.info('ISY:        (%5.2f) %3d  OK: %s', elapsed, scode, url)
    else:
        _LOGGER.error('ISY:        (%5.2f) %3d ERR: %s', elapsed, scode, url)

    return {'text': req.text, 'status_code': scode,
            'error_text': None, 'elapsed': elapsed}
