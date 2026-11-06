# Third-party notices

Blackmagic Fusion Comp Publisher is free software under the GNU General Public License, version 3
or later (see LICENSE). The Mac app made from it contains the following other software. Each keeps
its own license, which is not changed by this project.

## Python

The Python interpreter and standard library, under the Python Software Foundation License
(https://docs.python.org/3/license.html). Source: https://www.python.org/downloads/

## Qt and Qt for Python (PySide6)

The Mac app uses PySide6 and the Qt libraries under the GNU Lesser General Public License,
version 3 (https://www.gnu.org/licenses/lgpl-3.0.html). The Qt and PySide6 libraries are included
unchanged, as separate shared libraries inside the app bundle (Contents/Frameworks), so you can
replace them with your own build of the same versions.

- Qt for Python (PySide6) source: https://code.qt.io/cgit/pyside/pyside-setup.git
- Qt source: https://download.qt.io/official_releases/qt/
- Information: https://www.qt.io/licensing

## PyInstaller

The app is bundled with PyInstaller (https://pyinstaller.org), which is under the GNU General
Public License version 2 or later with a special exception that lets it be used to bundle a
program under any license. Its bootloader is part of the app. Source:
https://github.com/pyinstaller/pyinstaller

## Libraries inside Python and Qt

Python and the Qt libraries include further components under their own licenses (for example
OpenSSL, zlib, libffi, expat, FreeType, HarfBuzz, libpng and PCRE2). Their notices are in the
source distributions linked above.
