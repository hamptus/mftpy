import struct
from datetime import datetime
import binascii
from attributes import get_attribute_type


format_options = {
    1: '<B',
    2: '<H',
    4: '<L',
    8: '<Q',
    16: '<QQ',
}


class MftValueError(ValueError):
    """
    A basic value error
    """
    pass


class BaseField(object):
    """
    The base field. Other fields will be built on top of this field.
    """

    def __init__(self, data, validate=False, verbose=None):
        self.validate = validate
        self.raw = data
        self.verbose = verbose

    @property
    def title(self):
        if self.verbose:
            return self.verbose
        else:
            return None

    @property
    def value(self):
        """
        Override this function to change the returned value
        """
        if self.raw:
            return self.unpack()

    @property
    def hex(self):
        if type(self.raw) == int:
            return hex(self.raw)
        else:
            return "0x{0}".format(binascii.hexlify(self.raw).decode('utf-8'))

    def __repr__(self):
        return '{0} ({1})'.format(self.value, self.hex)

    def unpack(self):
        """
        Unpack the raw data
        """
        if type(self.raw) == int:
            return self.raw
        else:
            return struct.unpack(format_options[len(self.raw)], self.raw)[0]


class SiFlagsField(BaseField):
    """
    Returns the correct value for standard information attributes
    """

    # Flag values found on page 360-361
    SI_FLAGS = {
        0x0001: 'Read Only',
        0x0002: 'Hidden',
        0x0004: 'System',
        0x0020: 'Archive',
        0x0040: 'Device',
        0x0080: 'Normal',
        0x0100: 'Temporary',
        0x0200: 'Sparse file',
        0x0400: 'Reparse point',
        0x0800: 'Compressed',
        0x1000: 'Offline',
        0x2000: 'Content not being indexed for faster searches',
        0x4000: 'Encrypted',
    }

    @property
    def value(self):
        try:
            return self.SI_FLAGS[self.unpack()]
        except KeyError:
            return self.unpack()


class StringField(BaseField):
    """
    Used for holding string values
    """
    @property
    def value(self):
        return str(self.raw, 'utf-8')


class FileNameField(BaseField):
    """
    Used for filename values
    """
    @property
    def value(self):
        try:
            return self.raw.decode('utf-8').replace("\x00", "")
        except UnicodeDecodeError:
            try:
                return self.raw.decode('utf-16').replace("\x00", "")
            except UnicodeDecodeError:
                try:
                    return self.raw.decode('utf-32').replace('\x00', '')
                except UnicodeDecodeError:
                    return self.raw


class MftFlagsField(BaseField):
    """
    Stores the MFT Flags
    """
    @property
    def value(self):
        """
        Unpack the data
        """
        flag_choices = {
            0x01: 'In use',
            0x02: 'Directory',
            }

        if self.raw:
            flags = self.unpack()
            try:
                return flag_choices[flags]
            except KeyError:
                return flags


class NonResField(BaseField):
    """
    Stores the non resident flag. If the value is True (1) then the attr
    is non resident.
    """
    @property
    def value(self):
        return self.unpack() == 1


class WindowsTimeField(BaseField):
    """
    Stores time in Windows format.
    The formula to convert time was found at
    http://code.activestate.com/recipes/303344-converting-windows-64-bit-time-to-python-useable-f/
    """

    def unpack(self):
        """
        Unpack the raw data
        """
        return struct.unpack("<LL", self.raw)

    @property
    def value(self):
        low, high = self.unpack()
        # difference between 1601 and 1970
        d = 116444736000000000
        val = (((int(high) << 32) + int(low)) - d) / 10000000
        try:
            dt = datetime.utcfromtimestamp(val)
            self.datetime = dt
            return dt.strftime("%Y/%m/%d %H:%M")
        except ValueError:
            return "Invalid date and time"


class ParentDirField(BaseField):
    """
    Stores information about the file reference of the parent directory
    """
    # Solution found here:
    #   http://stackoverflow.com/questions/7949912/how-to-unpack-6-bytes-as-single-integer-using-struct-in-python
    # More can be found here:
    #   http://wiki.python.org/moin/BitwiseOperators
    def unpack(self):
        """
        Unpack the raw data
        """
        x1, x2, x3 = struct.unpack('<HHI', self.raw)
        return x1, x2 | (x3 >> 16)

    @property
    def value(self):
        return self.unpack()

    def __repr__(self):
        return '{0} / {1} ({2})'.format(self.value[0], self.value[1], self.hex)


class AttributeTypeField(BaseField):
    """
    Returns information about the AttributeType
    """
    @property
    def value(self):
        return get_attribute_type(self.unpack())[0]

    def id(self):
        return self.unpack()
