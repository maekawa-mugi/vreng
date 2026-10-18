# Linux / WSLg

Build from a fresh clone using the system development packages. `build` checks
dependencies, runs autoreconf/configure, and compiles. It does not install
packages, launch an X server, or edit Apache configuration.

On Ubuntu/Debian:

```sh
sudo apt-get install build-essential autoconf automake pkg-config python3 \
  libx11-dev libxmu-dev libxpm-dev libgl-dev libglu1-mesa-dev \
  libfreetype-dev libgif-dev libjpeg-dev libpng-dev libtiff-dev fonts-dejavu-core
./build
./run-local
```

`JOBS=8 ./build` limits parallel compilation. Configure arguments and compiler
flags can be passed to `build`, for example `./build --enable-debug`.
The bundled MPEG decoder is compiled as GNU C17 because it uses old-style C
function definitions that are incompatible with GCC 15's C23 default.

`run-local` serves this checkout's `data/` directory on a dynamically allocated
loopback HTTP port and starts VREng with that universe. The HTTP server closes
when VREng exits. It uses multicast mode to avoid the unavailable external
reflector, and disables database persistence. This does not verify multiplayer
connectivity. Additional VREng arguments are forwarded, for example:

```sh
./run-local -w /vre/board.vre
```

In WSL, use WSLg with `DISPLAY` set by WSL (normally `:0`). Do not run `startx`.
On a Linux desktop, use the existing X11/XWayland display. `./vr` is the plain
binary wrapper for users who already have their own asset server. It resolves
its checkout path so it can be called from another working directory.

`run-local` stores preferences and cache in `.local-state/` inside this checkout;
it does not reuse an old, potentially truncated `~/.vreng/cache`. Set
`VRENG_HOME` to an absolute directory to choose a different state location.
Set `VRENG_HTTP_LOG=1` to log local HTTP requests. The legacy application also
creates its usual `public_html/vreng` shortcut if it is absent.

Changes required for modern Linux include FreeType/JPEG pkg-config detection,
GNU ld archive groups, guards around obsolete resolver APIs, per-connection
HTTP buffers and serialized cache writes, matching JPEG headers/libraries,
font initialization and missing-glyph handling, and fixes for memory errors in
WSL kernel-name storage, world names, scene parsing, and world transitions.

Validated with Ubuntu 26.04, GCC 15.2 and WSLg/Mesa llvmpipe. The Rendezvous
world, local assets, keyboard movement and a diagnostic ASan run were checked.
This is not a full audit of every legacy world, optional tool or network mode.


## Regression checks

```sh
g++ -Isrc/base tests/nsl-smoke.cpp src/base/nsl.o -o /tmp/vreng-nsl-smoke
/tmp/vreng-nsl-smoke
# Close any running VREng window first. Requires xdotool and Xcomposite.
python3 tests/gui-smoke.py
```

The GUI test starts an isolated instance, resizes it four times, verifies the
menu and toolbar remain in their window regions, and performs 40 selections.
Resize-event coalescing now ignores stale callbacks from another window.
3D paint restores the GUI matrices and clip state; object picking balances
projection/modelview stacks and uses a correctly sized selection buffer.
Texture uploads use the image's actual RGB/RGBA/grayscale format and restore
the previous binding and unpack alignment.

Opaque ground patches keep their scene order instead of being sorted by eye
distance. Rendezvous contains overlapping coplanar ground rectangles with
different texture scales; changing their draw order made the visible floor
pattern switch abruptly while walking. Ordinary perspective foreshortening and
nearest-filter aliasing can still be visible in the default low-quality mode;
`./run-local -q` selects the existing higher-quality filtering option.
