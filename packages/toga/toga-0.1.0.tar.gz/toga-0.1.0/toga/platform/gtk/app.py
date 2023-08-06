from __future__ import print_function, absolute_import, division

import sys

from gi.repository import Gtk, Gio, GLib

from .window import Window


class MainWindow(Window):
    _IMPL_CLASS = Gtk.ApplicationWindow


class App(object):

    def __init__(self, name, app_id):
        # GLib.set_application_name(name.encode('ascii'))
        self._impl = Gtk.Application(application_id=app_id, flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.main_window = MainWindow()

        self._impl.connect('startup', self._startup)
        self._impl.connect('activate', self._activate)
        self._impl.connect('shutdown', self._shutdown)

    def _startup(self, data=None):
        self.main_window.app = self

        self._impl.add_window(self.main_window._impl)

        action = Gio.SimpleAction.new('stuff', None)
        action.connect('activate', self._quit)
        self._impl.add_action(action)

        app_name = sys.argv[0]

        # # App menu
        self.app_menu = Gio.Menu()

        section = Gio.Menu()
        section.append_item(Gio.MenuItem.new('About', 'about'))
        section.append_item(Gio.MenuItem.new('Preferences', 'preferences'))

        self.app_menu.append_section(None, section)

        section = Gio.Menu()
        item = Gio.MenuItem.new('Do Stuff', 'app.stuff')
        item.set_attribute_value('accel', GLib.Variant('s', '<Primary>S'))
        section.append_item(item)

        self.app_menu.append_section(None, section)

        self._impl.set_app_menu(self.app_menu)

        # # Main menu bar
        self.menu_bar = Gio.Menu()

        # FIXME - the app menu doesn't display correctly - it assumes a title of
        # "Unknown application name", which doesn't appear to be changeable, and may
        # be an ubuntu unity bug...
        # self.menu_bar.append_submenu('File', self.app_menu)

        # Help
        submenu = Gio.Menu()

        section = Gio.Menu()
        section.append_item(Gio.MenuItem.new('Help', 'help'))

        submenu.append_section(None, section)

        self.menu_bar.append_submenu('Help', submenu)

        self._impl.set_menubar(self.menu_bar)

        self.main_window.show()
        self.on_startup()

    def on_startup(self):
        pass

    def _activate(self, data=None):
        self.on_activate()

    def on_activate(self):
        pass

    def _shutdown(self, data=None):
        self.on_shutdown()

    def on_shutdown(self):
        pass

    def main_loop(self):
        self._impl.run(None)

    def _quit(self, widget, data=None):
        self.on_quit()

    def on_quit(self):
        self._impl.quit()
