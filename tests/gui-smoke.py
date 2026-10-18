#!/usr/bin/env python3
"""WSLg/X11 regression: resize the real application and verify toolbar pixels.
Requires xdotool, libX11 and libXcomposite; closes only its own process group.
"""
import ctypes as c
import ctypes.util
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time

root = Path(__file__).resolve().parents[1]
def windows():
    return subprocess.run(["xdotool", "search", "--name", "^vreng$"],
                          capture_output=True).stdout.splitlines()
if windows():
    raise SystemExit("Close VREng before running the GUI regression test.")

x = c.CDLL(ctypes.util.find_library("X11"))
composite = c.CDLL(ctypes.util.find_library("Xcomposite"))
x.XOpenDisplay.argtypes = [c.c_char_p]
x.XOpenDisplay.restype = c.c_void_p
display = x.XOpenDisplay(None)
if not display:
    raise SystemExit("No X11 display")
composite.XCompositeNameWindowPixmap.argtypes = [c.c_void_p, c.c_ulong]
composite.XCompositeNameWindowPixmap.restype = c.c_ulong
x.XGetGeometry.argtypes = [c.c_void_p, c.c_ulong, *([c.c_void_p] * 7)]
x.XGetImage.argtypes = [c.c_void_p, c.c_ulong, c.c_int, c.c_int,
                       c.c_uint, c.c_uint, c.c_ulong, c.c_int]
x.XGetImage.restype = c.c_void_p
x.XGetPixel.argtypes = [c.c_void_p, c.c_int, c.c_int]
x.XGetPixel.restype = c.c_ulong
x.XDestroyImage.argtypes = [c.c_void_p]
x.XFreePixmap.argtypes = [c.c_void_p, c.c_ulong]
x.XCloseDisplay.argtypes = [c.c_void_p]

def check_bars(window, width, height):
    pixmap = composite.XCompositeNameWindowPixmap(display, window)
    parent = c.c_ulong()
    px, py = c.c_int(), c.c_int()
    w, h, border, depth = c.c_uint(), c.c_uint(), c.c_uint(), c.c_uint()
    x.XGetGeometry(display, pixmap, c.byref(parent), c.byref(px), c.byref(py),
                   c.byref(w), c.byref(h), c.byref(border), c.byref(depth))
    assert (w.value, h.value) == (width, height), (w.value, h.value)
    image = x.XGetImage(display, pixmap, 0, 0, width, height, 0xffffffff, 2)
    assert image
    try:
        for px, py in ((width - 12, 10), (20, height - 20)):
            pixel = x.XGetPixel(image, px, py)
            rgb = [(pixel >> shift) & 255 for shift in (16, 8, 0)]
            assert min(rgb) > 80 and max(rgb) - min(rgb) < 30, (width, height, px, py, rgb)
    finally:
        x.XDestroyImage(image)
        x.XFreePixmap(display, pixmap)

with tempfile.TemporaryDirectory(prefix="vreng-gui-") as state:
    env = os.environ.copy()
    env["VRENG_HOME"] = state
    log_path = root / "log/gui-smoke.log"
    log_path.parent.mkdir(exist_ok=True)
    with log_path.open("w") as log:
        app = subprocess.Popen([str(root / "run-local")], cwd=root, env=env,
                               stdout=log, stderr=log, start_new_session=True)
        try:
            for _ in range(100):
                found = windows()
                if found: break
                assert app.poll() is None, "App exited during startup"
                time.sleep(.1)
            assert len(found) == 1, found
            window = int(found[0])
            time.sleep(2)
            for width, height in ((960, 629), (1200, 850), (760, 520), (960, 629)):
                subprocess.run(["xdotool", "windowsize", str(window), str(width), str(height)], check=True)
                time.sleep(.6)
                check_bars(window, width, height)
            subprocess.run(["xdotool", "mousemove", "--window", str(window), "400", "330"], check=True)
            for _ in range(40):
                subprocess.run(["xdotool", "click", "--window", str(window), "1"], check=True)
            time.sleep(.5)
            assert app.poll() is None, "App exited after selection"
            check_bars(window, 960, 629)
            subprocess.run(["xdotool", "keydown", "--window", str(window), "Up"], check=True)
            time.sleep(2)
            subprocess.run(["xdotool", "keyup", "--window", str(window), "Up"], check=True)
            subprocess.run(["xdotool", "keydown", "--window", str(window), "Left"], check=True)
            time.sleep(.3)
            subprocess.run(["xdotool", "keyup", "--window", str(window), "Left"], check=True)
            check_bars(window, 960, 629)
            print("PASS: four resize sizes, toolbar clipping, 40 selections, movement/turn")
        finally:
            if app.poll() is None:
                os.killpg(app.pid, signal.SIGKILL)
            app.wait()
x.XCloseDisplay(display)
