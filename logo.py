import math
import sys
import subprocess
from pathlib import Path

import moderngl
from pyrr import matrix44

import moderngl_window as mglw
from moderngl_window.conf import settings
from base import LogoGenerator


class PlainLogo(LogoGenerator):
    window_size = (504, 504)
    write_frames = False
    frames = 64 + 16 + 16 + 16
    filename = 'logo_spin_plain'

    def init_states(self):
        self.states = [
            0,   self.vao,
            180, self.vao_controller
        ]
        super().init_states()


GENERATORS = [
     PlainLogo,
]


if __name__ == '__main__':
    # action: gen/view
    # generator: filename attribute
    # size: size of texture
    action = sys.argv[1]
    generator = sys.argv[2]
    size = int(sys.argv[3])

    generator_cls = None
    for cls in GENERATORS:
        if cls.filename == generator:
            generator_cls = cls

    if generator_cls is None:
        raise ValueError("No generator class '{}'. Available: {}".format(generator, [c.filename for c in GENERATORS]))

    generator_cls.write_frames = action == 'gen'
    generator_cls.window_size = (size, size)

    # Use headless rendering when generating
    sys.argv = sys.argv[:1]
    if action == 'gen':
        sys.argv.extend(['-wnd', 'headless'])

    mglw.run_window_config(generator_cls)

    if action != "gen":
        exit(0)

    in_path = settings.SCREENSHOT_PATH
    out_path = Path(__file__).parent / 'output' / generator_cls.filename
    out_path.mkdir(parents=True, exist_ok=True)

    proc = subprocess.Popen([
        'convert',
        '-delay', '10',
        '-loop', '1',
        in_path / 'logo_*.png',
        out_path / f"{generator_cls.filename}_{size}.gif",
    ])


# window_size = (504, 504)
# window_size = (252, 252)
# window_size = (126, 126)
# window_size = (24, 24)
# window_size = (63, 63)
