'''
Definitions for incomming requests from the ISY.

Handlers will return 404 if a bad base url is provided.
Else, a 200 is returned. Commands are sent to Node Servers after
the HTTP response has been sent to the ISY.
'''
from polyglot.element_manager import http
import logging

_LOGGER = logging.getLogger(__name__)
PGLOT = None


def rem_node_prefix(node_address):
    """
    Remove node prefix from node address.

    :param node_address: The prefixed node address.
    """
    if len(node_address) >= 5:
        return node_address[5:]
    else:
        return node_address


class GenericNodeServerHandler(http.AbstractHandler):
    """ Generic Handler that verifies Node Server. """
    def __init__(self, *args, **kwargs):
        super(GenericNodeServerHandler, self).__init__(*args, **kwargs)
        self.node_server = None
        self.store = None
        self.request_id = None

    def get(self, base, *args):
        """ get handler """
        try:
            node_server = PGLOT.nodeservers[base]
        except KeyError:
            self.send_not_found()
        else:
            self.node_server = node_server
            self.store = args
            self.request_id = self.get_argument('requestId', None, True)
            self.send_ok()

    def send_ok(self):
        ''' sends on ok status back to the client. '''
        self.set_status(200, 'HTTP_OK')
        self.write('200 - HTTP_OK')
        self.finish()

    def send_unavailable(self):
        ''' sends an unavailable response back to the client. '''
        self.set_status(503, 'HTTP_SERVICE_UNAVAILABLE')
        self.write('503 - HTTP_SERVICE_UNAVAILABLE')
        self.finish()

    def send_not_found(self):
        ''' sends a not found response back to the client. '''
        self.set_status(404, 'HTTP_NOT_FOUND')
        self.write('404 - HTTP_NOT_FOUND')
        self.finish()

    def send_str(self, string):
        '''
        sends on ok status back to the client.

        :param string: String to send back
        '''
        self.set_status(200, 'HTTP_OK')
        self.write(string)
        self.finish()


class InstallHandler(GenericNodeServerHandler):
    ''' /([A-Za-z0-9]+)/install/([0-9]+) '''
    def on_finish(self):
        ''' worker '''
        if self.node_server:
            profile_number = int(self.store[0])
            self.node_server.send_install(profile_number)


class QueryHandler(GenericNodeServerHandler):
    ''' /([A-Za-z0-9]+)/nodes/([A-Za-z0-9_]+)/query '''
    def on_finish(self):
        ''' worker '''
        if self.node_server:
            node_address = rem_node_prefix(str(self.store[0]))
            self.node_server.send_query(node_address, self.request_id)


class StatusHandler(GenericNodeServerHandler):
    ''' /([A-Za-z0-9]+)/nodes/([A-Za-z0-9_]+)/status '''
    def on_finish(self):
        """ worker """
        if self.node_server:
            node_address = rem_node_prefix(str(self.store[0]))
            self.node_server.send_status(node_address, self.request_id)


class AddNodesHandler(GenericNodeServerHandler):
    ''' /([A-Za-z0-9]+)/add/nodes '''
    def on_finish(self):
        """ worker """
        if self.node_server:
            self.node_server.send_addall(self.request_id)


class ReportAddHandler(GenericNodeServerHandler):
    ''' /([A-Za-z0-9]+)/nodes/([A-Za-z0-9_]+)/report/add/([A-Za-z0-9_]+) '''
    def on_finish(self):
        """ worker """
        if self.node_server:
            node_address = rem_node_prefix(str(self.store[0]))
            node_def_id = str(self.store[1])
            primary_node = self.get_argument('primary', strip=True)
            primary_node = rem_node_prefix(primary_node)
            name = self.get_argument('name', strip=True)
            self.node_server.send_added(node_address, node_def_id,
                                        primary_node, name)


class ReportRemoveHandler(GenericNodeServerHandler):
    ''' /([A-Za-z0-9]+)/nodes/([A-Za-z0-9_]+)/report/remove '''
    def on_finish(self):
        """ worker """
        if self.node_server:
            node_address = rem_node_prefix(str(self.store[0]))
            self.node_server.send_removed(node_address)


class ReportRenameHandler(GenericNodeServerHandler):
    ''' /([A-Za-z0-9]+)/nodes/([A-Za-z0-9_]+)/report/rename '''
    def on_finish(self):
        """ worker """
        if self.node_server:
            node_address = rem_node_prefix(str(self.store[0]))
            name = self.get_argument('name', strip=True)
            self.node_server.send_renamed(node_address, name)


class ReportEnableHandler(GenericNodeServerHandler):
    ''' /([A-Za-z0-9]+)/nodes/([A-Za-z0-9_]+)/report/enable '''
    def on_finish(self):
        """ worker """
        if self.node_server:
            node_address = rem_node_prefix(str(self.store[0]))
            self.node_server.send_enabled(node_address)


class ReportDisableHandler(GenericNodeServerHandler):
    ''' /([A-Za-z0-9]+)/nodes/([A-Za-z0-9_]+)/report/disable '''
    def on_finish(self):
        """ worker """
        if self.node_server:
            node_address = rem_node_prefix(str(self.store[0]))
            self.node_server.send_disabled(node_address)


class NodeCommandHandler(GenericNodeServerHandler):
    '''
    /([A-Za-z0-9]+)/nodes/([A-Za-z0-9_]+)/cmd/([A-Za-z0-9_]+)
    /?([A-Za-z0-9.]*)/?([0-9]*)
    '''
    def on_finish(self):
        """ worker """
        if self.node_server:
            node_address = rem_node_prefix(str(self.store[0]))
            command = str(self.store[1])
            value = None if len(self.store[2]) == 0 else float(self.store[2])
            uom = None if len(self.store[3]) == 0 else int(self.store[3])
            raw_parameters = self.request.arguments
            parameters = {}

            # format parameter values
            for key, val in raw_parameters.items():
                if key != 'requestId':
                    parameters[key] = float(val[0])

            self.node_server.send_cmd(node_address, command, value, uom,
                                      self.request_id, **parameters)


HANDLERS = [InstallHandler, QueryHandler, StatusHandler,
            AddNodesHandler, ReportAddHandler, ReportRemoveHandler,
            ReportRenameHandler, ReportEnableHandler, ReportDisableHandler,
            NodeCommandHandler]
