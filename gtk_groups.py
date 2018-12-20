import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
import constants

class DebugBox(object):
    def __init__(self, container, window):
        self.label = Gtk.Label(container.text)
        self.label.get_style_context().add_class("output_container")
        self.label.set_size_request(200, 120)
        container.ext_width = 200
        container.ext_height = 120
        self.eventbox = Gtk.EventBox()
        self.eventbox.add(self.label)
        self.fixed = Gtk.Fixed()
        self.fixed.add(self.eventbox)
        #self.eventbox.connect('event', window.cb_test1)
        self.eventbox.connect('button-press-event', window.cb_click, container)
        self.eventbox.connect('button-release-event', window.cb_release, container)
        self.eventbox.connect('motion-notify-event', window.cb_motion, container)

    def reconstruct(self, container, window):
        self.label = Gtk.Label(container.text)
        self.label.get_style_context().add_class("output_container")
        self.label.set_size_request(200, 120)
        container.ext_width = 200
        container.ext_height = 120
        self.eventbox = Gtk.EventBox()
        self.eventbox.add(self.label)
        self.fixed = Gtk.Fixed()
        self.fixed.add(self.eventbox)
        self.fixed.move(self.eventbox, container.x, container.y)  # WIPSet to container position
        self.eventbox.connect('button-press-event', window.cb_click, container)
        self.eventbox.connect('button-release-event', window.cb_release, container)
        self.eventbox.connect('motion-notify-event', window.cb_motion, container)
