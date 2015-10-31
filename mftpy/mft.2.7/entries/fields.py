"""
Stores information about individual mft properties
"""

import struct
from datetime import datetime

format_options = {
    1: '<B',
    2: '<H',
    4: '<L',
    8: '<Q',
}


class MftValueError(ValueError):
    """
    A basic value error
    """
    pass


class Field(object):
    """
    The base field. Other fields will be built on top of this field.
    """

    def __init__(self, data, validate=False,):
        self.validate = validate
        self.raw = data

    @property
    def value(self):
        """
        Override this function to change the returned value
        """
        if self.raw:
            return self.unpack()

    def __repr__(self):
        #FIXME: Fuckin Unicode!
        try:
            return u'%s' % self.value
        except:
            return u'Fuckin Unicode!'

    def unpack(self):
        """
        Unpack the raw data
        """
        # FIXME: add better error handling
        try:
            return struct.unpack(format_options[len(self.raw)], self.raw)[0]
        except:
            return self.raw


class StringField(Field):
    """
    Used for holding string values
    """
    @property
    def value(self):
        return self.raw


class MftFlagsField(Field):
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
                if self.validate:
                    raise MftValueError("MftValueError: Invalid flags value")
                else:
                    return "Unknown"


# Attribute fields


class NonResField(Field):
    """
    Stores the non resident flag
    """
    @property
    def value(self):
        return self.unpack() == 1


class SiFlags(Field):
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
    
    #FIXME: This is not returning the correct value
    @property
    def value(self):
        try:
            return self.SI_FLAGS[self.unpack()]
        except KeyError:
            raise MftValueError(
            "MftValueError: Invalid Standard Info Flag Value"
            )

class WindowsTime(Field):
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
        d = 116444736000000000L
        val = (((long(high) << 32) + long(low)) - d) / 10000000
        try:
            dt = datetime.utcfromtimestamp(val)
            self.datetime = dt
            return dt.strftime("%Y/%m/%d %H:%M")
        except ValueError:
            return "Invalid date and time"
