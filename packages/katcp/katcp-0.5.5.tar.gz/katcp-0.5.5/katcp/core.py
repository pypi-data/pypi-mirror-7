# katcp.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4
# Copyright 2009 SKA South Africa (http://ska.ac.za/)
# BSD license - see COPYING for details

"""Utilities for dealing with KAT device control
language messages.
"""

import threading
import sys
import re
import time
import warnings

SEC_TO_MS_FAC = 1000
MS_TO_SEC_FAC = 1./1000
# The major version of the katcp protocol that is used by default
DEFAULT_KATCP_MAJOR = 5
# First major version to use seconds (in stead of milliseconds) for timestamps
SEC_TS_KATCP_MAJOR = 5
# First major version to allow floating point values for timestamps
FLOAT_TS_KATCP_MAJOR = 4
# First major version to support message IDs
MID_KATCP_MAJOR = 5
# First major version to support #version-connect informs
VERSION_CONNECT_KATCP_MAJOR = 5
# First major version to support #interface-changed informs
INTERFACE_CHANGED_KATCP_MAJOR = 5

def convert_method_name(prefix, name):
    """Convert a method name to the corresponding command name."""
    return name[len(prefix):].replace("_", "-")


class KatcpSyntaxError(ValueError):
    """Exception raised by parsers on encountering syntax errors."""

class KatcpClientError(Exception):
    """Raised by KATCP clients when errors occur."""

class KatcpVersionError(KatcpClientError):
    """
    Exception raised when a katcp feature not supported by the katcp version
    of the server/client is requested
    """

class Message(object):
    """Represents a KAT device control language message.

    Parameters
    ----------
    mtype : Message type constant
        The message type (request, reply or inform).
    name : str
        The message name.
    arguments : list of strings
        The message arguments.
    mid : str, digits only
        The message identifier. Replies and informs that
        are part of the reply to a request should have the
        same id as the request did.
    """

    # Message types
    REQUEST, REPLY, INFORM = range(3)

    # Reply codes
    # TODO: make use of reply codes in device client and server
    OK, FAIL, INVALID = "ok", "fail", "invalid"

    ## @brief Mapping from message type to string name for the type.
    TYPE_NAMES = {
        REQUEST: "REQUEST",
        REPLY: "REPLY",
        INFORM: "INFORM",
    }

    ## @brief Mapping from message type to type code character.
    TYPE_SYMBOLS = {
        REQUEST: "?",
        REPLY: "!",
        INFORM: "#",
    }

    # pylint fails to realise TYPE_SYMBOLS is defined
    # pylint: disable-msg = E0602

    ## @brief Mapping from type code character to message type.
    TYPE_SYMBOL_LOOKUP = dict((v, k) for k, v in TYPE_SYMBOLS.items())

    # pylint: enable-msg = E0602

    ## @brief Mapping from escape character to corresponding unescaped string.
    ESCAPE_LOOKUP = {
        "\\": "\\",
        "_": " ",
        "0": "\0",
        "n": "\n",
        "r": "\r",
        "e": "\x1b",
        "t": "\t",
        "@": "",
    }

    # pylint fails to realise ESCAPE_LOOKUP is defined
    # pylint: disable-msg = E0602

    ## @brief Mapping from unescaped string to corresponding escape character.
    REVERSE_ESCAPE_LOOKUP = dict((v, k) for k, v in ESCAPE_LOOKUP.items())

    # pylint: enable-msg = E0602

    ## @brief Regular expression matching all unescaped character.
    ESCAPE_RE = re.compile(r"[\\ \0\n\r\x1b\t]")

    ## @var mtype
    # @brief Message type.

    ## @var name
    # @brief Message name.

    ## @var arguments
    # @brief List of string message arguments.

    ## @brief Attempt to optimize messages by specifying attributes up front
    __slots__ = ["mtype", "name", "mid", "arguments"]

    def __init__(self, mtype, name, arguments=None, mid=None):
        self.mtype = mtype
        self.name = name

        if mid is None:
            self.mid = None
        else:
            self.mid = str(mid)

        if arguments is None:
            self.arguments = []
        else:
            self.arguments = [type(x) is float and repr(x) or str(x)
                              for x in arguments]

        # check message type

        if mtype not in self.TYPE_SYMBOLS:
            raise KatcpSyntaxError("Invalid command type %r." % (mtype,))

        # check message id

        if self.mid is not None and not self.mid.isdigit():
            raise KatcpSyntaxError("Invalid message id %r." % (mid,))

        # check command name validity

        if not name:
            raise KatcpSyntaxError("Command missing command name.")
        if not name.replace("-", "").isalnum():
            raise KatcpSyntaxError("Command name should consist only of"
                                " alphanumeric characters and dashes (got %r)."
                                % (name,))
        if not name[0].isalpha():
            raise KatcpSyntaxError("Command name should start with an"
                                " alphabetic character (got %r)."
                                % (name,))

    def copy(self):
        """Return a shallow copy of the message object and its arguments.

        Returns
        -------
        msg : Message
            A copy of the message object.
        """
        return Message(self.mtype, self.name, self.arguments)

    def __str__(self):
        """ Return Message serialized for transmission.

        Returns
        -------
        msg : str
           The message encoded as a ASCII string.
        """
        if self.arguments:
            escaped_args = [self.ESCAPE_RE.sub(self._escape_match, x)
                            for x in self.arguments]
            escaped_args = [x or "\\@" for x in escaped_args]
            arg_str = " " + " ".join(escaped_args)
        else:
            arg_str = ""

        if self.mid is not None:
            mid_str = "[%s]" % self.mid
        else:
            mid_str = ""

        return "%s%s%s%s" % (self.TYPE_SYMBOLS[self.mtype], self.name,
                             mid_str, arg_str)

    def __repr__(self):
        """ Return message displayed in a readable form
        """
        tp = self.TYPE_NAMES[self.mtype].lower()
        name = self.name
        if self.arguments:
            escaped_args = [self.ESCAPE_RE.sub(self._escape_match, x)
                            for x in self.arguments]
            for arg in escaped_args:
                if len(arg) > 10:
                    arg = arg[:10] + "..."
            args = "(" + ", ".join(escaped_args) + ")"
        else:
            args = ""
        return "<Message %s %s %s>" % (tp, name, args)

    def __eq__(self, other):
        if not isinstance(other, Message):
            return NotImplemented
        for name in self.__slots__:
            if getattr(self, name) != getattr(other, name):
                return False
        return True

    def __ne__(self, other):
        return not self == other

    def _escape_match(self, match):
        """Given a re.Match object, return the escape code for it."""
        return "\\" + self.REVERSE_ESCAPE_LOOKUP[match.group()]

    def reply_ok(self):
        """Return True if this is a reply and its first argument is 'ok'."""
        return (self.mtype == self.REPLY and self.arguments and
                self.arguments[0] == self.OK)

    # * and ** magic useful here
    # pylint: disable-msg = W0142

    @classmethod
    def request(cls, name, *args, **kwargs):
        """Helper method for creating request messages.

        Parameters
        ----------
        name : str
            The name of the message.
        args : list of strings
            The message arguments.
        """
        mid = kwargs.pop('mid', None)
        if len(kwargs) > 0:
            raise TypeError('Invalid keyword argument(s): %r' % kwargs)
        return cls(cls.REQUEST, name, args, mid)

    @classmethod
    def reply(cls, name, *args, **kwargs):
        """Helper method for creating reply messages.

        Parameters
        ----------
        name : str
            The name of the message.
        args : list of strings
            The message arguments.
        """
        mid = kwargs.pop('mid', None)
        if len(kwargs) > 0:
            raise TypeError('Invalid keyword argument(s): %r' % kwargs)
        return cls(cls.REPLY, name, args, mid)

    @classmethod
    def reply_to_request(cls, req_msg, *args):
        """Helper method for creating reply messages to a specific request.

        Copies the message name and message identifier from the request message

        Parameters
        ----------
        req_msg : katcp.core.Message instance
            The request message that this inform if in reply to
        args : list of strings
            The message arguments.
        """
        return cls(cls.REPLY, req_msg.name, args, req_msg.mid)


    @classmethod
    def inform(cls, name, *args, **kwargs):
        """Helper method for creating inform messages.

        Parameters
        ----------
        name : str
            The name of the message.
        args : list of strings
            The message arguments.
        """
        mid = kwargs.pop('mid', None)
        if len(kwargs) > 0:
            raise TypeError('Invalid keyword argument(s): %r' % kwargs)
        return cls(cls.INFORM, name, args, mid)

    @classmethod
    def reply_inform(cls, req_msg, *args):
        """Helper method for creating inform messages in reply to a request.

        Copies the message name and message identifier from the request message

        Parameters
        ----------
        req_msg : katcp.core.Message instance
            The request message that this inform if in reply to
        args : list of strings
            The message arguments except name
        """
        return cls(cls.INFORM, req_msg.name, args, req_msg.mid)

    # pylint: enable-msg = W0142


class MessageParser(object):
    """Parses lines into Message objects."""

    # We only want one public method
    # pylint: disable-msg = R0903

    ## @brief Copy of TYPE_SYMBOL_LOOKUP from Message.
    TYPE_SYMBOL_LOOKUP = Message.TYPE_SYMBOL_LOOKUP

    ## @brief Copy of ESCAPE_LOOKUP from Message.
    ESCAPE_LOOKUP = Message.ESCAPE_LOOKUP

    ## @brief Regular expression matching all special characters.
    SPECIAL_RE = re.compile(r"[\0\n\r\x1b\t ]")

    ## @brief Regular expression matching all escapes.
    UNESCAPE_RE = re.compile(r"\\(.?)")

    ## @brief Regular expresion matching KATCP whitespace (just space and tab)
    WHITESPACE_RE = re.compile(r"[ \t]+")

    ## @brief Regular expression matching name and ID
    NAME_RE = re.compile(
        r"^(?P<name>[a-zA-Z][a-zA-Z0-9\-]*)(\[(?P<id>[0-9]+)\])?$")

    def _unescape_match(self, match):
        """Given an re.Match, unescape the escape code it represents."""
        char = match.group(1)
        if char in self.ESCAPE_LOOKUP:
            return self.ESCAPE_LOOKUP[char]
        elif not char:
            raise KatcpSyntaxError("Escape slash at end of argument.")
        else:
            raise KatcpSyntaxError("Invalid escape character %r." % (char,))

    def _parse_arg(self, arg):
        """Parse an argument."""
        match = self.SPECIAL_RE.search(arg)
        if match:
            raise KatcpSyntaxError("Unescaped special %r." % (match.group(),))
        return self.UNESCAPE_RE.sub(self._unescape_match, arg)

    def parse(self, line):
        """Parse a line, return a Message.

        Parameters
        ----------
        line : str
            The line to parse (should not contain the terminating newline
            or carriage return).

        Returns
        -------
        msg : Message object
            The resulting Message.
        """
        # find command type and check validity
        if not line:
            raise KatcpSyntaxError("Empty message received.")

        type_char = line[0]
        if type_char not in self.TYPE_SYMBOL_LOOKUP:
            raise KatcpSyntaxError("Bad type character %r." % (type_char,))

        mtype = self.TYPE_SYMBOL_LOOKUP[type_char]

        # find command and arguments name
        # (removing possible empty argument resulting from whitespace at end
        #  of command)
        parts = self.WHITESPACE_RE.split(line)
        if not parts[-1]:
            del parts[-1]

        name = parts[0][1:]
        arguments = [self._parse_arg(x) for x in parts[1:]]

        # split out message id
        match = self.NAME_RE.match(name)
        if match:
            name = match.group('name')
            mid = match.group('id')
        else:
            raise KatcpSyntaxError("Bad message name (and possibly id) %r." %
                                   (name,))

        return Message(mtype, name, arguments, mid)


class ProtocolFlags(object):
    """Utility class for handling KATCP protocol flags.

    .. note::

       This class was introduced in katcp version 0.4.

    Currently understood flags are:

    * M - server supports multiple clients
    * I - server supports message identifiers

    Parameters
    ----------
    major : int
        Major version number.
    minor : int
        Minor version number.
    flags : set
        Set of supported flags.

    Attributes
    ----------
    multi_client : bool
        Whether the server the version string came from supports
        multiple clients.
    message_ids : bool
        Whether the server the version string came from supports
        message ids.
    """

    VERSION_RE = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)"
                            r"(-(?P<flags>.*))?$")

    # flags

    MULTI_CLIENT = 'M'
    MESSAGE_IDS = 'I'

    STRATEGIES_V4 = frozenset(['none', 'auto', 'period', 'event', 'differential'])
    STRATEGIES_V5 = STRATEGIES_V4 | frozenset(
        ['event-rate', 'differential-rate'])

    STRATEGIES_ALLOWED_BY_MAJOR_VERSION = {
        4: STRATEGIES_V4,
        5: STRATEGIES_V5
        }

    def __init__(self, major, minor, flags):
        self.major = major
        self.minor = minor
        self.flags = set(list(flags))
        self.multi_client = self.MULTI_CLIENT in self.flags
        self.message_ids = self.MESSAGE_IDS in self.flags
        if self.message_ids and self.major < MID_KATCP_MAJOR:
            raise ValueError(
                'MESSAGE_IDS is only supported in katcp v5 and newer')

    def strategy_allowed(self, strategy):
        return strategy in self.STRATEGIES_ALLOWED_BY_MAJOR_VERSION[self.major]

    def __eq__(self, other):
        if not isinstance(other, ProtocolFlags):
            return NotImplemented
        return (self.major == other.major and self.minor == other.minor
                and self.flags == other.flags)

    def __str__(self):
        flag_str = self.flags and ("-" + "".join(sorted(self.flags))) or ""
        return "%d.%d%s" % (self.major, self.minor, flag_str)

    def supports(self, flag):
        return flag in self.flags

    @classmethod
    def parse_version(cls, version_str):
        """Create a :class:`ProtocolFlags` object from a version string.

        Parameters
        ----------
        version_str : str
            The version string from a #version-connect katcp-protocol
            message.
        """
        match = cls.VERSION_RE.match(version_str)
        if match:
            major = int(match.group('major'))
            minor = int(match.group('minor'))
            flags = set(match.group('flags') or '')
        else:
            major, minor, flags = None, None, set()
        return cls(major, minor, flags)


class DeviceMetaclass(type):
    """Metaclass for DeviceServer and DeviceClient classes.

       Collects up methods named request\_* and adds
       them to a dictionary of supported methods on the class.
       All request\_* methods must have a doc string so that help
       can be generated.  The same is done for inform\_* and
       reply\_* methods.
       """

    def __init__(mcs, name, bases, dct):
        """Constructor for DeviceMetaclass.  Should not be used directly.

        Parameters
        ----------
        mcs : class
            The metaclass instance
        name : str
            The metaclass name
        bases : list of classes
            List of base classes
        dct : dict
            Class dictionary
        """
        super(DeviceMetaclass, mcs).__init__(name, bases, dct)
        mcs._request_handlers = {}
        mcs._inform_handlers = {}
        mcs._reply_handlers = {}

        for name in dir(mcs):
            if not callable(getattr(mcs, name)):
                continue
            if name.startswith("request_"):
                request_name = convert_method_name("request_", name)
                mcs._request_handlers[request_name] = getattr(mcs, name)
                assert(mcs._request_handlers[request_name].__doc__ is not None)
            elif name.startswith("inform_"):
                inform_name = convert_method_name("inform_", name)
                mcs._inform_handlers[inform_name] = getattr(mcs, name)
                assert(mcs._inform_handlers[inform_name].__doc__ is not None)
                # There is a bit of a name colission between the reply_*
                # convention and the server reply_inform() method
            elif name.startswith("reply_") and name != 'reply_inform':
                reply_name = convert_method_name("reply_", name)
                mcs._reply_handlers[reply_name] = getattr(mcs, name)
                assert(mcs._reply_handlers[reply_name].__doc__ is not None)


class KatcpDeviceError(Exception):
    """Raised by KATCP servers when errors occur.

    .. versionchanged:: 0.1
        Deprecated in 0.1. Servers should not raise errors if communication
        with a client fails -- errors are simply logged instead.
    """
    pass


class FailReply(Exception):
    """Raised by request handlers to indicate a failure.

    A custom exception which, when thrown in a request handler,
    causes DeviceServerBase to send a fail reply with the specified
    fail message, bypassing the generic exception handling, which
    would send a fail reply with a full traceback.

    Examples
    --------
    >>> class MyDevice(DeviceServer):
    ...     def request_myreq(self, req, msg):
    ...         raise FailReply("This request always fails.")
    ...
    """
    pass


class AsyncReply(Exception):
    """Raised by a request handlers to indicate it will reply later.

    A custom exception which, when thrown in a request handler,
    indicates to DeviceServerBase that no reply has been returned
    by the handler but that the handler has arranged for a reply
    message to be sent at a later time.

    Examples
    --------
    >>> class MyDevice(DeviceServer):
    ...     def request_myreq(self, req, msg):
    ...         self.callback_client.request(
    ...             Message.request("otherreq"),
    ...             reply_cb=self._send_reply,
    ...         )
    ...         raise AsyncReply()
    ...

    """
    pass


class ExcepthookThread(threading.Thread):
    """A custom Thread class that provides an exception hook.

    Exceptions are passed up to an excepthook callable that
    functions like sys.excepthook.

    Parameters
    ----------
    excepthook : callable
        Function to call when the thread raises an unhandled
        exception. The signature is the same as for sys.excepthook.
    args : additional arguments
        Passed to the threading.Thread constructor.
    kwargs: additional keyword arguments
        Passed to the threading.Thread constructor.
    """
    def __init__(self, excepthook=None, *args, **kwargs):
        if excepthook is None:
            excepthook = getattr(threading.currentThread(), "_excepthook",
                                 None)
        self._excepthook = excepthook
        # evil hack to support subclasses that override run
        self._old_run = self.run
        self.run = self._wrapped_run
        super(ExcepthookThread, self).__init__(*args, **kwargs)

    def _wrapped_run(self):
        try:
            self._old_run()
        except:
            if self._excepthook is not None:
                self._excepthook(*sys.exc_info())
            else:
                raise


from .kattypes import Int, Float, Bool, Discrete, Lru, Str, Timestamp, Address


class Sensor(object):
    """Instantiate a new sensor object.

    Subclasses will usually pass in a fixed sensor_type which should
    be one of the sensor type constants. The list params if set will
    have its values formatter by the type formatter for the given
    sensor type.

    .. note::

       The LRU sensor type was deprecated in katcp 0.4.

    .. note::

       The ADDRESS sensor type was added in katcp 0.4.

    Parameters
    ----------
    sensor_type : Sensor type constant
        The type of sensor.
    name : str
        The name of the sensor.
    description : str
        A short description of the sensor.
    units : str
        The units of the sensor value. May be the empty string
        if there are no applicable units.
    params : list
        Additional parameters, dependent on the type of sensor:

          * For :const:`INTEGER` and :const:`FLOAT` the list should
            give the minimum and maximum that define the range
            of the sensor value.
          * For :const:`DISCRETE` the list should contain all
            possible values the sensor may take.
          * For all other types, params should be omitted.
    default : object
        An initial value for the sensor. By default this is
        determined by the sensor type.
    """

    # Sensor needs the instance attributes it has and
    # is an abstract class used only outside this module
    # pylint: disable-msg = R0902

    # Type names and formatters
    #
    # Formatters take the sensor object and the value to
    # be formatted as arguments. They may raise exceptions
    # if the value cannot be formatted.
    #
    # Parsers take the sensor object and the value to
    # parse as arguments
    #
    # type -> (name, formatter, parser)
    (INTEGER, FLOAT, BOOLEAN, LRU, DISCRETE, STRING, TIMESTAMP,
     ADDRESS) = range(8)

    ## @brief Mapping from sensor type to tuple containing the type name,
    #  a kattype with functions to format and parse a value and a
    #  default value for sensors of that type.
    SENSOR_TYPES = {
        INTEGER: (Int, 0),
        FLOAT: (Float, 0.0),
        BOOLEAN: (Bool, False),
        LRU: (Lru, Lru.LRU_NOMINAL),
        DISCRETE: (Discrete, "unknown"),
        STRING: (Str, ""),
        TIMESTAMP: (Timestamp, 0.0),
        ADDRESS: (Address, Address.NULL),
    }

    SENSOR_SHORTCUTS = {
        int: INTEGER,
        float: FLOAT,
        str: STRING,
        bool: BOOLEAN,
      }

    # map type strings to types
    SENSOR_TYPE_LOOKUP = dict((v[0].name, k) for k, v in SENSOR_TYPES.items())

    # Sensor status constants
    UNKNOWN, NOMINAL, WARN, ERROR, FAILURE, UNREACHABLE, INACTIVE = range(7)

    ## @brief Mapping from sensor status to status name.
    STATUSES = {
        UNKNOWN: 'unknown',
        NOMINAL: 'nominal',
        WARN: 'warn',
        ERROR: 'error',
        FAILURE: 'failure',
        UNREACHABLE: 'unreachable',
        INACTIVE: 'inactive',
    }

    ## @brief Mapping from status name to sensor status.
    STATUS_NAMES = dict((v, k) for k, v in STATUSES.items())

    # LRU sensor values
    LRU_NOMINAL, LRU_ERROR = Lru.LRU_NOMINAL, Lru.LRU_ERROR

    ## @brief Mapping from LRU value constant to LRU value name.
    LRU_VALUES = Lru.LRU_VALUES

    # LRU_VALUES not found by pylint
    # pylint: disable-msg = E0602

    ## @brief Mapping from LRU value name to LRU value constant.
    LRU_CONSTANTS = dict((v, k) for k, v in LRU_VALUES.items())

    # pylint: enable-msg = E0602

    ## @brief kattype Timestamp instance for encoding and decoding timestamps
    TIMESTAMP_TYPE = Timestamp()

    ## @var stype
    # @brief Sensor type constant.

    ## @var name
    # @brief Sensor name.

    ## @var description
    # @brief String describing the sensor.

    ## @var units
    # @brief String contain the units for the sensor value.

    ## @var params
    # @brief List of strings containing the additional parameters (length and
    #        interpretation are specific to the sensor type)

    def __init__(self, sensor_type, name, description=None, units='', params=None,
                 default=None):
        if params is None:
            params = []

        sensor_type = self.SENSOR_SHORTCUTS.get(sensor_type, sensor_type)

        self._sensor_type = sensor_type
        self._observers = set()

        typeclass, default_value = self.SENSOR_TYPES[sensor_type]

        if self._sensor_type in [Sensor.INTEGER, Sensor.FLOAT]:
            # as of version 5 of the guidelines, integer and float
            # ranges are optional and informational
            if len(params) == 2:
                if not params[0] <= default_value <= params[1]:
                    default_value = params[0]
            self._kattype = typeclass()
        elif self._sensor_type == Sensor.DISCRETE:
            default_value = params[0]
            self._kattype = typeclass(params)
        else:
            if self._sensor_type == Sensor.TIMESTAMP and units:
                raise ValueError(
                    'Units cannot be specified for TIMESTAMP sensors since '
                    'their units is defined by the KATCP spec as either '
                    'seconds or, for katcp versions 4 and below, milliseconds')
            self._kattype = typeclass()

        if default is not None:
            default_value = default

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # self._value_tuple should also be set and read in a single
        # bytecode to avoid situations were an update in one thread
        # causes another thread to read the timestamp from one update
        # and the value and/or status from a different update.
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        self._value_tuple = (time.time(), Sensor.UNKNOWN, default_value)
        self._formatter = self._kattype.pack
        self._parser = self._kattype.unpack
        self.stype = self._kattype.name

        self.name = name
        if description is None:
            description = '%(type)s sensor %(name)r %(unit_description)s' % dict(
               type=self.stype.capitalize(), name=self.name,
               unit_description=('in unit '+units if units else 'with no unit'))

        self.description = description
        self.units = units
        self.params = params
        self.formatted_params = [self._formatter(p, True) for p in params]

    # support for legacy KATCP users that relied on being able to
    # read _timestamp, _status and _value. Such usage will be
    # deprecated in a future version of KATCP.

    def _value_tuple_getter(i, name):
        def getter(self):
            warnings.warn("Use of katcp.Sensor.%s attribute is deprecated"
                          % name, DeprecationWarning)
            return self._value_tuple[i]
        return getter

    _timestamp = property(_value_tuple_getter(0, "_timestamp"))
    _status = property(_value_tuple_getter(1, "_status"))
    _value = property(_value_tuple_getter(2, "_value"))

    del _value_tuple_getter

    def __repr__(self):
        cls = self.__class__
        return "<%s.%s object name=%r at 0x%x>" % \
               (cls.__module__, cls.__name__, self.name, id(self))

    @classmethod
    def integer(cls, name, description=None, unit='', params=None, default=None):
        """
        Instantiate a new integer sensor object.

        name : str
            The name of the sensor.
        description : str
            A short description of the sensor.
        units : str
            The units of the sensor value. May be the empty string
            if there are no applicable units.
        params : list
            [min, max] -- miniumum and maximum values of the sensor
        default : int
            An initial value for the sensor. Defaults to 0.
        """
        return cls(cls.INTEGER, name, description, unit, params, default)

    @classmethod
    def float(cls, name, description=None, unit='', params=None, default=None):
        """
        Instantiate a new float sensor object.

        name : str
            The name of the sensor.
        description : str
            A short description of the sensor.
        units : str
            The units of the sensor value. May be the empty string
            if there are no applicable units.
        params : list
            [min, max] -- miniumum and maximum values of the sensor
        default : float
            An initial value for the sensor. Defaults to 0.0.
        """
        return cls(cls.FLOAT, name, description, unit, params, default)

    @classmethod
    def boolean(cls, name, description=None, unit='', default=None):
        """
        Instantiate a new boolean sensor object.

        name : str
            The name of the sensor.
        description : str
            A short description of the sensor.
        units : str
            The units of the sensor value. May be the empty string
            if there are no applicable units.
        default : bool
            An initial value for the sensor. Defaults to False.
        """
        return cls(cls.BOOLEAN, name, description, unit, None, default)

    @classmethod
    def lru(cls, name, description=None, unit='', default=None):
        """
        Instantiate a new lru sensor object.

        name : str
            The name of the sensor.
        description : str
            A short description of the sensor.
        units : str
            The units of the sensor value. May be the empty string
            if there are no applicable units.
        default : enum, Sensor.LRU_*
            An initial value for the sensor. Defaults to self.LRU_NOMINAL
        """
        return cls(cls.LRU, name, description, unit, None, default)

    @classmethod
    def string(cls, name, description=None, unit='', default=None):
        """
        Instantiate a new string sensor object.

        name : str
            The name of the sensor.
        description : str
            A short description of the sensor.
        units : str
            The units of the sensor value. May be the empty string
            if there are no applicable units.
        default : string
            An initial value for the sensor. Defaults to the empty string.
        """
        return cls(cls.STRING, name, description, unit, None, default)

    @classmethod
    def discrete(cls, name, description=None, unit='', params=None, default=None):
        """
        Instantiate a new discrete sensor object.

        name : str
            The name of the sensor.
        description : str
            A short description of the sensor.
        units : str
            The units of the sensor value. May be the empty string
            if there are no applicable units.
        params : [str]
            Sequence of all allowable discrete sensor states
        default : str
            An initial value for the sensor. Defaults to the first item
            of params
        """
        return cls(cls.DISCRETE, name, description, unit, params, default)

    @classmethod
    def timestamp(cls, name, description=None, unit='', default=None):
        """
        Instantiate a new timestamp sensor object.

        name : str
            The name of the sensor.
        description : str
            A short description of the sensor.
        units : str
            The units of the sensor value. For timestamp sensor may only be the
            empty string.
        default : string
            An initial value for the sensor in seconds since the Unix Epoch.
            Defaults to 0.
        """
        return cls(cls.TIMESTAMP, name, description, unit, None, default)

    @classmethod
    def address(cls, name, description=None, unit='', default=None):
        """
        Instantiate a new IP address sensor object.

        name : str
            The name of the sensor.
        description : str
            A short description of the sensor.
        units : str
            The units of the sensor value. May be the empty string
            if there are no applicable units.
        default : (string, int)
            An initial value for the sensor. Tuple contaning (host, port).
            default is ("0.0.0.0", None)
        """
        return cls(cls.ADDRESS, name, description, unit, None, default)


    def attach(self, observer):
        """Attach an observer to this sensor.

        The observer must support a call to observer.update(sensor).

        Parameters
        ----------
        observer : object
            Object with an .update(sensor) method that will be called
            when the sensor value is set.
        """
        self._observers.add(observer)

    def detach(self, observer):
        """Detach an observer from this sensor.

        Parameters
        ----------
        observer : object
            The observer to remove from the set of observers notified
            when the sensor value is set.
        """
        self._observers.discard(observer)

    def notify(self):
        """Notify all observers of changes to this sensor."""
        # copy list before iterating in case new observers arrive
        for o in list(self._observers):
            o.update(self)

    def parse_value(self, s_value, katcp_major=DEFAULT_KATCP_MAJOR):
        """Parse a value from a string.

        Parameters
        ----------
        s_value : str
            A string value to attempt to convert to a value for
            the sensor.

        Returns
        -------
        value : object
            A value of a type appropriate to the sensor.
        """
        return self._parser(s_value, katcp_major)

    def set(self, timestamp, status, value):
        """Set the current value of the sensor.

        Parameters
        ----------
        timestamp : float in seconds
           The time at which the sensor value was determined.
        status : Sensor status constant
            Whether the value represents an error condition or not.
        value : object
            The value of the sensor (the type should be appropriate to the
            sensor's type).
        """
        self._value_tuple = (timestamp, status, value)
        self.notify()

    def set_formatted(self, raw_timestamp, raw_status, raw_value,
                      major=DEFAULT_KATCP_MAJOR):
        """Set the current value of the sensor.

        Parameters
        ----------
        timestamp : str
            KATCP formatted timestamp string
        status : str
            KATCP formatted sensor status string
        value : str
            KATCP formatted sensor value
        major : int, default = 5
            KATCP major version to use for interpreting the raw values
        """
        timestamp = self.TIMESTAMP_TYPE.decode(raw_timestamp, major)
        status = self.STATUS_NAMES[raw_status]
        value = self.parse_value(raw_value, major)
        self.set(timestamp, status, value)

    def read_formatted(self, major=DEFAULT_KATCP_MAJOR):
        """Read the sensor and return a timestamp, status, value tuple.

        All values are strings formatted as specified in the Sensor Type
        Formats in the katcp specification.

        Parameters
        ----------
        major : int. Defaults to latest implemented KATCP version (5)
            Major version of KATCP to use when interpreting types

        Returns
        -------
        timestamp : str
            KATCP formatted timestamp string
        status : str
            KATCP formatted sensor status string
        value : str
            KATCP formatted sensor value
        """
        timestamp, status, value = self.read()
        return (self.TIMESTAMP_TYPE.encode(timestamp, major),
                self.STATUSES[status],
                self._formatter(value, True, major))

    def read(self):
        """Read the sensor and return a timestamp, status, value tuple.

        Returns
        -------
        timestamp : float in seconds
           The time at which the sensor value was determined.
        status : Sensor status constant
            Whether the value represents an error condition or not.
        value : object
            The value of the sensor (the type will be appropriate to the
            sensor's type).
        """
        return self._value_tuple

    def set_value(self, value, status=NOMINAL, timestamp=None,
                  major=DEFAULT_KATCP_MAJOR):
        """Check and then set the value of the sensor.

        Parameters
        ----------
        value : object
            Value of the appropriate type for the sensor.
        status : Sensor status constant
            Whether the value represents an error condition or not.
        timestamp : float in seconds or None
           The time at which the sensor value was determined. Uses current time
           if None.
        major : int. Defaults to latest implemented KATCP version (5)
            Major version of KATCP to use when interpreting types
        """
        self._kattype.check(value, major)
        if timestamp is None:
            timestamp = time.time()
        self.set(timestamp, status, value)

    def value(self):
        """Read the current sensor value.

        Returns
        -------
        value : object
            The value of the sensor (the type will be appropriate to the
            sensor's type).
        """
        return self.read()[2]

    @classmethod
    def parse_type(cls, type_string):
        """Parse KATCP formatted type code into Sensor type constant.

        Parameters
        ----------
        type_string : str
            KATCP formatted type code.

        Returns
        -------
        sensor_type : Sensor type constant
            The corresponding Sensor type constant.
        """
        if type_string in cls.SENSOR_TYPE_LOOKUP:
            return cls.SENSOR_TYPE_LOOKUP[type_string]
        else:
            raise KatcpSyntaxError("Invalid sensor type string %s" %
                                   type_string)

    @classmethod
    def parse_params(cls, sensor_type, formatted_params,
                     major=DEFAULT_KATCP_MAJOR):
        """Parse KATCP formatted parameters into Python values.

        Parameters
        ----------
        sensor_type : Sensor type constant
            The type of sensor the parameters are for.
        formatted_params : list of strings
            The formatted parameters that should be parsed.
        major : int. Defaults to latest implemented KATCP version (5)
            Major version of KATCP to use when interpreting types

        Returns
        -------
        params : list of objects
            The parsed parameters.
        """
        typeclass, _value = cls.SENSOR_TYPES[sensor_type]
        if sensor_type == cls.DISCRETE:
            kattype = typeclass([])
        else:
            kattype = typeclass()
        return [kattype.decode(x, major) for x in formatted_params]
