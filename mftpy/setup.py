from distutils.core import setup
import os
import sys

sys.path.append(os.getcwd())

setup(
    name='mft',
    version='0.9',
    packages=[
        'mft',
        'mft.entries',
        'mft.tools',
        'mft.meta',
        ],
    )