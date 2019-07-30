# pydis-retro-logo

Generates animated retro-themed logos for the [Python Discord](https://pythondiscord.com/)
server.

## Details

We load 24 x 24 textures and covert each pixel into a cube. What pixel is made into
a cube is filtered by a list of RGB color values. To make this work as simple as
possible we only generate a color and cube position buffer and delegate the
cretion of cubes to a gemometry shader. The geometry shader takes a point
(cube center) and emits a cube around it as a 24 vertex triangle strip.

We then render this geometry based on the current rotation (switching
between them) and capture each frame by writing a numbered png file to disk.
These png files are then converted into a gif anim using
[imagemagick](https://imagemagick.org/)

## Dependecies

https://github.com/moderngl/moderngl_window

Clone and `pip install -e .` for now. The library does not exist on PyPI yet.

## Attributions

* Original pydis pixelated logo created by [Random832](https://github.com/)
