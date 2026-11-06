# Blackmagic Fusion Comp Publisher

Starts every Fusion comp for you. Point it at a folder of shots and it makes one `.comp` file
per shot, each already holding the shot's L1 clip in a Loader, with the render range and working
range set to the clip's length. A reference clip can go in as a second Loader.

From [Creative Video Tips](https://creativevideotips.com). Free software under the GNU GPL v3 or
later (see [License](#license)).

> **Not associated with Blackmagic Design.** Blackmagic Fusion Comp Publisher is an independent
> tool created by Creative Video Tips. It is not made, endorsed or supported by Blackmagic Design
> Pty Ltd. Blackmagic Design, DaVinci Resolve and Fusion are trademarks of Blackmagic Design Pty
> Ltd; the name only says which program the comps are for.

## Download

**[BlackmagicFusionCompPublisher-2.13.pkg](https://github.com/creativevideotips/cvt-fusion-comp-publisher/releases/download/v2.13/BlackmagicFusionCompPublisher-2.13.pkg)**
is a signed and notarized installer for Apple Silicon Macs (M1 and later) running macOS 12 or later. Double-click it and it puts
**Blackmagic Fusion Comp Publisher** in your Applications folder. It has Python and Qt inside, so
there is nothing else to install. The [PDF guide](Blackmagic_Fusion_Comp_Publisher_Guide.pdf)
explains how to use it, and every release is on the
[Releases page](https://github.com/creativevideotips/cvt-fusion-comp-publisher/releases).

## What it does

Say each shot folder has its footage in a `source` folder:

```
Shots/
  proj_sh010/
    source/
      proj_sh010_L1.mov
      proj_sh010_ref.mov
```

After you publish, every shot has a comp named after it:

```
Shots/
  proj_sh010/
    proj_sh010_v001.comp      <- new
    source/ ...
```

- The comp is a copy of your own **template comp**, so it has your Fusion layout, frame rate and
  settings. The default template is the one in your user Templates folder, where Fusion looks
  (`~/Library/Application Support/Blackmagic Design/Fusion/Templates/template.comp`), else the
  system-wide one. With no template yet, the app offers to create a starter one.
- The **L1 clip** is a movie in `source/` (`<shot>_L1.mov`, or `_L1_709`, `_L1_flat` for two
  versions) or an image sequence (EXR, DPX, TIFF, JPEG, PNG) in the shot's L1 folder
  (`source/<shot>_L1/<shot>_L1.1001.exr`). It is loaded through Fusion's `Comp:` path map.
- The **render range** is the clip (1001 to 1000 + frames) and the **working range** is one frame
  longer, the way Fusion sets them when you Shift-drag a Loader to the time ruler.
- The comp's **frame size** is set to the L1 clip's picture size (for example 2048 x 858), so a
  plate that is not HD or UHD does not open in a comp of the template's size. The size is read
  from the clip's own header; the frame rate and bit depth stay the template's. Turn it off to keep
  the template's size.
- A **reference clip** (a movie or image sequence whose name ends in `_ref`, found anywhere inside
  the shot folder) goes in as a second Loader to the right of the first. It never changes the range.
- You tick the shots to publish. A shot that already has this version's comp is left alone unless
  you turn on Replace.

## Run it from source

You need Python 3.10 or later and PySide6.

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python3 cvt_fusion_comp_publisher_gui_v2.13.py
```

The engine also runs on its own, with only the standard library:

```
python3 cvt_fusion_comp_publisher_v2.13.py /path/to/Shots --dry-run
python3 cvt_fusion_comp_publisher_v2.13.py --help
```

## Build the Mac app

The installer is the Python files above, bundled with PyInstaller:

```
pip install "PySide6-Essentials==6.8.3" pyinstaller
pyinstaller --windowed --name "Blackmagic Fusion Comp Publisher" \
  --osx-bundle-identifier com.creativevideotips.fusioncomppublisher \
  --add-data "cvt_fusion_comp_publisher_v2.13.py:." \
  cvt_fusion_comp_publisher_gui_v2.13.py
```

Signing, notarizing and making a `.pkg` are your own steps, with your own Apple Developer ID.

Build with a Python made for older macOS (the one from python.org, or a standalone build from
`uv`) and PySide6 6.8, not Homebrew's Python or the newest PySide6. Those are compiled for the
newest macOS, and an app built with them will not open on older Macs.

## Safety

It only writes comp files in the shot folders you tick. It never deletes or moves a file, never
replaces an existing comp unless you turn that on, never follows a symbolic link when writing, and
refuses a version tag or extension that could point outside the shot folder. It makes no network
connections.

## License

Free software under the GNU General Public License, version 3 or later. See [LICENSE](LICENSE). The
Mac app bundles Python, Qt for Python (PySide6) and PyInstaller, each under its own license: see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
