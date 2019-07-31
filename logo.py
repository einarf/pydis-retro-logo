import math
from pathlib import Path

import moderngl
from pyrr import matrix44

import moderngl_window as mglw
from base import LogoGenerator


class LogoVariant(LogoGenerator):
    window_size = (504 / 2, 504 / 2)
    # window_size = (252 / 2, 252 / 2)
    # window_size = (24 / 2, 24 / 2)
    write_frames = False
    frames = 64 + 16 + 16 + 16

    def render_frame(self, time: float):
        self.ctx.disable(moderngl.CULL_FACE | moderngl.DEPTH_TEST)

        # Render background
        self.program_bg['texture0'].value = 0
        self.texture_bg.use(location=0)
        self.quad_fs.render(self.program_bg)

        # Render logo
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
