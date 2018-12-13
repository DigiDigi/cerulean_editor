import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
import constants

class DebugBox(object):
    def __init__(self, container):
        self.label = Gtk.Label(container.text)
        self.label.get_style_context().add_class("output_container")
        self.fixed = Gtk.Fixed()
        self.fixed.add(self.label)
        self.fixed.move(self.label, 300, 300)

    def reconstruct(self, container):
        self.label = Gtk.Label(container.text)
        self.label.get_style_context().add_class("output_container")
        self.fixed = Gtk.Fixed()
        self.fixed.add(self.label)
        self.fixed.move(self.label, container.x, container.y)  # WIPSet to container position
