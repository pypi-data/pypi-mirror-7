# client.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2009 SKA South Africa (http://ska.ac.za/)
# BSD license - see COPYING for details
from __future__ import with_statement

"""Clients for the KAT device control language.
   """

import threading
import socket
import sys
import traceback
import select
import time
import logging
import errno
from .core import (DeviceMetaclass, MessageParser, Message, ExcepthookThread,
                   KatcpClientError, KatcpVersionError, ProtocolFlags,
                   SEC_TS_KATCP_MAJOR, FLOAT_TS_KATCP_MAJOR, SEC_TO_MS_FAC)


#logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("katcp")


class DeviceClient(object):
    """Device client proxy.

    Subclasses should implement .reply\_*, .inform\_* and
    send_request\_* methods to take actions when messages arrive,
    and implement unhandled_inform, unhandled_reply and
    unhandled_request to provide fallbacks for messages for
    which there is no handler.

    Request messages can be sent by calling .send_request().

    Parameters
    ----------
    host : string
        Host to connect to.
    port : int
        Port to connect to.
    tb_limit : int
        Maximum number of stack frames to send in error traceback.
    logger : object
        Python Logger object to log to.
    auto_reconnect : bool
        Whether to automatically reconnect if the connection dies.

    Examples
    --------
    >>> MyClient(DeviceClient):
    ...     def reply_myreq(self, msg):
    ...         print str(msg)
    ...
    >>> c = MyClient('localhost', 10000)
    >>> c.start()
    >>> c.send_request(katcp.Message.request('myreq'))
    >>> # expect reply to be printed here
    >>> # stop the client once we're finished with it
    >>> c.stop()
    >>> c.join()
    """

    __metaclass__ = DeviceMetaclass

    def __init__(self, host, port, tb_limit=20, logger=log,
                 auto_reconnect=True):
        self._parser = MessageParser()
        self._bindaddr = (host, port)
        self._tb_limit = tb_limit
        self._sock = None
        self._waiting_chunk = ""
        self._running = threading.Event()
        self._connected = threading.Event()
        self._received_protocol_info = threading.Event()
        self._send_lock = threading.Lock()
        self._thread = None
        self._logger = logger
        self._auto_reconnect = auto_reconnect
        self._connect_failures = 0
        self._server_supports_ids = False
        self._protocol_flags = None
        self._static_protocol_configuration = False

        # message id and lock
        self._last_msg_id = 0
        self._msg_id_lock = threading.Lock()

    @property
    def protocol_flags(self):
        return self._protocol_flags

    @protocol_flags.setter
    def protocol_flags(self, val):
        self._protocol_flags = val
        self._server_supports_ids = self.protocol_flags.supports(
            ProtocolFlags.MESSAGE_IDS)
        self._received_protocol_info.set()

    @property
    def bindaddr(self):
        return self._bindaddr

    def convert_seconds(self, time_seconds):
        """Convert a time in seconds to the device timestamp units

        KATCP v4 and earlier, specified all timestamps in milliseconds. Since
        KATCP v5, all timestamps are in seconds. If the device KATCP version has
        been detected, this method converts a value in seconds to the
        appropriate (seconds or milliseconds) quantity. For version smaller than
        V4, the time value will be truncated to the nearest millisecond.
        """
        if self.protocol_flags.major >= SEC_TS_KATCP_MAJOR:
            return time_seconds
        else:
            device_time = time_seconds * SEC_TO_MS_FAC
            if self.protocol_flags.major < FLOAT_TS_KATCP_MAJOR:
                device_time = int(device_time)
            return device_time

    def _next_id(self):
        """Return the next available message id."""
        self._msg_id_lock.acquire()
        try:
            self._last_msg_id += 1
            return str(self._last_msg_id)
        finally:
            self._msg_id_lock.release()

    def preset_protocol_flags(self, protocol_flags):
        """
        Preset server protocol flags.

        Sets the assumed server protocol flags and disables automatic server
        version detection.

        Parameters
        ----------

        protocol_flags : katcp.core.ProtocolFlags instance
        """
        self._static_protocol_configuration = True
        self.protocol_flags = protocol_flags

    def inform_version_connect(self, msg):
        """Process a #version-connect message."""
        if len(msg.arguments) < 2:
            return
        if msg.arguments[0] == "katcp-protocol":
            protocol_flags = ProtocolFlags.parse_version(msg.arguments[1])
            self._set_protocol_from_inform(protocol_flags, msg)

    def inform_version(self, msg):
        """Handle katcp v4 and below version inform"""
        self._set_v4_protocol(msg)

    def inform_build_state(self, msg):
        """Handle katcp v4 and below build-state inform"""
        self._set_v4_protocol(msg)

    def _set_v4_protocol(self, inform):
        # We don't know if the server supports multiple connections (katcp v4
        # has no way of indicating this), but this should not really make any
        # difference to the client
        protocol_flags = ProtocolFlags(4, 0, '')
        self._set_protocol_from_inform(protocol_flags, inform)

    def _set_protocol_from_inform(self, protocol_flags, inform):
        if protocol_flags == self.protocol_flags:
            # New value matches old, no need to do consistency checking
            return
        if self.protocol_flags:
            # It seems that the protocol flags have been set before. Now we need
            # to do some consistency checking.
            if self._static_protocol_configuration:
                # Only warn if a static protocol definition is used
                self._logger.warn(
                    'Protocol Version Warning: Ignoring inform received from '
                    'server indicating a katcp protocol revision inconsistent '
                    'with the static configuration. Static configuration: %r.'
                    'Inform received: %r' % (
                        str(self.protocol_flags), str(inform)))
                return
            else:
                # Log an error and disconnect if we are in auto-detection mode
                self._logger.error(
                    'Protocol Version Error: Inform received from '
                    'server indicating a katcp protocol revision inconsistent '
                    'with the previously detected version. Disconnecting in '
                    'disgust. Previous version: %r. Inform received: %r' % (
                        str(self.protocol_flags), str(inform)))
                # Prevent an infinite loop
                self._auto_reconnect = False
                self._disconnect()

        self.protocol_flags = protocol_flags

    def _get_mid_and_update_msg(self, msg, use_mid):
        """
        Get message ID for current request and assign to msg.mid if needed

        Parameters
        ----------
        msg : katcp.Message ?request message
        use_mid : bool or None

        If msg.mid is None, a new message ID will be created. msg.mid will be
        filled with this ID if use_mid is True or if use_mid is None and the
        server supports message ids. If msg.mid is already assigned, it will not
        be touched, and will be used as the active message ID

        Return value
        ------------
        The active message ID
        """
        if use_mid is None:
            use_mid = self._server_supports_ids

        if msg.mid is None:
            mid = self._next_id()
            if use_mid:
                msg.mid = mid
            # An internal mid may be needed for the request/inform/response machinery
            # to work, so we return it
            return mid
        else:
            return msg.mid

    def request(self, msg, use_mid=None, timeout=None):
        """
        Send a request message, automatically assign a message ID if requested

        Parameters
        ----------
        msg : katcp.Message request message
        use_mid : bool or None, default=None
        timeout : float or None, default=None
            Set timeout for sending request message, or None for no timeout

        Returns
        -------

        mid : string or None
            The message id, or None if no msg id is used

        If use_mid is None and the server supports msg ids, or if use_mid is
        True a message ID will automatically be assigned msg.mid is None.

        if msg.mid has a value, and the server supports msg ids, that value will
        be used. If the server does not support msg ids, KatcpVersionError will
        be raised
        """

        mid = self._get_mid_and_update_msg(msg, use_mid)
        self.send_request(msg, timeout=timeout)
        return mid

    def send_request(self, msg, timeout=None):
        """Send a request messsage.

        Parameters
        ----------
        msg : Message object
            The request Message to send.
        timeout : float or None, default=None
            Set timeout for sending request message, or None for no timeout
        """
        assert(msg.mtype == Message.REQUEST)
        if msg.mid and not self._server_supports_ids:
            raise KatcpVersionError
        self.send_message(msg, timeout=timeout)

    def send_message(self, msg, timeout=None):
        """Send any kind of message.

        Parameters
        ----------
        msg : Message object
            The message to send.
        timeout : float or None, default=None
            Set timeout for sending request message, or None for no timeout.
        """
        # TODO: should probably implement this as a queue of sockets and
        #       messages to send and have the queue processed in the main loop
        data = str(msg) + "\n"
        datalen = len(data)
        totalsent = 0
        sock = self._sock

        # Log all sent messages here so no one else has to.
        self._logger.debug(data)

        # do not do anything inside here which could call send_message!
        send_failed = False
        self._send_lock.acquire()
        t0 = time.time()
        e = 'unknown error'
        try:
            if sock is None:
                raise KatcpClientError("Client not connected")

            while totalsent < datalen:
                if timeout is not None and time.time() - t0 > timeout:
                    self._logger.warn('Timeout sending message')
                    send_failed = True
                    e = 'Could not send  message withing timeout {0}'.format(
                        timeout)
                    break
                try:
                    sent = sock.send(data[totalsent:])
                except socket.error, e:
                    if len(e.args) == 2 and e.args[0] == errno.EAGAIN and \
                            sock is self._sock:
                        continue
                    else:
                        send_failed = True
                        break

                if sent == 0:
                    send_failed = True
                    break

                totalsent += sent
        finally:
            self._send_lock.release()

        if send_failed:
            try:
                server_name = sock.getpeername()
            except socket.error:
                server_name = "<disconnected server>"
            msg = "Failed to send message to server %s (%s)" % (server_name, e)
            self._logger.error(msg)
            self._disconnect()

    def _connect(self):
        """Connect to the server."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(self._bindaddr)
            sock.setblocking(0)
            if hasattr(socket, 'TCP_NODELAY'):
                # our message packets are small, don't delay sending them.
                sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            if self._connect_failures >= 5:
                self._logger.warn("Reconnected to %r" % (self._bindaddr,))
            self._connect_failures = 0
        except Exception, e:
            self._connect_failures += 1
            if self._connect_failures % 5 == 0:
                # warn on every fifth failure
                self._logger.warn("Failed to connect to %r: %s" %
                                  (self._bindaddr, e))
            else:
                self._logger.debug("Failed to connect to %r: %s" %
                                   (self._bindaddr, e))
            sock.close()
            sock = None

        if sock is None:
            return

        self._sock = sock
        self._waiting_chunk = ""
        self._connected.set()

        try:
            self.notify_connected(True)
        except Exception:
            self._logger.exception("Notify connect failed. Disconnecting.")
            self._disconnect()

    def _disconnect(self):
        """Disconnect and cleanup."""
        # avoid disconnecting multiple times by immediately setting
        # self._sock to None
        sock = self._sock
        self._sock = None

        if sock is not None:
            sock.close()
            self._connected.clear()
            self.notify_connected(False)

    def _handle_chunk(self, chunk):
        """Handle a chunk of data from the server.

        Parameters
        ----------
        chunk : data
            The data string to process.
        """
        chunk = chunk.replace("\r", "\n")
        lines = chunk.split("\n")

        for line in lines[:-1]:
            full_line = self._waiting_chunk + line
            self._waiting_chunk = ""
            if full_line:
                try:
                    msg = self._parser.parse(full_line)
                # We do want to catch everything that inherits from Exception
                # pylint: disable-msg = W0703
                except Exception:
                    e_type, e_value, trace = sys.exc_info()
                    reason = "\n".join(traceback.format_exception(
                        e_type, e_value, trace, self._tb_limit))
                    self._logger.error("BAD COMMAND: %s" % (reason,))
                else:
                    self.handle_message(msg)

        self._waiting_chunk += lines[-1]

    def handle_message(self, msg):
        """Handle a message from the server.

        Parameters
        ----------
        msg : Message object
            The Message to dispatch to the handler methods.
        """
        # log messages received so that no one else has to
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(str(msg))

        if msg.mtype == Message.INFORM:
            self.handle_inform(msg)
        elif msg.mtype == Message.REPLY:
            self.handle_reply(msg)
        elif msg.mtype == Message.REQUEST:
            self.handle_request(msg)
        else:
            self._logger.error("Unexpected message type from server ['%s']."
                % (msg,))

    def handle_inform(self, msg):
        """Dispatch an inform message to the appropriate method.

        Parameters
        ----------
        msg : Message object
            The inform message to dispatch.
        """
        method = self.__class__.unhandled_inform
        if msg.name in self._inform_handlers:
            method = self._inform_handlers[msg.name]

        try:
            method(self, msg)
        except Exception:
            e_type, e_value, trace = sys.exc_info()
            reason = "\n".join(traceback.format_exception(
                e_type, e_value, trace, self._tb_limit))
            self._logger.error("Inform %s FAIL: %s" % (msg.name, reason))

    def handle_reply(self, msg):
        """Dispatch a reply message to the appropriate method.

        Parameters
        ----------
        msg : Message object
            The reply message to dispatch.
        """
        method = self.__class__.unhandled_reply
        if msg.name in self._reply_handlers:
            method = self._reply_handlers[msg.name]

        try:
            method(self, msg)
        except Exception:
            e_type, e_value, trace = sys.exc_info()
            reason = "\n".join(traceback.format_exception(
                e_type, e_value, trace, self._tb_limit))
            self._logger.error("Reply %s FAIL: %s" % (msg.name, reason))

    def handle_request(self, msg):
        """Dispatch a request message to the appropriate method.

        Parameters
        ----------
        msg : Message object
            The request message to dispatch.
        """
        method = self.__class__.unhandled_request
        if msg.name in self._request_handlers:
            method = self._request_handlers[msg.name]

        try:
            reply = method(self, msg)
            reply.mid = msg.mid
            assert (reply.mtype == Message.REPLY)
            assert (reply.name == msg.name)
            self._logger.info("%s OK" % (msg.name,))
            self.send_message(reply)
        # We do want to catch everything that inherits from Exception
        # pylint: disable-msg = W0703
        except Exception:
            e_type, e_value, trace = sys.exc_info()
            reason = "\n".join(traceback.format_exception(
                e_type, e_value, trace, self._tb_limit))
            self._logger.error("Request %s FAIL: %s" % (msg.name, reason))

    def unhandled_inform(self, msg):
        """Fallback method for inform messages without a registered handler

        Parameters
        ----------
        msg : Message object
            The inform message that wasn't processed by any handlers.
        """
        pass

    def unhandled_reply(self, msg):
        """Fallback method for reply messages without a registered handler

        Parameters
        ----------
        msg : Message object
            The reply message that wasn't processed by any handlers.
        """
        pass

    def unhandled_request(self, msg):
        """Fallback method for requests without a registered handler

        Parameters
        ----------
        msg : Message object
            The request message that wasn't processed by any handlers.
        """
        pass

    def run(self):
        """Process reply and inform messages from the server."""
        self._logger.debug("Starting thread %s" % (
                threading.currentThread().getName()))
        timeout = 0.5  # s

        # save globals so that the thread can run cleanly
        # even while Python is setting module globals to
        # None.
        _select = select.select
        _socket_error = socket.error
        _sleep = time.sleep

        if not self._auto_reconnect:
            self._connect()
            if not self.is_connected():
                raise KatcpClientError("Failed to connect to %r" %
                                       (self._bindaddr,))

        self._running.set()
        while self._running.isSet():
            # this is equivalent to self.is_connected()
            # but ensure we have a socket object and not
            # None for the select-and-read part of this loop
            sock = self._sock
            if sock is not None:
                try:
                    readers, _writers, errors = _select([sock], [], [sock],
                                                        timeout)
                except Exception, e:
                    # catch Exception because class of exception thrown
                    # various drastically between Mac and Linux
                    self._logger.debug("Select error: %s" % (e,))
                    errors = [sock]

                if errors:
                    self._disconnect()

                elif readers:
                    try:
                        chunk = sock.recv(4096)
                    except _socket_error:
                        # an error when sock was within ready list presumably
                        # means the client needs to be ditched.
                        chunk = ""
                    if chunk:
                        self._handle_chunk(chunk)
                    else:
                        # EOF from server
                        self._disconnect()
            else:
                # not currently connected so attempt to connect
                # if auto_reconnect is set
                if not self._auto_reconnect:
                    self._running.clear()
                    break
                else:
                    self._connect()
                    if not self.is_connected():
                        _sleep(timeout)

        self._disconnect()
        self._logger.debug("Stopping thread %s" % (
                threading.currentThread().getName()))

    def start(self, timeout=None, daemon=None, excepthook=None):
        """Start the client in a new thread.

        Parameters
        ----------
        timeout : float in seconds
            Seconds to wait for client thread to start.
        daemon : boolean
            If not None, the thread's setDaemon method is called with this
            parameter before the thread is started.
        excepthook : function
            Function to call if the client throws an exception. Signature
            is as for sys.excepthook.
        """
        if self._thread:
            raise RuntimeError("Device client already started.")

        self._thread = ExcepthookThread(target=self.run, excepthook=excepthook)
        if daemon is not None:
            self._thread.setDaemon(daemon)
        self._thread.start()
        if timeout:
            self._connected.wait(timeout)
            if not self._connected.isSet():
                raise RuntimeError("Device client failed to start.")

    def join(self, timeout=None):
        """Rejoin the client thread.

        Parameters
        ----------
        timeout : float in seconds
            Seconds to wait for thread to finish.
        """
        if not self._thread:
            raise RuntimeError("Device client thread not started.")

        self._thread.join(timeout)
        if not self._thread.isAlive():
            self._thread = None

    def stop(self, timeout=1.0):
        """Stop a running client (from another thread).

        Parameters
        ----------
        timeout : float in seconds
           Seconds to wait for client thread to have *started*.
        """
        self._running.wait(timeout)
        if not self._running.isSet():
            raise RuntimeError("Attempt to stop client that wasn't running.")
        self._running.clear()

    def running(self):
        """Whether the client is running.

        Returns
        -------
        running : bool
            Whether the client is running.
        """
        return self._running.isSet()

    def is_connected(self):
        """Check if the socket is currently connected.

        Returns
        -------
        connected : bool
            Whether the client is connected.
        """
        return self._sock is not None

    def wait_connected(self, timeout=None):
        """Wait until the client is connected.

        Parameters
        ----------
        timeout : float in seconds
            Seconds to wait for the client to connect.

        Returns
        -------
        connected : bool
            Whether the client is connected.
        """
        self._connected.wait(timeout)
        return self._connected.isSet()


    def wait_protocol(self, timeout=None):
        """Wait until katcp protocol information has been received from the client.

        Parameters
        ----------
        timeout : float in seconds
            Seconds to wait for the client to connect.

        Returns
        -------
        received : bool
            Whether protocol information was received

        If this method returns True, the server's protocol information is
        available in the ProtocolFlags instance self.protocol_flags.
        """
        self._received_protocol_info.wait(timeout)
        return self._received_protocol_info.isSet()

    def notify_connected(self, connected):
        """Event handler that is called whenever the connection status changes.

        Override in derived class for desired behaviour.

        .. note::

           This function should never block. Doing so will cause the client to
           cease processing data from the server until notify_connected
           completes.

        Parameters
        ----------
        connected : bool
            Whether the client has just connected (True) or just disconnected
            (False).
        """
        pass


class BlockingClient(DeviceClient):
    """Implement blocking requests on top of DeviceClient.

    This client will use message IDs if the server supports them.

    Parameters
    ----------
    host : string
        Host to connect to.
    port : int
        Port to connect to.
    tb_limit : int
        Maximum number of stack frames to send in error traceback.
    logger : object
        Python Logger object to log to.
    auto_reconnect : bool
        Whether to automatically reconnect if the connection dies.
    timeout : float in seconds
        Default number of seconds to wait before a blocking send_request times
        out. Can be overriden in individual calls to blocking_request.

    Examples
    --------
    >>> c = BlockingClient('localhost', 10000)
    >>> c.start()
    >>> reply, informs = c.blocking_request(katcp.Message.request('myreq'))
    >>> print reply
    >>> print [str(msg) for msg in informs]
    >>> c.stop()
    >>> c.join()
    """

    def __init__(self, host, port, tb_limit=20, timeout=5.0, logger=log,
                 auto_reconnect=True):
        super(BlockingClient, self).__init__(host, port, tb_limit=tb_limit,
                                             logger=logger,
                                             auto_reconnect=auto_reconnect)
        self._request_timeout = timeout

        self._request_end = threading.Event()
        self._request_lock = threading.Lock()
        self._current_name = None
        self._current_msg_id = None  # only used if server supports msg ids
        self._current_informs = None
        self._current_reply = None
        self._current_inform_count = None

    def _message_matches(self, msg):
        """Check whether message matches current request.

           Must be called with _request_lock held.
           """
        return ((self._current_msg_id is not None and
                 msg.mid == self._current_msg_id)
                or
                (self._current_msg_id is None and
                 msg.name == self._current_name))

    def blocking_request(self, msg, timeout=None, keepalive=False, use_mid=None):
        """Send a request messsage.

        Parameters
        ----------
        msg : Message object
            The request Message to send.
        timeout : float in seconds
            How long to wait for a reply. The default is the
            the timeout set when creating the BlockingClient.
        keepalive : boolean, optional
            Whether the arrival of an inform should
            cause the timeout to be reset.
        use_mid : boolean, optional
            Whether to use message IDs. Default is to use message IDs
            if the server supports them.

        Returns
        -------
        reply : Message object
            The reply message received.
        informs : list of Message objects
            A list of the inform messages received.
        """
        with self._request_lock:
            self._request_end.clear()
            self._current_name = msg.name
            self._current_informs = []
            self._current_reply = None
            self._current_inform_count = 0

        if timeout is None:
            timeout = self._request_timeout

        try:
            self._get_mid_and_update_msg(msg, use_mid)
            self._current_msg_id = msg.mid
            self.send_request(msg, timeout=timeout)
            while True:
                self._request_end.wait(timeout)
                if self._request_end.isSet() or not keepalive:
                    break
                new_inform_count = len(self._current_informs)
                if new_inform_count == self._current_inform_count:
                    # no new informs received either
                    break
                self._current_inform_count = new_inform_count
        finally:
            try:
                self._request_lock.acquire()

                success = self._request_end.isSet()
                informs = self._current_informs
                reply = self._current_reply

                self._request_end.clear()
                self._current_inform_count = None
                self._current_informs = None
                self._current_reply = None
                self._current_name = None
                self._current_msg_id = None
            finally:
                self._request_lock.release()

        if success:
            return reply, informs
        else:
            raise RuntimeError("Request %s timed out after %s seconds." %
                                (msg.name, timeout))

    def handle_inform(self, msg):
        """Handle inform messages related to any current requests.

        Inform messages not related to the current request go up to the
        base class method.

        Parameters
        ----------
        msg : Message object
            The inform message to handle.
        """
        try:
            self._request_lock.acquire()
            if self._message_matches(msg):
                self._current_informs.append(msg)
                return
        finally:
            self._request_lock.release()

        super(BlockingClient, self).handle_inform(msg)

    def handle_reply(self, msg):
        """Handle a reply message related to the current request.

        Reply messages not related to the current request go up to the
        base class method.

        Parameters
        ----------
        msg : Message object
            The reply message to handle.
        """
        try:
            self._request_lock.acquire()
            if self._message_matches(msg):
                # unset _current_name so that no more replies or informs
                # match this request
                self._current_name = None
                self._current_reply = msg
                self._request_end.set()
                return
        finally:
            self._request_lock.release()

        super(BlockingClient, self).handle_reply(msg)


class CallbackClient(DeviceClient):
    """Implement callback-based requests on top of DeviceClient.

    This client will use message IDs if the server supports them.

    Parameters
    ----------
    host : string
        Host to connect to.
    port : int
        Port to connect to.
    tb_limit : int, optional
        Maximum number of stack frames to send in error traceback. Default
        is 20.
    logger : object, optional
        Python Logger object to log to. Default is a logger named 'katcp'.
    auto_reconnect : bool, optional
        Whether to automatically reconnect if the connection dies. Default
        is True.
    timeout : float in seconds, optional
        Default number of seconds to wait before a callback callback_request times
        out. Can be overriden in individual calls to callback_request. Default is 5s.

    Examples
    --------
    >>> def reply_cb(msg):
    ...     print "Reply:", msg
    ...
    >>> def inform_cb(msg):
    ...     print "Inform:", msg
    ...
    >>> c = CallbackClient('localhost', 10000)
    >>> c.start()
    >>> c.callback_request(
    ...     katcp.Message.request('myreq'),
    ...     reply_cb=reply_cb,
    ...     inform_cb=inform_cb,
    ... )
    ...
    >>> # expect reply to be printed here
    >>> # stop the client once we're finished with it
    >>> c.stop()
    >>> c.join()
    """

    def __init__(self, host, port, tb_limit=20, timeout=5.0, logger=log,
                 auto_reconnect=True):
        super(CallbackClient, self).__init__(host, port, tb_limit=tb_limit,
                                             logger=logger,
                                             auto_reconnect=auto_reconnect)

        self._request_timeout = timeout

        # lock for checking and popping requests
        self._async_lock = threading.Lock()

        # pending requests
        # msg_id -> (request, reply_cb, inform_cb, user_data, timer)
        #           callback tuples
        self._async_queue = {}

        # stack mapping request names to a stack of message ids
        # msg_name -> [ list of msg_ids ]
        self._async_id_stack = {}

    def _push_async_request(self, msg_id, request, reply_cb, inform_cb,
                            user_data, timer):
        """Store the callbacks for a request we've sent so we
           can forward any replies and informs to them.
           """
        with self._async_lock:
            self._async_queue[msg_id] = (
                request, reply_cb, inform_cb, user_data, timer)
            if request.name in self._async_id_stack:
                self._async_id_stack[request.name].append(msg_id)
            else:
                self._async_id_stack[request.name] = [msg_id]

    def _pop_async_request(self, msg_id, msg_name):
        """Pop the set of callbacks for a request.

           Return tuple of Nones if callbacks already popped (or don't exist).
           """
        self._async_lock.acquire()
        try:
            if msg_id is None:
                msg_id = self._msg_id_for_name(msg_name)
            if msg_id in self._async_queue:
                callback_tuple = self._async_queue[msg_id]
                del self._async_queue[msg_id]
                self._async_id_stack[callback_tuple[0].name].remove(msg_id)
                return callback_tuple
            else:
                return None, None, None, None, None
        finally:
            self._async_lock.release()

    def _peek_async_request(self, msg_id, msg_name):
        """Peek at the set of callbacks for a request

           Return tuple of Nones if callbacks don't exist.
           """
        self._async_lock.acquire()
        try:
            if msg_id is None:
                msg_id = self._msg_id_for_name(msg_name)
            if msg_id in self._async_queue:
                return self._async_queue[msg_id]
            else:
                return None, None, None, None, None
        finally:
            self._async_lock.release()

    def _msg_id_for_name(self, msg_name):
        """Find the msg_id for a given request name.

           Should only be called while the async lock is acquired.

           Return None if no message id exists.
           """
        if msg_name in self._async_id_stack and self._async_id_stack[msg_name]:
            return self._async_id_stack[msg_name][0]

    def callback_request(self, msg, reply_cb=None, inform_cb=None,
                user_data=None, timeout=None, use_mid=None):
        """Send a request messsage.

        Parameters
        ----------
        msg : Message object
            The request message to send.
        reply_cb : function
            The reply callback with signature reply_cb(msg)
            or reply_cb(msg, \*user_data)
        inform_cb : function
            The inform callback with signature inform_cb(msg)
            or inform_cb(msg, \*user_data)
        user_data : tuple
            Optional user data to send to the reply and inform
            callbacks.
        timeout : float in seconds
            How long to wait for a reply. The default is the
            the timeout set when creating the CallbackClient.
        use_mid : boolean, optional
            Whether to use message IDs. Default is to use message IDs
            if the server supports them.
        """
        if timeout is None:
            timeout = self._request_timeout

        mid = self._get_mid_and_update_msg(msg, use_mid)

        if timeout is None: # deal with 'no timeout', i.e. None
            timer = None
        else:
            timer = threading.Timer(timeout, self._handle_timeout, (mid,))


        self._push_async_request(
            mid, msg, reply_cb, inform_cb, user_data, timer)
        if timer:
            timer.start()

        try:
            self.send_request(msg, timeout=timeout)
        except KatcpClientError, e:
            error_reply = Message.request(msg.name, "fail", str(e))
            error_reply.mid = mid
            self.handle_reply(error_reply)
            if isinstance(e, KatcpVersionError):
                raise


    def blocking_request(self, msg, timeout=None, use_mid=None):
        """Send a request messsage.

        Parameters
        ----------
        msg : Message object
            The request Message to send.
        timeout : float in seconds
            How long to wait for a reply. The default is the
            the timeout set when creating the CallbackClient.
        use_mid : boolean, optional
            Whether to use message IDs. Default is to use message IDs
            if the server supports them.

        Returns
        -------
        reply : Message object
            The reply message received.
        informs : list of Message objects
            A list of the inform messages received.
        """
        if timeout is None:
            timeout = self._request_timeout

        done = threading.Event()
        informs = []
        replies = []

        def reply_cb(msg):
            self._logger.debug('received reply %r', str(msg))
            replies.append(msg)
            done.set()

        def inform_cb(msg):
            self._logger.debug('received inform %r', str(msg))
            informs.append(msg)

        self.callback_request(msg, reply_cb=reply_cb, inform_cb=inform_cb,
                              timeout=timeout, use_mid=use_mid)
        ## We wait on the done event that should be set by the reply
        # handler callback. If this event does not occur within the
        # timeout it means something unexpected went wrong. We give it
        # an extra second to deal with (unlikely?) slowness in the
        # rest of the code
        extra_wait = 1
        wait_timeout = timeout
        if wait_timeout is not None:
            wait_timeout = wait_timeout + extra_wait
        done.wait(timeout=wait_timeout)
        if not done.isSet():
            raise RuntimeError('Unexpected error: Async request handler did '
                               'not call reply handler within timeout period')
        reply = replies[0]

        return reply, informs

    def handle_inform(self, msg):
        """Handle inform messages related to any current requests.

        Inform messages not related to the current request go up
        to the base class method.

        Parameters
        ----------
        msg : Message object
            The inform message to dispatch.
        """
        # this may also result in inform_cb being None if no
        # inform_cb was passed to the request method.
        if msg.mid is not None:
            _request, _reply_cb, inform_cb, user_data, _timer = \
                    self._peek_async_request(msg.mid, None)
        else:
            request, _reply_cb, inform_cb, user_data, _timer = \
                self._peek_async_request(None, msg.name)
            if request is not None and request.mid != None:
                # we sent a mid but this inform doesn't have one
                inform_cb, user_data = None, None

        if inform_cb is None:
            inform_cb = super(CallbackClient, self).handle_inform
            # override user_data since handle_inform takes no user_data
            user_data = None

        try:
            if user_data is None:
                inform_cb(msg)
            else:
                inform_cb(msg, *user_data)
        except Exception:
            e_type, e_value, trace = sys.exc_info()
            reason = "\n".join(traceback.format_exception(
                e_type, e_value, trace, self._tb_limit))
            self._logger.error("Callback inform %s FAIL: %s" %
                               (msg.name, reason))

    def _do_fail_callback(
            self, reason, msg, reply_cb, inform_cb, user_data, timer):
        """Do callback for a failed request"""
        # this may also result in reply_cb being None if no
        # reply_cb was passed to the request method

        if reply_cb is None:
            # this happens if no reply_cb was passed in to the request or
            return

        reason_msg = Message.reply(msg.name, "fail", reason)

        try:
            if user_data is None:
                reply_cb(reason_msg)
            else:
                reply_cb(reason_msg, *user_data)
        except Exception:
            e_type, e_value, trace = sys.exc_info()
            exc_reason = "\n".join(traceback.format_exception(
                e_type, e_value, trace, self._tb_limit))
            self._logger.error("Callback reply during failure %s, %s FAIL: %s" %
                               (reason, msg.name, exc_reason))

    def _handle_timeout(self, msg_id):
        """Handle a timed out callback request.

        Parameters
        ----------
        msg_id : uuid.UUID for message
            The name of the reply which was expected.
        """
        msg, reply_cb, inform_cb, user_data, timer  = \
            self._pop_async_request(msg_id, None)
        # We may have been racing with the actual reply handler if the reply
        # arrived close to the timeout expiry, which means the
        # self._pop_async_request() call gave us None's. In this case, just bail
        if timer is None:
            return

        reason = "Timed out after %f seconds" % timer.interval
        self._do_fail_callback(
            reason, msg, reply_cb, inform_cb, user_data, timer)

    def handle_reply(self, msg):
        """Handle a reply message related to the current request.

        Reply messages not related to the current request go up
        to the base class method.

        Parameters
        ----------
        msg : Message object
            The reply message to dispatch.
        """
        # this may also result in reply_cb being None if no
        # reply_cb was passed to the request method
        if not msg.mid is None:
            _request, reply_cb, _inform_cb, user_data, timer = \
                    self._pop_async_request(msg.mid, None)
        else:
            request, _reply_cb, _inform_cb, _user_data, timer = \
                self._peek_async_request(None, msg.name)
            if request is not None and request.mid == None:
                # we didn't send a mid so this is the request we want
                _request, reply_cb, _inform_cb, user_data, timer = \
                          self._pop_async_request(None, msg.name)
            else:
                reply_cb, user_data = None, None

        if timer is not None:
            timer.cancel()

        if reply_cb is None:
            reply_cb = super(CallbackClient, self).handle_reply
            # override user_data since handle_reply takes no user_data
            user_data = None

        try:
            if user_data is None:
                reply_cb(msg)
            else:
                reply_cb(msg, *user_data)
        except Exception:
            e_type, e_value, trace = sys.exc_info()
            reason = "\n".join(traceback.format_exception(
                e_type, e_value, trace, self._tb_limit))
            self._logger.error("Callback reply %s FAIL: %s" %
                               (msg.name, reason))

    def stop(self, *args, **kwargs):
        super(CallbackClient, self).stop(*args, **kwargs)
        # Stop all async timeout handlers
        with self._async_lock:
            for request_data in self._async_queue.values():
                timer = request_data[-1]   # Last one should be timeout timer
                if timer is not None:
                    timer.cancel()
                self._do_fail_callback('Client stopped before reply was received',
                                       *request_data)

    def join(self, timeout=None):
        with self._async_lock:
            for (_, _, _, _, timer) in self._async_queue.values():
                if timer is not None:
                    timer.join(timeout=timeout)
        super(CallbackClient, self).join(timeout=timeout)

def request_check(client, exception, *msg_parms, **kwargs):
    """Make a blocking_request to DeviceClient and raise an exception if reply is not ok

    Parameters
    ==========

    client : DeviceClient instance
    exception: Exception class to raise
    *msg_parms : Message parameters sent to the Message.request() call
    **kwargs : Keyword arguments
        Uses kwargs['timeout'], passed as timeout kwarg to client.blocking_request()
        Forwards kwargs['mid'] to the Message.request() call kwargs

    Return Value
    ============

    reply, informs, as returned by client.blocking_request

    Raises
    ======

    <exception> as in the parameters.
        <exception>('Unexpected failure with <client.name> <req message> request'
        is raised if reply.reply_ok() is False

    Notes
    =====

    A typical use-case for this function is to use functools.partial() to bind a
    particular client and exception. The resulting function can then be used instead of
    direct client.blocking_request() calls to automate error handling.
    """
    timeout = kwargs.get('timeout', None)
    req_msg = Message.request(*msg_parms)
    if timeout is not None:
        reply, informs = client.blocking_request(req_msg, timeout=timeout)
    else:
        reply, informs = client.blocking_request(req_msg)

    if not reply.reply_ok():
        raise exception('Unexpected failure reply "{2}"\n with device at {0}, '
                        'request \n"{1}"'
                        .format(':'.join(str(x) for x in client.bindaddr), req_msg, reply))
    return reply, informs
