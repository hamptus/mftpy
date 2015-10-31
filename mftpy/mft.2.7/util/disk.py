"""
Basic tools for getting a little bit of information
"""

import platform
import os

class PermissionError(Exception):
    pass

def list_disks():
    """
    Returns a list of hard disks.
    """
    if platform.system() == 'Linux':
        res = os.popen('fdisk -l').read()
        # FIXME: Prevent error about invalid partition tables from being displayed
        if len(res) < 1:
            raise PermissionError(
                'You must have administrator priveleges to run this command.'
            )
        res = res.split("\n")
        return_res = [i.split(" ")[1].replace(":", "") for i in res if i.startswith('Disk /')]
        return return_res
            
        

if __name__=='__main__':
    x = list_disks()
    for i in x: 
        print i