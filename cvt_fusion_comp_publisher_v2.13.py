#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# cvt_fusion_comp_publisher_v2.13
#
# From Creative Video Tips (CVT)
# Created by Chadwick  |  https://creativevideotips.com
#
# Blackmagic Fusion Comp Publisher
# Copyright (C) 2026 Chadwick, Creative Video Tips (https://creativevideotips.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Not associated with Blackmagic Design. This is an independent tool created by
# Creative Video Tips; it is not made, endorsed or supported by Blackmagic Design
# Pty Ltd. Blackmagic Design, DaVinci Resolve and Fusion are trademarks of
# Blackmagic Design Pty Ltd.
#
# What it does:
#   1. Looks in a parent folder (e.g. a "shots" folder) for its subfolders,
#      optionally at every depth and filtered by a name pattern.
#   2. Puts one Fusion .comp in each, named after the folder plus a version
#      tag (SHOT_010/SHOT_010_v001.comp), copied from a template comp so it
#      carries your frame format, frame rate, bit depth and path mapping.
#   3. Adds a Loader for the shot's L1 clip (a movie or an image sequence: EXR,
#      DPX, TIFF, JPEG, PNG) from its source folder (path
#      Comp:/source/..., so the comp can move with the shot), and sets the
#      render range and the working range to the exact length of that clip.
#      If a shot has both an untagged L1 and tagged ones (_L1_709, _L1_flat),
#      the colour-space tag you choose picks the clip.
#   4. Skips comps that already exist unless told to overwrite, can be limited
#      to chosen shot folders, and prints what was created, overwritten,
#      skipped or failed.
#
# This is the publishing engine and command-line tool; the window is
# cvt_fusion_comp_publisher_gui_v2.13.py, which loads this file.
#
# v1.01: renumbered to match the set (the window now remembers your settings);
#        publishing works the same.
# v1.02: licence text: a Cutting Club thank-you script, for your own use only,
#        not for resale and not for sharing.
# v2.00: each new comp starts with a Loader for the shot's L1 clip and the
#        render and working ranges set to the clip length (no more Shift-drag
#        to the time ruler). A colour-space tag chooses between a flat and a
#        709 clip. Publish only the shot folders you choose. Needs ffprobe
#        (ffmpeg) to read the clip length.
# v2.01: works with EXR sequences (<shot>_L1.0001.exr) as well as movies; the
#        Loader is added to the node graph and the ranges are set (it is not
#        loaded into a viewer, which Fusion does not save in a comp).
# v2.02: renumbered to match the set (the window's template is now required
#        and pre-filled with the default template); publishing works the same.
# v2.03: the default template is the one in your user Templates folder (where
#        Fusion looks for Templates:), else the system-wide one.
# v2.04: every kind of image sequence gets a Loader, not only EXR: DPX, TIFF,
#        JPEG and PNG as well (names like <shot>_L1.0001.dpx).
# v2.05: reads a movie's frame count itself, so ffmpeg is no longer needed
#        (ffprobe is only a fallback); can make a starter template when you
#        have none.
# v2.06: now called Blackmagic Fusion Comp Publisher (it sorts beside Blackmagic
#        Fusion in Applications); a reference clip (<shot>_ref.mov or an image
#        sequence ending _ref) is added as a second Loader when you tick the
#        option, and is never taken for the L1 clip; the window has the CVT
#        look and its sections are numbered.
# v2.07: an image sequence is found in the shot's L1 folder inside source
#        (source/<shot>_L1/<shot>_L1.1001.exr), and the _ref clip is found
#        anywhere inside the shot folder (the root of source first). Loader
#        paths are written relative to the shot folder, Comp:/...
# v2.08: the reference Loader sits to the right of the L1 Loader, with a gap
#        between them (it was stacked under it).
# v2.09: renumbered to match the set (the installer's Read Me says the tool is
#        independent of Blackmagic Design); publishing works the same.
# v2.10: safety checks before it is shared: the version tag and file extension
#        can only hold plain characters (no folders), a file name with quotes
#        or control characters cannot break the comp text, a symbolic link is
#        never written through, and an existing comp is never overwritten by
#        accident.
# v2.11: free software under the GNU GPL v3 or later, for anyone to use, change and
#        share (it was for Cutting Club members only); a notice says it is not
#        associated with Blackmagic Design. Publishing works the same.
# v2.12: renumbered to match the set; the app is now built so it opens on older Macs
#        (macOS 12 or later). The v2.11 app needed the newest macOS. Publishing works
#        the same.
# v2.13: the comp's frame size is set to match the L1 clip (a movie, or an EXR,
#        DPX, TIFF, JPEG or PNG sequence), so a 2048 x 858 plate no longer opens
#        in a 3840 x 2160 comp. Turn it off to keep the template's size.
#
# Install location: the Mac installer puts the app in /Applications; the engine
#   also runs from a terminal (standard library only)
# ---------------------------------------------------------------------------
"""
cvt_fusion_comp_publisher_v2.13.py
==================================

VFX publishing utility: given a parent directory (e.g. a "shots" folder),
create one Blackmagic Fusion composition (.comp) file inside each of its
immediate subfolders, named to match that subfolder. Each comp starts with a
Loader for the shot's L1 clip (source/<shot>_L1.mov) and the render and
working ranges set to that clip's length.

Example layout before running:

    /project/shots/
        SHOT_010/
        SHOT_020/
        SHOT_030/

After running `python3 cvt_fusion_comp_publisher_v2.13.py /project/shots`:

    /project/shots/
        SHOT_010/SHOT_010_v001.comp
        SHOT_020/SHOT_020_v001.comp
        SHOT_030/SHOT_030_v001.comp

By default, existing .comp files with the target name are left untouched
and reported as skipped. Pass --overwrite to replace them instead.

Every generated comp is a byte-for-byte copy of a template .comp file (see
DEFAULT_TEMPLATE below), so it inherits whatever Global/Default settings
were active in Fusion when that template was saved -- frame format, frame
rate, bit depth, path mapping, etc. Point --template at a different file to
use a different template, or pass --no-template to fall back to a bare-bones
comp with none of that baked in (Fusion then uses its live preferences at
open time instead).

Usage:
    python3 cvt_fusion_comp_publisher_v2.13.py /path/to/shots
    python3 cvt_fusion_comp_publisher_v2.13.py /path/to/shots --recursive
    python3 cvt_fusion_comp_publisher_v2.13.py /path/to/shots --overwrite
    python3 cvt_fusion_comp_publisher_v2.13.py /path/to/shots --pattern "SHOT_*"
    python3 cvt_fusion_comp_publisher_v2.13.py /path/to/shots --version v002
    python3 cvt_fusion_comp_publisher_v2.13.py /path/to/shots --template ~/fusion/template.comp
    python3 cvt_fusion_comp_publisher_v2.13.py /path/to/shots --no-template
    python3 cvt_fusion_comp_publisher_v2.13.py /path/to/shots --dry-run
    python3 cvt_fusion_comp_publisher_v2.13.py /path/to/shots --clip-tag 709
    python3 cvt_fusion_comp_publisher_v2.13.py /path/to/shots --only ltx_sh120 ltx_sh130
    python3 cvt_fusion_comp_publisher_v2.13.py /path/to/shots --no-loader
"""

from __future__ import annotations

import argparse
import os
import struct
import fnmatch
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

SCRIPT_TITLE = "Blackmagic Fusion Comp Publisher"  # printed messages and window titles
BRAND = "Creative Video Tips"
VERSION = "2.13"                        # keep in sync with the filename, header and docstring


def window_title() -> str:
    return f"{SCRIPT_TITLE} - v{VERSION}  |  {BRAND}"

# Default template comp -- saved from Fusion via File > New Comp, then Save As,
# with no other changes. Copied byte-for-byte into every published comp so
# generated comps inherit these Global/Default settings: frame format, frame
# rate, bit depth, path mapping, etc. Override per-run with --template, or
# skip it entirely with --no-template.
SYSTEM_TEMPLATE = Path(
    "/Library/Application Support/Blackmagic Design/Fusion/Templates/template.comp"
)
USER_TEMPLATE = (
    Path.home()
    / "Library/Application Support/Blackmagic Design/Fusion/Templates/template.comp"
)


def default_template() -> Path:
    """The template Fusion itself uses: the user's, else the system-wide one."""
    if USER_TEMPLATE.is_file():
        return USER_TEMPLATE
    # No template anywhere: the user's path, where a starter template can be made.
    return SYSTEM_TEMPLATE if SYSTEM_TEMPLATE.is_file() else USER_TEMPLATE


DEFAULT_TEMPLATE = default_template()


def starter_template_content() -> str:
    """A minimal Fusion comp that works as a template: frames 1001 to 1100, no tools.

    Fusion fills in everything else (layout, frame format, frame rate) from its own
    defaults when the comp is opened. To make it your own, open it in Fusion, set up
    your layout and preferences, and save it over the template file.
    """
    return (
        "Composition {\n"
        "\tCurrentTime = 1001,\n"
        "\tRenderRange = { 1001, 1100 },\n"
        "\tGlobalRange = { 1001, 1100 },\n"
        "\tCurrentID = 1,\n"
        "\tHiQ = true,\n"
        "\tPlaybackUpdateMode = 0,\n"
        "\tStereoMode = false,\n"
        "\tSavedOutputs = 0,\n"
        "\tHeldTools = 0,\n"
        "\tDisabledTools = 0,\n"
        "\tLockedTools = 0,\n"
        "\tAudioOffset = 0,\n"
        "\tResumable = true,\n"
        "\tOutputClips = {\n"
        "\t},\n"
        "\tTools = {\n"
        "\t},\n"
        "}\n"
    )


def create_starter_template(dest: Path) -> Path:
    """Write a starter template to `dest` (never over an existing file)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    # "x" creates the file only if nothing is there, not even a link pointing elsewhere.
    with open(dest, "x", encoding="utf-8") as f:
        f.write(starter_template_content())
    return dest


def build_blank_comp_content() -> str:
    """
    Return the text content of a minimal, valid, empty Fusion composition.

    Fusion .comp files are serialized as a Lua table literal. An empty
    composition just needs an (empty) ordered Tools table; Fusion fills in
    everything else (frame format, current time, etc.) from the user's
    preferences when the file is opened. No comments, no extra data --
    just the bare structure Fusion itself would consider a blank comp.
    """
    return (
        "{\n"
        "\tTools = ordered() {\n"
        "\t},\n"
        "\tActiveTool = nil\n"
        "}\n"
    )


# --- Loader and frame range ------------------------------------------------

SOURCE_DIR = "source"                       # folder inside each shot that holds the clips
CLIP_EXTENSIONS = (".mov", ".mp4", ".m4v")  # movie clips that get a Loader
# Image sequences that get a Loader: extension -> (Fusion format name, extra Loader inputs),
# as Fusion itself saves them.
_SLOG = '["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, }'
SEQUENCE_FORMATS = {
    ".exr": ("OpenEXRFormat", [
        '["Clip1.OpenEXRFormat.RedName"] = Input { Value = FuID { "R" }, }',
        '["Clip1.OpenEXRFormat.GreenName"] = Input { Value = FuID { "G" }, }',
        '["Clip1.OpenEXRFormat.BlueName"] = Input { Value = FuID { "B" }, }',
    ]),
    ".dpx": ("DPXFormat", ['["Clip1.DPXFormat.SLogVersion"] = Input { Value = FuID { "SLog2" }, }']),
    ".tif": ("TiffFormat", []),
    ".tiff": ("TiffFormat", []),
    ".jpg": ("JpegFormat", []),
    ".jpeg": ("JpegFormat", []),
    ".png": ("PNGFormat", ['["Clip1.PNGFormat.PostMultiply"] = Input { Value = 1, }']),
}
DEFAULT_PREFERRED_TAG = "709"               # picked when several tagged clips and no choice
FFPROBE_CANDIDATES = (
    "/opt/homebrew/bin/ffprobe",
    "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe",
    "/usr/local/bin/ffprobe",
)
_L1_RE = re.compile(r"_L1(?:_(.+))?$", re.IGNORECASE)
_REF_NAME_RE = re.compile(r"_ref$", re.IGNORECASE)   # a reference clip: <shot>_ref
_SEQ_RE = re.compile(r"^(?P<base>.+)\.(?P<num>\d+)$")   # <name>.0001 (stem of an .exr)


def _is_ref(name: str) -> bool:
    """True for a reference clip's name (it ends in _ref), which is never the L1 clip."""
    return bool(_REF_NAME_RE.search(name))


def find_ref_clip(folder: Path, source_dir: str = SOURCE_DIR) -> Path | None:
    """The shot's reference clip: a movie, or the first frame of an image sequence,
    whose name ends in _ref (ltx_sh120_ref.mov, ltx_sh120_ref.0001.exr).

    It is looked for anywhere inside the shot folder, and the one at the root of the
    source folder wins, then the shallowest. None if there is none.
    """
    source = folder / source_dir
    first_frames: dict[tuple[str, str], tuple[int, Path]] = {}
    found = []
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for name in sorted(filenames):
            if name.startswith("."):
                continue
            path = Path(dirpath) / name
            suffix = path.suffix.lower()
            if suffix in CLIP_EXTENSIONS and _is_ref(path.stem):
                found.append(path)
            elif suffix in SEQUENCE_FORMATS:
                seq = _SEQ_RE.match(path.stem)
                if seq and _is_ref(seq.group("base")):
                    num = int(seq.group("num"))
                    key = (str(path.parent), seq.group("base") + suffix)
                    if key not in first_frames or num < first_frames[key][0]:
                        first_frames[key] = (num, path)
    found += [path for _, path in first_frames.values()]
    if not found:
        return None

    def rank(path: Path) -> tuple[int, int, str]:
        at_source_root = 0 if path.parent == source else 1
        depth = len(path.relative_to(folder).parts)
        return (at_source_root, depth, str(path))

    return sorted(found, key=rank)[0]


def find_clips(folder: Path, source_dir: str = SOURCE_DIR) -> list[tuple[Path, str]]:
    """Return (clip, tag) for each L1 clip of a shot, sorted by name.

    Clips are looked for in <folder>/<source_dir> (or in the folder itself if
    there is no such subfolder) and, for image sequences, in the L1 folder inside it.
    `ltx_sh120_L1.mov` has the tag "";
    `ltx_sh120_L1_709.mov` has the tag "709".
    """
    base = folder / source_dir if (folder / source_dir).is_dir() else folder
    # Movies and sequences in the source folder itself, and sequences in its L1 folder
    # (source/<shot>_L1/<shot>_L1.1001.exr; the folder carries no colour tag).
    places = [base] + sorted(
        d for d in base.iterdir()
        if d.is_dir() and not d.name.startswith(".") and _L1_RE.search(d.name) and not _is_ref(d.name)
    )
    found = []
    first_frames: dict[tuple[str, str, str], tuple[int, Path]] = {}  # (dir, name, ext) -> (lowest frame, file)
    for place in places:
        for path in sorted(place.iterdir()):
            if path.name.startswith("."):
                continue
            suffix = path.suffix.lower()
            if suffix in CLIP_EXTENSIONS:
                match = _L1_RE.search(path.stem)
                if match and not _is_ref(path.stem):
                    found.append((path, match.group(1) or ""))
            elif suffix in SEQUENCE_FORMATS:
                seq = _SEQ_RE.match(path.stem)
                if seq and _L1_RE.search(seq.group("base")) and not _is_ref(seq.group("base")):
                    num = int(seq.group("num"))
                    key = (str(place), seq.group("base"), suffix)
                    if key not in first_frames or num < first_frames[key][0]:
                        first_frames[key] = (num, path)
    for (_, base_name, _), (_, path) in first_frames.items():
        found.append((path, _L1_RE.search(base_name).group(1) or ""))
    return sorted(found, key=lambda item: str(item[0]))


def choose_clip(
    clips: list[tuple[Path, str]], wanted_tag: str = ""
) -> tuple[Path | None, str]:
    """Pick the clip to load; returns (clip or None, a note for the report).

    wanted_tag "" means Auto: the untagged L1 if there is one, else the only
    clip, else the 709 one, else the first by name. A tag that no clip has
    falls back to Auto and says so in the note.
    """
    if not clips:
        return None, "no L1 clip found"
    note = ""
    wanted = wanted_tag.strip().lower()
    if wanted:
        for path, tag in clips:
            if tag.lower() == wanted:
                return path, ""
        note = f"no clip tagged '{wanted_tag}', used Auto instead; "
    for path, tag in clips:
        if not tag:
            return path, note
    if len(clips) == 1:
        return clips[0][0], note
    for path, tag in clips:
        if tag.lower() == DEFAULT_PREFERRED_TAG:
            return path, note + f"several tagged clips, used {tag}"
    return clips[0][0], note + f"several tagged clips, used {clips[0][1]}"


def find_ffprobe() -> str | None:
    found = shutil.which("ffprobe")
    if found:
        return found
    for candidate in FFPROBE_CANDIDATES:
        if Path(candidate).is_file():
            return candidate
    return None


def _boxes(f, start: int, end: int):
    """Yield (type, payload start, payload end) for the MP4/MOV boxes in a byte range."""
    pos = start
    while pos + 8 <= end:
        f.seek(pos)
        header = f.read(8)
        if len(header) < 8:
            return
        size, kind = struct.unpack(">I4s", header)
        head = 8
        if size == 1:                      # 64-bit size follows
            size = struct.unpack(">Q", f.read(8))[0]
            head = 16
        elif size == 0:                    # runs to the end of the file/range
            size = end - pos
        if size < head:
            return
        yield kind, pos + head, min(pos + size, end)
        pos += size


def mov_frame_count(clip: Path) -> int:
    """Frame count of a QuickTime/MP4 movie's first video track, read from the file."""
    return mov_video_info(clip)[0]


def mov_video_info(clip: Path) -> tuple[int, int | None, int | None]:
    """(frames, width, height) of a QuickTime/MP4 movie's first video track, read from the file.

    Walks the boxes to the video track's sample table: stsz holds the number of samples
    (one per frame) and stsd the picture size. Width and height are None if the sample
    description is not one this reader understands. Raises RuntimeError if the file has
    no readable video track.
    """
    with open(clip, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        moov = next(((a, b) for kind, a, b in _boxes(f, 0, size) if kind == b"moov"), None)
        if moov is None:
            raise RuntimeError("no movie header (moov) in the file")
        for kind, a, b in _boxes(f, *moov):
            if kind != b"trak":
                continue
            mdia = next(((x, y) for k, x, y in _boxes(f, a, b) if k == b"mdia"), None)
            if mdia is None:
                continue
            handler = None
            minf = None
            for k, x, y in _boxes(f, *mdia):
                if k == b"hdlr":
                    f.seek(x + 8)           # skip version/flags and the 'mhlr' type;
                    handler = f.read(4)     # the handler subtype ('vide', 'soun', 'tmcd'...)
                elif k == b"minf":
                    minf = (x, y)
            if handler != b"vide" or minf is None:
                continue
            stbl = next(((x, y) for k, x, y in _boxes(f, *minf) if k == b"stbl"), None)
            if stbl is None:
                continue
            count, width, height = 0, None, None
            for k, x, y in _boxes(f, *stbl):
                if k == b"stsz":
                    f.seek(x + 4)
                    _sample_size, count = struct.unpack(">II", f.read(8))
                elif k == b"stsd" and y - x >= 44:
                    f.seek(x + 40)   # version/flags, count, then the first entry's fixed fields
                    width, height = struct.unpack(">HH", f.read(4))
            if count > 0:
                return count, (width or None), (height or None)
    raise RuntimeError("no video track with frames found")


def clip_frame_count(clip: Path) -> int:
    """Number of video frames in a movie. Raises RuntimeError.

    Reads the file itself; ffprobe (if installed) is only a fallback for files
    this reader does not understand.
    """
    try:
        return mov_frame_count(clip)
    except (RuntimeError, OSError, struct.error):
        pass
    ffprobe = find_ffprobe()
    if ffprobe is None:
        raise RuntimeError("could not read the frame count of this movie")
    for entry in ("nb_frames", "nb_read_frames"):
        cmd = [ffprobe, "-v", "error", "-select_streams", "v:0"]
        if entry == "nb_read_frames":
            cmd.append("-count_frames")
        cmd += ["-show_entries", f"stream={entry}", "-of", "default=nw=1:nk=1", "-i", str(clip)]
        try:
            lines = subprocess.run(cmd, capture_output=True, text=True, timeout=300).stdout.split()
            out = lines[0] if lines else ""
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError(f"ffprobe failed: {exc}") from exc
        if out.isdigit() and int(out) > 0:
            return int(out)
    raise RuntimeError("could not read the frame count")


def _cstring(f) -> str:
    out = bytearray()
    while len(out) < 256:
        ch = f.read(1)
        if not ch or ch == b"\0":
            break
        out += ch
    return out.decode("latin-1")


def _exr_size(f) -> tuple[int, int]:
    if f.read(4) != b"\x76\x2f\x31\x01":
        raise ValueError("not an EXR file")
    f.read(4)                                   # version and flags
    found = {}
    for _ in range(200):                        # header attributes, ended by an empty name
        name = _cstring(f)
        if not name:
            break
        kind = _cstring(f)
        (size,) = struct.unpack("<i", f.read(4))
        if size < 0 or size > (1 << 20):
            raise ValueError("odd EXR header")
        data = f.read(size)
        if kind == "box2i" and size == 16 and name in ("dataWindow", "displayWindow"):
            x0, y0, x1, y1 = struct.unpack("<4i", data)
            found[name] = (x1 - x0 + 1, y1 - y0 + 1)
    # The display window is the canvas the picture is meant for.
    size = found.get("displayWindow") or found.get("dataWindow")
    if not size:
        raise ValueError("no window in the EXR header")
    return size


def _dpx_size(f) -> tuple[int, int]:
    head = f.read(780)
    if head[:4] == b"SDPX":
        order = ">"
    elif head[:4] == b"XPDS":
        order = "<"
    else:
        raise ValueError("not a DPX file")
    return struct.unpack(order + "II", head[772:780])


def _tiff_size(f) -> tuple[int, int]:
    head = f.read(8)
    order = {b"II": "<", b"MM": ">"}.get(head[:2])
    if order is None or struct.unpack(order + "H", head[2:4])[0] != 42:
        raise ValueError("not a classic TIFF file")
    f.seek(struct.unpack(order + "I", head[4:8])[0])
    (count,) = struct.unpack(order + "H", f.read(2))
    width = height = None
    for _ in range(min(count, 512)):
        tag, kind, _n = struct.unpack(order + "HHI", f.read(8))
        raw = f.read(4)
        value = struct.unpack(order + ("H" if kind == 3 else "I"), raw[:2] if kind == 3 else raw)[0]
        if tag == 256:
            width = value
        elif tag == 257:
            height = value
    if not width or not height:
        raise ValueError("no size in the TIFF")
    return width, height


def _png_size(f) -> tuple[int, int]:
    head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        raise ValueError("not a PNG file")
    return struct.unpack(">II", head[16:24])


def _jpeg_size(f) -> tuple[int, int]:
    data = f.read(1 << 17)
    if data[:2] != b"\xff\xd8":
        raise ValueError("not a JPEG file")
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7 or marker == 0xFF:
            i += 1 if marker == 0xFF else 2
            continue
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            return width, height
        i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    raise ValueError("no size in the JPEG")


_SIZE_READERS = {".exr": _exr_size, ".dpx": _dpx_size, ".tif": _tiff_size, ".tiff": _tiff_size,
                 ".png": _png_size, ".jpg": _jpeg_size, ".jpeg": _jpeg_size}


def clip_size(clip: Path) -> tuple[int, int] | None:
    """(width, height) of a clip's picture: a movie, or the first frame of an image sequence.

    Read from the file's own header, with no other program. None if it can't be read.
    """
    try:
        suffix = clip.suffix.lower()
        if suffix in SEQUENCE_FORMATS:
            with open(clip, "rb") as f:
                width, height = _SIZE_READERS[suffix](f)
        else:
            _frames, width, height = mov_video_info(clip)
        if width and height and 0 < width <= 65536 and 0 < height <= 65536:
            return int(width), int(height)
    except (OSError, ValueError, RuntimeError, struct.error):
        pass
    return None


_KNOWN_SIZES = {(1920, 1080): "HD 1080", (3840, 2160): "Ultra HD 2160"}


def set_frame_size(text: str, width: int, height: int) -> str:
    """Return the comp text with its frame format set to width x height.

    The size lives in Prefs.Comp.FrameFormat. The format's Name is only a label, so it
    is "HD 1080" or "Ultra HD 2160" when the size is one of those and "Custom" otherwise.
    The frame rate and bit depths of the template are left as they are. The guide ratio
    follows the new picture. A template with no frame format of its own (the starter
    template) gets one, with Fusion's usual rate.
    """
    name = _KNOWN_SIZES.get((width, height), "Custom")
    ratio = "%.14g" % (width / height)
    match = re.search(r"FrameFormat = \{[^{}]*\}", text)
    if match:
        block = match.group(0)
        for pattern, value in ((r'Name = "[^"]*"', 'Name = "%s"' % name),
                               (r"Width = \d+", "Width = %d" % width),
                               (r"Height = \d+", "Height = %d" % height),
                               (r"GuideRatio = [\d.]+", "GuideRatio = %s" % ratio)):
            block = re.sub(pattern, value, block, count=1)
        return text[:match.start()] + block + text[match.end():]
    if "Prefs = {" in text:
        return text    # a Prefs table without a frame format: leave it alone
    prefs = (
        "\tPrefs = {\n\t\tComp = {\n\t\t\tFrameFormat = {\n"
        f'\t\t\t\tName = "{name}",\n\t\t\t\tWidth = {width},\n\t\t\t\tHeight = {height},\n'
        f"\t\t\t\tRate = 24,\n\t\t\t\tGuideRatio = {ratio},\n"
        "\t\t\t}\n\t\t}\n\t},\n"
    )
    body = text.rstrip()
    if not body.endswith("}"):
        return text
    return body[:-1].rstrip() + "\n" + prefs + "}\n"


def measure_clip(clip: Path) -> tuple[int | None, int]:
    """(first frame number or None for a movie, number of frames) of a clip."""
    if clip.suffix.lower() in SEQUENCE_FORMATS:
        return sequence_frames(clip)
    return None, clip_frame_count(clip)


def sequence_frames(first: Path) -> tuple[int, int]:
    """For an image sequence given by one frame, return (first frame number, frame count).

    The count runs from the lowest to the highest numbered file of the sequence,
    so a gap shows as a longer clip (Fusion's Missing Frames setting handles it).
    """
    seq = _SEQ_RE.match(first.stem)
    if not seq:
        raise ValueError("not a numbered frame")
    base = seq.group("base")
    numbers = []
    for path in first.parent.iterdir():
        if path.suffix.lower() == first.suffix.lower():
            other = _SEQ_RE.match(path.stem)
            if other and other.group("base") == base:
                numbers.append(int(other.group("num")))
    return min(numbers), max(numbers) - min(numbers) + 1


def _lua_string(text: str) -> str:
    """Escape text for a double-quoted string in a Fusion comp file.

    A file name can hold quotes or backslashes; left as they are, they would end the
    string early and corrupt the comp. Control characters have no safe form and raise.
    """
    out = []
    for ch in text:
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif ord(ch) < 32 or ord(ch) == 127:
            raise ValueError("the file name has a control character")
        else:
            out.append(ch)
    return "".join(out)


def _loader_lines(
    tool: str, clip_path: str, frames: int, start: int, first_frame: int | None,
    ext: str, pos: tuple[float, float],
) -> list[str]:
    """The lines of one Loader, in the form Fusion saves it (no trailing comma)."""
    t = "\t"
    clip = ['ID = "Clip1"', f'Filename = "Comp:/{_lua_string(clip_path)}"']
    if first_frame is None:
        clip += ['FormatID = "QuickTimeMovies"', f"Length = {frames}", "Multiframe = true"]
    else:
        clip += [
            f'FormatID = "{SEQUENCE_FORMATS[ext][0]}"',
            f"StartFrame = {first_frame}",
            f"Length = {frames}",
            "LengthSetManually = true",
        ]
    clip += [
        "TrimIn = 0",
        f"TrimOut = {frames - 1}",
        "ExtendFirst = 0",
        "ExtendLast = 0",
        "Loop = 1",
        "AspectMode = 0",
        "Depth = 0",
        "TimeCode = 0",
        f"GlobalStart = {start}",
        f"GlobalEnd = {start + frames - 1}",
    ]
    inputs = [_SLOG]
    if first_frame is not None:
        inputs += SEQUENCE_FORMATS[ext][1]
    lines = [f"{t*2}{tool} = Loader {{", f"{t*3}Clips = {{", f"{t*4}Clip {{"]
    lines += [f"{t*5}{item}," if i < len(clip) - 1 else f"{t*5}{item}" for i, item in enumerate(clip)]
    lines += [f"{t*4}}}", f"{t*3}}},", f"{t*3}CtrlWZoom = false,", f"{t*3}Inputs = {{"]
    lines += [f"{t*4}{item}," if i < len(inputs) - 1 else f"{t*4}{item}" for i, item in enumerate(inputs)]
    lines += [
        f"{t*3}}},",
        f"{t*3}ViewInfo = OperatorInfo {{ Pos = {{ {pos[0]:g}, {pos[1]:g} }} }},",
        f"{t*2}}}",
    ]
    return lines


def build_loader_block(
    clip_path: str, frames: int, start: int, first_frame: int | None = None,
    ext: str = ".exr", ref: tuple | None = None,
) -> str:
    """Text of the Tools table: Loader1 for the L1 clip and, if given, Loader2 for a reference.

    first_frame is None for a movie; for an image sequence it is the number of the
    first frame (the clip path is that first frame's file, relative to the shot
    folder, like source/<shot>_L1/<shot>_L1.1001.exr) and ext is its
    file extension, which picks Fusion's format name. ref is the reference clip as
    (clip path, frames, first frame or None, extension); it starts at the same frame.
    """
    loaders = _loader_lines("Loader1", clip_path, frames, start, first_frame, ext, (104, 219.485))
    if ref is not None:
        ref_name, ref_frames, ref_first, ref_ext = ref
        loaders[-1] += ","
        loaders += _loader_lines(
            "Loader2", ref_name, ref_frames, start, ref_first, ref_ext, (219.5, 219.485)
        )
    return "\n".join(["\tTools = {"] + loaders + ["\t},"]) + "\n"


def add_loader_to_comp(
    text: str,
    clip_path: str,
    frames: int,
    first_frame: int | None = None,
    ext: str = ".exr",
    ref: tuple | None = None,
    size: tuple[int, int] | None = None,
) -> str:
    """Return the template text with a Loader added and the ranges set.
    If a size (width, height) is given, the comp's frame size is set to it too.

    The render range is the clip (start to start + frames - 1) and the working
    (global) range runs one frame further, the way Fusion sets them when you
    Shift-drag a Loader to the time ruler; a reference clip does not change them.
    Raises ValueError if the text is not
    shaped like a Fusion comp saved with no tools.
    """
    empty_tools = "\tTools = {\n\t},\n"
    match = re.search(r"RenderRange = \{ (\d+), \d+ \}", text)
    if empty_tools not in text or not match:
        raise ValueError("the template is not an empty comp this tool can add a Loader to")
    start = int(match.group(1))
    end = start + frames - 1

    text = text.replace(empty_tools, build_loader_block(clip_path, frames, start, first_frame, ext, ref), 1)
    text = re.sub(r"CurrentTime = [\d.]+,", f"CurrentTime = {start},", text, count=1)
    text = re.sub(r"RenderRange = \{[^}]*\}", f"RenderRange = {{ {start}, {end} }}", text, count=1)
    text = re.sub(r"GlobalRange = \{[^}]*\}", f"GlobalRange = {{ {start}, {end + 1} }}", text, count=1)
    text = re.sub(
        r"VisibleRange = \{[^}]*\}", f"VisibleRange = {{ {start}, {end}.9999 }}", text
    )
    if size is not None:
        text = set_frame_size(text, size[0], size[1])
    return text


_SAFE_VERSION = re.compile(r"^[A-Za-z0-9_-][A-Za-z0-9._-]*$|^$")
_SAFE_EXTENSION = re.compile(r"^\.[A-Za-z0-9]{1,12}$")


def check_name_options(version: str, extension: str) -> None:
    """Raise ValueError unless the version tag and extension are plain file-name text.

    They are added to the shot name to make the comp's path, so they must not hold a
    folder separator or "..", which could write a file outside the shot folder.
    """
    if not _SAFE_VERSION.match(version):
        raise ValueError(
            "The version tag can only hold letters, numbers, dots, dashes and underscores "
            "(like v001), and cannot start with a dot."
        )
    if not _SAFE_EXTENSION.match(extension):
        raise ValueError("The file extension must be a dot and letters or numbers, like .comp.")


def comp_path_for(folder: Path, version: str, extension: str) -> Path:
    stem = f"{folder.name}_{version}" if version else folder.name
    return folder / f"{stem}{extension}"


@dataclass
class PublishSummary:
    created: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)
    overwritten: list[Path] = field(default_factory=list)
    errored: list[tuple[Path, str]] = field(default_factory=list)
    notes: dict[Path, str] = field(default_factory=dict)  # comp path -> what was set up

    def print_report(self) -> None:
        if self.created:
            print(f"\nCreated ({len(self.created)}):")
            for p in self.created:
                print(f"  + {p}" + (f"   [{self.notes[p]}]" if p in self.notes else ""))
        if self.overwritten:
            print(f"\nOverwritten ({len(self.overwritten)}):")
            for p in self.overwritten:
                print(f"  ~ {p}" + (f"   [{self.notes[p]}]" if p in self.notes else ""))
        if self.skipped:
            print(f"\nSkipped, already exists ({len(self.skipped)}):")
            for p in self.skipped:
                print(f"  - {p}")
        if self.errored:
            print(f"\nErrors ({len(self.errored)}):")
            for p, msg in self.errored:
                print(f"  ! {p}: {msg}")
        total = len(self.created) + len(self.overwritten)
        print(
            f"\nDone. {total} comp file(s) written, "
            f"{len(self.skipped)} skipped, {len(self.errored)} error(s)."
        )


def find_target_folders(root: Path, recursive: bool, pattern: str) -> list[Path]:
    """
    Return the list of folders that should each receive a comp file.

    Non-recursive: immediate subfolders of `root` only.
    Recursive: every subfolder at any depth under `root`.

    `pattern` is a glob-style filter (fnmatch) applied to folder names,
    e.g. "SHOT_*". Use "*" (the default) to match everything.
    """
    if recursive:
        candidates = [p for p in root.rglob("*") if p.is_dir()]
    else:
        candidates = [p for p in root.iterdir() if p.is_dir()]

    matched = [p for p in candidates if fnmatch.fnmatch(p.name, pattern)]
    return sorted(matched)


def publish_comps(
    root: Path,
    recursive: bool = False,
    overwrite: bool = False,
    dry_run: bool = False,
    pattern: str = "*",
    extension: str = ".comp",
    version: str = "v001",
    template: Path | None = None,
    add_loader: bool = True,
    clip_tag: str = "",
    only: set[str] | None = None,
    add_ref: bool = True,
    match_size: bool = True,
) -> PublishSummary:
    """Write one comp per shot folder.

    add_loader: put a Loader for the shot's L1 clip in the comp and set the
    ranges to its length (needs a template that is an empty comp).
    clip_tag: colour-space tag to choose between L1 clips ("" = Auto).
    only: folder names to publish; None means every matching folder.
    add_ref: also add a second Loader for the shot's _ref clip, if it has one.
    match_size: set the comp's frame size to the L1 clip's picture size.
    """
    check_name_options(version, extension)
    summary = PublishSummary()

    if template is not None:
        if not template.is_file():
            raise FileNotFoundError(f"Template comp not found: {template}")
        content_bytes = template.read_bytes()
    else:
        content_bytes = build_blank_comp_content().encode("utf-8")

    targets = find_target_folders(root, recursive=recursive, pattern=pattern)
    if only is not None:
        targets = [f for f in targets if f.name in only]

    for folder in targets:
        comp_path = comp_path_for(folder, version, extension)
        if comp_path.is_symlink():
            summary.errored.append((comp_path, "is a symbolic link, so it was left alone"))
            continue
        exists = comp_path.exists()

        if exists and not overwrite:
            summary.skipped.append(comp_path)
            continue

        data = content_bytes
        note = ""
        if add_loader and template is not None:
            clip, note = choose_clip(find_clips(folder), clip_tag)
            if clip is not None:
                try:
                    first_frame, frames = measure_clip(clip)
                    size = clip_size(clip) if match_size else None
                    size_note = ""
                    if match_size:
                        size_note = (f"{size[0]}x{size[1]}" if size
                                     else "size not read, kept the template's")
                    ref = None
                    ref_note = ""
                    ref_clip = find_ref_clip(folder) if add_ref else None
                    if ref_clip is not None:
                        try:
                            ref_first, ref_frames = measure_clip(ref_clip)
                            ref = (ref_clip.relative_to(folder).as_posix(), ref_frames,
                                   ref_first, ref_clip.suffix.lower())
                            ref_note = f"ref: {ref_clip.name}, {ref_frames} frames"
                        except (RuntimeError, ValueError, OSError) as exc:
                            ref_note = f"ref {ref_clip.name} skipped: {exc}"
                    data = add_loader_to_comp(
                        content_bytes.decode("utf-8"), clip.relative_to(folder).as_posix(),
                        frames, first_frame,
                        clip.suffix.lower(), ref, size,
                    ).encode("utf-8")
                    note = note.strip("; ")
                    kind = "frame sequence" if first_frame is not None else "movie"
                    note = f"{clip.name}, {frames} frames ({kind})" + (
                        f", {size_note}" if size_note else "") + (
                        f"; {note}" if note else ""
                    ) + (f"; {ref_note}" if ref_note else "")
                except (RuntimeError, ValueError, OSError) as exc:
                    note = f"{clip.name}: {exc}; plain template, no Loader"
            else:
                note = (note.strip("; ") + "; " if note else "") + "plain template, no Loader"
        if note:
            summary.notes[comp_path] = note

        if dry_run:
            (summary.overwritten if exists else summary.created).append(comp_path)
            continue

        try:
            if exists:   # only reached with Overwrite on
                comp_path.write_bytes(data)
            else:        # "xb" fails rather than replace something that appeared since
                with open(comp_path, "xb") as f:
                    f.write(data)
        except FileExistsError:
            summary.skipped.append(comp_path)
            continue
        except OSError as exc:
            summary.errored.append((comp_path, str(exc)))
            continue

        if exists:
            summary.overwritten.append(comp_path)
        else:
            summary.created.append(comp_path)

    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            f"{window_title()}: create a blank Fusion (.comp) file inside each subfolder of a "
            "given directory, named to match that subfolder. Useful for "
            "scaffolding starter comps across many shots at once."
        )
    )
    parser.add_argument(
        "root",
        type=Path,
        help="Parent directory whose immediate subfolders should each get a comp file.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Walk subfolders at every depth under root, not just the immediate children.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing comp file of the same name instead of skipping it.",
    )
    parser.add_argument(
        "--pattern",
        default="*",
        help='Glob pattern to filter which folder names are targeted (default: "*", i.e. all).',
    )
    parser.add_argument(
        "--extension",
        default=".comp",
        help='File extension to use for the generated files (default: ".comp").',
    )
    parser.add_argument(
        "--version",
        default="v001",
        help='Version tag appended to the folder name, e.g. "<folder>_v001" '
        '(default: "v001"). Pass an empty string ("") to omit it entirely.',
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help=(
            "Path to a template .comp file (saved from Fusion via File > New Comp, "
            "then Save As, with no other changes) to copy for each shot instead of "
            "generating a bare-bones comp. This is how generated comps inherit your "
            f"Fusion Global/Default settings. Default: {DEFAULT_TEMPLATE}"
        ),
    )
    parser.add_argument(
        "--no-template",
        action="store_true",
        help="Ignore the template (default or otherwise) and generate a bare-bones comp.",
    )
    parser.add_argument(
        "--no-loader",
        action="store_true",
        help="Do not add a Loader or set the frame ranges; copy the template as is.",
    )
    parser.add_argument(
        "--no-match-size",
        action="store_true",
        help="Keep the template's frame size instead of matching the L1 clip's picture size.",
    )
    parser.add_argument(
        "--no-ref",
        action="store_true",
        help="Do not add a second Loader for a <shot>_ref reference clip.",
    )
    parser.add_argument(
        "--clip-tag",
        default="",
        help='Colour-space tag that chooses between L1 clips, e.g. "709" or "flat" '
        "(default: Auto -- the untagged L1, else the only clip, else the 709 one).",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        metavar="FOLDER",
        help="Publish only these shot folder names (e.g. ltx_sh120 ltx_sh130).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created/overwritten/skipped without writing any files.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    root: Path = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"{SCRIPT_TITLE}: '{root}' is not a directory.", file=sys.stderr)
        return 1

    template: Path | None = None
    if not args.no_template and args.template is not None:
        template = args.template.expanduser().resolve()
        if not template.is_file():
            print(f"{SCRIPT_TITLE}: template comp '{template}' is not a file.", file=sys.stderr)
            print(
                "Pass --template to point at a different file, or --no-template "
                "for a bare-bones comp instead.",
                file=sys.stderr,
            )
            return 1

    if args.dry_run:
        print("Dry run -- no files will be written.\n")

    print(window_title())
    print(f"Scanning: {root}")
    print(f"Mode: {'recursive' if args.recursive else 'immediate subfolders only'}")
    print(f"Pattern: {args.pattern}")
    print(f"Template: {template if template else '(none -- bare-bones comp)'}")

    try:
        check_name_options(args.version, args.extension)
    except ValueError as exc:
        print(f"{SCRIPT_TITLE}: {exc}", file=sys.stderr)
        return 1
    summary = publish_comps(
        root=root,
        recursive=args.recursive,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
        pattern=args.pattern,
        extension=args.extension,
        version=args.version,
        template=template,
        add_loader=not args.no_loader,
        add_ref=not args.no_ref,
        match_size=not args.no_match_size,
        clip_tag=args.clip_tag,
        only=set(args.only) if args.only else None,
    )
    summary.print_report()

    return 1 if summary.errored else 0


if __name__ == "__main__":
    raise SystemExit(main())
