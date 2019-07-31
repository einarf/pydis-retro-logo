import bisect
import math
from pathlib import Path

import numpy
from pyrr import matrix44

import moderngl
import moderngl_window as mglw
from moderngl_window import screenshot
from moderngl_window.conf import settings
from moderngl_window.opengl.vao import VAO
from moderngl_window import geometry

settings.SCREENSHOT_PATH = Path(__file__).parent / 'screenshots'


class LogoGenerator(mglw.WindowConfig):
    title = "Logo Generator"
    window_size = (504, 504)
    aspect_ratio = 1.0  # Always retain a fixed 1.0 aspect ratio
    size = 24  # x/y resolution regardless of framebuffer size
    speed = 6  # Rot speed in realtime preview
    resource_dir = Path(__file__).parent / 'resources'
    write_frames = True
    frames = 64
    frames_per_rotation = 32
    # List of (int) rotation degrees, vao to render
    states = []
    filename = 'logo_'

    def __init__(self, **kwargs):
        # Ensure the frmebuffer has the exact pixel size.
        # Some window system are using subpixel scaling.
        super().__init__(**kwargs)

        self.projection = matrix44.create_orthogonal_projection(-1, 1, -1, 1, 1, -1).astype('f4')

        # Background
        self.texture_bg = self.load_texture_2d('textures/python_bg.png')

        # Geometry Textures
        self.texture_bg.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.texture_logo_front = self.load_texture_2d('textures/geometry/logo_front.png')
        self.texture_controller_front = self.load_texture_2d('textures/geometry/logo_controller.png')

        # Programs
        self.program_bg = self.load_program('programs/texture.glsl')
        self.logo_program = self.load_program('programs/cube_geometry.glsl')

        # VAOs
        self.quad_fs = geometry.quad_fs()
        self.vao_controller = self.create_geometry(
            self.texture_controller_front,
            exclude_colors=[
                (32, 34, 37),
                (143, 161, 255),
            ],
        )
        self.vao = self.create_geometry(
            self.texture_logo_front,
            include_colors=[
                (209, 216, 255),
                (64, 81, 208),
                (254, 254, 255),
            ],
        )
        self.init_states()

    def init_states(self):
        """Populate rotation states"""
        self.event_values = self.states[::2]
        self.event_vaos = self.states[1::2]

    def render(self, time: float, frame_time: float):
        """Main render function deciding if render to screen or files"""
        if self.write_frames:
            time = math.pi * 2 * (self.wnd.frames / self.frames_per_rotation)

            # Rotation in degrees
            if self.wnd.frames >= self.frames:
                self.wnd.close()
                return
        else:
            time *= self.speed

        self.render_frame(time)

        if self.write_frames:
            screenshot.create(self.wnd.fbo, name=f"logo_{str(self.wnd.frames).zfill(3)}.png")

    def render_frame(self, time):
        self.ctx.disable(moderngl.CULL_FACE | moderngl.DEPTH_TEST)

        # Render background
        self.program_bg['texture0'].value = 0
        self.texture_bg.use(location=0)
        self.quad_fs.render(self.program_bg)

        # Render logo
        self.ctx.enable(moderngl.CULL_FACE | moderngl.DEPTH_TEST)
        time = time / 4
        m_model = matrix44.create_from_y_rotation(time)

        self.logo_program['m_proj'].write(self.projection.tobytes())
        self.logo_program['m_model'].write(m_model.astype('f4').tobytes())

        # Look up what vao to render
        deg = time * 180 / math.pi
        index = bisect.bisect_left(self.event_values, math.floor(deg)) - 1
        index = max(0, min(index, len(self.event_vaos) - 1))

        self.event_vaos[index].render(self.logo_program)

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
