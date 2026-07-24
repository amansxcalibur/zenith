from fabric.widgets.box import Box
from fabric.widgets.shapes import Corner

from widgets.overrides import PatchedX11Window as Window

from gi.repository import Gdk


class MyCorner(Box):
    def __init__(self, corner, radius: int):
        super().__init__(
            name="corner-container",
            children=Corner(
                name="corner",
                orientation=corner,
                size=radius,
            ),
        )


class Corners(Window):
    def __init__(self, radius: int):
        super().__init__(
            layer="top",
            geometry="top",
            type_hint="normal",
            focusable=False,
            visible=True,
            pass_through=True,
            all_visible=True,
        )

        display = Gdk.Display.get_default()
        monitor = display.get_monitor_at_window(self.get_window())
        geo = monitor.get_geometry()

        self.set_size_request(geo.width, geo.height)

        self.all_corners = Box(
            orientation="v",
            pass_through=True,
            focusable=False,
            h_expand=True,
            v_expand=True,
            h_align="fill",
            v_align="fill",
            children=[
                Box(
                    name="top-corners",
                    orientation="h",
                    h_align="fill",
                    children=[
                        MyCorner("top-left", radius),
                        Box(h_expand=True),
                        MyCorner("top-right", radius),
                    ],
                ),
                Box(v_expand=True),
                Box(
                    name="bottom-corners",
                    orientation="h",
                    h_align="fill",
                    children=[
                        MyCorner("bottom-left", radius),
                        Box(h_expand=True),
                        MyCorner("bottom-right", radius),
                    ],
                ),
            ],
        )

        self.add(self.all_corners)

        self.connect("delete-event", self.on_delete_event)
        self.show_all()

    def on_delete_event(self, *_):
        # don't close me :(
        return True
