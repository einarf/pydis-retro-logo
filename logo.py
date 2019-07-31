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

    # Configure generator / window
    generator_cls.write_frames = action == 'gen'
    generator_cls.window_size = (size, size)
    settings.SCREENSHOT_PATH = Path(__file__).parent / 'screenshots' / generator_cls.filename / str(size)

    # Use headless rendering when generating
    sys.argv = sys.argv[:1]
    if action == 'gen':
        sys.argv.extend(['-wnd', 'headless'])

    # Delete old frames
    if action == 'gen':
        if settings.SCREENSHOT_PATH.exists():
            for frame in settings.SCREENSHOT_PATH.iterdir():
                frame.unlink()

    # Run the window / generator
    mglw.run_window_config(generator_cls)

    # Don't continue in view mode
    if action != "gen":
        exit(0)

    # Output for final gif anim
    out_path = Path(__file__).parent / 'output' / generator_cls.filename
    out_path.mkdir(parents=True, exist_ok=True)

    proc = subprocess.Popen([
        'convert',
        '-delay', '10',
        '-loop', '1',
        settings.SCREENSHOT_PATH / 'logo_*.png',
        out_path / f"{generator_cls.filename}_{size}.gif",
    ])
