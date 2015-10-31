"""
Parse MFT Entries
"""

from mft.entries.entry import Entry


def parse_entry(entry):
    """
    Parse an individual mft entry
    """
    with open(entry, 'rb') as e:
        entry = Entry(e.read())
    print entry
