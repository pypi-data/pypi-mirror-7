===============
ctypes-bitfield
===============

The ctypes-bitfield library consists of two modules, `bitfield` and `remotestruct`.

`bitfield` provides a mechanism for creating ctypes compatible
implementations of registers made up of bitfields.

`remotestruct` allows for ctypes derived classes, such as Structure and Bitfield, to be
accessed over a remote interface, such as TCP/IP or a VME indirection
scheme.

bitfield
--------

`bitfield` provides a mechanism for creating ctypes compatible
implementations of registers made up of bitfields.  The base
ctypes library already provides much of this functionality, but the
bitfield builder implementation wraps it up for simpler usage and avoids some
of the quirky behaviors.

Normally the underlying register type would be a fixed size integer, a 
c_uint16 or c_uint64 or the like.  However, a somewhat strange example usage
would look something like this::

    >>> from bitfield import *
    >>> IEEE754 = make_bf('IEEE754', [
    ...     ('mantissa', c_uint, 23),
    ...     ('exponent', c_uint, 8),
    ...     ('sign', c_uint, 1)
    ... ], basetype=c_float, doc='Bitfields of an IEEE754 single precision float.')
    >>> x = IEEE754()
    >>> x.keys()
    ['mantissa', 'exponent', 'sign']
    >>> x.base = 5.0
    >>> list(x.items()) #doctest: +ELLIPSIS
    [('mantissa', 2097152...), ('exponent', 129...), ('sign', 0...)]
    >>> x.sign = 1
    >>> x.base
    -5.0
    >>> x.exponent -= 2
    >>> x.base
    -1.25
    >>> x.update(sign = 0, mantissa = 0)
    >>> x.base
    1.0
    
Bitfield objects are derived from ctypes.Union.  Because of this derivation,
these classes can be stacked into ctypes.Structures, which means they can
work directly on memory mapped data.  If the memory-mapped data is volatile, 
such as hardware registers, then the fact that the update() method operates
on the entire register in one write, rather than one write per field, may
be of use.

remotestruct
------------

`remotstruct` allows for ctypes derived classes, such as Structure and Bitfield, to be
accessed over a remote interface, such as TCP/IP or a VME indirection
scheme.  Effectively, this means turning requests for elements of the
structure into requests for arbitrary byte sequences, fetching them,
and managing the translation.

If, for instance, you had a mechanism whereby, over an Ethernet
socket, you could write 8 bytes to address 0x100 as 
``W 0x100 55 45 10 18 26 28 33 47``, then read back four of those
bytes by sending ``R 0x100 4`` and getting back ``55 45 10 18`` (all
of that newline delimited), then you would write a protocol handler::

    >>> class SerialHandler(object):
    ...    def __init__(self, sock):
    ...        self.sock = sock
    ...        
    ...    def writeBytes(self, addr, data):
    ...        msg = "W " + hex(addr) + ' '.join(str(d) for d in data)
    ...        self.sock.sendall(msg.encode('ascii'))
    ...        
    ...    def readBytes(self, addr, size):
    ...        msg = "R 0x{0:X} {1}".format(addr, size)
    ...        self.sock.sendall(msg.encode('ascii'))
    ...         
    ...        received = []
    ...        while True:
    ...            x = self.sock.recv(4096)
    ...            received.append(x)
    ...            if b'\n' in x:
    ...                break
    ...                
    ...        msg = b''.join(received)
    ...        data = bytes(int(b) for b in msg.split(b' '))
    ...        return data

    >>> class DataStructure(Structure):
    ...     _fields_ = [
    ...         ('flags', c_uint32),
    ...         ('_dummy1', c_uint32),
    ...         ('offset', c_int32),
    ...         ('slope', c_float)
    ...     ]
    
    >>> sock = socket.create_connection(('1.2.3.4', 80))
    >>> handler = SerialHandler(sock)
    >>> rs = remotestruct.Remote(DataStructure, handler)
    >>> rs.flags
    5
    >>> rs.flags = 183
    >>> rs.flags
    183

Works under Python 2.6+ and 3.0+

:author:    Rob Gaddi, Highland Technology, Inc.
:date:      02-Sep-2014
:version:   0.2.6
