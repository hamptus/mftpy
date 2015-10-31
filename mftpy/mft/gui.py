import settings
from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showwarning
from tkinter.scrolledtext import ScrolledText
from exceptions import ValidationError
import entry
import os


class Application(Frame):
    """ The application GUI for the MFT Parser """
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title(settings.title)
        self.centerWindow()
        self.master.config(menu=self.buildMenu())

        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1000)
        top.columnconfigure(0, weight=1000)

        self.rowconfigure(0, weight=999)
        self.columnconfigure(2, weight=999)

        self.grid(sticky=N+E+S+W, padx=10, pady=5)

        self.createWidgets()

    def centerWindow(self):
        """ Center the application window """
        w = settings.width
        h = settings.height
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()

        x = (sw - w)/2
        y = (sh - h)/2
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def buildMenu(self):
        # Add a menu bar
        menubar = Menu(self)
        # Create the file menu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open, underline=0)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit, underline=1)
        # Add the file menu to the menu bar
        menubar.add_cascade(label="File", menu=filemenu, underline=0)
        return menubar

    def createWidgets(self):
        self.buildListbox()
        self.buildNotebook()

    def buildListbox(self):
        scrollbar = Scrollbar(self, orient=VERTICAL)
        scrollbar.grid(row=0, column=1, sticky=N+S, pady=5)

        self.listbox = Listbox(self,
                               selectmode=SINGLE,
                               relief=SUNKEN,
                               yscrollcommand=scrollbar.set)
        self.listbox.grid(row=0,
                          column=0,
                          sticky=N+S+W,
                          padx=2,
                          pady=5,
                          ipadx=10)
        self.listbox.bind("<<ListboxSelect>>", self.update)
        self.listbox.rowconfigure(0, weight=1)
        self.listbox.columnconfigure(0, weight=10)
        self.listitems = []
        scrollbar.configure(command=self.listbox.yview)

        self.buttons = Frame(self)
        self.buttons.grid(row=1, column=0, sticky=N+E+S+W, padx=2, pady=2)

        self.clearButton = Button(self.buttons,
                                  text="Clear",
                                  command=self.clearListbox)
        self.clearButton.grid(row=0, column=0, padx=2, sticky=E+W)

        self.exportButton = Button(
            self.buttons, text="Export", command=self.exportEntry)
        self.exportButton.grid(row=0, column=1, padx=2, sticky=E+W)

    def clearListbox(self):
        self.listbox.delete(0, END)
        self.listitems = []
        self.removeTabs()

    def exportEntry(self):
        self.selected = self.listbox.curselection()
        if self.selected:
            e = self.listitems[int(self.selected[0])]
            if hasattr(e, 'filename'):
                fn = asksaveasfilename(initialfile=e.filename + ".mft")
            else:
                fn = asksaveasfilename()
            with open(fn, 'wb') as mftfile:
                mftfile.write(e.dump())

    def buildNotebook(self):
        self.notebook = Notebook(self)
        self.notebook.grid(row=0, column=2, sticky=N+S+W+E, pady=5, padx=5)
        self.notebook.rowconfigure(0, weight=2)
        self.notebook.columnconfigure(1, weight=2)

    def open(self):
        self.filename = askopenfilename()
        if self.filename:
            self.validate_entry(self.filename)

    def add_entry(self, entry):
        self.master.update_idletasks()
        self.listitems.append(entry)
        self.listbox.insert(END, os.path.basename(entry.filename))

    def validate_entry(self, filename):
        if os.path.getsize(filename) == 1024:
            self.filetype = 'entry'
        else:
            self.filetype = 'partition'

        if self.filetype == 'partition':
            p = entry.Partition(filename)
            while True:
                try:
                    w = p.walk()
                    self.add_entry(w.__next__())
                except StopIteration:
                    break

        else:
            with open(filename, 'rb') as data:
                d = data.read(1024)
                e = entry.Entry(d)
                try:
                    e.validate()
                except ValidationError:
                    showwarning(
                        "Invalid Mft entry",
                        "This file is not a valid MFT entry. Its signature value is %s" % e.signature.raw)
                else:
                    self.add_entry(e)

    def get_attribute(self, attributes, attribute_name):
        data = []
        for attr in attributes:
            if hasattr(attr, attribute_name):
                data.append(getattr(attr, attribute_name))
        if data:
            return data
        else:
            return None

    def removeTabs(self):
        tabs = self.notebook.tabs()
        for tab in tabs:
            self.notebook.forget(tab)

    def update(self, event):
        self.selected = self.listbox.curselection()
        self.removeTabs()
        try:
            e = self.listitems[int(self.selected[0])]

            self.entryTab = ScrolledText(
                self.notebook, relief=SUNKEN, padx=10, pady=5)

            self.entryTab.insert(END, "Signature: %s\n" % e.signature)
            self.entryTab.insert(
                END, "Fixup array offset: %s\n" % e.fixup_array_offset)
            self.entryTab.insert(
                END, "Fixup array entries: %s\n" % e.fixup_array_entries)
            self.entryTab.insert(END, "$LogFile sequence number: %s\n" % e.lsn)
            self.entryTab.insert(END, "Sequence: %s\n" % e.sequence)
            self.entryTab.insert(END, "Link count: %s\n" % e.link_count)
            self.entryTab.insert(
                END, "Attribute offset: %s\n" % e.attribute_offset)
            self.entryTab.insert(END, "Flags: %s\n" % e.flags)
            self.entryTab.insert(END, "Used size: %s\n" % e.used_size)
            self.entryTab.insert(
                END, "Allocated size: %s\n" % e.allocated_size)
            self.entryTab.insert(END, "File reference: %s\n" % e.file_ref)
            self.entryTab.insert(
                END, "Next attribute ID: %s\n" % e.next_attr_id)

            self.entryTab.config(state=DISABLED)
            self.notebook.add(self.entryTab, text=e.filename)

            for attribute in e.attributes:
                tab = ScrolledText(
                    self.notebook, relief=SUNKEN, padx=10, pady=5)
                for i in attribute.export():
                    tab.insert(END, i + "\n")
                tab.config(state=DISABLED)
                self.notebook.add(tab, text=attribute.attr_type.value)

        except IndexError:
            pass

if __name__ == '__main__':
    root = Tk()
    app = Application(master=root)
    app.mainloop()
