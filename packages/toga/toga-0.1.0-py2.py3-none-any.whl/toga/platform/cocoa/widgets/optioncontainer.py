from __future__ import print_function, absolute_import, division

from ..libs import *
from .base import Widget


class OptionContainer(Widget):
    def __init__(self):
        super(OptionContainer, self).__init__()
        self._content = []

    def _startup(self):
        self._impl = NSTabView.alloc().init()
        self._impl.setTranslatesAutoresizingMaskIntoConstraints_(False)

        for label, container in self._content:
            self._add_panel(label, container)

    def add(self, label, container):
        self._content.append((label, container))
        container.window = self.window
        if self._impl:
            self._add_panel(label, container)

    def _add_panel(self, label, container):
        item = NSTabViewItem.alloc().initWithIdentifier_(get_NSString('%s-Tab-%s' % (id(self), id(container))))
        item.setLabel_(get_NSString(label))
        container.app = self.app

        # TabView items don't layout well with autolayout (especially when
        # they are scroll views); so revert to old-style autoresize masks for the
        # content views.
        container._impl.setTranslatesAutoresizingMaskIntoConstraints_(True)
        item.setView_(container._impl)

        self._impl.addTabViewItem_(item)
