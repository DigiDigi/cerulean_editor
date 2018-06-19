import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio

# Found the problem. If a treeview is within a box it expands in a weird truncated way.
# Put it inside a listboxrow and it solves the issue. It also looks nicer.

class AppWindow(Gtk.ApplicationWindow):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.gladefile = "treeviewtest.glade"
        self.builder = Gtk.Builder()                # Used to build gui objects from our glade file.
        self.builder.add_from_file(self.gladefile)  #
        self.builder.connect_signals(self)          # Connect the signals to our callbacks in this object.

        self.mainbox = self.builder.get_object("mainbox")
        self.mainbox.reparent(self)

        self.add(self.mainbox)

        self.treeview = self.builder.get_object("treeview")
        self.treeview.set_fixed_height_mode(False)
        self.treestore = Gtk.TreeStore(str, int)
        self.treeview.set_model(self.treestore)
        self.celltext = Gtk.CellRendererText()
        self.treecolumn = Gtk.TreeViewColumn("Objects", self.celltext, text=0)
        self.treeview.append_column(self.treecolumn)

        piter = self.treestore.append(None, ['A', 0])
        self.treestore.append(piter, ['1', 1])
        self.treestore.append(piter, ['2', 2])
        self.treestore.append(piter, ['3', 3])
        self.treestore.append(piter, ['4', 4])
        self.treestore.append(piter, ['5', 5])
        self.treestore.append(piter, ['6', 6])
        self.treestore.append(piter, ['7', 7])
        self.treestore.append(piter, ['8', 8])
        piter = self.treestore.append(None, ['B', 0])
        self.treestore.append(piter, ['1', 1])
        self.treestore.append(piter, ['2', 2])
        self.treestore.append(piter, ['3', 3])
        self.treestore.append(piter, ['4', 4])
        self.treestore.append(piter, ['5', 5])
        self.treestore.append(piter, ['6', 6])
        self.treestore.append(piter, ['7', 7])
        self.treestore.append(piter, ['8', 8])
        piter = self.treestore.append(None, ['C', 0])
        self.treestore.append(piter, ['1', 1])
        self.treestore.append(piter, ['2', 2])
        self.treestore.append(piter, ['3', 3])
        self.treestore.append(piter, ['4', 4])
        self.treestore.append(piter, ['5', 5])
        self.treestore.append(piter, ['6', 6])
        self.treestore.append(piter, ['7', 7])
        self.treestore.append(piter, ['8', 8])

def on_activate(app):
    # Show the application window
    win = AppWindow()
    win.props.application = app
    win.set_title("TreeView")
    win.set_default_size(600, 600)
    win.show_all()

if __name__ == '__main__':
    app = Gtk.Application(application_id='treeviewtest', flags=Gio.ApplicationFlags.FLAGS_NONE)
    # Activate reveals the application window.
    app.connect('activate', on_activate)
    print Gtk.Application.__gsignals__

    app.run()