import datetime
import decimal
import math

from psycopg2cffi._impl.libpq import libpq, ffi
from psycopg2cffi._impl.exceptions import ProgrammingError
from psycopg2cffi._config import PG_VERSION
from psycopg2cffi.tz import LOCAL as TZ_LOCAL


adapters = {}


class _BaseAdapter(object):
    def __init__(self, wrapped_object):
        self._wrapped = wrapped_object
        self._conn = None

    def __str__(self):
        return self.getquoted()

    @property
    def adapted(self):
        return self._wrapped


class ISQLQuote(_BaseAdapter):
    def getquoted(self):
        pass


class AsIs(_BaseAdapter):
    def getquoted(self):
        return str(self._wrapped)


class Binary(_BaseAdapter):
    def prepare(self, connection):
        self._conn = connection

    def __conform__(self, proto):
        return self

    def getquoted(self):
        if self._wrapped is None:
            return 'NULL'

        to_length = ffi.new('size_t *')
        _wrapped = ffi.new('unsigned char[]', str(self._wrapped))
        if self._conn:
            data_pointer = libpq.PQescapeByteaConn(
                self._conn._pgconn, _wrapped, len(self._wrapped), to_length)
        else:
            data_pointer = libpq.PQescapeBytea(
                _wrapped, len(self._wrapped), to_length)

        data = ffi.string(data_pointer)[:to_length[0] - 1]
        libpq.PQfreemem(data_pointer)

        if self._conn and self._conn._equote:
            return r"E'%s'::bytea" % data

        return r"'%s'::bytea" % data


class Boolean(_BaseAdapter):
    def getquoted(self):
        return 'true' if self._wrapped else 'false'


class DateTime(_BaseAdapter):
    def getquoted(self):
        obj = self._wrapped
        if isinstance(obj, datetime.timedelta):
            us = str(obj.microseconds)
            us = '0' * (6 - len(us)) + us
            return "'%d days %d.%s seconds'::interval" % (
                obj.days, obj.seconds, us)
        else:
            iso = obj.isoformat()
            if isinstance(obj, datetime.datetime):
                format = 'timestamp'
                if getattr(obj, 'tzinfo', None):
                    format = 'timestamptz'
            elif isinstance(obj, datetime.time):
                format = 'time'
            else:
                format = 'date'
            return "'%s'::%s" % (str(iso), format)


def Date(year, month, day):
    date = datetime.date(year, month, day)
    return DateTime(date)


def DateFromTicks(ticks):
    date = datetime.datetime.fromtimestamp(ticks).date()
    return DateTime(date)


class Decimal(_BaseAdapter):
    def getquoted(self):
        if self._wrapped.is_finite():
            value = str(self._wrapped)

            # Prepend a space in front of negative numbers
            if value.startswith('-'):
                value = ' ' + value
            return value
        return "'NaN'::numeric"


class Float(ISQLQuote):
    def getquoted(self):
        n = float(self._wrapped)
        if math.isnan(n):
            return "'NaN'::float"
        elif math.isinf(n):
            if n > 0:
                return "'Infinity'::float"
            else:
                return "'-Infinity'::float"
        else:
            value = repr(self._wrapped)

            # Prepend a space in front of negative numbers
            if value.startswith('-'):
                value = ' ' + value
            return value


class Int(_BaseAdapter):
    def getquoted(self):
        value = str(self._wrapped)

        # Prepend a space in front of negative numbers
        if value.startswith('-'):
            value = ' ' + value
        return value


class List(_BaseAdapter):

    def prepare(self, connection):
        self._conn = connection

    def getquoted(self):
        length = len(self._wrapped)
        if length == 0:
            return "'{}'"

        quoted = [None] * length
        for i in xrange(length):
            obj = self._wrapped[i]
            quoted[i] = str(_getquoted(obj, self._conn))
        return "ARRAY[%s]" % ", ".join(quoted)


class Long(_BaseAdapter):
    def getquoted(self):
        value = str(self._wrapped)

        # Prepend a space in front of negative numbers
        if value.startswith('-'):
            value = ' ' + value
        return value


def Time(hour, minutes, seconds, tzinfo=None):
    time = datetime.time(hour, minutes, seconds, tzinfo=tzinfo)
    return DateTime(time)


def TimeFromTicks(ticks):
    time = datetime.datetime.fromtimestamp(ticks).time()
    return DateTime(time)


def Timestamp(year, month, day, hour, minutes, seconds, tzinfo=None):
    dt = datetime.datetime(
        year, month, day, hour, minutes, seconds, tzinfo=tzinfo)
    return DateTime(dt)


def TimestampFromTicks(ticks):
    dt = datetime.datetime.fromtimestamp(ticks, TZ_LOCAL)
    return DateTime(dt)


class QuotedString(_BaseAdapter):
    def __init__(self, obj):
        super(QuotedString, self).__init__(obj)
        self._default_encoding = "latin1"

    def prepare(self, conn):
        self._conn = conn

    @property
    def encoding(self):
        if self._conn:
            return self._conn._py_enc
        else:
            return self._default_encoding

    def getquoted(self):
        obj = self._wrapped
        if isinstance(self._wrapped, unicode):
            obj = obj.encode(self.encoding)
        string = str(obj)
        length = len(string)

        if not self._conn:
            to = ffi.new('char []', ((length * 2) + 1))
            libpq.PQescapeString(to, string, length)
            return "'%s'" % ffi.string(to)

        if PG_VERSION < 0x090000:
            to = ffi.new('char []', ((length * 2) + 1))
            err = ffi.new('int *')
            libpq.PQescapeStringConn(
                self._conn._pgconn, to, string, length, err)

            if self._conn and self._conn._equote:
                return "E'%s'" % ffi.string(to)
            return "'%s'" % ffi.string(to)

        data_pointer = libpq.PQescapeLiteral(
            self._conn._pgconn, string, length)
        data = ffi.string(data_pointer)
        libpq.PQfreemem(data_pointer)
        return data


def adapt(value, proto=ISQLQuote, alt=None):
    """Return the adapter for the given value"""
    obj_type = type(value)
    try:
        return adapters[(obj_type, proto)](value)
    except KeyError:
        for subtype in obj_type.mro()[1:]:
            try:
                return adapters[(subtype, proto)](value)
            except KeyError:
                pass

    conform = getattr(value, '__conform__', None)
    if conform is not None:
        return conform(proto)
    raise ProgrammingError("can't adapt type '%s'" % obj_type.__name__)


def _getquoted(param, conn):
    """Helper method"""
    if param is None:
        return 'NULL'
    adapter = adapt(param)
    try:
        adapter.prepare(conn)
    except AttributeError:
        pass
    return adapter.getquoted()


built_in_adapters = {
    bool: Boolean,
    str: QuotedString,
    unicode: QuotedString,
    list: List,
    bytearray: Binary,
    buffer: Binary,
    int: Int,
    long: Long,
    float: Float,
    datetime.date: DateTime, # DateFromPY
    datetime.datetime: DateTime, # TimestampFromPy
    datetime.time: DateTime, # TimeFromPy
    datetime.timedelta: DateTime, # IntervalFromPy
    decimal.Decimal: Decimal,
}

try:
    built_in_adapters[memoryview] = Binary
except NameError:
    # Python 2.6
    pass

for k, v in built_in_adapters.iteritems():
    adapters[(k, ISQLQuote)] = v
