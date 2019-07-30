import math
from pathlib import Path

from pyrr import matrix44
import moderngl

import moderngl_window as mglw
from moderngl_window import geometry
from base import LogoGenerator


class LogoVariant(LogoGenerator):
    window_size = (504 / 2, 504 / 2)
    # window_size = (252 / 2, 252 / 2)
    # window_size = (24 / 2, 24 / 2)
    write_frames = False
    frames = 64 + 16 + 16 + 16

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg = self.load_texture_2d('textures/python_bg.png')
        self.texture = self.load_texture_2d('textures/python_logo_small.png')
        self.controller = self.load_texture_2d('textures/python_logo_controller2.png')
        self.program = self.load_program('programs/texture.glsl')
        self.quad_fs = geometry.quad_fs()

        self.bg.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.vao_controller = self.create_geometry(
            self.controller,
            exclude_colors=[
                (32, 34, 37),
                (143, 161, 255),
            ],
        )
        self.vao = self.create_geometry(
            self.texture,
            include_colors=[
                (209, 216, 255),
                (64, 81, 208),
                (254, 254, 255),
            ],
        )
        self.logo_program = self.load_program('programs/cube_geometry.glsl')
        self.projection = matrix44.create_orthogonal_projection(-1, 1, -1, 1, 1, -1).astype('f4')

    def render_frame(self, time: float):
        self.ctx.disable(moderngl.CULL_FACE | moderngl.DEPTH_TEST)
        self.program['texture0'].value = 0
        self.bg.use(location=0)
        self.quad_fs.render(self.program)

        self.ctx.enable(moderngl.CULL_FACE | moderngl.DEPTH_TEST)
        m_model = matrix44.create_from_y_rotation(time)

        self.logo_program['m_proj'].write(self.projection.tobytes())
        self.logo_program['m_model'].write(m_model.astype('f4').tobytes())

        if math.fmod(time - (math.pi * 0.25), math.pi * 2) < math.pi:
            self.vao.render(self.logo_program)
        else:
            self.vao_controller.render(self.logo_program)


if __name__ == '__main__':
    mglw.run_window_config(LogoVariant)
