from utils import byte_range as br
import fields
import attributes
import meta
from exceptions import ValidationError
import struct


class Entry(object):
    """
    Creates a python object from an MFT entry
    """
    def __init__(self, data):
        self.raw = data
        self.signature = fields.StringField(br(data, 0, 3))
        self.fixup_array_offset = fields.BaseField(br(data, 4, 5))
        self.fixup_array_entries = fields.BaseField(br(data, 6, 7))
        self.lsn = fields.BaseField(br(data, 8, 15))
        self.sequence = fields.BaseField(br(data, 16, 17))
        self.link_count = fields.BaseField(br(data, 18, 19))
        self.attribute_offset = fields.BaseField(br(data, 20, 21))
        self.flags = fields.MftFlagsField(br(data, 22, 23))
        self.used_size = fields.BaseField(br(data, 24, 27))
        self.allocated_size = fields.BaseField(br(data, 28, 31))
        self.file_ref = fields.BaseField(br(data, 32, 39))
        self.next_attr_id = fields.BaseField(br(data, 40, 41))
        self.attributes_and_fixups = data[42:]

    def dump(self):
        """
        Return the raw data of the mft entry
        """
        return self.raw

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
                return attribute.name.value
        return "*[No Filename Attribute]*"

    def validate(self):
        """ An MFT entry can have one of the following three values:
            - 0x454c4946 (Good)
            - 0x44414142 (Bad)
            - 0x00000000 (Zero) """
        if self.signature.unpack() not in [0x454c4946, 0x44414142, 0x00000000]:
            raise ValidationError("Invalid MFT entry")


class Partition(object):
    """ Stores data about partitions """
    def __init__(self, partition_name=None):
        self.pn = partition_name
        self.offset = None
        self.validate()

    def validate(self):
        with open(self.pn, 'rb') as partition:
            boot = meta.BootFile(partition.read(512))
            if boot.validate():
                self.offset = boot.get_mft_start_offset()
            else:
                raise ValidationError("Invalid partition")

    def walk(self):
        if self.offset:
            with open(self.pn, 'rb') as partition:
                while True:
                    try:
                        partition.seek(self.offset)
                        d = partition.read(1024)
                        e = Entry(d)
                        self.offset = partition.tell()
                        #FIXME: Properly handle the validation error
                        try:
                            e.validate()
                        except ValidationError:
                            pass
                        else:
                            # We don't want to show unknown empty entries
                            if e.filename == '*[No Filename Attribute]*' and e.next_attr_id.value == 0:
                                pass
                            else:
                                yield(e)
                    except struct.error:
                        break


def gimme():
    with open('test.mft', 'rb') as mftfile:
        e = Entry(mftfile.read(1024))
        return e
