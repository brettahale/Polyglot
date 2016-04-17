""" Generic utilities used by Polyglot. """
# pylint: disable=import-error, unused-import, invalid-name, undefined-variable
# flake8: noqa

import sys
import threading

# Uniform Queue and Empty locations b/w Python 2 and 3
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty

# Unform ProcessLookupError b/w Python 2 and 3
if sys.version_info[0] == 2:
    MyProcessLookupError = OSError
else:
    MyProcessLookupError = ProcessLookupError


class AsyncFileReader(threading.Thread):
    '''
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.

    Source:
    http://stefaanlippens.net/python-asynchronous-subprocess-pipe-reading
    '''

    def __init__(self, fd, handler):
        assert callable(handler)
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self.daemon = True
        self._fd = fd
        self._handler = handler

    def run(self):
        '''The body of the thread: read lines and put them on the queue.'''
        for line in iter(self._fd.readline, ''):
            self._handler(line.replace('\n', ''))


class LockQueue(Queue):
    """ Python queue with a locking utility """

    def __init__(self, *args, **kwargs):
        Queue.__init__(self, *args, **kwargs)
        # Queue is old style class in Python 2.x
        self.locked = True

    def put(self, *args, **kwargs):
        """ Put item into queue """
        if not self.locked:
            Queue.put(self, *args, **kwargs)

    def put_nowait(self, *args, **kwargs):
        """ Put item into queue without waiting """
        if not self.locked:
            Queue.put_nowait(self, *args, **kwargs)
