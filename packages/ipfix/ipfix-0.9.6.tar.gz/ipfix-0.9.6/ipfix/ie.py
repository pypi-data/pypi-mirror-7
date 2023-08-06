#
# python-ipfix (c) 2013 Brian Trammell.
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
IESpec-based interface to IPFIX information elements,
and interface to use the default IPFIX IANA Information Model

An IESpec is a string representation of an IPFIX information element,
including all the information required to define it, as documented in
Section 9 of http://tools.ietf.org/html/draft-ietf-ipfix-ie-doctors.
It has the format:

  name(pen/num)<type>[size]

To specify a new Information Element, a complete IESpec
must be passed to for_spec():

>>> import ipfix.ie
>>> e = ipfix.ie.for_spec("myNewInformationElement(35566/1)<string>")
>>> e
InformationElement('myNewInformationElement', 35566, 1, ipfix.types.for_name('string'), 65535)

The string representation of an InformationElement is its IESpec:

>>> str(e)
'myNewInformationElement(35566/1)<string>[65535]'

To get an Information Element already specified, an incomplete specification
can be passed; a name or number is enough:

>>> ipfix.ie.use_iana_default()
>>> ipfix.ie.use_5103_default()
>>> str(ipfix.ie.for_spec("octetDeltaCount"))
'octetDeltaCount(0/1)<unsigned64>[8]'
>>> str(ipfix.ie.for_spec("(2)"))
'packetDeltaCount(0/2)<unsigned64>[8]'

Reduced-length encoding and fixed-length sequence types are supported by the
for_length method; this is used internally by templates.

>>> str(e.for_length(32))
'myNewInformationElement(35566/1)<string>[32]'

An Information Element object can also be used to translate 
between native Python and string representations of an Information Element value:

>>> ipfix.ie.for_spec("sourceIPv4Address").parse("192.0.2.19")
IPv4Address('192.0.2.19')
>>> from datetime import datetime
>>> ipfix.ie.for_spec("flowEndMilliseconds").unparse(datetime(2013,6,21,14))
'2013-06-21 14:00:00.000'


Most client code will only need the :func:`use_iana_default`, 
:func:`use_5103_default`, and :func:`use_specfile` functions; 
client code using tuple interfaces will need :func:`spec_list` as well.

"""            
import re
import os.path
from . import types
from functools import total_ordering, reduce
import operator

_iespec_re = re.compile('^([^\s\[\<\(]+)?(\(((\d+)\/)?(\d+)\))?'
                        '(\<(\S+)\>)?(\[(\S+)\])?')

# Internal information element registry
_ieForName = {}
_ieForNum = {}

def _register_ie(ie):
    _ieForName[ie.name] = ie
    _ieForNum[(ie.pen, ie.num)] = ie
    
    return ie
    
@total_ordering
class InformationElement:
    """
    An IPFIX Information Element (IE). This is essentially a five-tuple of
    name, element number (num), a private enterprise number (pen; 0 if it
    is an IANA registered IE), a type, and a length.

    Information Elements may also have value string and parser functions,
    for representing the values as strings; if not set, these default to 
    
    InformationElement instances should be obtained using the :func:`for_spec`
    or :func:`for_template_entry` functions.
    
    """
    
    def __init__(self, name, pen, num, ietype=types._roottypes[0], length=None, valstr=None, valparse=None):    
        if name:
            self.name = name
        else: 
            self.name = "_ipfix_%u_%u" % (pen, num)

        if length:
            self.length = length
        else:
            self.length = ietype.length

        self.pen = pen
        self.num = num
        self.type = ietype.for_length(self.length)

        self.valparse = valparse
        self.valstr = valstr

    def __eq__(self, other):
        """
        Determine if an IE is equal to another IE. 
        Two IEs are considered equal if they share a PEN, number, and length.

        """
        return ((self.pen, self.num) == (other.pen, other.num))
    
    def __lt__(self, other):
        return ((self.pen, self.num) < (other.pen, other.num))

    def __repr__(self):
        return "InformationElement(%s, %s, %s, %s, %s)" % (repr(self.name), 
               repr(self.pen), repr(self.num), repr(self.type), 
               repr(self.length))

    def __str__(self):
        return "%s(%u/%u)%s[%u]" % (self.name, self.pen, self.num, str(self.type), self.length)
    
    def __hash__(self):
        return ((self.num << 16) + self.length) ^ self.pen
    
    def for_length(self, length):
        """
        Get an instance of this IE for the specified length.
        Used to support reduced-length encoding (RLE).
        
        :param length: length of the new IE
        :returns: this IE if length matches, or a new IE for the length
        :raises: ValueError
        """
        
        if not length or length == self.length:
            return self
        else:
            return self.__class__(self.name, self.pen, self.num, self.type, length)

    def unparse(self, v):
        """
        Unparse a value to a string using the conversion function 
        for this Information Element. Uses the default string conversion
        for the IE's type if not overridden at IE creation time.

        :param v: value to unparse using this IEs's string conversion
        :returns: string representation of v
        :raises: ValueError if v is not a valid value for this IE
        """

        if self.valstr:
            return self.valstr(v)
        else:
            return self.type.valstr(v)

    def parse(self, s):
        """
        Parse a string to a value using the conversion function 
        for this Information Element. Uses the default string conversion
        for the IE's type if not overridden at IE creation time.

        :param s: string to parse using this IEs's string conversion
        :returns: value for given string
        :raises: ValueError is not a valid string representation for this IE
        """
        if self.valparse:
            return self.valparse(s)
        else:
            return self.type.valparse(s)

@total_ordering
class InformationElementList:
    """
    A hashable ordered list of Information Elements.
    
    Used internally by templates, and to specify the
    order of tuples to the tuple append and iterator interfaces. Get an
    instance by calling :func:`spec_list`
    """
    def __init__(self, iterable = None):
        self.inner = []
        
        if iterable:
            for x in iterable:
                self.append(x)

    def __iter__(self):
        return iter(self.inner)

    def __eq__(self, other):
        return self.inner == other.inner
        
    def __lt__(self, other):
        return self.inner < other.inner
    
    def __repr__(self):
        return "InformationElementList(" + ",".join((repr(x) for x in self.inner)) + ")"

    def __str__(self):
        return "\n".join((str(x) for x in self.inner))
    
    def __hash__(self):
        if not self.hashcache:
            self.hashcache = reduce(operator.xor, (hash(x) for x in self.inner))

        return self.hashcache

    def __len__(self):
        return len(self.inner)
    
    def __getitem__(self, key):
        return self.inner[key]
    
    def index(self, x):
        return self.inner.index(x)

    def append(self, ie):
        self.inner.append(ie)
        self.hashcache = None

def parse_spec(spec):
    """Parse an IESpec into name, pen, number, typename, and length fields"""
    (name, pen, num, typename, length) = _iespec_re.match(spec).group(1,4,5,7,9)
    
    if pen: 
        pen = int(pen)
    else:
        pen = 0
    
    if num:
        num = int(num)
    else:
        num = 0
    
    if length:
        length = int(length)
    else:
        length = 0
        
    if not typename:
        typename = False
    
    return (name, pen, num, typename, length)
    
def for_spec(spec):
    """
    Get an IE from the cache of known IEs, or create a
    new IE if not found, given an IESpec.
    
    :param spec: IEspec, as in draft-ietf-ipfix-ie-doctors, of the 
                 form name(pen/num)<type>[size]; some fields may be
                 omitted unless creating a new IE in the cache.
    :returns: an IE for the name
    :raises: ValueError
                 
    
    """
    (name, pen, num, typename, length) = parse_spec(spec)

    if not name and not pen and not num and not typename and not length:
        raise ValueError("unrecognized IE spec "+spec)
    
    if name and not pen and not num and name in _ieForName:
            # lookup in name registry
            return _ieForName[name].for_length(length)
    
    if num and (pen, num) in _ieForNum:
            # lookup in number registry
            return _ieForNum[(pen, num)].for_length(length)
    
    # try to create new registered IE
    if not typename:
        raise ValueError("IE "+str(spec)+
                         " unknown; use a full IEspec to create a new IE.")
    
    ietype = types.for_name(typename)
        
    return _register_ie(InformationElement(name, pen, num, ietype, length))
 
def for_template_entry(pen, num, length):
    """
    Get an IE from the cache of known IEs, or create a
    new IE if not found, given a private enterprise number,
    element number, and length. Used internally by Templates.
    
    :param pen: private enterprise number, or 0 for an IANA IE
    :param num: IE number (Element ID)
    :param length: length of the IE in bytes
    :returns: an IE for the given pen, num, and length. If the IE has not
             been previously added to the cache of known IEs, the IE will be 
             named _ipfix_pen_num, and have octetArray as a type.

    """
    if ((pen, num) in _ieForNum):
        return _ieForNum[(pen, num)].for_length(length)
    
    return _register_ie(InformationElement(None, pen, num, types.for_name("octetArray"), length))

def spec_list(specs):
    """
    Given a list or iterable of IESpecs, return a hashable list of IEs.
    Pass this as the ielist argument to the tuple export
    and iterator functions.
    
    :param specs: list of IESpecs
    :returns: a new Information Element List, suitable for use with the tuple
              export and iterator functions in :mod:`message`
    :raises: ValueError
    
    """
    return InformationElementList(for_spec(spec) for spec in specs)    

def clear_infomodel():
    """Reset the cache of known Information Elements."""
    _ieForName.clear()
    _ieForNum.clear()

def dump_infomodel():
    return sorted([_ieForNum[x] for x in _ieForNum])

def use_specfile(filename):
    """
    Load a file listing IESpecs into the cache of known IEs
    
    :param filename: name of file containing IESpecs to open
    :raises: ValueError
    
    """
    with open(filename) as f:
        for line in f:
            for_spec(line)

def use_iana_default():
    """
    Load the module internal list of IANA registered IEs into the
    cache of known IEs. Normally, client code should call this before
    using any other part of this module.

    """ 
    use_specfile(os.path.join(os.path.dirname(__file__), "iana.iespec"))
    
def use_5103_default():
    """
    Load the module internal list of RFC 5103 reverse IEs for IANA
    registered IEs into the cache of known IEs. Normally, biflow-aware
    client code should call this just after use_iana_default().

    """
    use_specfile(os.path.join(os.path.dirname(__file__), "rfc5103.iespec"))

def test_ie_internals():
    # Tests for full statement coverage of the ipfix.ie module
    # (not already covered in doctest or elsewhere)
    la = InformationElementList([InformationElement(None, 35566, 9999, length=1)])
    lb = InformationElementList([InformationElement(None, 35566, 9999, length=4)])
    lc = InformationElementList([InformationElement(None, 35566, 9998)])

    assert la[0].name == "_ipfix_35566_9999"
    assert la == lb
    assert la > lc

    try:
        for_spec("not a spec")
        assert False
    except ValueError as e:
        pass

    assert for_template_entry(35566,9999,4) == InformationElement(None, 35566, 9999, length=4)