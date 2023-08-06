#
# python-ipfix (c) 2013-2014 Brian Trammell.
#
# Many thanks to the mPlane consortium (http://www.ict-mplane.eu) for
# its material support of this effort.
# 
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Implementation of IPFIX abstract data types (ADT) and mappings to Python types.

Maps each IPFIX ADT to the corresponding Python type, as below:

======================= =============
       IPFIX Type        Python Type
======================= =============
octetArray              bytes
unsigned8               int
unsigned16              int
unsigned32              int
unsigned64              int
signed8                 int
signed16                int
signed32                int
signed64                int
float32                 float
float64                 float
boolean                 bool
macAddress              bytes
string                  str
dateTimeSeconds         datetime
dateTimeMilliseconds    datetime
dateTimeMicroseconds    datetime
dateTimeNanoseconds     datetime
ipv4Address             ipaddress
ipv6Address             ipaddress
======================= =============

Though client code generally will not use this module directly, it defines how
each IPFIX abstract data type will be represented in Python, and the concrete
IPFIX representation of each type. Type methods operate on buffers, as used
internally by the :class:`ipfix.message.MessageBuffer` class, so we'll create 
one to illustrate encoding and decoding:

>>> import ipfix.types
>>> buf = memoryview(bytearray(16))

Each of the encoding methods returns the offset into the buffer of the first
byte after the encoded value; since we're always encoding to the beginning
of the buffer in this example, this is equivalent to the length. 
We use this to bound the encoded value on subsequent decode.

Integers are represented by the python int type:

>>> unsigned32 = ipfix.types.for_name("unsigned32")
>>> length = unsigned32.encode_single_value_to(42, buf, 0)
>>> buf[0:length].tolist()
[0, 0, 0, 42]
>>> unsigned32.decode_single_value_from(buf, 0, length)
42

...floats by the float type, with the usual caveats about precision:

>>> float32 = ipfix.types.for_name("float32")
>>> length = float32.encode_single_value_to(42.03579, buf, 0)
>>> buf[0:length].tolist()
[66, 40, 36, 166]
>>> float32.decode_single_value_from(buf, 0, length)
42.035789489746094

...strings by the str type, encoded as UTF-8:

>>> string = ipfix.types.for_name("string")
>>> length = string.encode_single_value_to("Grüezi", buf, 0)
>>> buf[0:length].tolist()
[71, 114, 195, 188, 101, 122, 105]
>>> string.decode_single_value_from(buf, 0, length)
'Grüezi'

...addresses as the IPv4Address and IPv6Address types in the ipaddress module:

>>> from ipaddress import ip_address
>>> ipv4Address = ipfix.types.for_name("ipv4Address")
>>> length = ipv4Address.encode_single_value_to(ip_address("198.51.100.27"), buf, 0)
>>> buf[0:length].tolist()
[198, 51, 100, 27]
>>> ipv4Address.decode_single_value_from(buf, 0, length)
IPv4Address('198.51.100.27')
>>> ipv6Address = ipfix.types.for_name("ipv6Address")
>>> length = ipv6Address.encode_single_value_to(ip_address("2001:db8::c0:ffee"), buf, 0)
>>> buf[0:length].tolist()
[32, 1, 13, 184, 0, 0, 0, 0, 0, 0, 0, 0, 0, 192, 255, 238]
>>> ipv6Address.decode_single_value_from(buf, 0, length)
IPv6Address('2001:db8::c0:ffee')

...and the timestamps of various precision as a python datetime, 
encoded as per RFC5101bis:

>>> from datetime import datetime
>>> from datetime import timezone
>>> dtfmt = "%Y-%m-%d %H:%M:%S.%f"
>>> dt = datetime.strptime("2013-06-21 14:00:03.456789", dtfmt)

dateTimeSeconds truncates microseconds:

>>> dateTimeSeconds = ipfix.types.for_name("dateTimeSeconds")
>>> length = dateTimeSeconds.encode_single_value_to(dt, buf, 0)
>>> buf[0:length].tolist()
[81, 196, 92, 99]
>>> dateTimeSeconds.decode_single_value_from(buf, 0, length).strftime(dtfmt)
'2013-06-21 14:00:03.000000'

dateTimeMilliseconds truncates microseconds to the nearest millisecond:

>>> dateTimeMilliseconds = ipfix.types.for_name("dateTimeMilliseconds")
>>> length = dateTimeMilliseconds.encode_single_value_to(dt, buf, 0)
>>> buf[0:length].tolist()
[0, 0, 1, 63, 103, 8, 228, 128]
>>> dateTimeMilliseconds.decode_single_value_from(buf, 0, length).strftime(dtfmt)
'2013-06-21 14:00:03.456000'

dateTimeMicroseconds exports microseconds fully in NTP format:

>>> dateTimeMicroseconds = ipfix.types.for_name("dateTimeMicroseconds")
>>> length = dateTimeMicroseconds.encode_single_value_to(dt, buf, 0)
>>> buf[0:length].tolist()
[81, 196, 92, 99, 116, 240, 32, 0]
>>> dateTimeMicroseconds.decode_single_value_from(buf, 0, length).strftime(dtfmt)
'2013-06-21 14:00:03.456789'

dateTimeNanoseconds is also supported, but is identical to
dateTimeMicroseconds, as the datetime class in Python only supports
microsecond-level timing.

"""
from datetime import datetime, timedelta, timezone
from functools import total_ordering
from ipaddress import ip_address
import binascii
import struct
import math

VARLEN = 65535

ISO8601_FMT = "%Y-%m-%d %H:%M:%S"

class IpfixTypeError(ValueError):
    """Raised when attempting to do an unsupported operation on a type"""
    def __init__(self, *args):
        super().__init__(args)

# Table for downconverting struct elements for reduced length encoding
_stel_rle = { ('H', 1) : 'B',
              ('L', 2) : 'H',
              ('L', 1) : 'B',
              ('Q', 4) : 'L',
              ('Q', 2) : 'H',
              ('Q', 1) : 'B',
              ('h', 1) : 'b',
              ('l', 2) : 'h',
              ('l', 1) : 'b',
              ('q', 4) : 'l',
              ('q', 2) : 'h',
              ('q', 1) : 'b',
              ('d', 4) : 'f'}

# Builtin structs for varlen information
_varlen1_st = struct.Struct("!B")
_varlen2_st = struct.Struct("!H")

# builtin default encode/decode function
def _identity(x):
    return x

# Builtin type implementation
@total_ordering
class IpfixType:
    """Abstract interface for all IPFIX types. Used internally. """
    def __init__(self, name, num, valenc, valdec, valstr, valparse, roottype=None):
        self.name = name
        self.num = num
        self.valenc = valenc
        self.valdec = valdec
        self.valstr = valstr
        self.valparse = valparse
        if roottype:
            self.roottype = roottype
        else:
            self.roottype = self
        self.length = 0

    def __eq__(self, other):
        return (self.num, self.length) == (other.num, other.length)
    
    def __lt__(self, other):
        return (self.num, self.length) < (other.num, other.length)
    
    def __str__(self):
        return "<%s>" % self.name

    def __repr__(self):
        return "ipfix.types.for_name(%s)" % repr(self.name)

class StructType(IpfixType):
    """Type encoded by struct packing. Used internally."""
    def __init__(self, name, num, stel, valenc=_identity, valdec=_identity, valstr=str, valparse=int, roottype=None):
        super().__init__(name, num, valenc, valdec, valstr, valparse, roottype)
        self.stel = stel
        self.st = struct.Struct("!"+stel)
        self.length = self.st.size
        self.skipel = str(self.length)+"x"

    def for_length(self, length):
        if not length or length == self.length:
            return self
        elif self.roottype is _roottypes[0]:
            # FIXME this is kind of a hack to allow any-length encoding of octet arrays
            return StructType(self.name, self.num, str(length)+"s",
                              self.valenc, self.valdec, self.roottype)
        else:
            try:
                return StructType(self.name, self.num, 
                                  _stel_rle[(self.stel, length)], 
                                  self.valenc, self.valdec, self.roottype)
            except KeyError:
                raise IpfixTypeError("No RLE for <%s>[%u]" % 
                                     (self.name, length))

    def encode_single_value_to(self, val, buf, offset):
        self.st.pack_into(buf, offset, self.valenc(val))
        return offset + self.length
    
    def decode_single_value_from(self, buf, offset, length):
        assert(self.length == length)
        return self.valdec(self.st.unpack_from(buf, offset)[0])

class OctetArrayType(IpfixType):
    """Type encoded by byte array packing. Used internally."""
    def __init__(self, name, num, valenc=_identity, valdec=_identity, valstr=binascii.hexlify, valparse=binascii.unhexlify, roottype=None):
        super().__init__(name, num, valenc, valdec, valstr, valparse, roottype)
        self.length = VARLEN
    
    def for_length(self, length):
        if not length or length == self.length:
            return self
        else:
            return StructType(self.name, self.num, str(length)+"s", 
                              self.valenc, self.valdec, self.roottype)

    def encode_single_value_to(self, val, buf, offset):
        enc = self.valenc(val)
        buf[offset:offset+len(enc)] = enc
        return offset + len(enc)

    def decode_single_value_from(self, buf, offset, length):
        return self.valdec(buf[offset:offset+length].tobytes())

# Utility calls for buildin encoders/decoders
def dt2epoch(dt):
    return (dt - datetime(1970,1,1,0,0,tzinfo=None)).total_seconds()

# Builtin encoders/decoders

def _encode_smibool(bool):
    if bool:
        return 1
    else:
        return 2

def _decode_smibool(byte):
    if byte == 1:
        return True
    else:
        return False

def _str_bool(bool):
    if bool:
        return "true"
    else:
        return "false"

def _parse_bool(string):
    if string == 'true':
        return True
    else:
        return False

def _encode_utf8(string):   
    return string.encode()

def _decode_utf8(octets):
    return octets.decode()

def _encode_sec(dt):
    return int(dt2epoch(dt))
    
def _decode_sec(epoch):
    return datetime.utcfromtimestamp(epoch)

def _str_sec(dt):
    return dt.strftime(ISO8601_FMT)

def _parse_sec(string):
    return datetime.strptime(string, ISO8601_FMT)

def _encode_msec(dt):
    return int(dt2epoch(dt) * 1000)
    
def _decode_msec(epoch):
    return datetime.utcfromtimestamp(epoch/1000)

def _str_msec(dt):
    return "%s.%03u" % (dt.strftime(ISO8601_FMT), int(dt.microsecond / 1000))

def _parse_msec(string):
    (ss, mss) = string.split(".")
    return datetime.strptime(ss, ISO8601_FMT).replace(microsecond = int(mss) * 1000)

def _encode_ntp(dt):
    (tsf, tsi) = math.modf(dt2epoch(dt))
    return int((int(tsi) << 32) + (tsf * 2**32))

def _decode_ntp(ntp):
    tsf = ntp & (2**32 - 1)
    tsi = ntp >> 32
    return datetime.utcfromtimestamp(tsi + tsf / 2**32)

def _str_usec(dt):
    return "%s.%06u" % (dt.strftime(ISO8601_FMT), dt.microsecond)

def _parse_usec(string):
    (ss, uss) = string.split(".")
    return datetime.strptime(ss, ISO8601_FMT).replace(microsecond = int(uss))

def _encode_ip(ipaddr):
    return ipaddr.packed
    
# builtin type registry
_roottypes = [
    OctetArrayType("octetArray", 0),
    StructType("unsigned8",  1, "B"),
    StructType("unsigned16", 2, "H"),
    StructType("unsigned32", 3, "L"),
    StructType("unsigned64", 4, "Q"),
    StructType("signed8",    5, "b"),
    StructType("signed16",   6, "h"),
    StructType("signed32",   7, "l"),
    StructType("signed64",   8, "q"),
    StructType("float32",    9, "f", valparse=float),
    StructType("float64",    10, "d", valparse=float),
    StructType("boolean",    11, "B", 
                valenc=_encode_smibool, valdec=_decode_smibool,
                valstr=_str_bool, valparse=_parse_bool),
    StructType("macAddress", 12, "6s"),
    OctetArrayType("string", 13, 
                valenc=_encode_utf8, valdec=_decode_utf8,
                valstr=_identity, valparse=_identity),
    StructType("dateTimeSeconds", 14, "L", 
                valenc=_encode_sec, valdec=_decode_sec,
                valstr=_str_sec, valparse=_parse_sec),
    StructType("dateTimeMilliseconds", 15, "Q", 
                valenc=_encode_msec, valdec=_decode_msec,
                valstr=_str_msec, valparse=_parse_msec),
    StructType("dateTimeMicroseconds", 16, "Q", 
                valenc=_encode_ntp, valdec=_decode_ntp,
                valstr=_str_usec, valparse=_parse_usec),
    StructType("dateTimeNanoseconds", 17, "Q", 
                valenc=_encode_ntp, valdec=_decode_ntp, 
                valstr=_str_usec, valparse=_parse_usec),
    StructType("ipv4Address", 18, "4s", 
                valenc=_encode_ip, valdec=ip_address, 
                valparse=ip_address),
    StructType("ipv6Address", 19, "16s", 
                valenc=_encode_ip, valdec=ip_address, 
                valparse=ip_address)
]

_TypeForName = { ietype.name: ietype for ietype in _roottypes }

def use_integer_ipv4():
    """
    Use integers instead of ipaddress.IPv4Address to store IPv4 addresses.
    Changes behavior globally; should be called before using any IPFIX types.
    Designed for use with numpy arrays, to not require a Python object for
    storing IP addresses.
    """
    _roottypes[18] = StructType("ipv4address", 18, "L")
    _TypeForName = { ietype.name: ietype for ietype in _roottypes }

def for_name(name):
    """
    Return an IPFIX type for a given type name
    
    :param name: the name of the type to look up
    :returns: IpfixType -- type instance for that name
    :raises: IpfixTypeError
    
    """
    try: 
        return _TypeForName[name]
    except KeyError:
        raise IpfixTypeError("no such type "+name)

def decode_varlen(buf, offset):
    """Decode a IPFIX varlen encoded length; used internally by template"""
    length = _varlen1_st.unpack_from(buf, offset)[0]
    offset += _varlen1_st.size
    if length == 255:
        length = _varlen2_st.unpack_from(buf, offset)[0]
        offset += _varlen2_st.size
    return (length, offset)
    
def encode_varlen(buf, offset, length):
    """Encode a IPFIX varlen encoded length; used internally by template"""
    if length >= 255:
        _varlen1_st.pack_into(buf, offset, 255)
        offset += _varlen1_st.size
        _varlen2_st.pack_into(buf, offset, length)
        offset += _varlen2_st.size
    else:
        _varlen1_st.pack_into(buf, offset, length)
        offset += _varlen1_st.size
    return offset
    
def test_types_internals():
    try:
        for_name("bogus")
        assert False
    except IpfixTypeError:
        pass

    