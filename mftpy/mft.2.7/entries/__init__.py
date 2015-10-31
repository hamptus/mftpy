"""
MFT basic file structure is on page 353

Table 13.1 Data structure for a basic MFT Entry pg 353
Byte Range    Description                    Essential
======================================================
0-3           Signature ("FILE")             No
4-5           Offset to fixup array          Yes
6-7           Entries in fixup array         Yes
8-15          $LogFile Sequence Number       No
16-17         Sequence Value                 No
18-19         Link Count                     No
20-21         Offset to first attribute      Yes
22-23         Flags (in use and directory)   Yes
24-27         Used size of MFT Entry         Yes
28-31         Allocated size of MFT entry    Yes
32-39         File reference to base record  No
40-41         Next attribute ID              No
42-1023       Attributes and fixup values    Yes

Table 13.3 Data structure for a resident attribute pg 356
Byte Range    Description                    Essential
======================================================
0-15          General header (Table 13.2)    Yes
16-19         Size of content                Yes
20-21         Offset to content              Yes

Table 13.4 Data structure for a non-resident attribute pg 357
Byte Range    Description                    Essential
======================================================
0-15          General header (Table 13.2)    Yes
16-23         Starting VCN of runlist        Yes
24-31         Ending VCN of runlist          Yes
32-33         Offset to runlist              Yes
34-35         Compression unit size          Yes
36-39         Unused                         No
40-47         Allocated size                 No
48-55         Actual size                    Yes
56-63         Initialized size               No
"""

__all__ = ['fields', 'attributes']
