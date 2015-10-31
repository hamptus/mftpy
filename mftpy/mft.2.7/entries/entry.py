import attributes
import fields
from mft.util import byte_range as br


class Entry(object):
    """
    Create a python object of an MFT Entry
    """
    def __init__(self, data):
        self.raw = data
        self.signature = fields.StringField(br(data, 0, 3,))
        self.fixup_array_offset = fields.Field(br(data, 4, 5))
        self.fixup_array_entries = fields.Field(br(data, 6, 7))
        self.lsn = fields.Field(br(data, 8, 15))
        self.sequence = fields.Field(br(data, 16, 17))
        self.link_count = fields.Field(br(data, 18, 19))
        self.attribute_offset = fields.Field(br(data, 20, 21))
        self.flags = fields.MftFlagsField(br(data, 22, 23))
        self.used_size = fields.Field(br(data, 24, 27))
        self.allocated_size = fields.Field(br(data, 28, 31))
        self.file_ref = fields.Field(br(data, 32, 39))
        self.next_attr_id = fields.Field(br(data, 40, 41))
        self.attributes_and_fixups = data[42:]

    @property
    def attributes(self):
        """
        Returns the attributes from the MFT entry as a generator
        """
        data = self.raw[self.attribute_offset.value:]
        offset = 0
        while True:
            data = data[offset:]
            attr = attributes.create(data)
            if attr:
                yield attr
                offset = attr.attr_length.value
            else:
                break
            if attr.attr_type.value == 0xffffffff:
                break
    @property
    def filename(self):
        for attribute in self.attributes:
            if type(attribute) == attributes.FileName:
                return attribute.name.value.replace("\x00", "")
        return "Unknown"
    
    def export(self):
        """
        Export items one at a time based on key
        """
        # Ignore the following attributes
        IGNORE_KEYS = ['raw', 'attributes_and_fixups']
        
        for k,v in self.__dict__.items():
            if k not in IGNORE_KEYS:
                yield("%s: %s" % (k, v))
    
    def __repr__(self):
        return self.filename
    
    def dump(self):
		return self.raw

def create(data):
    """
    Return an MFT Entry for the submitted data
    """
    entry = Entry(data)
    return entry
