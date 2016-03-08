''' The HTTP Basic Auth module for Tornado '''
# pylint: disable=protected-access
import base64


def basic_auth(auth_func, after_login_func=lambda *args, **kwargs: None,
               realm='Restricted'):
    '''
    The Basic Auth decorator for Tornado handlers.

    :param auth_fun: The function to be used for checking the credentials
    :param after_login_func: Function to run after a user successfully logs in
    :param realm: The realm to which the user is authenticating
    '''

    def basic_auth_decorator(handler_class):
        '''
        The template for the decorated handler class.

        :param handler_class: The Tornado handler class to be decorated.
        '''
        def wrap_execute(handler_execute):
            '''
            Return the handler _execute method wrapped with auth utility.

            :param handler_execute: The handler's ._execute method.
            '''
            def require_basic_auth(handler, kwargs):
                '''
                Authenticates the user credentials.

                :param handler: The Tornado handler
                :param kwargs: Keyword arguments sent to _execute
                '''
                def create_auth_header():
                    ''' Create HTTP header to ask for credentials. '''
                    handler.set_status(401)
                    handler.set_header('WWW-Authenticate',
                                       'Basic realm={}'.format(realm))
                    handler._transforms = []
                    handler.finish()

                # get provided auth credentials, quit if none provided
                auth_header = handler.request.headers.get('Authorization')
                if auth_header is None or not auth_header.startswith('Basic '):
                    create_auth_header()
                    return

                # decode auth credentials
                auth_decoded = base64.decodestring(auth_header[6:])
                user, pwd = auth_decoded.split(':', 2)

                # authenticate credentials
                if auth_func(user, pwd):
                    after_login_func(handler, kwargs, user, pwd)
                else:
                    create_auth_header()

            def _execute(self, transforms, *args, **kwargs):
                '''
                Wrapped Tornado handler _execute method.
                Parameters are identical.
                '''
                require_basic_auth(self, kwargs)
                return handler_execute(self, transforms, *args, **kwargs)

            return _execute

        handler_class._execute = wrap_execute(handler_class._execute)
        return handler_class

    return basic_auth_decorator
