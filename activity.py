#/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007, Eduardo Silva <edsiper@gmail.com>.
# Copyright (C) 2008, One Laptop Per Child
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# Blender.jam
# Esta basado en la actividad Terminal.xo
# Quienes sus autores estan mencionados al comienzo de este archivo.
# Contact information:
# Sergio Castro : cattom22@yahoo.com.ar
# Ceibal Jam http://ceibaljam.org

import os
import platform

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Vte
from gi.repository import GLib
from gi.repository import Pango

from sugar3 import env
from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbarbox import ToolbarButton
from sugar3.activity.widgets import EditToolbar
from sugar3.graphics.toolbutton import ToolButton
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton

MASKED_ENVIRONMENT = [
    'DBUS_SESSION_BUS_ADDRESS',
    'PPID'
]

bundle_path = activity.get_bundle_path()

ARCH = "x86-64"
if platform.machine().startswith('arm'):
    ARCH = "arm"
else:
    if platform.architecture()[0] == '64bit':
        ARCH = "x86-64"
    else:
        ARCH = "x86"


class BlenderActivity(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        #self.set_title('Blender Activity')

        os.environ['LD_LIBRARY_PATH'] = "%s:%s" % (os.path.join(bundle_path, ARCH, 'lib'), os.environ.get('LD_LIBRARY_PATH', ''))
        #os.environ['PATH'] = "%s:%s" % (os.path.join(bundle_path, ARCH, 'bin'), os.environ.get('PATH', ''))

        toolbarbox = ToolbarBox()
        self.set_toolbar_box(toolbarbox)
        toolbarbox.show_all()

        button = ActivityToolbarButton(self)
        toolbarbox.toolbar.insert(button, -1)

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbarbox.toolbar.insert(separator, -1)

        button = StopButton(self)
        toolbarbox.toolbar.insert(button, -1)

        self.hbox = Gtk.HBox()
        self.set_canvas(self.hbox)

        self.vt = Vte.Terminal()
        self.vt.connect("child-exited", self._child_exited)
        self.vt.connect("realize", self.start_all)
        self.hbox.pack_start(self.vt, True, True, 0)

        self.vt.set_font(Pango.FontDescription("Monospace 13"))
        self.vt.set_audible_bell(False)

        foreground = Gdk.Color.parse('#000000')[1]
        background = Gdk.Color.parse('#E7E7E7')[1]
        self.vt.set_colors(Gdk.RGBA.from_color(foreground),
                           Gdk.RGBA.from_color(background),
                           [])

        scrollbar = Gtk.VScrollbar.new(self.vt.get_vadjustment())
        self.hbox.pack_start(scrollbar, False, False, 0)

        self.show_all()

    def start_all(self, _activity):
        if ARCH != "arm":
            bin_path = os.path.join(bundle_path, "bin", ARCH, "blender")

            argv = [
                "/bin/bash",
                "-c",
                bin_path
            ]

        else:
            bin_path = os.path.join(bundle_path, "arm_alert.py")
            argv = [
                "/bin/bash",
                "-c",
                bin_path
            ]

        os.system("chmod +x %s" % bin_path)

        args = (Vte.PtyFlags.DEFAULT,
                os.environ['HOME'],
                argv,
                [],
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                None,
                None)

        if hasattr(self.vt, 'fork_command_full'):
            self.vt.fork_command_full(*args)
        else:
            self.vt.spawn_sync(*args)

    def _child_exited(self, vte, *args):
        self.close()

