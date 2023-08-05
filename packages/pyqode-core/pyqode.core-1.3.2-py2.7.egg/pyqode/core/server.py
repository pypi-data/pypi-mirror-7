#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#The MIT License (MIT)
#
#Copyright (c) <2013-2014> <Colin Duquesnoy and others, see AUTHORS.txt>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#
"""
This module contains the subprocess server used to run heavy task such as
code completion, code analysis,... in a background thread.

The server will start automatically when you create your first pyqode widget
but it can also be started manually with custom startup parameters (you can
choose to reuse an existing local server or start a new one for your process).
There can only be one server per process, the server is shared among all code
editor instances.

The server is able to run multiple background worker in a dedicated worker
slot. A worker slot is a named background thread that will be used to run a
specific kind of worker. Worker object must define a _slot attribute that will
be used to dispatch them on the matching slot thread.
"""
import multiprocessing
from multiprocessing.connection import Client, Listener
import os

Listener.fileno = lambda self: self._listener._socket.fileno()
import select
import sys
import time
if sys.version_info[0] == 3:
    import _thread as thread
else:
    import thread

from pyqode.core import logger
from pyqode.qt import QtGui, QtCore


class _ServerSignals(QtCore.QObject):
    """
    Holds the server signals.
    """
    #: Signal emitted when a new work is requested.
    #:
    #: **Parameters**:
    #:   * caller id
    #:   * worker object
    workRequested = QtCore.Signal(object, object)

    #: Signal emitted when a new work is requested.
    #:
    #: **Parameters**:
    #:   * caller id
    #:   * worker object
    #:   * worker results
    workCompleted = QtCore.Signal(object, object, object)


class Worker(object):
    _slot = "default"


class Server(object):
    """
    Utility class to run a child process use to execute heavy load computations
    such as file layout analysis, code completion requests...

    To use the server, just create an instance and call the
    :meth:`pyqode.core.SubprocessServer.start` method.

    To request a job, use the requestWork method and pass it your worker object
    (already configured to do its work).

    The server will send the request to the child process and will emit the
    workCompleted signal when the job finished.
    """

    class _AppendSlotWorker(Worker):
        def __init__(self, slot):
            self._slot = slot


    def __init__(self, name="pyqode-server", autoCloseOnQuit=True,
                 slots=None):
        #: Server signals; see :meth:`pyqode.core.system._ServerSignals`
        if slots is None:
            slots = ["default", "__server__"]
        self.signals = _ServerSignals()
        self._slots = slots
        self.__name = name
        self.__running = False
        self._workQueue = []
        if autoCloseOnQuit:
            QtGui.QApplication.instance().aboutToQuit.connect(self.close)
        self._lock = thread.allocate_lock()

    def close(self):
        """
        Closes the server, terminates the child process.
        """
        logger.info("Close server")
        if self.__running:
            self.__running = False
            self.__process.terminate()

    def start(self, port=8080):
        """
        Starts the server. This will actually start the child process.

        :param port: Local TCP/IP port to which the underlying socket is
                     connected to.
        """
        self.__process = multiprocessing.Process(target=_childProcess,
                                                 name=self.__name,
                                                 args=(port, self._slots))
        self.__process.start()
        self.__running = False
        try:
            try:
                self._client = Client(('localhost', port))
            except OSError:
                # wait a second before starting, this occur if we were connected to
                # previously running server that has just closed (we need to wait a
                # little before starting a new one)
                time.sleep(1)
                self._client = Client(('localhost', port))
            logger.info("Connected to Code Completion Server on 127.0.0.1:%d" %
                        port)
            self.__running = True
            thread.start_new_thread(self._threadFct, ())
        except OSError:
            logger.exception("Failed to connect to Code Completion Server on "
                             "127.0.0.1:%d" % port)
        return self.__running

    def add_slot(self, slot):
        if self.__running:
            self.requestWork(self, self._AppendSlotWorker(slot=slot))
        else:
            self._slots.append(slot)

    def _threadFct(self, *args):
        while self.__running:
            with self._lock:
                while len(self._workQueue):
                    msg = self._workQueue.pop(0)
                    self._client.send(msg)
            self.__poll()
            time.sleep(0.001)

    def requestWork(self, caller, worker):
        """
        Requests a work. The work will be called in the child process and its
        results will be available through the
        :attr:`pyqode.core.SubprocessServer.signals.workCompleted` signal.

        :param caller: caller object
        :type caller: object

        :param worker: Callable **object**, must override __call__ with no
                       parameters.
        :type worker: callable
        """
        logger.debug("SubprocessServer requesting work: %s " % worker)
        caller_id = id(caller)
        with self._lock:
            self._workQueue.append((caller_id, worker))

    def __poll(self):
        """
        Poll the child process for any incoming results
        """
        try:
            if self._client.poll():
                try:
                    data = self._client.recv()
                    if len(data) == 3:
                        caller_id = data[0]
                        worker = data[1]
                        results = data[2]
                        if results is not None:
                            self.signals.workCompleted.emit(caller_id, worker, results)
                    else:
                        logger.info(data)
                except (IOError, EOFError):
                    logger.warning("Lost completion server, restarting")
                    self.start()
        except OSError:
            pass


def _execWorkerInSlot(caller_id, cli, dicts, worker, worker_queues):
    setattr(worker, "slotDict", dicts[worker._slot])
    worker_queues[worker._slot].append((cli, caller_id, worker))


def _serverLoop(dicts, threads, worker_queues, listener):
    clients = []
    while True:
        r, w, e = select.select((listener, ), (), (), 0.1)
        if listener in r:
            cli = listener.accept()
            clients.append(cli)
            logger.debug("Client accepted: %s" % cli)
            logger.debug("Nb clients connected: %s" % len(clients))
        for cli in clients:
            try:
                if cli.poll():
                    data = cli.recv()
                    if len(data) == 2:
                        caller_id, worker = data[0], data[1]
                        try:
                            dicts[worker._slot]
                        except KeyError:
                            if not isinstance(worker, Server._AppendSlotWorker):
                                logger.warning("Unknown slot '%s' for worker '%r', the missing slot "
                                               "will be created" % (worker._slot, worker))
                            _create_slot(worker._slot, dicts, threads, worker_queues)
                            _execWorkerInSlot(caller_id, cli, dicts, worker, worker_queues)
                        except AttributeError:
                            logger.warning("Worker '%r' has no _slot attribute" % worker)
                        else:
                            _execWorkerInSlot(caller_id, cli, dicts, worker, worker_queues)
            except (IOError, OSError, EOFError):
                clients.remove(cli)


def _create_slot(slot, slot_dicts, slot_threads, slot_worker_queues):
    slot_dicts[slot] = {}
    slot_worker_queues[slot] = []
    slot_threads[slot] = thread.start_new(slot_thread_fct, (slot, slot_worker_queues[slot]))


def _childProcess(port, slots):
    """
    This is the child process. It run endlessly waiting for incoming work
    requests.
    """
    slot_dicts = {}
    slot_threads = {}
    slot_worker_queues = {}
    try:
        if sys.platform == "win32":
            listener = Listener(('localhost', port))
        else:
            listener = Listener(('', port))
        #client = listener.accept()
    except :
        logger.warning("Failed to start the code completion server process on "
                       "port %d, there is probably another completion server "
                       "already running with a socket open on the same port..."
                       "The existing server process will be used instead." % port)
        return 0
    else:
        logger.debug("Code Completion Server started on 127.0.0.1:%d" % port)
        for slot in slots:
            _create_slot(slot, slot_dicts, slot_threads, slot_worker_queues)
        _serverLoop(slot_dicts, slot_threads, slot_worker_queues, listener)


def slot_thread_fct(slot, worker_queue):
    while True:
        if len(worker_queue):
            cli, caller_id, worker = worker_queue.pop(0)
            logger.debug("Running %r in slot '%s'" % (worker, slot))
            _execWorker(cli, caller_id, worker)
            logger.debug("Finished running %r in slot '%s'" % (worker, slot))
        else:
            time.sleep(0.001)


def _execWorker(conn, caller_id, worker):
    """
    This function call the worker object.

    :param conn: connection

    :param id: caller id

    :param worker: worker instance
    """
    try:
        results = worker(conn, caller_id)
    except Exception as e:
        logger.exception("SubprocessServer.Worker (%r)" % worker)
        results = []
    # reset obj attributes before sending it back to the main process
    worker.__dict__ = {}
    conn.send([caller_id, worker, results])


#
# Global server instance
#
_SERVER = None


def start_server(name="pyqode-server", port=8080, slots=None):
    """
    Starts the global subprocess server

    :param name: Process name
    :param port: Server port. Default is 8080
    """
    global _SERVER
    if "PYQODE_NO_COMPLETION_SERVER" in os.environ:
        return
    if _SERVER is None:
        _SERVER = Server(name=name, slots=slots)
        _SERVER.start(port=port)


def get_server():
    """
    Gets the global subprocess server
    """
    global _SERVER
    return _SERVER
