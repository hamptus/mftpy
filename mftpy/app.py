from mft.entries import entry
import Tkinter
import tkFileDialog


class App(Tkinter.Frame):
	def __init__(self, master=None):
		Tkinter.Frame.__init__(self, master)
		self._create_menubar()
		self.pack(fill=Tkinter.BOTH, expand=1)
		self.center_window()

	def _create_menubar(self):
		self.menubar = Tkinter.Menu()
		self.filemenu = Tkinter.Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label="File", menu=self.filemenu)
		self.filemenu.add_command(label="Open", command=self.open_entry)
		self.filemenu.add_command(label="Quit", command=self.quit)

		self.master.config(menu=self.menubar)

	def open_entry(self):
		self.mft_entry = entry.Entry(tkFileDialog.askopenfile(mode='r').read(1024))
		mft_content = Tkinter.StringVar()
		parsed_mft = Tkinter.Message(
			self,
			textvariable=mft_content,
			justify=Tkinter.LEFT,
			width=5000)
		parsed_mft.config(anchor=Tkinter.W)

		content = "Filename: %s\n" % self.mft_entry.filename
		content += "Signature: %s\n" % self.mft_entry.signature
		content += "LSN: %s\n" % self.mft_entry.lsn
		content += "Sequence: %s\n" % self.mft_entry.sequence
		content += "Link Count: %s\n" % self.mft_entry.link_count
		content += "Fixup Array Offset: %s\n" % self.mft_entry.fixup_array_offset
		content += "Fixup Array Entries: %s\n" % self.mft_entry.fixup_array_entries
		content += "Attribute Offset: %s\n" % self.mft_entry.attribute_offset
		content += "Flags: %s\n" % self.mft_entry.flags
		content += "Used Size: %s\n" % self.mft_entry.used_size
		content += "Allocated Size: %s\n" % self.mft_entry.allocated_size
		content += "File Reference: %s\n" % self.mft_entry.file_ref
		content += "Next Attribute ID: %s\n" % self.mft_entry.next_attr_id
		for attribute in self.mft_entry.attributes:
			for c in attribute.export():
				# FIXME: Motherfucking unicode errors. Just use Python 3. Fuck this.
				try:
					content += "%s\n" % c.decode("utf-8")
				except UnicodeDecodeError:
					pass
		mft_content.set(content)
		parsed_mft.pack(pady=10, padx=10, anchor=Tkinter.W)

	def center_window(self):
		ws = self.master.winfo_screenwidth()
		hs = self.master.winfo_screenheight()

		x = (ws / 2) - 300
		y = (hs / 2) - 200
		self.master.geometry("%dx%d+%d+%d" % (600, 400, x, y))

mftapp = App()
mftapp.master.title("MFT Browser")
mftapp.mainloop()
