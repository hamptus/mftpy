"""
MFT Attributes
see page 355
"""


import struct
import fields
from utils import byte_range as br

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
        self.attr_type = fields.AttributeTypeField(
            br(data, 0, 3), verbose='Attribute type')
        self.attr_length = fields.BaseField(
            br(data, 4, 7), verbose='Attribute length')

        if not self.attr_type.id == 0xffffffff:
            self.non_resident = fields.NonResField(
                br(data, 8, 8), verbose="Non-resident flag")
            self.name_length = fields.BaseField(
                br(data, 9, 9), verbose="Name length")
            self.name_offset = fields.BaseField(
                br(data, 10, 11), verbose="Name offset")
            self.flags = fields.BaseField(
                br(data, 12, 13), verbose="Attribute flags")
            self.attr_id = fields.BaseField(
                br(data, 14, 15), verbose="Attribute identifier")

            if self.non_resident.value:
                self.vcn_start = fields.BaseField(
                    br(data, 16, 23),
                    verbose="Virtual cluster number (VCN) start")
                self.vcn_end = fields.BaseField(
                    br(data, 24, 31),
                    verbose="Virtual cluster number (VCN) end")
                self.runlist_offset = fields.BaseField(
                    br(data, 32, 33), verbose="Runlist offset")
                self.compression_size = fields.BaseField(
                    br(data, 34, 35), verbose="Compression unit size")
                #self.non_res_unused = fields.BaseField(
                #    br(data, 36, 39), verbose="Unused")
                self.attr_allocated_size = fields.BaseField(
                    br(data, 40, 47), verbose="Attribute allocated size")
                self.attr_actual_size = fields.BaseField(
                    br(data, 48, 55), verbose="Attribute actual size")
                self.attr_init_size = fields.BaseField(
                    br(data, 56, 63),
                    verbose="Initialized size of attribute content")
            else:
                self.content_size = fields.BaseField(
                    br(data, 16, 19), verbose="Content size")
                self.content_offset = fields.BaseField(
                    br(data, 20, 21), verbose="Content offset")
                self.content = data[
                    self.content_offset.value:(
                        self.content_size.value + self.content_offset.value
                    )]

    def export(self):
        """
        Export items one at a time based on key
        """
        # Ignore the following attributes
        IGNORE_KEYS = ['raw', 'content']

        keys = list(self.__dict__.keys())
        keys.sort()

        for k in keys:
            if k not in IGNORE_KEYS:
                attr = self.__getattribute__(k)
                if attr.title:
                    yield("{0}: {1}".format(
                        attr.title, self.__getattribute__(k)))
                else:
                    yield("{0}: {1}".format(k, self.__getattribute__(k)))


class StandardInfo(Attribute):
    """
    $STANDARD_INFORMATION Attribute
    Attribute type = 16
    See page 360
    """
    def __init__(self, data):
        super(StandardInfo, self).__init__(data)
        self.created = fields.WindowsTimeField(
            br(self.content, 0, 7), verbose="Created")
        self.altered = fields.WindowsTimeField(
            br(self.content, 8, 15), verbose="Altered")
        self.mft_altered = fields.WindowsTimeField(
            br(self.content, 16, 23), verbose="MFT altered")
        self.accessed = fields.WindowsTimeField(
            br(self.content, 24, 31), verbose="Accessed")
        # Standard info flags
        self.si_flags = fields.SiFlagsField(
            br(self.content, 32, 35), verbose="Standard information flags")
        self.version_max = fields.BaseField(
            br(self.content, 36, 39), verbose="Maximum versions")
        self.version = fields.BaseField(
            br(self.content, 40, 43), verbose="Version")
        self.class_id = fields.BaseField(
            br(self.content, 44, 47), verbose="Class ID")
        self.owner_id = fields.BaseField(
            br(self.content, 48, 51), verbose="Owner ID")
        self.security_id = fields.BaseField(
            br(self.content, 52, 55), verbose="Security ID")
        self.quota = fields.BaseField(
            br(self.content, 56, 63), verbose="Quota")
        # FIXME: Change the verbose name
        self.usn = fields.BaseField(br(self.content, 64, 71), verbose="USN")


# Attribute type = 42
class FileName(Attribute):
    """
    Stores FileNameAttributes
    """

    # See page 362
    def __init__(self, data):
        super(FileName, self).__init__(data)
        self.parent_dir = fields.ParentDirField(
            br(self.content, 0, 7), verbose="Parent directory")
        self.file_creation_time = fields.WindowsTimeField(
            br(self.content, 8, 15),
            verbose="Creation time",
        )
        self.file_modification_time = fields.WindowsTimeField(
            br(self.content, 16, 23),
            verbose="File modification time",
        )
        self.mft_modification_time = fields.WindowsTimeField(
            br(self.content, 24, 31),
            verbose="MFT modification time",
        )
        self.file_access_time = fields.WindowsTimeField(
            br(self.content, 32, 39),
            verbose="File access time",)
        self.allocated_size = fields.BaseField(
            br(self.content, 40, 47),
            verbose="Allocated size",)
        self.actual_size = fields.BaseField(
            br(self.content, 48, 55),
            verbose="Actual size")
        self.content_flags = fields.BaseField(
            br(self.content, 56, 59), verbose="Content flags")
        self.reparse_value = fields.BaseField(
            br(self.content, 60, 63), verbose="Reparse value")
        self.name_length = fields.BaseField(
            br(self.content, 64, 64), verbose="Name length")
        # FIXME: FIND OUT WHAT NAMESPACE IS FOR
        self.namespace = fields.BaseField(
            br(self.content, 65, 65), verbose="Namespace")
        self.name = fields.FileNameField(
            self.content[66:self.content_size.value],
            verbose="File name",
        )


class AttributeList(Attribute):
    """
    Page 365
    Attribute type = 32
    """
    def __init__(self, data):
        super(AttributeList, self).__init__(data)
        self.alist_attr_type = fields.AttributeTypeField(
            br(self.content, 0, 3), verbose="Attribute type")
        self.alist_entry_length = fields.BaseField(
            br(self.content, 4, 5), verbose="Entry length")
        self.alist_name_length = fields.BaseField(
            br(self.content, 6, 6), verbose="Name length")
        self.alist_name_offset = fields.BaseField(
            br(self.content, 7, 7), verbose="Name offset")
        self.alist_vcn_start = fields.BaseField(
            br(self.content, 8, 15), verbose="VCN start")
        self.alist_file_ref = fields.BaseField(
            br(self.content, 16, 23),
            verbose="File reference to attribute location")
        self.alist_attr_id = fields.BaseField(
            br(self.content, 24, 24), verbose="Attribute ID")


class ObjectId(Attribute):
    """
    Page 367
    Attribute type = 64
    """

    def __init__(self, data):
        super(ObjectId, self).__init__(data)
        self.oid_object_id = fields.BaseField(
            br(self.content, 0, 15), verbose="Object ID")
        self.oid_birth_vol_id = fields.BaseField(
            br(self.content, 16, 31), verbose="Birth volume ID")
        self.oid_birth_obj_id = fields.BaseField(
            br(self.content, 32, 47), verbose="Birth object ID")
        self.oid_birth_dom_id = fields.BaseField(
            br(self.content, 48, 63), verbose="Birth domain ID")


class Data(Attribute):
    """
    Page 364
    Attribute type = 128
    From FSFA:
    "After the header, there is only raw content that corresponds to the
    contents of a file"
    We do not need to define additional fields for this attribute
    """
    pass


class IndexRoot(Attribute):
    """
    Page 369
    Attribute type = 144
    """

    def __init__(self, data):
        super(IndexRoot, self).__init__(data)
        self.ir_attr_type = fields.AttributeTypeField(
            br(self.content, 0, 3), verbose="Type of attribute in index")
        self.ir_collation_rule = fields.BaseField(
            br(self.content, 4, 7), verbose="Collation sorting rule")
        self.ir_index_byte_size = fields.BaseField(
            br(self.content, 8, 11), verbose="Index record size (bytes)")
        self.ir_index_cluster_size = fields.BaseField(
            br(self.content, 12), verbose="Index record size (clusters)")
        #self.ir_unused = fields.StringField(
        #    br(self.content, 13, 15), verbose="Unused")
        #self.ir_node_header = fields.StringField(
        #    br(self.content, 16, len(self.content)), verbose="Node header")


class IndexAllocation(Attribute):
    """
    Page 370
    Attribute type = 160
    """
    def __init__(self, data):
        super(IndexAllocation, self).__init__(data)
        #self.ia_signature = fields.StringField(
            #br(self.content, 0, 3), verbose="Signature")
        #self.ia_fixup_array_offset = fields.BaseField(
            #br(self.content, 4, 5), verbose="Offset to fixup array")
        #self.ia_entries_in_fixup_array = fields.BaseField(
            #br(self.content, 6, 7),
            #verbose="Number of entries in fixup array")
        #self.ia_lsn = fields.BaseField(
            #br(self.content, 8, 15), verbose="$LogFile sequence number")
        #self.ia_vcn = fields.BaseField(
            #br(self.content, 16, 23), verbose="VCN")


class ReparsePoint(Attribute):
    """
    Page 368
    Attribute type = 192
    """

    def __init__(self, data):
        super(ReparsePoint, self).__init__(data)
        self.rpoint_flags = fields.BaseField(
            br(self.content, 0, 3), verbose="Reparse point flags")
        self.rpoint_size = fields.BaseField(
            br(self.content, 4, 5), verbose="Size")
        #self.rpoint_unused = fields.BaseField(
        #    br(self.content, 6, 7), verbose="Unused")
        self.rpoint_target_name_offset = fields.BaseField(
            br(self.content, 8, 9), verbose="Target name offset")
        self.rpoint_target_name_length = fields.BaseField(
            br(self.content, 10, 11), verbose="Target name length")
        self.rpoint_print_name_offset = fields.BaseField(
            br(self.content, 12, 13), verbose="Print name offset")
        self.rpoint_print_name_length = fields.BaseField(
            br(self.content, 14, 15), verbose="Print name length")


def get_type(data):
    """
    Unpack the data to an integer
    """
    return struct.unpack('<L', data)[0]


def create(data):
    """
    Create an MFT entry attribute from the entered data
    """
    attr_type = get_type(data[0:4])
    if attr_type == 16:
        return StandardInfo(data)
    if attr_type == 32:
        return AttributeList(data)
    if attr_type == 48:
        return FileName(data)
    if attr_type == 64:
        return ObjectId(data)
    if attr_type == 128:
        return Data(data)
    if attr_type == 144:
        return IndexRoot(data)
    if attr_type == 160:
        return IndexAllocation(data)
    if attr_type == 192:
        return ReparsePoint(data)
    if attr_type in ATTRIBUTE_TYPES:
        return Attribute(data)
