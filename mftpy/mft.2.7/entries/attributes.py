"""
MFT Attributes
see page 355
"""


import struct
import fields
from mft.util import byte_range as br

# See table 11.2 on page 282

ATTRIBUTE_TYPES = {
 16: ("$STANDARD_INFORMATION", "General information"),
 32: ("$ATTRIBUTE_LIST", "Lists where other attributes for file can be found"),
 48: ("$FILE_NAME", "File name, in unicode. Last accessed, written, created"),
 64: ("$OBJECT_ID", "16 byte ID for the file or directory."),
 80: ("$SECURITY_DESCRIPTOR", "Access control and security properties"),
 96: ("$VOLUME_NAME", "Volume name"),
 112: ("$VOLUME_INFORMATION", "File system version and other flags"),
 128: ("$DATA", "File contents"),
 144: ("$INDEX_ROOT", "Root node of an index tree"),
 160: ("$INDEX_ALLOCATION", "Nodes of an index tree"),
 176: ("$BITMAP", "A bitmap for the $MFT file and for indexes"),
 192: ("$REPARSE_POINT", "Data about a reparse point"),
 208: ("$EA_INFORMATION", "Used for backward compatability with OS/2 apps"),
 224: ("$EA", "Used for backward compatability with OS/2 apps"),
 256: ("$LOGGED_UTILITY_STREAM", "Keys and info about encrypted attributes"),
}


def get_attribute_type(attr_key, version=None):
    """
    Returns the attribute type based on attribute key
    """
    # The following types are different in version 1.2 of Windows NT
    # FIXME: Find out how to determine version
    if version == 1.2:
        ATTRIBUTE_TYPES[64] = ("$VOLUME_VERSION", "Volume information")
        ATTRIBUTE_TYPES[192] = ("$SYMBOLIC_LINK", "Soft link information")

    try:
        return ATTRIBUTE_TYPES[attr_key]
    except KeyError:
        return None


class Attribute(object):
    """
    Table 13.2 Data structure for the first 16 bytes of an attribute pg 356
    Byte Range    Description                    Essential
    ======================================================
    0-3           Attribute type indentifier     Yes
    4-7           Length of attribute            Yes
    8-8           Non-resident flag              Yes
    9-9           Length of name                 Yes
    10-11         Offset to name                 Yes
    12-13         Flags                          Yes
    14-15         Attribute identifier           Yes
    """
    def __init__(self, data):
        self.attr_type = fields.Field(br(data, 0, 3))
        self.attr_length = fields.Field(br(data, 4, 7))

        if not self.attr_type.value == 0xffffffff:
            self.non_resident = fields.NonResField(br(data, 8, 8))
            self.name_length = fields.Field(br(data, 9, 9))
            self.name_offset = fields.Field(br(data, 10, 11))
            self.flags = fields.Field(br(data, 12, 13))
            self.attr_id = fields.Field(br(data, 14, 15))

            if self.non_resident.value:
                self.vcn_start = fields.Field(br(data, 16, 23))
                self.vcn_end = fields.Field(br(data, 24, 31))
                self.runlist_offset = fields.Field(br(data, 32, 33))
                self.compression_size = fields.Field(br(data, 34, 35))
                self.non_res_unused = fields.Field(br(data, 36, 39))
                self.attr_allocated_size = fields.Field(br(data, 40, 47))
                self.attr_actual_size = fields.Field(br(data, 47, 55))
                self.attr_init_size = fields.Field(br(data, 56, 63))
            else:
                self.content_size = fields.Field(br(data, 16, 19))
                self.content_offset = fields.Field(br(data, 20, 21))
                self.content = data[
                    self.content_offset.value:(
                        self.content_size.value + self.content_offset.value
                    )]
    def export(self):
        """
        Export items one at a time based on key
        """
        # Ignore the following attributes
        IGNORE_KEYS = ['raw', 'attributes_and_fixups']
        
        for k,v in self.__dict__.items():
            if k not in IGNORE_KEYS:
                yield("{0}: {1}".format(k, v))


class StandardInfo(Attribute):
    """
    $STANDARD_INFORMATION Attribute
    Attribute type = 16
    See page 360
    """
    def __init__(self, data):
        super(StandardInfo, self).__init__(data)
        self.created = fields.WindowsTime(br(self.content, 0, 7))
        self.altered = fields.WindowsTime(br(self.content, 8, 15))
        self.mft_altered = fields.WindowsTime(br(self.content, 16, 23))
        self.accessed = fields.WindowsTime(br(self.content, 24, 31))
        # Standard info flags
        self.si_flags = fields.SiFlags(br(self.content, 32, 35))
        self.version_max = fields.Field(br(self.content, 36, 39))
        self.version = fields.Field(br(self.content, 40, 43))
        self.class_id = fields.Field(br(self.content, 44, 47))
        self.owner_id = fields.Field(br(self.content, 48, 51))
        self.security_id = fields.Field(br(self.content, 52, 55))
        self.quota = fields.Field(br(self.content, 56, 63))
        self.usn = fields.Field(br(self.content, 64, 71))


# Attribute type = 42
class FileName(Attribute):
    """
    Stores FileNameAttributes
    """

    # See page 362
    def __init__(self, data):
        super(FileName, self).__init__(data)
        self.parent_dir = fields.Field(br(self.content, 0, 7))
        self.file_creation_time = fields.Field(
            br(self.content, 8, 15)
        )
        self.file_modification_time = fields.Field(
            br(self.content, 16, 23)
        )
        self.mft_modification_time = fields.Field(
            br(self.content, 24, 31)
        )
        self.file_access_time = fields.Field(
            br(self.content, 32, 39)
        )
        self.allocated_size = fields.Field(
            br(self.content, 40, 47)
        )
        self.actual_size = fields.Field(
            br(self.content, 48, 55)
        )
        self.content_flags = fields.Field(br(self.content, 56, 59))
        self.reparse_value = fields.Field(br(self.content, 60, 63))
        self.name_length = fields.Field(br(self.content, 64, 64))
        # FIXME: FIND OUT WHAT NAMESPACE IS FOR
        self.namespace = fields.Field(br(self.content, 65, 65))
        self.name = fields.StringField(
            self.content[66:self.content_size.value]
        )


def get_type(data):
    """
    Unpack the data to an integer
    """
    return struct.unpack('<L', data)[0]


def create(data):
    """
    Create an MFT entry attribute from the entered data
    """
    attr = Attribute(data)
    # attr_type = get_type(data[0:4])
    # if attr_type == 16:
    #    attr = StandardInfo(data)
    #elif attr_type == 48:
    #    attr = FileName(data)
    #elif attr_type not in ATTRIBUTE_TYPES:
    #    attr = None
    #else:
    #    attr = Attribute(data)
    return attr
