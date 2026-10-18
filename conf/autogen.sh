#!/bin/sh
set -eu
cd -- "$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
autoreconf -fvi
exec ./configure "$@"
