import Tkinter
from mbr import get_partition_tables
import ttk
import tkFileDialog

# FIXME: All of this code will probably need to be refactored and cleaned up

DISK_TO_READ = '/dev/sda'


class App(object):
    def __init__(self, master):
        self.master = master
        self.all_partitions = []
        self.frame = Tkinter.Frame(self.master)
        self.frame.pack(fill=Tkinter.BOTH, expand=1)
        self.vsb = ttk.Scrollbar(self.frame)
        self.vsb.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        self.disk = None

        self.menubar = Tkinter.Menu(self.frame)
        filemenu = Tkinter.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label='Open Disk', command=self.open_disk)
        filemenu.add_command(label='Quit', command=self.frame.quit)
        self.menubar.add_cascade(label='File', menu=filemenu)
        
        self.create_mbr_menu()

        
        self.mftmenu = Tkinter.Menu(self.menubar, tearoff=0)
        self.mftmenu.entryconfig(0,state=Tkinter.DISABLED)
        self.menubar.add_cascade(label='MFT', menu=self.mftmenu)

        master.config(menu=self.menubar)
        self.center_window()

    def center_window(self):
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()

        x = (ws / 2) - 300
        y = (hs / 2) - 200
        self.master.geometry("%dx%d+%d+%d" % (600, 400, x, y))
        
    def open_disk(self):
        self.disk = tkFileDialog.askopenfilename(initialdir="/dev/")
        self.enable_mbr_menu()
    
    def create_mbr_menu(self):
        self.mbrmenu = Tkinter.Menu(self.menubar, tearoff=0)
        self.mbrmenu.add_command(label='View MBR', command=self.open_mbr)
        self.mbrmenu.add_command(
            label='Extract as JSON',
            command=self.extract_mbr_json,
        )
        self.disable_mbr_menu()
        self.menubar.add_cascade(label='MBR', menu=self.mbrmenu)
        
    def disable_mbr_menu(self):
        self.mbrmenu.entryconfig('View MBR', state=Tkinter.DISABLED)
        self.mbrmenu.entryconfig('Extract as JSON', state=Tkinter.DISABLED)
    def enable_mbr_menu(self):
        self.mbrmenu.entryconfig('View MBR', state=Tkinter.NORMAL)
        self.mbrmenu.entryconfig('Extract as JSON', state=Tkinter.NORMAL)
    
    def extract_mbr_json(self):
        if self.disk:
            self.load_mbr()            
            with tkFileDialog.asksaveasfile(defaultextension='json') as out:
                out.write(self.record.json())
        
    def load_mbr(self):
        if self.disk:
            partition_tables = [i for i in get_partition_tables(self.disk)]
            self.record = partition_tables[0]
            for mbr in partition_tables:
                for partition in mbr.partitions:
                    if partition.get_type() != 'Empty':
                        self.all_partitions.append(partition)
        else:
            self.record = None

    def open_mbr(self):
        """
        FIXME: Right now the DISK_TO_READ value is hard coded. We need to find 
        a way to list all of the disks attached to the computer and read the
        mbr from the selected disk. (We also need to learn about extended
        partitions.
        """
        self.all_partitions = []
        self.load_mbr()
        if self.record:
            if hasattr(self, 'tree'):
                self.tree.destroy()
            self.tree = ttk.Treeview(
                self.frame,
                columns=('value'),
                displaycolumns='value',
                height=15,
                yscrollcommand=self.vsb.set,
            )
            self.vsb.config(command=self.tree.yview)
            self.tree.heading("#0", text='Master Boot Record')
            self.tree.heading("value", text="Value")
            self.mbrtree = self.tree.insert('', 'end', text='MBR',)
            if self.record.validate_signature():
                sig_val = "0xAA55"
            else:
                sig_val = 'Invalid'
    
            signature = self.tree.insert(
                self.mbrtree,
                'end',
                text='Signature',
                value=[sig_val])
            
            for number, partition in enumerate(self.all_partitions):
                partition_name = 'Partition%s' % (number + 1)
                p = self.tree.insert(
                    self.mbrtree,
                    'end',
                    text=partition_name.capitalize(),
                    values=[partition.get_type()])
                bootable = self.add_item(
                    p,
                    'Bootable',
                    [partition.is_bootable()]
                )
                size = self.add_item(p, 'Size', [partition.size])
                start_chs = self.add_item(
                    p,
                    'Start CHS Address',
                    [partition.start_chs_address]
                )
                end_chs = self.add_item(
                    p,
                    'End CHS Address',
                    [partition.end_chs_address]
                )
                lba = self.add_item(p, 'Logical Block Address', [partition.lba])
                
    
            self.tree.pack(fill=Tkinter.BOTH, expand=1)

    def add_item(self, parent, name, values):
        item = self.tree.insert(
            parent,
            'end',
            text=name.capitalize(),
            values=values,
            )

    def insert_partition(self, partition):
        mbr_part = getattr(self.record, partition_name.lower().strip())
        partition = self.tree.insert(
            self.mbrtree,
            'end',
            text=partition_name.capitalize(),
            values=[mbr_part.get_type()])
        bootable = self.add_item(
            partition,
            'Bootable',
            [mbr_part.is_bootable()]
        )
        size = self.add_item(partition, 'Size', [mbr_part.size])
        start_chs = self.add_item(
            partition,
            'Start CHS Address',
            [mbr_part.start_chs_address]
        )
        end_chs = self.add_item(
            partition,
            'End CHS Address',
            [mbr_part.end_chs_address]
        )
        lba = self.add_item(partition, 'Logical Block Address', [mbr_part.lba])

        return partition
        

root = Tkinter.Tk()
app = App(root)
root.mainloop()
