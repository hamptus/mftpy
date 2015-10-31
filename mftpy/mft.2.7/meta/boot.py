"""
Decode the BootFile pg 379-380

Table 13.18 Data structure for the boot sector 379 - 380
Byte Range    Description                    Essential
======================================================
0-3           Assembly instruction           No
3-10          OEM Name                       No
11-12         Bytes per sector               Yes
13-13         Sectors per cluster            No
14-15         Reserved sectors (must be 0)   No
16-20         Unused (must be 0)             No
21-21         Media descriptor               No
22-23         Unused (must be 0)             No
24-31         Unused (unchecked)             No
32-35         Unused (must be 0)             No
36-39         Unused (unchecked)             No
40-47         Total sectors in file system   Yes
48-55         Starting MFT Cluster           Yes
56-63         Starting MFT Mirror cluster    No
64-64         MFT entry size                 Yes
65-67         Unused                         No
68-68         Index record size              Yes
69-71         Unused                         No
72-79         Serial number                  No
80-83         Unused                         No
84-509        Boot code                      No
510-511       Signature 0xAA55               No
"""

import struct


class BootFile(object):
    """
    Creates an object from the $BOOT file
    """
    def __init__(self, data):
        self.assembly_instructions = struct.unpack('<3B', data[0:3])
        self.oem_name = struct.unpack('<8s', data[3:11])
        self.bytes_per_sector = struct.unpack("<H", data[11:13])
        self.sectors_per_cluster = struct.unpack("<B", data[13])
        self.reserved_sectors = struct.unpack("<H", data[14:16])
        self.unused_1 = struct.unpack("<5B", data[16:21])
        self.media_descriptor = struct.unpack("<B", data[21])
        self.unused_2 = struct.unpack("<H", data[22:24])
        self.unused_3 = struct.unpack("<Q", data[24:32])
        self.unused_4 = struct.unpack("<L", data[32:36])
        self.unused_5 = struct.unpack("<L", data[36:40])
        self.file_system_sectors = struct.unpack("<Q", data[40:48])
        self.mft_start = struct.unpack("<Q", data[48:56])
        self.mft_mirror_start = struct.unpack("<Q", data[56:64])
        self.entry_size = struct.unpack("<B", data[64])
        self.unused_6 = struct.unpack("<3B", data[65:68])
        self.index_record_size = struct.unpack("<B", data[68])
        self.unused_7 = struct.unpack("<3B", data[69:72])
        self.serial_number = struct.unpack("<Q", data[72:80])
        self.unused_8 = struct.unpack("<L", data[80:84])
        self.boot_code = struct.unpack("<426B", data[84:510])
        self.signature = struct.unpack('<H', data[510:512])

    def validate(self):
        """
        Checks the signature
        """
        return self.signature[0] == 43605

    def get_cluster_size(self):
        """
        Returns the cluster size
        """
        return self.bytes_per_sector[0] * self.sectors_per_cluster[0]

    def get_mft_start_offset(self):
        """
        Returns the offset to the start of the MFT
        """
        return self.get_cluster_size() * self.mft_start[0]
