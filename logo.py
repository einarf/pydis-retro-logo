import math
from pathlib import Path

import moderngl
from pyrr import matrix44

import moderngl_window as mglw
from base import LogoGenerator


class Logo(LogoGenerator):
    window_size = (504 / 2, 504 / 2)
    # window_size = (252 / 2, 252 / 2)
    # window_size = (24 / 2, 24 / 2)
    write_frames = False
    frames = 64 + 16 + 16 + 16

    def init_states(self):
        self.states = [
            0, self.vao,
            180, self.vao_controller
        ]
        super().init_states()


if __name__ == '__main__':
    mglw.run_window_config(Logo)
