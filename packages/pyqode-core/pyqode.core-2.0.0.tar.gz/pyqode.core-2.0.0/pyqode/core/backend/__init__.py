"""
The backend package contains the API to use on the server side:
    - server + methods for running it
    - workers definitions

pyQode uses a client-server architecture for running heavy tasks such as code
analysis (lint), code completion,...

Protocol
--------

We use a worker based json messaging server using the TCP/IP protocol.

We build our own, very simple protocoal where each message is made up of two
parts:

  - a header: simply contains the length of the payload
  - a payload: a json formatted string, the content of the message.

The content of the json object depends on if this is a request or a response.

Request
+++++++
For a request, the object will contains the following fields:

  - 'request_id': uuid generated client side
  - 'worker': fully qualified name to the worker callable (class or function),
    e.g. 'pyqode.core.backend.workers.echo_worker'
  - 'data': data specific to the chose worker.

E.g::

    {
        'request_id': 'a97285af-cc88-48a4-ac69-7459b9c7fa66',
        'worker': 'pyqode.core.backend.workers.echo_worker',
        'data': ['some code', 0]
    }

Response
++++++++

For a response, the object will contains the following fields:
    - 'request_id': uuid generated client side that is simply echoed back
    - 'status': worker status, boolean
    - 'results': worker results (list, tuple, string,...)

E.g::

    {
        'request_id': 'a97285af-cc88-48a4-ac69-7459b9c7fa66',
        'status': True,
        'results': ['some code', 0]
    }

Server script
~~~~~~~~~~~~~

The server script must be written by the user. Don't worry, its very simple.
All you have to do is to create and run a JsonTcpServer instance.

We choose to let you write the main script to let you easily configure it.

Some workers will requires some tweaking (for the completion worker,
you will want to add custom completion providers, you might also want to
modify sys.path,...). It also makes the packaging process more consistent,
your script will be packaged on linux using setup.py and will be frozen on
windows using cx_Freeze.

Here is the most simple and basic example of a server script:

.. code-block: python
    from pyqode.core import backend

    if __name__ == '__main__':
        backend.serve_forever()

.. warning:: The user can choose the python interpreter that will run the
    server. That means that classes and functions that run server side (
    workers) **should fully support python2 syntax** and that pyqode.core
    should be installed on the target interpreter sys path!!! (even for a
    virtual env). An alternative is to keep pyqode.core package in a zip
    archive that you mount on the sys path in your server script.

.. note:: print statements on the server side will be logged as debug messages
    on the client side. To have your messages logged as error message, use
    sys.stderr instead of print.

"""
# server
from .server import JsonServer
from .server import default_parser
from .server import serve_forever

# workers
from .workers import CodeCompletionWorker
from .workers import DocumentWordsProvider
from .workers import echo_worker


class NotConnected(Exception):
    """
    Raised if the client is not connected to the server when an operation
    is requested.
    """
    def __init__(self):
        super().__init__('Client socket not connected or '
                         'server not started')


__all__ = [
    'JsonServer',
    'default_parser',
    'serve_forever',
    'CodeCompletionWorker',
    'DocumentWordsProvider',
    'echo_worker',
    'NotConnected'
]
