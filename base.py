from pathlib import Path

import numpy

import moderngl
import moderngl_window as mglw
from moderngl_window import screenshot
from moderngl_window.conf import settings
from moderngl_window.opengl.vao import VAO

settings.SCREENSHOT_PATH = Path(__file__).parent / 'screenshots'


class LogoGenerator(mglw.WindowConfig):
    title = "Logo Generator"
    window_size = (504, 504)
    aspect_ratio = 1.0  # Always retain a fixed 1.0 aspect ratio
    size = 24  # x/y resolution regardless of framebuffer size
    resource_dir = Path(__file__).parent / 'resources'
    write_frames = True
    frames = 64
    frames_per_rotation = 16

    def __init__(self, **kwargs):
        # Ensure the frmebuffer has the exact pixel size.
        # Some window system are using subpixel scaling.
        self.window_size = (
            int(self.window_size[0] / kwargs['wnd'].pixel_ratio),
            int(self.window_size[1] / kwargs['wnd'].pixel_ratio),
        )
        super().__init__(**kwargs)

    def render(self, time: float, frame_time: float):
        if self.write_frames:
            time = math.pi * (self.wnd.frames / frames_per_rotation)
            if self.wnd.frames >= frames:
                self.wnd.close()
                return

        self.render_frame(time)

        if self.write_frames:
            screenshot.create(self.wnd.fbo, name=f"logo_{str(self.wnd.frames).zfill(3)}.png")

    def render_frame(self, time):
        pass

    def create_geometry(self, texture, include_colors=None, exclude_colors=None):
        """Create gemetry from texture.

        Selects pixels from an image based on `include_colors` or `exclude_colors`
        inside the default -1, 1 projection.

        Args:
            texture (moderngl.Texture): The texture to inspect
            include_colors (list): List of rgb tuples
            exclude_colors (list): List of rgb tuples
        """
        data = texture.read()
        values = [int(d) for d in data]

        positions = []
        colors = []
        delta = (2.0 / self.size)  # grid
        half = (2.0 / self.size) / 2  # half pixel
        xoffset = half * (self.size - texture.width)
        yoffset = half * (self.size - texture.height)

        for y in range(texture.height):
            for x in range(texture.width):

                row = (texture.height - 1 - y)
                xpos = -1.0 + delta * x + half + xoffset
                ypos = -1.0 + delta * row + half + yoffset
                i = (row * texture.width + x) * 3
                r, g, b = values[i:i + 3]

                if include_colors:
                    if (r, g, b) in include_colors:
                        positions.extend([xpos, ypos, 0.0])
                        colors.extend([r / 256, g / 256, b / 256])
                elif exclude_colors:
                    if (r, g, b) not in exclude_colors:
                        positions.extend([xpos, ypos, 0.0])
                        colors.extend([r / 256, g / 256, b / 256])

        vao = VAO("logo", mode=moderngl.POINTS)
        vao.buffer(numpy.array(positions, dtype="f4"), "3f", "in_position")
        vao.buffer(numpy.array(colors, dtype="f4"), "3f", "in_color")
        return vao

    def unique_colors(selv, values):
        """Get unique colors from texture.
        This is mainly a helper method when doing
        inital analysis of the color space.

        Args:
            values (list): List of integer values
        """
        unique_colors = []

        for i in range(len(values) // 3):
            r, g, b = values[i:i + 3]
            if (r, g, b) not in unique_colors:
                unique_colors.append((r, g, b))

        return unique_colors
