"""
This tool is used to extract MFT entries
"""

from mft.meta.boot import BootFile


# FIXME pass an argument to function so it knows if you are extracting from disk or partition
def extract_meta(partition=None):
    """
    Extract the system meta files from a partition
    """

    bootdata = open(partition, 'rb').read(1024)
    # FIXME: Validate partition to ensure we are pulling files from an NTFS partition
    bootfile = BootFile(bootdata)

    filenames = [
        '0_$MFT.txt',
        '1_$MFTMirr.txt',
        '2_$LogFile.txt',
        '3_$Volume.txt',
        "4_$AttrDef.txt",
        "5_$dot.txt",
        "6_$Bitmap.txt",
        "7_$Boot.txt",
        "8_$BadClus.txt",
        "9_$Secure.txt",
        "10_$Upcase.txt",
        "11_$Extend.txt",
    ]

    with open(partition, 'rb+') as partition:
        partition.seek(bootfile.get_mft_start_offset())

        for filename in filenames:
            mftentry = open(filename, "w")
            mftentry.write(partition.read(1024))
            mftentry.close()


def extract_mft_files(partition=None, count=1, start=0):
    """
    partition = Which partition to extract from
    count = How many files to extract. Default 1.
    start = Where to start extracting files. Default is 0.
    """
    if not partition:
        partition = raw_input("Which partition should I extract from? ")

    bootdata = open(partition, 'rb').read(1024)
    bootfile = BootFile(bootdata)

    with open(partition, 'rb+') as partition:
        offset = bootfile.get_mft_start_offset() + (1024 * start)
        partition.seek(offset)
        for i in xrange(count):
            with open("%s_mft.txt" % i, "w") as mft:
                mft.write(partition.read(1024))


# def list_filenames(partition=r'/dev/sda1', count=1, start=0):
    """
    Returns a list of filenames parsed from the mft entry
    """
    #bootdata = open(partition, 'rb').read(1024)
    #bootfile = BootFile(bootdata)

    #with open(partition, 'rb+') as partition:
        #offset = bootfile.get_mft_start_offset() + (1024 * start)
        #partition.seek(offset)
        #for i in xrange(count):
            #mft = MftEntry(partition.read(1024))
            #for attr in mft.attributes:
                #try:
                    #yield attr.name
                #except AttributeError:
                    #pass


    # for i in list_filenames(partition="/dev/sda2", start=150, count=50):
    #    print i

    # To run, uncomment the line below
    # extract_meta_from_partition()



if __name__ == "__main__":
    # partition = raw_input("Which partition would you like to extract from? ")
    # extract_meta(partition=partition)
    extract_mft_files('/dev/sda1', count=10, start=500)