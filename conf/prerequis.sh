#!/bin/sh
# Check only: never install packages or modify system services during a build.
set -eu
missing=
for tool in cc c++ make autoconf automake aclocal autoreconf pkg-config; do
    command -v "$tool" >/dev/null 2>&1 || missing="$missing $tool"
done
if [ -n "$missing" ]; then
    echo "Missing build tools:$missing" >&2
    echo "Ubuntu/Debian: sudo apt-get install build-essential autoconf automake pkg-config" >&2
    exit 1
fi
if [ "$(uname -s)" = Linux ]; then
    if ! pkg-config --exists x11 xmu xpm gl glu freetype2 libpng libjpeg libtiff-4; then
        echo "Missing development libraries. Ubuntu/Debian:" >&2
        echo "sudo apt-get install libx11-dev libxmu-dev libxpm-dev libgl-dev libglu1-mesa-dev libfreetype-dev libgif-dev libjpeg-dev libpng-dev libtiff-dev" >&2
        exit 1
    fi
fi
