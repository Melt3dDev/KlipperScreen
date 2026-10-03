import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from ks_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):
    distances = [".5", "1", "2", "5", "10", "15"]
    distance = "5"

    def __init__(self, screen, title):
        title = title or _("Bed Angle")
        super().__init__(screen, title)

        # Plus shaped controls: A angle on the vertical axis, B angle on the horizontal axis
        self.buttons = {
            "a-": self._gtk.Button("arrow-up", "A-", "color1"),
            "a+": self._gtk.Button("arrow-down", "A+", "color1"),
            "b-": self._gtk.Button("arrow-left", "B-", "color2"),
            "b+": self._gtk.Button("arrow-right", "B+", "color2"),
        }
        self.buttons["a+"].connect("clicked", self.rotate, "A", "+")
        self.buttons["a-"].connect("clicked", self.rotate, "A", "-")
        self.buttons["b-"].connect("clicked", self.rotate, "B", "-")
        self.buttons["b+"].connect("clicked", self.rotate, "B", "+")

        self.labels["step"] = Gtk.Label()
        self.update_step_label()

        grid = Gtk.Grid(row_homogeneous=True, column_homogeneous=True)
        grid.attach(self.buttons["a-"], 1, 0, 1, 1)
        grid.attach(self.buttons["b-"], 0, 1, 1, 1)
        grid.attach(self.labels["step"], 1, 1, 1, 1)
        grid.attach(self.buttons["b+"], 2, 1, 1, 1)
        grid.attach(self.buttons["a+"], 1, 2, 1, 1)

        distgrid = Gtk.Grid()
        for j, i in enumerate(self.distances):
            self.labels[i] = self._gtk.Button(label=i)
            self.labels[i].set_direction(Gtk.TextDirection.LTR)
            self.labels[i].connect("clicked", self.change_distance, i)
            ctx = self.labels[i].get_style_context()
            ctx.add_class("horizontal_togglebuttons")
            if i == self.distance:
                ctx.add_class("horizontal_togglebuttons_active")
            distgrid.attach(self.labels[i], j, 0, 1, 1)

        self.labels["angle_dist"] = Gtk.Label(label=_("Rotation Angle (°)"))

        # Current angles reported by the melt Klipper module
        self.labels["a_angle"] = Gtk.Label()
        self.labels["b_angle"] = Gtk.Label()
        # A angle | label | B angle share one row so the selector keeps its space
        current = Gtk.Grid(column_homogeneous=True)
        current.attach(self.labels["a_angle"], 0, 0, 1, 1)
        current.attach(self.labels["angle_dist"], 1, 0, 2, 1)
        current.attach(self.labels["b_angle"], 3, 0, 1, 1)
        # Sit at the bottom of the row, next to the angle selector
        current.set_valign(Gtk.Align.END)
        current.set_margin_bottom(4)
        self.update_angles()

        layout = Gtk.Grid(row_homogeneous=True, column_homogeneous=True)
        layout.attach(grid, 0, 0, 1, 4)
        layout.attach(current, 0, 4, 1, 1)
        layout.attach(distgrid, 0, 5, 1, 1)

        self.content.add(layout)

    def update_angles(self):
        for axis in ("a", "b"):
            value = self._printer.get_stat("melt", f"{axis}_angle")
            text = f"{value:.1f}°" if isinstance(value, (int, float)) else "?"
            self.labels[f"{axis}_angle"].set_markup(f"<b>{axis.upper()}:</b> {text}")

    def process_update(self, action, data):
        if action == "notify_status_update" and "melt" in data:
            self.update_angles()

    def update_step_label(self):
        self.labels["step"].set_text(f"± {self.distance}°")

    def change_distance(self, widget, distance):
        self.labels[f"{self.distance}"].get_style_context().remove_class(
            "horizontal_togglebuttons_active"
        )
        self.labels[f"{distance}"].get_style_context().add_class("horizontal_togglebuttons_active")
        self.distance = distance
        self.update_step_label()

    def rotate(self, widget, axis, direction):
        angle = f"{float(self.distance):g}"
        if direction == "-":
            angle = f"-{angle}"
        a = angle if axis == "A" else "0"
        b = angle if axis == "B" else "0"
        self._screen._send_action(
            widget, "printer.gcode.script", {"script": f"G14 A{a} B{b} R"}
        )
