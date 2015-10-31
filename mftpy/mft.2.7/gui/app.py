import mft
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
		
		self.master.config(menu=self.menubar)
	
	def open_entry(self):
		self.mft_entry = entry.Entry(tkFileDialog.askopenfile(mode='r').read(1024))
		print self.mft_entry
		print dir(self.mft_entry)
		
	def center_window(self):
		ws = self.master.winfo_screenwidth()
		hs = self.master.winfo_screenheight()

		x = (ws / 2) - 300
		y = (hs / 2) - 200
		self.master.geometry("%dx%d+%d+%d" % (600, 400, x, y))
		
mftapp = App()
mftapp.master.title("MFT Browser")
mftapp.mainloop()		
		
