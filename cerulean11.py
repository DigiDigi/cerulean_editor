import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
import cairo, math, random, dill
import treestorage, gtk_groups
from constants import *

from node_functions import functions
from node_functions import noncalling

class Config(object):
    scroll_inverted = False
    scroll_speed = 2

class NumPrint(object):
    line = 0
    def printline(self, st):
        NumPrint.line += 1
        print(str(NumPrint.line) + '*: ' + st)
numprint = NumPrint()
printline = numprint.printline


# WIP: Move quadtree stuff into its own pymodule.
class QuadTree(object):
    __slots__ = ('objects', 'buckets', 'bid', 'boundary')
    split_number = 2  # Object number at which new buckets are added.
    minimum_size = 16  # Minimum size of buckets.
    next_obj_id = -1
    overlaps = set()   # Temporary set holding buckets that are newly overlapped by an object.

    def new_obj_id(self):  # New object IDs.
        QuadTree.next_obj_id += 1
        return QuadTree.next_obj_id

    def __init__(self):
        self.objects = set()
        self.buckets = []     # .: Only 4 buckets, positioning is important.
        # Note: It takes its boundary from the drawarea, applies it and divides it recursively when adding objects.
        self.bid = self.new_obj_id()
        self.boundary = []


def recurse_bucket_draw(cr, bucket):
    cr.set_source_rgba(1, 1, 0, 1.0)
    cr.set_line_width(1.0)
    cr.move_to(bucket.boundary[0], bucket.boundary[1])
    cr.line_to(bucket.boundary[2], bucket.boundary[1])
    cr.line_to(bucket.boundary[2], bucket.boundary[3])
    cr.line_to(bucket.boundary[0], bucket.boundary[3])
    cr.line_to(bucket.boundary[0], bucket.boundary[1])
    cr.stroke()
    if bucket.buckets:
        recurse_bucket_draw(cr, bucket.buckets[0])
        recurse_bucket_draw(cr, bucket.buckets[1])
        recurse_bucket_draw(cr, bucket.buckets[2])
        recurse_bucket_draw(cr, bucket.buckets[3])


# Check for overlaps to later split buckets and/or add objects to.
def recurse_splitoverlap(bucket, obj):
    # Check if obj overlaps this bucket.
    x_collision = obj.x + obj.ext_width >= bucket.boundary[0] and bucket.boundary[2] >= obj.x
    y_collision = obj.y + obj.ext_height >= bucket.boundary[1] and bucket.boundary[3] >= obj.y
    if x_collision and y_collision:
        QuadTree.overlaps.add(bucket)
    # Recurse to sub buckets.
    for sbucket in bucket.buckets:
        recurse_splitoverlap(sbucket, obj)


# Split buckets and add objects.
def split_adding(obj):
    # obj should be the same object in recurse_splitoverlap.
    for bucket in QuadTree.overlaps:
        bucket.objects.add(obj)
        obj.buckets.append(bucket)
        if len(bucket.objects) >= QuadTree.split_number and not bucket.buckets:
            w = bucket.boundary[2] - bucket.boundary[0]
            h = bucket.boundary[3] - bucket.boundary[1]
            if w <= QuadTree.minimum_size or h <= QuadTree.minimum_size:
                # No splitting beyond minimum size.
                pass
            else:
                # Create sub buckets and boundaries.
                bucket.buckets = [QuadTree(), QuadTree(), QuadTree(), QuadTree()]

                # WIP: Some off-by-one geometry here.
                bucket.buckets[0].boundary = [bucket.boundary[0],
                                              bucket.boundary[1],
                                              bucket.boundary[0]+(w/2),
                                              bucket.boundary[1]+(h/2)]
                bucket.buckets[1].boundary = [bucket.boundary[2]-(w/2),
                                              bucket.boundary[1],
                                              bucket.boundary[2],
                                              bucket.boundary[1]+(h/2)]
                bucket.buckets[2].boundary = [bucket.boundary[2]-(w/2),
                                              bucket.boundary[3]-(h/2),
                                              bucket.boundary[2],
                                              bucket.boundary[3]]
                bucket.buckets[3].boundary = [bucket.boundary[0],
                                              bucket.boundary[3]-(h/2),
                                              bucket.boundary[0]+(w/2),
                                              bucket.boundary[3]]
                # Add all bucket.objects to proper subbuckets.
                for sobj in bucket.objects:
                    # Bucket0
                    x_collision = sobj.x + sobj.ext_width >= bucket.buckets[0].boundary[0] and \
                                                           bucket.buckets[0].boundary[2] >= sobj.x
                    y_collision = sobj.y + sobj.ext_height >= bucket.buckets[0].boundary[1] and \
                                                            bucket.buckets[0].boundary[3] >= sobj.y
                    if x_collision and y_collision:
                        bucket.buckets[0].objects.add(sobj)
                        sobj.buckets.append(bucket.buckets[0])
                    # Bucket1
                    x_collision = sobj.x + sobj.ext_width >= bucket.buckets[1].boundary[0] and \
                                  bucket.buckets[1].boundary[2] >= sobj.x
                    y_collision = sobj.y + sobj.ext_height >= bucket.buckets[1].boundary[1] and \
                                  bucket.buckets[1].boundary[3] >= sobj.y
                    if x_collision and y_collision:
                        bucket.buckets[1].objects.add(sobj)
                        sobj.buckets.append(bucket.buckets[1])
                    # Bucket2
                    x_collision = sobj.x + sobj.ext_width >= bucket.buckets[2].boundary[0] and \
                                  bucket.buckets[2].boundary[2] >= sobj.x
                    y_collision = sobj.y + sobj.ext_height >= bucket.buckets[2].boundary[1] and \
                                  bucket.buckets[2].boundary[3] >= sobj.y
                    if x_collision and y_collision:
                        bucket.buckets[2].objects.add(sobj)
                        sobj.buckets.append(bucket.buckets[2])
                    # Bucket3
                    x_collision = sobj.x + sobj.ext_width >= bucket.buckets[3].boundary[0] and \
                                  bucket.buckets[3].boundary[2] >= sobj.x
                    y_collision = sobj.y + sobj.ext_height >= bucket.buckets[3].boundary[1] and \
                                  bucket.buckets[3].boundary[3] >= sobj.y
                    if x_collision and y_collision:
                        bucket.buckets[3].objects.add(sobj)
                        sobj.buckets.append(bucket.buckets[3])
    QuadTree.overlaps = set()


def remove_from_bucket(obj):
    for bucket in reversed(obj.buckets):
        if len(bucket.objects) - 1 <= 0:
            bucket.buckets = []
        if obj in bucket.objects:  # WIP: Some case exists where this isn't true.
            bucket.objects.remove(obj)


class Main(object):
    def __init__(self):
        self.containers = set()
        # WIP: Two sets of containers maybe? Doubt more than one sub layer is needed.
        self.next_obj_id = -1
        self.next_z_index = -1 # Objects take the next highest z_index when they are brought to front.

        # Nodes to ref for a particular function segment index. (Function chains are populated once indexing is done.)
        self.node_index = dict()  # Line index : [nodes, ]

        # Nodes outside of each function segment after indexing step.
        self.outside_nodes = dict()  # Line index : [nodes,]
        self.quadtree = QuadTree()
        self.quadtree.buckets = []

        self.drawarea_size = None

    def new_obj_id(self):  # New object IDs.
        self.next_obj_id += 1
        return self.next_obj_id

    def new_z_index(self):
        self.next_z_index += 1
        return self.next_z_index

    def bring_top(self, t_obj):
        new_z = self.new_z_index()
        t_obj.z_index = new_z

    def remove_object(self, t_obj):
        self.containers.remove(t_obj)

    def set_object_bounds(self, obj):
        cr = cairo.Context(cairo.ImageSurface(1, 1, cairo.FORMAT_RGB24))
        cr.set_font_size(12)
        cr.select_font_face("Bitstream Vera Sans")

        obj.text_x, obj.text_y, obj.text_width, obj.text_height, dx, dy = cr.text_extents(obj.text)
        obj.ext_width = obj.text_width + obj.w
        obj.ext_height = obj.text_height + obj.h
        # !: Might have to do something with padding here.

    def add_object(self, t_obj):  # Add an object to the rendering list.
        self.containers.add(t_obj)

        if not t_obj.is_gtk_widget:
            self.set_object_bounds(t_obj)

        w, h = self.drawarea_size
        self.quadtree.boundary = [0, 0, w-1, h-1]

        recurse_splitoverlap(self.quadtree, t_obj)
        split_adding(t_obj)

main = Main()


class Edge(object):
    def __init__(self, super_node, sub_node, edgetype=0):
        self.super_node = super_node
        self.sub_node = sub_node
        self.edgetype = edgetype  # 0==Code line, 1==Function line.


# Prototype node object.
class Node(object):
    def __init__(self, text="default", container=None):
        self.module_name = ''
        self.node_name = text                # Also the variable/instance name.
        self.function = lambda _=None: None  # Each node has a function. The default does nothing.
        self.parameters = []                 # Function parameters.
        self.container = container           # Graphical wrapping of this node.

        self.super_edges = []
        self.sub_edges = []
        self.functional = True           # If false, this node is a variable assignment or input without ().
        self.index_flag = False  # Keeps track of whether the node was indexed, then whether the code was written.

    def add_subnode(self, sub_node, edgetype=0):  # Creates an edge from this node to a subnode; connecting the two.
        edge = Edge(self, sub_node, edgetype)
        self.sub_edges.append(edge)
        sub_node.super_edges.append(edge)


class Container(object):
    def __init__(self, text="default", pos=(0, 0)):
        self.test_container = False  # WIP: Testing spacious containers.
        self.is_gtk_widget = False   # True if this is a cairo-drawn element, false if Gtk.
        self.gtks = None             # Class that holds all the gtk widgets for this container.
        self.container_type = None   # Different container types with specific conditions.
        self.obj_id = main.new_obj_id()
        self.z_level = 0                    # z_level is how many sub containers down the object is
        self.z_index = main.new_z_index()   # z_index is determines which containers overlap on the same level.
        self.node = None  # Node obj if is a node.
        self.parent = None  # Parent container. This container is restricted to that containers extents.
        self.free = True  # Shares vertical space or not.

        # With containers that share a vertical space, sizing and positioning is dependant on other containers.
        self.container_above = None
        self.container_below = None
        # Resize handling is a bit quirky where the shared edges of two containers functions in a similar way.
        # Side edges of these types of containers use the parent container
        self.children = set()  # Kept to handle horizontal resizing.

        self.text = text
        self.x = pos[0]
        self.y = pos[1]
        self.w = 20
        self.h = 20
        self.ext_width = 100    # Dimensions of box after padding with text.
        self.ext_height = 100
        self.text_width = 0     # Text string dimensions.
        self.text_height = 0
        self.text_x = 0
        self.text_y = 0
        self.buckets = []  # Quadtree buckets this object is a part of for removing.



class AppWindow(Gtk.ApplicationWindow):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.gladefile = "cerulean.glade"
        self.builder = Gtk.Builder()                # Used to build gui objects from our glade file.
        self.builder.add_from_file(self.gladefile)  #
        self.builder.connect_signals(self)          # Connect the signals to our callbacks in this object.
        self.mainbox = self.builder.get_object("mainbox")
        self.mainbox.reparent(self)  # Glade has a separate parent window widget for previewing.

        self.connect('check-resize', self.cb_windowresize)

        self.dialog_paramset = self.builder.get_object("dialog_paramset")
        self.dialog_paramset.set_transient_for(self)
        self.dialog_paramset.set_attached_to(self.mainbox)
        # WIP: This dialog goofs when escape is pressed.. But as far as I can tell, it's not caused by a callback.

        self.scroll_draw = self.builder.get_object("scroll_draw")
        self.entry_rename = self.builder.get_object("entry_rename")
        self.dialog_newnode = self.builder.get_object("dialog_newnode")
        self.entry_newnode = self.builder.get_object("entry_newnode")
        self.widget_area = self.builder.get_object("widget_area")
        self.drawarea = self.builder.get_object("drawarea")
        self.drawarea.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.drawarea.connect('draw', self.cb_draw)
        self.eventbox = self.builder.get_object("eventbox")
        self.eventbox.connect('button-press-event', self.cb_click)
        self.eventbox.connect('button-release-event', self.cb_release)
        self.eventbox.connect('motion-notify-event', self.cb_motion)
        self.statusbar = self.builder.get_object("statusbar")

        self.flag_expanded = False  # Flagged when an object is dragged off the drawarea and expands it.
        self.flag_scrolldragging = False  # Flagged when an empty space is clicked and held to scroll.
        self.flag_objectdragging = False  # Flagged when moving an object within the drawarea.
        self.flag_clicked = False  # Flagged after clicking so that release events don't fire out of order.
        self.grabbed_diff = []  # Space between the position of each grabbed box and the cursor.
        self.remove_grabbed = None # Reference to object being grabbed for temporary removal.
        self.grabbed_objects = []
        self.selected_objects = []
        self.target_obj = None  # Object targeted with right click.
        self.mod_ctrl = False
        self.mod_shift = False

        self.drag_creating_object = None  # Object being created before being dragged.
        # Drag'n'drop.
        self.selected_container_type = 0  # References a type of container. Selected when doing drag'n'drop.
        self.selected_container_name = ''      # Name of the referenced container.

        # Buffer for seen nodes while compiling the exec string.
        self.seen_nodes = []
        self.execstring = ''

        self.widget_area.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.eventbox.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)

        self.listview = self.builder.get_object("listview")
        self.liststore = Gtk.ListStore(str)
        self.liststore.append(['xmodal'])
        self.listview.set_model(self.liststore)
        self.listcolumn = Gtk.TreeViewColumn("Saved Models")
        self.listview.append_column(self.listcolumn)
        celltext = Gtk.CellRendererText()
        self.listcolumn.pack_start(celltext, True)
        self.listcolumn.add_attribute(celltext, 'text', 0)
        self.listview2 = self.builder.get_object("listview2")
        self.liststore2 = Gtk.ListStore(str)
        self.liststore2.append(['VGG'])
        self.listview2.set_model(self.liststore2)
        self.listcolumn2 = Gtk.TreeViewColumn("Premade Models")
        self.listview2.append_column(self.listcolumn2)
        celltext = Gtk.CellRendererText()
        self.listcolumn2.pack_start(celltext, True)
        self.listcolumn2.add_attribute(celltext, 'text', 0)

        self.treeview = self.builder.get_object("treeview")
        self.treeview.set_fixed_height_mode(False)
        self.treestore = Gtk.TreeStore(str, int)
        self.treeview.set_model(self.treestore)
        self.celltext = Gtk.CellRendererText()
        self.treecolumn = Gtk.TreeViewColumn("Objects", self.celltext, text=0)
        self.treecolumn.set_sizing(Gtk.TreeViewColumnSizing.GROW_ONLY)
        self.treecolumn.set_expand(True)
        self.treecolumn.set_resizable(True)
        self.treeview.append_column(self.treecolumn)

        treestorage.additems(self.treestore, self.treeview)

        # Bug: The last couple of trees are often hidden/clipped behind the next widgets if the tree expands too much.
        self.dragactions = Gdk.DragAction.COPY
        self.targetentry = Gtk.TargetEntry.new('text/plain', 1, 0)
        self.targets = Gtk.TargetList.new([self.targetentry])

        self.widget_area.drag_dest_set(Gtk.DestDefaults.ALL, [self.targetentry], self.dragactions)
        self.widget_area.drag_dest_set_target_list(self.targets)
        self.widget_area.drag_dest_add_text_targets()

        self.widget_area.connect('drag-drop', self.cb_drag_drop)
        self.widget_area.connect('drag-end', self.cb_drag_end)
        self.treeview.connect('drag-data-get', self.cb_drag_data_get)
        self.treeview.connect('drag-begin', self.cb_drag_begin)
        self.treeview.connect('button-press-event', self.cb_treeclick)

        self.nodemenu = Gtk.Menu()
        self.nodemenu.connect('button-release-event', self.cb_release)

        self.nm_connectcode = Gtk.MenuItem("Connect code")
        self.nodemenu.append(self.nm_connectcode)
        self.nm_connectcode.connect('button-press-event', self.cb_node_connectcode)
        self.nm_connectcode.show()

        self.nm_connectoutput = Gtk.MenuItem("Connect output")
        self.nodemenu.append(self.nm_connectoutput)
        self.nm_connectoutput.connect('button-press-event', self.cb_node_connectoutput)
        self.nm_connectoutput.show()

        self.nm_paramset = Gtk.MenuItem("Modify parameters")
        self.nodemenu.append(self.nm_paramset)
        self.nm_paramset.connect('button-press-event', self.cb_node_paramset)
        self.nm_paramset.show()

        self.nm_rungraph = Gtk.MenuItem("Execute to here")
        self.nodemenu.append(self.nm_rungraph)
        self.nm_rungraph.connect('button-press-event', self.cb_node_rungraph)
        self.nm_rungraph.show()

        # CSS styling and settings >
        settings = Gtk.Settings.get_default()
        settings.props.gtk_button_images = True
        style_provider = Gtk.CssProvider()
        css = open('cerulean.css', 'rb')
        css_data = css.read()
        css.close()
        style_provider.load_from_data(css_data)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        allocation = self.widget_area.get_allocation()
        w = allocation.width
        h = allocation.height
        main.drawarea_size = [w, h]
        main.quadtree.boundary = [0, 0, w, h]
        self.default_window_size = self.get_size()

    # Remake quadtrees altogether.
    def bucket_remake(self):
        printline('bucket_remake')
        main.quadtree = QuadTree()
        w, h = main.drawarea_size
        main.quadtree.boundary = [0, 0, w - 1, h - 1]
        for obj in main.containers:
            obj.buckets = []  # Clear associated buckets.
            recurse_splitoverlap(main.quadtree, obj)
            split_adding(obj)
        self.drawarea.queue_draw_area(0, 0, main.drawarea_size[0], main.drawarea_size[1])

    def further_indexing(self):  # Indexing the next nodes outside of the current function chain.
        if len(main.outside_nodes) > 0:  # Else: Recursion finished.

            outside_nodes = main.outside_nodes.copy()
            main.outside_nodes = dict()

            for idx in outside_nodes:
                for node in outside_nodes[idx]:
                    idx_node = self.indexing(node, idx)
                    if idx_node is not None:
                        if idx in main.node_index:
                            main.node_index[idx].append(idx_node)
                        else:
                            main.node_index[idx] = [idx_node, ]
            self.further_indexing()

    def indexing(self, node, idx):  # Index nodes recursively.
        if node.index_flag == False:  # Else: Recursion finished.
            node.index_flag = True
            self.downward_indexing(node, idx)
            self.upward_indexing(node, idx)
            return node

    def downward_indexing(self, node, idx):  # Index nodes walking through subnodes recursively.
        for subedge in node.sub_edges:
            subnode = subedge.sub_node

            if subedge.edgetype == 1:  # Function edge between node and subnode.
                if node.functional is True:
                    self.indexing(subnode, idx)
                else:
                    functional_edge = [False]
                    for superedge in node.super_edges:
                        if superedge.edgetype == 1:
                            functional_edge[0] = True
                            break
                    if functional_edge[0] is True:  # Function edge exists in node super edges.
                        if idx + 1 not in main.outside_nodes:
                            main.outside_nodes[idx + 1] = []
                        main.outside_nodes[idx + 1].append(subnode)
                    else:
                        self.indexing(subnode, idx)
            else:
                if idx + 1 not in main.outside_nodes:
                    main.outside_nodes[idx + 1] = []
                main.outside_nodes[idx + 1].append(subnode)

    def upward_indexing(self, node, idx):   # Index nodes walking through supernodes recursively
        node_index = 0
        for superedge in node.super_edges:
            supernode = superedge.super_node

            if superedge.edgetype == 1:  # Functional edge between node and supernode.
                if supernode.functional is True:
                    self.indexing(supernode, idx)
                else:
                    # If any of its super nodes have solid connections to it, this a place for an upward marker.
                    functional_edge = [False]
                    for superedge in supernode.super_edges:
                        if superedge.edgetype == 1:
                            functional_edge[0] = True
                            break
                    if functional_edge[0] == True:
                        if idx - 1 not in main.outside_nodes:
                            main.outside_nodes[idx - 1] = []
                        main.outside_nodes[idx - 1].append(supernode)
                    else:
                        self.indexing(supernode, idx)
            else:
                if idx - 1 not in main.outside_nodes:
                    main.outside_nodes[idx - 1] = []
                main.outside_nodes[idx - 1].append(supernode)
            node_index += 1


    # Recurse back through nodes and fill out their parameters.
    def upward_writing(self, node):
        params = []

        if not node.functional:
            return node.node_name

        else:
            for supernode in node.supernodes:
                # Don't iterate over a node if its behind a code line.
                params.append(upward_writing(supernode))

            paramstring = ''
            for param in params:
                paramstring = paramstring + param + ', '
            paramstring = paramstring[:-2]  # trim the last comma.

            paramstring = node.node_name + '(' + paramstring + ')'

            return paramstring

    def downward_writing(self, node):
        if node.functional == True:
            pass
        else:
            pass

    def recursive_writing(self, node):
        pass

    def cb_savefile(self, widget):
        print main.drawarea_size
        main.windowsize = self.get_size()
        with open('save.pkl', 'wb') as f:
            dill.dump(main, f)

    def cb_openfile(self, widget):
        global main

        for container in main.containers:
            if container.is_gtk_widget:
                self.widget_area.remove(container.gtks.fixed)

        with open('save.pkl', 'rb') as f:
            new_main = dill.load(f)
        main = new_main

        for container in main.containers:
            if container.is_gtk_widget:
                container.gtks.reconstruct(container)
                self.widget_area.add_overlay(container.gtks.fixed)
                self.widget_area.set_overlay_pass_through(container.gtks.fixed, True)
                self.widget_area.show_all()


        self.resize(main.windowsize[0], main.windowsize[1])
        self.drawarea.set_size_request(main.drawarea_size[0], main.drawarea_size[1])
        self.drawarea.queue_draw_area(0, 0, main.drawarea_size[0], main.drawarea_size[1])

    def cb_node_rungraph(self, widget, data):
        """ Indexing stage. Nodes are segmented into function chains for each index.
            The index determines where the line of code for that function chain will end up. """

        node = self.target_obj.node
        self.indexing(node, 0)
        main.node_index[0] = [node, ]
        self.further_indexing()

        """ Code resolution stage. Segments at each index are iterated through and lines are written when resolved. """

        node_index_keys = main.node_index.keys()
        node_index_keys.sort()  # Sorted list of index keys in numerical order.

        self.execstring = ''
        # Reset indexing stuff.
        main.node_index = {}
        main.outside_nodes = {}
        # DebugOnly: Clearing the index flags. This will normally be done on the writing pass.
        for obj in main.containers:
            if isinstance(obj, Node):
                obj.index_flag = False

    def create_f_python(self, node):
        tv = Gtk.TextView()
        tv.set_can_focus(False)
        tv.show_all()
        tv.set_visible(True)
        tv.set_size_request(100, 100)
        tv.set_border_width(2)
        te = Gtk.EventBox()
        te.set_above_child(False)
        te.connect('button-release-event', self.cb_edit_click)
        te.add(tv)
        te.set_size_request(100, 100)
        # te.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
        te.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        tf = Gtk.Fixed()
        tf.add(te)
        tf.move(te, 300, 300)
        self.widget_area.add_overlay(tf)
        self.widget_area.set_overlay_pass_through(tf, True)
        self.widget_area.show_all()

        def nodefunction(node):
            # WIP: Capture the last return line of the textview for this return value assuming it exists.
            textview_return = None
            return textview_return
        return nodefunction

    def create_debug_gtk(self, node):
        node.container.is_gtk_widget = True
        node.container.gtks = gtk_groups.DebugBox(node.container)
        self.widget_area.add_overlay(node.container.gtks.fixed)
        self.widget_area.set_overlay_pass_through(node.container.gtks.fixed, True)
        self.widget_area.show_all()

        def nodefunction(node):
            # WIP: Capture the last return line of the textview for this return value assuming it exists.
            textview_return = None
            return textview_return
        return nodefunction

    def cb_drag_drop(self, widget, drag_context, x,y, time):
        # Create a node/object of the gathered type at the x/y.
        nodetext = self.selected_container_type

        cont = Container(self.selected_container_name, (x, y))
        n = Node(self.selected_container_name, cont)
        cont.node = n
        cont.container_type = self.selected_container_type

        if cont.container_type == DEBUG_TESTCONTAINER:
            cont.w = 200
            cont.h = 120
            cont.text = ''
            main.set_object_bounds(cont)
        elif cont.container_type == DEBUG_TESTCONTAINER2:
            cont.w = 250
            cont.h = 400
            cont.text = ''
            main.set_object_bounds(cont)
        elif cont.container_type == CONT_CLASS:
            cont.w = 250
            cont.h = 400
            cont.text = 'classname'
            main.set_object_bounds(cont)
        elif cont.container_type == DEBUG_GTK:
            n.function = self.create_debug_gtk(cont.node)
            n.container.gtks.fixed.move(n.container.gtks.label, n.container.x, n.container.y)

        if not cont.is_gtk_widget:
            n.function = functions[self.selected_container_type]

        if self.selected_container_type in noncalling:
            n.functional = False

        main.add_object(cont)

        # !: Copy-pasted from cb_release. Places the container into any containers it lands on.
        potential_overlaps = set()
        # Check if there are any objects in the same bucket.
        for bucket in cont.buckets:
            if not bucket.buckets:  # Bottom-most only buckets.
                # Collect potential collisions into a set.
                for bobj in bucket.objects:
                    if bobj is not cont:
                        potential_overlaps.add(bobj)
        overlaps = {}  # Overlaps that could be on multiple z levels. {z_index : overlap}
        for cobj in potential_overlaps:
            if cont.x >= cobj.x and cont.x + cont.ext_width <= cobj.x + cobj.ext_width:
                if cont.y >= cobj.y and cont.y + cont.ext_height <= cobj.y + cobj.ext_height:
                    # Grabbed object is within the bounds of a container. Place it inside.
                    overlaps[cobj.z_index] = cobj
        if overlaps:
            # Get the highest z_index container and make it a new parent container.
            newparent = overlaps[max(overlaps)]
            newparent.children.add(cont)
            cont.parent = newparent
        self.recurse_zlevel(cont)

        self.bucket_remake()
        self.drawarea.queue_draw_area(0, 0, main.drawarea_size[0], main.drawarea_size[1])

    def cb_drag_data_get(self, widget, drag_context, data, info, time):
        selected_path = self.treeview.get_selection().get_selected_rows()
        selected_iter = self.treestore.get_iter(selected_path[1][0])
        v1 = self.treestore.get_value(selected_iter, 0)
        v2 = self.treestore.get_value(selected_iter, 1)
        self.selected_container_name = v1
        self.selected_container_type = v2

    def cb_drag_end(self, widget, drag_context):
        pass

    def cb_drag_begin(self, widget, drag_context):
        pass

    def cb_treeclick(self, widget, event):
        x = event.x
        y = event.y
        path, column, x, y = self.treeview.get_path_at_pos(x, y)

        try:
            path[1]
            self.treeview.drag_begin_with_coordinates(self.targets, self.dragactions, event.button, event, x, y)

        except IndexError:
            pass

    # TextView (EventBox) is clicked.
    def cb_edit_click(self, widget, event):
        widget.get_window().set_cursor(Gdk.Cursor.new_from_name(self.get_display(), "row-resize"))
        widget.get_child().set_can_focus(True)
        widget.get_child().grab_focus()
        widget.get_child().set_can_focus(False)

    def cb_button_click(self, widget, event):
        widget.get_window().set_cursor(Gdk.Cursor.new_from_name(self.get_display(), "row-resize"))
        widget.get_child().set_can_focus(True)
        widget.get_child().grab_focus()
        widget.get_child().set_can_focus(False)

    def node_recurse(self, node):
        if len(node.supernodes) > 0:
            self.seen_nodes.append(node)
            for supernode in node.supernodes:
                if supernode not in self.seen_nodes:
                    self.node_recurse(supernode)

        parameters = list(node.parameters[:])
        parameters.insert(0, node.supernodes)

        pstring = ''
        for param in parameters:
            if isinstance(param, int):
                pstring += str(param) + ','
            elif isinstance(param, float):
                pstring += str(param) + ','
            elif isinstance(param, str):
                pstring += '\"' + param + '\"' + ','
            elif isinstance(param, list):
                if len(param) > 0:
                    pstring += '('
                    for item in param:
                        if isinstance(item, int):
                            pstring += str(item) + ','
                        elif isinstance(item, float):
                            pstring += str(item) + ','
                        elif isinstance(item, str):
                            pstring += '\"' + item + '\"' + ','
                        elif isinstance(item, Node):
                            pstring += item.node_name + ','
                        else:  # Variable?
                            pstring += item.__name__ + ','
                    pstring = pstring[:-1]
                    pstring += ')' + ','
            elif isinstance(item, Node):
                pstring += param.node_name + ','
            else:  # Variable?
                pstring += param.__name__ + ','
        pstring = pstring[:-1]
        pstring2 = node.node_name + ' = ' + node.function.__module__ + '.' + node.function.__name__ + '(' + pstring + ')'

        self.execstring += pstring2 + '\n'

    # WIP: Naming needs to be limited to valid variable names.
    # I guess it could be handled in the parameter setting dialog also.
    def cb_node_paramset(self, widget, data):
        if self.target_obj:
            if self.target_obj.node:
                self.dialog_paramset.show()

    # Connect nodes to target.
    def cb_node_connectcode(self, widget, data):
        for obj in self.selected_objects:
            if obj.node:
                node = obj.node
                if node is not self.target_obj.node:
                    # Conditional for preventing two-way edges.
                    sub_edge_exists = 0
                    for sub_edge in self.target_obj.node.sub_edges:
                        if node is sub_edge.sub_node:
                            sub_edge_exists += 1
                            break  # Break for loop; sub_edge found.
                    if sub_edge_exists < 1:
                        # Conditonal for preventing dupe same edges.
                        super_edge_exists = 0
                        for super_edge in self.target_obj.node.super_edges:
                            if node is super_edge.super_node:
                                super_edge_exists += 1
                                break  # Break for loop; super_edge found.
                        if super_edge_exists < 1:
                            node.add_subnode(self.target_obj.node, 0)
        self.target_obj = None
        self.drawarea.queue_draw_area(0, 0, main.drawarea_size[0], main.drawarea_size[1])

    # Connect nodes to target.
    def cb_node_connectoutput(self, widget, data):
        for obj in self.selected_objects:
            if obj.node:
                node = obj.node
                if node is not self.target_obj.node:
                    # Conditional for preventing two-way edges.
                    sub_edge_exists = 0
                    for sub_edge in self.target_obj.node.sub_edges:
                        if node is sub_edge.sub_node:
                            sub_edge_exists += 1
                            break  # Break for loop; sub_edge found.
                    if sub_edge_exists < 1:
                        # Conditonal for preventing dupe same edges.
                        super_edge_exists = 0
                        for super_edge in self.target_obj.node.super_edges:
                            if node is super_edge.super_node:
                                super_edge_exists += 1
                                break  # Break for loop; super_edge found.
                        if super_edge_exists < 1:
                            node.add_subnode(self.target_obj.node, 1)
        self.target_obj = None
        self.drawarea.queue_draw_area(0, 0, main.drawarea_size[0], main.drawarea_size[1])

    def cb_focus(self, widget, data):
        pass

    def cb_focus_in(self, widget, data):
        self.mod_ctrl = False
        self.mod_shift = False

    def cb_focus_out(self, widget, data):
        pass

    # Go through children and further children of a container and add them into a set.
    def recurse_subobjects(self, obj, sobj_set):
        if obj.children:
            for sobj in obj.children:
                self.recurse_subobjects(sobj, sobj_set)
                sobj_set.add(sobj)

    def recurse_click(self, bucket, event, hpos, vpos):
        if bucket.buckets:
            # Start by testing if the x click event is within the left or right side buckets.
            # The buckets are stored clockwise. Buckets [1] and [2] share boundary[0].
            # ex            x1   y1   x2     y2
            #     bucket[0] 0,   0,   200,   200
            #     bucket[1] 201, 0,   400,   200
            #     bucket[2] 201, 201, 400,   400
            #     bucket[3] 0,   201, 200,   400
            if event.x < bucket.buckets[1].boundary[0]:
                # bucket[0] or bucket[3]
                if event.y < bucket.buckets[3].boundary[1]:
                    obj0 = self.recurse_click(bucket.buckets[0], event, hpos, vpos)
                    return obj0
                else:
                    obj1 = self.recurse_click(bucket.buckets[3], event, hpos, vpos)
                    return obj1
            else:
                # bucket[1] or bucket[2]
                if event.y < bucket.buckets[2].boundary[1]:
                    obj2 = self.recurse_click(bucket.buckets[1], event, hpos, vpos)
                    return obj2
                else:
                    obj3 = self.recurse_click(bucket.buckets[2], event, hpos, vpos)
                    return obj3
        else:
            if bucket.objects:
                if self.target_obj:
                    if self.target_obj.is_gtk_widget:
                        self.target_obj.gtks.label.get_style_context().remove_class("targeted_border")
                self.target_obj = None

                clicked_objects = {}
                for obj in bucket.objects:
                    if obj.node:
                        if event.x >= obj.x and event.x < obj.x + obj.ext_width:
                            if event.y >= obj.y and event.y < obj.y + obj.ext_height:
                                clicked_objects[obj.z_index] = obj

                if clicked_objects:
                    selected_obj = clicked_objects[max(clicked_objects)]
                    if event.button == Gdk.BUTTON_PRIMARY:
                        if self.mod_ctrl:  # Ctrl-add selection.
                            if selected_obj in self.selected_objects:  # Invert selection.
                                sindex = self.selected_objects.index(selected_obj)
                                if self.selected_objects[sindex].is_gtk_widget:
                                    self.selected_objects[sindex].gtks.label.get_style_context().remove_class(
                                        "targeted_border")
                                    self.selected_objects[sindex].gtks.label.get_style_context().remove_class(
                                        "selected_border")
                                self.selected_objects.pop(sindex)
                            else:
                                self.selected_objects.append(selected_obj)
                        else:
                            for sobj in self.selected_objects:
                                if sobj.is_gtk_widget:
                                    sobj.gtks.label.get_style_context().remove_class("targeted_border")
                                    sobj.gtks.label.get_style_context().remove_class("selected_border")

                            self.selected_objects = [selected_obj]
                        self.flag_objectdragging = True

                        #for sobj in self.selected_objects:
                        #    pass
                        #    print 'z_level', sobj, sobj.z_level

                        # Select all descendants of a container if the container is selected.
                        # Combine them in a set with currently selected objects.
                        selected_and_sub_objects = set()
                        for selected_obj in self.selected_objects:
                            self.recurse_subobjects(selected_obj, selected_and_sub_objects)
                            selected_and_sub_objects.add(selected_obj)

                        # !: UI thought. It's hard to tell whats just selected vs whats a child of a container.
                        # .. Might want a subtle graphical distinction between the two.

                        # !: This turns the set into a list so it can be self.selected_objects.
                        # TD: Need to check if that even needs to be a list.
                        selected_and_sub_object_list = []
                        for sobj in selected_and_sub_objects:
                            selected_and_sub_object_list.append(sobj)
                        self.grabbed_objects = selected_and_sub_object_list[:]

                        # Remove selected objects from parent containers if they exist.
                        for sobj in self.selected_objects:
                            if sobj.parent:
                                sobj.parent.children.remove(sobj)
                                sobj.parent = None

                        # Dict for sorting each grabbed object by their z_index.
                        zdct = {}
                        coindex = 0
                        for gobj in self.grabbed_objects:
                            zdct[gobj.z_index] = gobj
                            # Remove object from bucket on being dragged.
                            remove_from_bucket(gobj)

                            # Diff of clicked position and each grabbed object.
                            self.grabbed_diff.append([event.x - self.grabbed_objects[coindex].x, event.y - self.grabbed_objects[coindex].y])
                            coindex += 1

                        # Bring all grabbed objects to front and maintain their relative zindices.
                        for z, gobj in sorted(zdct.items()):
                            main.bring_top(gobj) # Grants new highest z_index for the object.

                    elif event.button == Gdk.BUTTON_SECONDARY:
                        if selected_obj.node:
                            self.target_obj = selected_obj
                            if selected_obj.is_gtk_widget:
                                selected_obj.gtks.label.get_style_context().add_class("targeted_border")


                        self.nodemenu.popup(None, None, None, None, event.button, event.time)
                    return selected_obj
                self.drawarea.queue_draw_area(0, 0, main.drawarea_size[0], main.drawarea_size[1])


    def cb_click(self, widget, event):
        if not self.flag_clicked:  # Flag to keep additional click events from firing before cb_release.
            # Keep this stuff in mind for rendering optimization..
            hvis = self.scroll_draw.get_hadjustment().get_page_size()  # Visible area.
            vvis = self.scroll_draw.get_vadjustment().get_page_size()
            hpos = self.scroll_draw.get_hadjustment().get_value()  # Scrollbar position.
            vpos = self.scroll_draw.get_vadjustment().get_value()

            clickedobject = self.recurse_click(main.quadtree, event, hpos, vpos)

            for sobj in self.selected_objects:
                if sobj.is_gtk_widget:
                    self.widget_area.reorder_overlay(sobj.gtks.fixed, -1)
                    sobj.gtks.label.get_style_context().add_class("selected_border")
                    sobj.gtks.label.set_size_request(100,100)

            if not clickedobject:
                if not self.flag_objectdragging:
                    self.flag_scrolldragging = True
                    self.scroll_initial_click = (event.x, event.y)
                    self.scroll_initial_adjustment = (hpos, vpos)
                    for sobj in self.selected_objects:
                        if sobj.is_gtk_widget:
                            sobj.gtks.label.get_style_context().remove_class("targeted_border")
                            sobj.gtks.label.get_style_context().remove_class("selected_border")
                    self.selected_objects = []

                    if self.target_obj:
                        if self.target_obj.is_gtk_widget:
                            self.target_obj.gtks.label.get_style_context().remove_class("targeted_border")
                    self.target_obj = None
            self.eventbox.grab_focus()
            self.flag_clicked = True

    def recurse_zlevel(self, obj):
        if obj.parent:
            obj.z_level = obj.parent.z_level + 1
        else:
            obj.z_level = 0
        if obj.children:
            for child in obj.children:
                self.recurse_zlevel(child)

    def cb_release(self, widget, event):
        # This is also called within the nodemenu so that click release properly clears flags.
        self.flag_scrolldragging = False
        self.flag_objectdragging = False
        if self.grabbed_objects:
            for gobj in self.grabbed_objects:
                exp_w = None
                exp_h = None
                if gobj.x + gobj.ext_width >= main.drawarea_size[0]:
                    exp_w = True
                    main.drawarea_size[0] = gobj.x + gobj.ext_width
                if gobj.y + gobj.ext_height >= main.drawarea_size[1]:
                    exp_h = True
                    main.drawarea_size[1] = gobj.y + gobj.ext_height
                if exp_w or exp_h:
                    self.flag_expanded = True

                # Tests the object against each quad bucket recursively and asks if it will split the bucket.
                # If so, it adds it to QuadTree.overlaps.
                recurse_splitoverlap(main.quadtree, gobj)
                # Add objects back in using QuadTree.overlaps.
                split_adding(gobj)
                self.grabbed_diff = []

            # Place the selected objects into any containers where they land.
            for gobj in self.selected_objects:
                potential_overlaps = set()
                # Check if there are any objects in the same bucket.
                for bucket in gobj.buckets:
                    if not bucket.buckets:  # Bottom-most only buckets.
                        # Collect potential collisions into a set.
                        for bobj in bucket.objects:
                            if bobj is not gobj:
                                potential_overlaps.add(bobj)

                # TD: Need to also do this when dragging from list menu.

                overlaps = {}  # Overlaps that could be on multiple z levels. {z_index : overlap}
                for cobj in potential_overlaps:
                    if gobj.x >= cobj.x and gobj.x + gobj.ext_width <= cobj.x + cobj.ext_width:
                        if gobj.y >= cobj.y and gobj.y + gobj.ext_height <= cobj.y + cobj.ext_height:
                            # Grabbed object is within the bounds of a container. Place it inside.
                            overlaps[cobj.z_index] = cobj
                if overlaps:
                    # Get the highest z_index container and make it a new parent container.
                    newparent = overlaps[max(overlaps)]
                    newparent.children.add(gobj)
                    gobj.parent = newparent

                self.recurse_zlevel(gobj)

            if self.flag_expanded:
                self.drawarea.set_size_request(main.drawarea_size[0], main.drawarea_size[1])
                self.bucket_remake()

            self.grabbed_objects = []
            self.drawarea.queue_draw_area(0, 0, main.drawarea_size[0], main.drawarea_size[1])
        self.flag_clicked = False

    def cb_motion(self, widget, event):
        if self.flag_objectdragging:
            coindex = 0
            for gobj in self.grabbed_objects:
                gox = event.x - self.grabbed_diff[coindex][0]
                goy = event.y - self.grabbed_diff[coindex][1]
                new_posx = gox
                new_posy = goy
                if gox < 0:
                    new_posx = 0
                if goy < 0:
                    new_posy = 0

                gobj.x = new_posx
                gobj.y = new_posy

                if gobj.is_gtk_widget:
                    gobj.gtks.fixed.move(gobj.gtks.label, gobj.x, gobj.y)

                coindex += 1
            self.drawarea.queue_draw_area(0, 0, main.drawarea_size[0], main.drawarea_size[1])
        elif self.flag_scrolldragging:
            # !: Non inverted scrolling feels a bit too slippery. Inverted scrolling feels jittery.
            # Maybe would be better to slowly pulse in scroll updates instead of rubber-banding.
            if Config.scroll_inverted:
                new_adjustment_x = (self.scroll_initial_click[0] - event.x) / Config.scroll_speed
                new_adjustment_y = (self.scroll_initial_click[1] - event.y) / Config.scroll_speed
            else:
                new_adjustment_x = (event.x - self.scroll_initial_click[0]) / Config.scroll_speed
                new_adjustment_y = (event.y - self.scroll_initial_click[1]) / Config.scroll_speed
            self.scroll_draw.get_hadjustment().set_value(self.scroll_initial_adjustment[0] + new_adjustment_x)
            self.scroll_draw.get_vadjustment().set_value(self.scroll_initial_adjustment[1] + new_adjustment_y)

    # WIP: Rename to removenodes.
    def cb_removenode(self, widget):

        #WIP: Fix for container/node removal.
        if len(self.selected_nodes) > 0:
            for node in self.selected_nodes:

                # Remove subedge reference for each node connected to this node.
                for superedge in node.super_edges:
                    for subedge in superedge.super_node.sub_edges:
                        if subedge is superedge:
                            superedge.super_node.sub_edges.index(subedge)
                            superedge.super_node.sub_edges.pop(superedge.super_node.sub_edges.index(subedge))  # aaaaa
                            break
                # Remove superedge reference for each node connected to this node.
                for subedge in node.sub_edges:
                    for superedge in subedge.sub_node.super_edges:
                        if superedge is subedge:
                            subedge.sub_node.super_edges.index(superedge)
                            subedge.sub_node.super_edges.pop(subedge.sub_node.super_edges.index(superedge))
                            break

                # Remove edges.
                node.super_edges = None
                node.sub_edges = None
                main.remove_object(node)
                remove_from_bucket(node)

            self.selected_nodes = []
            self.grabbed_objects = None
            self.target_obj = None
            self.drawarea.queue_draw_area(0, 0, main.drawarea_size[0], main.drawarea_size[1])

    def cb_removenode_confirmed(self, widget):
        pass

    def cb_removenode_cancel(self, widget):
        pass

    def cb_paramset_confirm(self, widget):
        self.dialog_paramset.hide()
        # WIP: Also set this for node.
        self.target_obj.text = self.entry_rename.get_text()
        main.set_object_bounds(self.target_obj)
        self.entry_rename.set_text("")

    def cb_paramset_cancel(self, widget):
        self.dialog_paramset.hide()

    def cb_paramset_keyrelease(self, widget, event):
        if event.keyval == Gdk.KEY_Return:  # !: Should probably also only do this only if Ok is highlighted.
            # WIP: Also set this for node.
            self.target_obj.text = self.entry_rename.get_text()
            main.set_object_bounds(self.target_obj)
            self.entry_rename.set_text("")
            self.dialog_paramset.hide()
        """
        if event.keyval == Gdk.KEY_Escape:
            self.entry_rename.set_text("")
            self.dialog_paramset.hide()
        """

    def cb_newnode(self, widget):
        if len(self.selected_objects) > 0:
            self.dialog_newnode.show()
        else:
            if len(main.containers) == 0:
                self.dialog_newnode.show()
            else:
                self.dialog_newnode.show()

    def cb_newnode_confirmed(self, widget):
        self.newnode_confirmed()

    def cb_newnode_cancel(self, widget):
        self.entry_newnode.set_text("")
        self.dialog_newnode.hide()

    def cb_newnode_keypress(self, widget, event):
        if event.keyval == Gdk.KEY_Return:  # !: Should probably also only do this only if Ok is highlighted.
            self.newnode_confirmed()
        if event.keyval == Gdk.KEY_Escape:
            self.entry_newnode.set_text("")
            self.dialog_newnode.hide()

    def cb_keypress(self, widget, event, data=None):
        # WIP: Key auto-repeat is manageable if a flag is set on each pressed, reset on on released.

        #if event.keyval == Gdk.KEY_Escape:
        #    self.destroy()  # WIP: Add quit dialog.

        if event.keyval == Gdk.KEY_Delete:
            self.cb_removenode(None)
        #if event.keyval == Gdk.KEY_n:
        #    self.cb_newnode(None)
        if event.keyval == Gdk.KEY_Control_L:
            self.mod_ctrl = True
        if event.keyval == Gdk.KEY_Control_R:
            self.mod_ctrl = True
        if event.keyval == Gdk.KEY_Shift_L:
            self.mod_shift = True
        if event.keyval == Gdk.KEY_Shift_R:
            self.mod_shift = True

    def cb_keyrelease(self, widget, event, data=None):
        if event.keyval == Gdk.KEY_Control_L:
            self.mod_ctrl = False
        if event.keyval == Gdk.KEY_Control_R:
            self.mod_ctrl = False
        if event.keyval == Gdk.KEY_Shift_L:
            self.mod_shift = False
        if event.keyval == Gdk.KEY_Shift_R:
            self.mod_shift = False

    def get_drawarea_size(self):
        allocation = self.widget_area.get_allocation()
        w = allocation.width
        h = allocation.height
        main.drawarea_size = [w, h]

    def cb_windowresize(self, widget):
        # !: The first time this is called via cb_release the change to self.flag_expanded isn't seen.
        # .. is this a weird threading thing?
        if self.flag_expanded:  # Skip bucket_remake if this was resized by expanding.
            self.flag_expanded = False
        else:
            # TD: Only do this check when finished resizing
            if main.drawarea_size[0]-1 > main.quadtree.boundary[2]:
                self.bucket_remake()
            if main.drawarea_size[1]-1 > main.quadtree.boundary[3]:
                self.bucket_remake()

    def cb_draw(self, widget, cr):
        self.get_drawarea_size()

        cr.set_source_rgba(0.2, 0.2, .4, 1.0)
        cr.rectangle(0, 0, main.drawarea_size[0], main.drawarea_size[1])
        cr.fill()

        #cr.set_source_rgba(0.2, 0.7, 1, 1.0)
        #cr.rectangle(0, 0, w, h)
        #cr.stroke()
        #cr.fill()

        # Draw quadtree boundaries.
        recurse_bucket_draw(cr, main.quadtree)

        # Corner decoration.
        for n in xrange(0, 2):
            x1 = -88
            x2 = 104
            m1 = 6
            cr.set_source_rgba(0.5, 0.5, .8, 1.0)
            cr.set_line_width(7)
            cr.move_to(x1 + n*m1, x2 + n*m1)
            cr.line_to(x2 + n*m1, x1 + n*m1)
            cr.stroke()

            cr.set_source_rgba(0.5, 0.5, .8, 1.0)
            cr.set_line_width(7)
            cr.move_to((main.drawarea_size[0] - (x1 + n*m1)), (main.drawarea_size[1] - (x2 + n*m1)))
            cr.line_to((main.drawarea_size[0] - (x2 + n*m1)), (main.drawarea_size[1] - (x1 + n*m1)))

            cr.set_source_rgba(0.5, 0.5, .8, 1.0)
            cr.set_line_width(7)
            cr.move_to((main.drawarea_size[0] - (x1 + n*m1)), (x2 + n*m1))
            cr.line_to((main.drawarea_size[0] - (x2 + n*m1)), (x1 + n*m1))

            cr.set_source_rgba(0.5, 0.5, .8, 1.0)
            cr.set_line_width(7)
            cr.move_to((x1 + n*m1), (main.drawarea_size[1] - (x2 + n*m1)))
            cr.line_to((x2 + n*m1), (main.drawarea_size[1] - (x1 + n*m1)))
            cr.stroke()

        cr.set_font_size(12)
        cr.select_font_face("Bitstream Vera Sans")

        # TD: Iterate only through objects in the current visible quadtree section.
        z_index_dct = {}
        for obj in main.containers:
            z_index_dct[obj.z_index] = obj

        sorted_grabbed = {}
        for gobj in self.grabbed_objects:
            del z_index_dct[gobj.z_index]
            sorted_grabbed[gobj.z_index] = gobj

        # !: Edges already seen attached to a node are added to this to be ignored. Fairly inefficient.
        collected_edges = set()
        render_order_list = []

        # Edges and nodes are sorted for proper rendering.
        for z, obj in sorted(z_index_dct.items()):
            if obj.node:
                # Sort edges for rendering first.
                if obj.node.super_edges:
                    for edge in obj.node.super_edges:
                        if edge not in collected_edges:
                            render_order_list.append(edge)
                        collected_edges.add(edge)
                if obj.node.sub_edges:
                    for edge in obj.node.sub_edges:
                        if edge not in collected_edges:
                            render_order_list.append(edge)
                        collected_edges.add(edge)
            render_order_list.append(obj)

        # Render grabbed items last.
        for z, obj in sorted(sorted_grabbed.items()):
            if obj.node:
                if obj.node.super_edges:
                    for edge in obj.node.super_edges:
                        if edge not in collected_edges:
                            render_order_list.append(edge)
                        collected_edges.add(edge)
                if obj.node.sub_edges:
                    for edge in obj.node.sub_edges:
                        if edge not in collected_edges:
                            render_order_list.append(edge)
                        collected_edges.add(edge)
            render_order_list.append(obj)

        for obj in render_order_list:
            if obj.__class__.__name__ == 'Edge':
                # Draw lines.
                edge = obj
                supernode = edge.super_node
                subnode = edge.sub_node

                startx = supernode.container.x + (supernode.container.ext_width / 2)
                starty = supernode.container.y + (supernode.container.ext_height / 2)
                endx = subnode.container.x + (subnode.container.ext_width / 2)
                endy = subnode.container.y + (subnode.container.ext_height / 2)

                # Draw lines between nodes.
                cr.set_line_cap(0)
                cr.set_source_rgba(0.5, 0.5, .8, 1.0)
                cr.move_to(startx, starty)
                cr.set_line_width(4)

                if edge.edgetype == 0:
                    cr.set_dash([2, 4, 2])
                elif edge.edgetype == 1:
                    cr.set_dash([])
                cr.line_to(endx, endy)
                cr.stroke()
                cr.fill()

                # !: Could either have the arrows in the exposed middle of the line, or connecting on the edges.
                # Draw arrows between nodes.

                arrow_length = 12
                arrow_degrees = 10
                # Arrow/Line Positions.
                difx = (endx - startx) / 3
                dify = (endy - starty) / 3
                arrow_endx = endx - difx
                arrow_endy = endy - dify
                line_angle = math.atan2(arrow_endy - endy, arrow_endx - endx) + math.pi
                p1_x = arrow_endx + arrow_length * math.cos(line_angle - arrow_degrees)
                p1_y = arrow_endy + arrow_length * math.sin(line_angle - arrow_degrees)
                p2_x = arrow_endx + arrow_length * math.cos(line_angle + arrow_degrees)
                p2_y = arrow_endy + arrow_length * math.sin(line_angle + arrow_degrees)
                cr.set_line_cap(cairo.LINE_CAP_SQUARE)
                cr.set_dash([])
                cr.set_line_width(3)
                # cr.set_source_rgba(1, 1, 1, 1.0)
                cr.set_source_rgba(0.5, 0.5, .8, 1.0)
                cr.move_to(p1_x, p1_y)
                cr.line_to(arrow_endx, arrow_endy)
                cr.line_to(p2_x, p2_y)
                cr.line_to(p1_x, p1_y)
                cr.close_path()
                cr.stroke_preserve()
                cr.fill()

            elif obj.__class__.__name__ == 'Container':
                if obj.is_gtk_widget:
                    w_h = obj.gtks.label.get_allocation()
                    obj.ext_width = w_h.width
                    obj.ext_height = w_h.height
                else:
                    if obj.node:
                        # Draw boxes
                        cr.set_line_width(2)
                        cr.set_line_cap(cairo.LINE_CAP_ROUND)
                        if obj.node.functional is True:
                            cr.set_dash([])
                        else:
                            cr.set_dash([5])
                        # !: Using dashed lines fudges the rectangle outward. Maybe just slightly adjusting them works. (+1.., -2..)
                        if self.target_obj == obj:
                            cr.set_source_rgba(1, 1, 0, 1.0)
                            cr.rectangle(obj.x + 1, obj.y + 1, obj.ext_width - 2, obj.ext_height - 2)
                            cr.stroke()
                            cr.fill()
                        elif obj in self.selected_objects:
                            cr.set_source_rgba(1, 1, 1, 1.0)
                            cr.rectangle(obj.x + 1, obj.y + 1, obj.ext_width - 2, obj.ext_height - 2)
                            cr.stroke()
                            cr.fill()
                        else:
                            cr.set_source_rgba(0.5, 0.5, .8, 1.0)
                            cr.rectangle(obj.x + 1, obj.y + 1, obj.ext_width - 2, obj.ext_height - 2)
                            cr.stroke()
                            cr.fill()

                        cr.set_source_rgba(0.3, 0.3, .6, 1.0)
                        cr.rectangle(obj.x + 2, obj.y + 2, obj.ext_width - 4, obj.ext_height - 4)

                        cr.fill()

                        # Draw text.
                        cr.set_source_rgba(.9, .9, .9, 1.0)
                        if obj.container_type == CONT_CLASS:
                            # WIP: Need to do some serious text alignment here.
                            cr.move_to((obj.x + obj.ext_width / 2) - obj.text_width / 2 - obj.text_x,
                                       (obj.y + obj.text_height) - obj.text_height / 2 - obj.text_y)
                            cr.show_text(obj.text)
                        else:
                            cr.move_to((obj.x + obj.ext_width / 2) - obj.text_width / 2 - obj.text_x,
                                       (obj.y + obj.ext_height / 2) - obj.text_height / 2 - obj.text_y)
                            cr.show_text(obj.text)


def on_activate(app):
    # Show the application window
    win = AppWindow()
    win.props.application = app
    win.set_title("Cerulean")
    win.set_default_size(600, 500)
    win.connect('key-press-event', win.cb_keypress)
    win.connect('key-release-event', win.cb_keyrelease)
    win.connect('focus-in-event', win.cb_focus_in)
    win.show()


def finish(self, widget, data=None):
    self.destroy()


if __name__ == '__main__':
    app = Gtk.Application(application_id='com.dgdg.cerulean', flags=Gio.ApplicationFlags.FLAGS_NONE)
    # Activate reveals the application window.
    app.connect('activate', on_activate)

    app.run()

