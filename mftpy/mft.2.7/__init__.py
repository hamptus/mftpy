""" mftpy - parse MFT entries
    Copyright (C) 2011  Aaron Hampton

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


Table 11.1 The standard NTFS file system metadata files (page 278)
Entry    File Name    Description
=============================================================
0        $MFT         The entry for the MFT itself
1        $MFTMirr     Contains backup of first entries in MFT
2        $LogFile     Contains journal that records metadata transactions
3        $Volume      Contains volume information
4        $AttrDef     Contains attribute information
5        . (Dot)      Contains root directory of file system
6        $Bitmap      Contains the allocation status of each cluster
7        $Boot        Contains the boot sector and boot code of the file system
8        $BadClus     Contains clusters with bad sectors
9        $Secure      Info about security and access control
10       $Upcase      Uppercase version of every Unicode character
11       $Extend      Directory that has files for optional extensions

"""

__all__ = ["entries", "meta", "tools"]
from mft.entries import entry
from mft.meta import boot


def get_mft(data):
    return entry.Entry(data)

def get_bootfile(partition):
    """
    FIXME: Validate partition to ensure we are pulling files from
    an NTFS partition
    """
    return boot.BootFile(open(partition, 'rb').read(1024))

def get_meta(partition=None):
    """
    Returns the MFT metafiles
    Example:

    import mft

    metafiles = mft.get('/dev/sda1')
    for metafile in metafiles:
        print metafile
    """

    # Load the $Boot file to find where the MFT begins

    bootfile = get_bootfile(partition)

    # Open the partition. It must be an NTFS partition
    with open(partition, 'rb+') as partition:
        partition.seek(bootfile.get_mft_start_offset())
        for i in xrange(12):
            yield get_mft(partition.read(1024))

def walk(partition):
    """
    Walk the entered partition and return MFT entries one at a time

    Usage:

    import mft

    walker = mft.walk('/dev/sda1')
    print walker.next()

    for i in xrange(100):
        print walker.next()
    """
    bootdata = open(partition, 'rb').read(1024)
    bootfile = get_bootfile(partition)

    with open(partition, 'rb+') as partition:
        partition.seek(bootfile.get_mft_start_offset())
        while True:
            yield get_mft(partition.read(1024))

def get_mft_start(partition):
	with open(partition, 'rb') as bootdata:
		bootfile = boot.BootFile(bootdata.read(1024))
	return bootfile.get_mft_start_offset()
	
def extract_entry(partition, entry_number, outfile=None):
	mft_start = get_mft_start(partition)
	with open(partition, 'rb+') as disk:
		disk.seek(0)
		entry_offset = 1024 * entry_number
		disk.seek(mft_start + entry_offset)
		mft_entry = entry.Entry(disk.read(1024))

		if not outfile:
			outfile = mft.filename
		with open(outfile, 'wb') as output:
			output.write(mft_entry.dump())

def parse_entry(data):
	return entry.Entry(data)

def parse_entry_file(data_file):
	with open(data_file, 'rb') as mftfile:
		mft_entry = parse_entry(mftfile.read())
		return mft_entry
