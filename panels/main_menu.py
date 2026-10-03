import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from panels.menu import Panel as MenuPanel


class Panel(MenuPanel):
    def __init__(self, screen, title, items=None):
        super().__init__(screen, title, items)
        logging.info("### Making MainMenu")

        # Buttons are kept at a fixed fraction of the screen and centered,
        # instead of stretching to fill the whole content area
        columns = 2 if self._screen.vertical_mode else 3
        self.labels["menu"] = self.arrangeMenuItems(items, columns)
        self.labels["menu"].set_halign(Gtk.Align.CENTER)
        self.labels["menu"].set_valign(Gtk.Align.CENTER)
        self.labels["menu"].set_hexpand(True)
        self.labels["menu"].set_vexpand(True)
        self.labels["menu"].set_row_spacing(10)
        self.labels["menu"].set_column_spacing(10)

        rows = max(1, -(-len(self.labels["menu"].get_children()) // columns))
        width = int(self._screen.width * 0.8 / columns)
        height = int(self._screen.height * 0.75 / rows)
        size = min(width, height)
        for button in self.labels["menu"].get_children():
            button.set_size_request(size, size)
            button.set_hexpand(False)
            button.set_vexpand(False)

        self.content.add(self.labels["menu"])

    def activate(self):
        # Keep the layout built in __init__ (the parent class would rebuild it in a scroll)
        pass
