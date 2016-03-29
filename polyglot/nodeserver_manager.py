''' The element management module for Polyglot '''

from collections import OrderedDict
import copy
import json
import logging
import os
from polyglot import SOURCE_DIR
from polyglot.utils import AsyncFileReader, Queue, Empty, MyProcessLookupError
import polyglot.nodeserver_helpers as helpers
import random
import string
import subprocess
import sys
import threading
import time

_LOGGER = logging.getLogger(__name__)
ELEMENT = 'core'
SERVER_TYPES = {'python': [sys.executable]}
NS_QUIT_WAIT_TIME = 5
PGVER = '1.0.1'
PGAPIVER = '1'
NSAPIVER = '1'

class NodeServerManager(object):
    """
    Node Server Manager

    :param pglot: The parent Polyglot object

    :ivar pglot: The parent Polyglot object
    :ivar servers: Dictionary of active Node Servers
    """

    servers = OrderedDict()

    def __init__(self, pglot):
        self.pglot = pglot

    def __getitem__(self, key):
        """ Get server by base name. """
        return self.servers[key]

    @property
    def config(self):
        """ Node Server configuration block. """
        output = []
        for nsbase_url, nodeserver in self.servers.items():
            output.append({'platform': nodeserver.platform,
                           'url_base': nsbase_url,
                           'name': nodeserver.name,
                           'profile_number': nodeserver.profile_number,
                           'config': nodeserver.config})
        return output

    def start_server(self, ns_platform, profile_number, nsname=None, base=None,
                     config=None):
        """ starts a node server """
        # pylint: disable=broad-except
        _LOGGER.info('Starting Node Server: %s:%s', ns_platform, nsname)
        # find node server
        path = helpers.get_path(ns_platform)

        # read node server attributes
        try:
            def_file = os.path.join(path, 'server.json')
            definition = json.loads(open(def_file).read())
        except (IOError, ValueError, KeyError):
            raise ValueError("Error reading server.json for {}".format(path))

        # parse server attributes
        try:
            nstype = definition['type']
            nsexe = os.path.join(path, definition['executable'])
        except KeyError:
            raise ValueError(
                "server.json for {} is missing type or executable."
                .format(ns_platform))

        # get server base name
        while base in self.servers or base is None:
            base = random_string(5)

        # create sandbox
        sandbox = self.pglot.config.nodeserver_sandbox(ns_platform)

        # create server
        try:
            server = NodeServer(self.pglot, ns_platform, profile_number,
                                nstype, nsexe, nsname or ns_platform,
                                config or {}, sandbox)
        except Exception:
            _LOGGER.exception('Node Server %s could not start', ns_platform)
            raise ValueError(
                "Error starting Node Server: {}.", ns_platform)

        # store server
        self.servers[base] = server
        return True

    def load(self):
        """ Initial load of the active Node Servers """
        _LOGGER.info('Loading Node Servers')

        nsconfigs = self.pglot.config.get("nodeservers", [])
        for count, nsconfig in enumerate(nsconfigs, 1):
            ns_platform = nsconfig.get("platform", None)
            profile_number = nsconfig.get("profile_number", None)
            url_base = nsconfig.get("url_base", None)
            name = nsconfig.get("name", ns_platform)
            config = nsconfig.get("config", {})

            if None in [ns_platform, profile_number]:
                _LOGGER.error(
                    'Bad Node Server configuration in config file. ' +
                    'Node Server %d', count)
            else:
                try:
                    self.start_server(
                        ns_platform, profile_number, name, url_base, config)
                except ValueError as err:
                    _LOGGER.error(err.args[0])

    def delete(self, base_url):
        """ Remove a server from Polyglot. """
        node_server = self.servers[base_url]
        node_server.send_exit()

        for _ in range(10):
            if not node_server.alive:
                break
            time.sleep(0.5)
        else:
            node_server.kill()

        del self.servers[base_url]

    def unload(self):
        """ Unload all node servers """
        # request node server shutdowns
        for node_server in self.servers.values():
            node_server.send_exit()

        # wait for node servers to quit gracefully
        ns_running = any([node_server.alive
                          for node_server in self.servers.values()])
        timer = 0
        while ns_running and timer < NS_QUIT_WAIT_TIME:
            time.sleep(1)
            timer += 1
            ns_running = any([node_server.alive
                              for node_server in self.servers.values()])

        # kill any remaining node servers
        for node_server in self.servers.values():
            if node_server.alive:
                node_server.kill()
                _LOGGER.warning(
                    'Timed out waiting for Node Server %s to quit. ' +
                    'Terminated Node Server.', node_server.name)

        _LOGGER.info('Unloaded Node Servers')


class NodeServer(object):
    """ Node Server Class """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, pglot, ns_platform, profile_number, nstype, nsexe,
                 nsname, config, sandbox):
        # build run command
        if nstype in SERVER_TYPES:
            cmd = copy.deepcopy(SERVER_TYPES[nstype])
        else:
            _LOGGER.error("Unrecognized server type %s for %s", nstype,
                          ns_platform)
            raise TypeError('bad server type')
        cmd.append(nsexe)

        self.pglot = pglot
        self.isy_version = self.pglot.isy_version
        self.config = config
        self._cmd = cmd
        self.platform = ns_platform
        self.profile_number = profile_number
        self.type = nstype
        self.exe = nsexe
        self.path = os.path.dirname(nsexe)
        self.name = nsname
        self.sandbox = sandbox
        """ This is the new 'API Version' Please increment if you update the API """ 
        self.pgver =  PGVER
        self.pgapiver = PGAPIVER
        self.nsapiver = NSAPIVER
        self.params = {'isyver': self.isy_version,
            'sandbox': self.sandbox,
            'name': self.name,
            'pgver': self.pgver,
            'pgapiver': self.pgapiver,
            'nsapiver': self.nsapiver}
        self._proc = None
        self._inq = None
        self._lastping = None
        self._lastpong = None

        # define handlers
        isy = self.pglot.elements.isy
        self._handlers = {'status': isy.report_node_status,
                          'command': isy.report_command,
                          'add': isy.node_add,
                          'change': isy.node_change,
                          'remove': isy.node_remove,
                          'request': isy.report_request_status}

        self.start()

    def start(self):
        """ start the node server """
        # start process
        proc = subprocess.Popen(
            self._cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, bufsize=1, env={'PYTHONPATH': SOURCE_DIR},
            cwd=self.sandbox)

        self._proc = proc
        self._inq = Queue()
        self._lastping = None
        self._lastpong = None

        # start Threads
        self._threads = {}
        self._threads['stdout'] = AsyncFileReader(self._proc.stdout,
                                                  self._recv_out)
        self._threads['stderr'] = AsyncFileReader(self._proc.stderr,
                                                  self._recv_err)
        self._threads['stdin'] = threading.Thread(target=self._send_in)
        self._threads['stdin'].daemon = True
        for _, thread in self._threads.items():
            thread.start()

        # wait, then send config
        time.sleep(1)
        self.send_params()        
        self.send_config()

        _LOGGER.info('Started Node Server: %s:%s (%s)',
                     self.platform, self.name, self._proc.pid)

    def restart(self):
        """ restart the nodeserver """
        self.send_exit()

        for _ in range(10):
            if not self.alive:
                break
            time.sleep(0.5)
        else:
            self.kill()

        self.start()

    @property
    def definition(self):
        """ Return the server defintion from server.json """
        def_file = os.path.join(self.path, 'server.json')
        instruct_file = os.path.join(self.path, 'instructions.txt')
        definition = json.loads(open(def_file).read())
        definition['running'] = self.alive and self.responding
        definition['instructions'] = open(instruct_file).read()
        definition['profile_number'] = self.profile_number

        return definition

    @property
    def profile(self):
        """ Return the profile.zip data. """
        return open(os.path.join(self.path, 'profile.zip'), 'rb').read()

    @property
    def alive(self):
        """ Indicates if the Node Server is running. """
        try:
            os.kill(self._proc.pid, 0)
        except MyProcessLookupError:
            return False
        return self._inq is not None

    @property
    def responding(self):
        """ Indicates if the Node Server is responding. """
        if self._lastping is None:
            # node server has not been pinged
            self.send_ping()
            self._lastping = time.time()
            return True

        elif time.time() - self._lastping >= 30:
            # last ping has expired (more than 30 seconds old)
            if self._lastpong and self._lastpong > self._lastping:
                # pong was recieved
                self.send_ping()
                self._lastping = time.time()
                return True
            else:
                # pong was not recieved
                return False

        else:
            # ping hasn't expired, we have to assume responding
            return True

    # manage IO
    def _send_in(self):
        """
        Write pending input to node server.
        Kill process if unresponsive.
        """
        while True and self._inq:
            try:
                # try to get a line from the queue
                line = self._inq.get(True, 5)
            except Empty:
                # no line in queue, check if the Node Server is responding
                if not self.responding:
                    _LOGGER.error(
                        'Node Server %s has stopped responding.', self.name)
                    self._inq = None
                    self._proc.kill()
            else:
                try:
                    # found line, try to write it
                    self._proc.stdin.write('{}\n'.format(line))
                    self._proc.stdin.flush()
                except IOError:
                    # stdin pipe is broken. process is likely dead.
                    _LOGGER.error(
                        'Node Server %s has exited unexpectedly.', self.name)
                    self._inq = None
                    self._proc.kill()
                else:
                    # line wrote successfully
                    _LOGGER.debug('%s STDIN: %s', self.name, line)
                    if self._inq:
                        self._inq.task_done()

    def _recv_out(self, line):
        """ Process node server output. """
        _LOGGER.debug('%s STDOUT: %s', self.name, line)
        # parse message
        message = json.loads(line)
        command = list(message.keys())[0]
        arguments = message[command]

        # direct command
        if command == 'pong':
            # store pong time
            self._lastpong = time.time()
        elif command == 'config':
            # store new configuration in config file
            self.config = arguments
            self.pglot.update_config()
        elif command == 'install':
            # install node server on isy
            # [future] impliment when documentation is available
            raise NotImplementedError('Install command is not yet supported.')
        elif command == 'exit':
            # node server is done. Kill it. Clean up is automatic.
            self._proc.kill()
            self._inq = None
        else:
            fun = self._handlers.get(command)
            if fun:
                fun(self.profile_number, **arguments)
            else:
                _LOGGER.error('Node Server %s delivered bad command %s',
                              self.name, command)

    def _recv_err(self, line):
        """ Process error stream from node server. """
        _LOGGER.error('%s: %s', self.name, line)

    # handle output
    def _mk_cmd(self, cmd_code, **kwargs):
        """ Enqueue a command for transmission to server. """
        msg = json.dumps({cmd_code: kwargs})
        if self._inq:
            self._inq.put(msg, True, 5)

    def send_config(self):
        """ Send configuration to Node Server. """
        self._mk_cmd('config', **self.config)

    def send_params(self):
        """ Send parameters to Node Server. """
        self._mk_cmd('params', **self.params)        

    def send_install(self, profile_number=None):
        """ Send install command to Node Server. """
        if not profile_number:
            profile_number = self.profile_number
        else:
            self.profile_number = profile_number
            self.pglot.update_config()
        self._mk_cmd('install', profile_number=self.profile_number)

    def send_query(self, node_address, request_id=None):
        """ Send query command to Node Server. """
        self._mk_cmd('query', node_address=node_address, request_id=request_id)

    def send_status(self, node_address, request_id=None):
        """ Send status request to Node Server. """
        self._mk_cmd('status', node_address=node_address,
                     request_id=request_id)

    def send_addall(self, request_id=None):
        """ Send add all request to Node Server. """
        self._mk_cmd('add_all', request_id=request_id)

    def send_added(self, node_address, node_def_id,
                   primary_node_address, name):
        """ Send node added confirmation to Node Server. """
        self._mk_cmd('added', node_address=node_address,
                     node_def_id=node_def_id,
                     primary_node_address=primary_node_address, name=name)

    def send_removed(self, node_address):
        """ Send node removed confirmation to Node Server. """
        self._mk_cmd('removed', node_address=node_address)

    def send_renamed(self, node_address, name):
        """ Send node renamed confirmation to Node Server. """
        self._mk_cmd('renamed', node_address=node_address, name=name)

    def send_enabled(self, node_address):
        """ Send node enabled confirmation to Node Server. """
        self._mk_cmd('enabled', node_address=node_address)

    def send_disabled(self, node_address):
        """ Send node disabled confirmation to Node Server. """
        self._mk_cmd('disabled', node_address=node_address)

    def send_cmd(self, node_address, command, value=None, uom=None,
                 request_id=None, **kwargs):
        """ Send run command signal to Node Server. """
        self._mk_cmd('cmd', node_address=node_address, command=command,
                     value=value, uom=uom, request_id=request_id, **kwargs)

    def send_ping(self):
        """ Send Ping request to the Node Server. """
        self._mk_cmd('ping')

    def send_exit(self):
        """ Send exit command to the Node Server. """
        self._mk_cmd('exit')

    def kill(self):
        """ Kill the node server process. """
        try:
            self._proc.kill()
        except MyProcessLookupError:
            pass


def random_string(length):
    """ Generate a random string of uppercase, lowercase, and digits """
    library = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.choice(library) for _ in range(length))
