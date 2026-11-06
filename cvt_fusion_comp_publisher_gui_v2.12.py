#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# cvt_fusion_comp_publisher_gui_v2.12
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
#   1. Opens the Blackmagic Fusion Comp Publisher window: pick a shots folder,
#      the comps to publish, a template comp and a few options.
#   2. Lists the shot folders with a tick box each; shots that already have a
#      comp start unticked, so a re-run leaves them alone. Publish only the
#      ticked ones.
#   3. Each new comp gets a Loader for the shot's L1 clip and the render and
#      working ranges set to the clip length. A colour tag (709, flat ...)
#      picks the clip when a shot has more than one. A reference clip
#      (<shot>_ref) can be added as a second Loader.
#   4. Preview lists the comps that would be created, overwritten or skipped
#      without writing anything; Publish writes them.
#   5. Double-click a result to reveal that folder in the Finder.
#   6. Remembers your last choices for next time (Overwrite always starts off).
#
# Needs cvt_fusion_comp_publisher_v2.12.py in the same folder, and PySide6
# (see requirements.txt; installed in ~/.venvs/fusion-tools).
#
# v1.01: remembers your last folder, template, pattern, extension, version tag
#        and Recursive setting between runs. Overwrite always starts off.
# v1.02: licence text: a Cutting Club thank-you script, for your own use only,
#        not for resale and not for sharing.
# v2.00: Loader and frame range set up in each new comp, a clip colour tag
#        choice, and tick boxes to publish only the shots you choose.
# v2.01: renumbered to match the set; EXR sequences get a Loader too.
# v2.02: the template is required, not optional, and is pre-filled with the
#        default template path (it carries your layout and Fusion settings);
#        a Use Default button puts the default path back.
# v2.03: the default template is the one in your user Templates folder (where
#        Fusion looks), else the system-wide one; a saved system-wide path
#        moves to the user one when it exists.
# v2.04: every option has a short plain-language explanation under it (the
#        folder name filter says what * means); image sequences of every type
#        (EXR, DPX, TIFF, JPEG, PNG) get a Loader.
# v2.05: with no template yet, the window offers to create a starter one;
#        movie lengths are read without ffmpeg.
# v2.06: now called Blackmagic Fusion Comp Publisher, in the CVT charcoal and
#        teal look with numbered sections ("Comps to publish" is section 2),
#        opened in the middle of the screen; the less-used options sit under
#        More options; an option adds a second Loader for the shot's _ref
#        clip; the results show each comp's path from your source folder.
# v2.07: image sequences are found in the shot's L1 folder inside source
#        (source/<shot>_L1/), and the _ref clip anywhere inside the shot folder
#        (the root of source first).
# v2.08: renumbered to match the set (the reference Loader is placed beside
#        the L1 Loader in the node graph); the window is unchanged.
# v2.09: renumbered to match the set; the window is unchanged.
# v2.10: a version tag or extension with a slash or other odd character is
#        refused with a clear message.
# v2.11: free software under the GNU GPL v3 or later (it was for Cutting Club
#        members only); the window is unchanged.
# v2.12: renumbered to match the set; the app is now built so it opens on older Macs
#        (macOS 12 or later); the window is unchanged.
#
# Install location: the Mac installer puts the app in /Applications; from source,
#   run this file with Python and PySide6
# ---------------------------------------------------------------------------
"""
cvt_fusion_comp_publisher_gui_v2.12.py
======================================

A PySide6 desktop UI for cvt_fusion_comp_publisher_v2.12.py.

Point it at a parent folder (e.g. a shots directory), tick the comps you want,
preview what would happen, then publish Fusion (.comp) files into each ticked
subfolder, named to match that subfolder. Each comp starts with a Loader for
the shot's L1 clip and its frame range set to the clip.

The publishing engine is loaded from the file with this script's own
version number, so the window and the engine always come from one release.

Your options are saved in ~/.cvt/fusion_comp_publisher.json when you Preview,
Publish or close the window, and filled back in next time. Overwrite is left
out on purpose, so a new session never starts ready to replace comps.

Run:
    ~/.venvs/fusion-tools/bin/python3 cvt_fusion_comp_publisher_gui_v2.12.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

VERSION = "2.12"                   # keep in sync with the filename, header and docstring
SCRIPT_NAME = "fusion_comp_publisher"  # settings file name, no version in it


def load_engine():
    """Load cvt_fusion_comp_publisher_v<VERSION>.py from this script's folder.

    The version dots in the file name keep it from being imported by name,
    so it is loaded from its path instead.
    """
    # In the packaged app the engine sits beside this script inside the bundle.
    folder = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    path = folder / f"cvt_fusion_comp_publisher_v{VERSION}.py"
    if not path.is_file():
        sys.exit(f"Blackmagic Fusion Comp Publisher: {path.name} not found next to this script.")
    spec = importlib.util.spec_from_file_location("cvt_fusion_comp_publisher", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses need the module registered
    spec.loader.exec_module(module)
    return module


_engine = load_engine()
DEFAULT_TEMPLATE = _engine.DEFAULT_TEMPLATE
SYSTEM_TEMPLATE = _engine.SYSTEM_TEMPLATE
PublishSummary = _engine.PublishSummary
publish_comps = _engine.publish_comps
find_target_folders = _engine.find_target_folders
find_clips = _engine.find_clips
comp_path_for = _engine.comp_path_for
window_title = _engine.window_title
SCRIPT_TITLE = _engine.SCRIPT_TITLE

# ---------------------------------------------------------------------------
# CVT look: charcoal slate with teal accents (the same colours as the CVT
# scripts for DaVinci Resolve)
# ---------------------------------------------------------------------------

WINDOW_STYLE = """
QWidget { background-color: rgb(46, 58, 66); color: rgb(233, 239, 242); }
QLineEdit, QComboBox {
    background-color: rgb(31, 40, 46); border: 1px solid rgb(76, 95, 107);
    border-radius: 3px; padding: 3px 6px; }
QLineEdit:focus, QComboBox:focus { border: 1px solid rgb(34, 184, 174); }
QComboBox QAbstractItemView { background-color: rgb(31, 40, 46);
    selection-background-color: rgb(26, 140, 132); }
QPushButton { background-color: rgb(59, 73, 82); border: 1px solid rgb(76, 95, 107);
    border-radius: 4px; padding: 5px 16px; }
QPushButton:hover { background-color: rgb(70, 86, 96); }
QPushButton:pressed { background-color: rgb(50, 62, 70); }
QPushButton#mainButton { background-color: rgb(34, 184, 174); border: 1px solid rgb(34, 184, 174);
    color: rgb(255, 255, 255); font-weight: bold; padding: 5px 22px; }
QPushButton#mainButton:hover { background-color: rgb(46, 204, 193); }
QPushButton#smallButton { padding: 3px 12px; }
QCheckBox { spacing: 8px; }
QCheckBox::indicator, QListView::indicator { width: 14px; height: 14px; border-radius: 3px;
    border: 1px solid rgb(76, 95, 107); background-color: rgb(31, 40, 46); }
QCheckBox::indicator:checked, QListView::indicator:checked {
    background-color: rgb(34, 184, 174); border: 1px solid rgb(34, 184, 174); }
QListWidget, QTableWidget { background-color: rgb(31, 40, 46); border: 1px solid rgb(76, 95, 107);
    border-radius: 3px; alternate-background-color: rgb(36, 46, 53);
    selection-background-color: rgb(26, 140, 132); outline: 0; }
QListWidget::item { padding: 2px 4px; }
QHeaderView::section { background-color: rgb(38, 48, 55); color: rgb(150, 165, 174);
    border: 0; border-bottom: 1px solid rgb(76, 95, 107); padding: 3px 6px; }
QTableCornerButton::section { background-color: rgb(38, 48, 55); border: 0; }
QScrollArea { border: 0; }
QScrollBar:vertical { background-color: rgb(38, 48, 55); width: 10px; margin: 0; }
QScrollBar::handle:vertical { background-color: rgb(76, 95, 107); border-radius: 5px; min-height: 24px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background-color: rgb(38, 48, 55); height: 10px; margin: 0; }
QScrollBar::handle:horizontal { background-color: rgb(76, 95, 107); border-radius: 5px; min-width: 24px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QToolTip { background-color: rgb(31, 40, 46); color: rgb(233, 239, 242);
    border: 1px solid rgb(76, 95, 107); }
QToolButton { border: 0; padding: 2px 0; color: rgb(150, 165, 174); }
QToolButton:hover { color: rgb(233, 239, 242); }
"""
# A section heading with the divider line above it (the line is its top border).
HEADING_STYLE = ("color: rgb(95, 224, 212); font-size: 11px; font-weight: bold;"
                 " border-top: 1px solid rgb(76, 95, 107); margin-top: 6px; padding-top: 8px;")
HINT_STYLE = "color: rgb(150, 165, 174); font-size: 12px;"
WARNING_STYLE = "color: rgb(230, 170, 60); font-size: 12px;"

STATUS_COLORS = {
    "created": "#5fe0d4",
    "overwritten": "#e6aa3c",
    "skipped": "#96a5ae",
    "error": "#f07070",
}

# ---------------------------------------------------------------------------
# Remembered settings (unversioned file, so they carry over between versions)
# ---------------------------------------------------------------------------

SETTINGS_PATH = os.path.join(os.path.expanduser("~"), ".cvt", SCRIPT_NAME + ".json")


def default_settings() -> dict:
    return {
        "source_folder": "",
        "template": str(DEFAULT_TEMPLATE),
        "recursive": False,
        "pattern": "*",
        "extension": ".comp",
        "version_tag": "v001",
        "add_loader": True,
        "clip_tag": "",
        "add_ref": True,
    }


def load_settings() -> dict:
    settings = default_settings()
    try:
        with open(SETTINGS_PATH) as f:
            saved = json.load(f)
    except (OSError, ValueError):
        return settings
    if isinstance(saved, dict):
        for key, default in settings.items():
            if isinstance(saved.get(key), type(default)):
                settings[key] = saved[key]
    return settings


def save_settings(settings: dict) -> None:
    try:
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f, indent=2)
    except OSError as exc:
        print(f"{SCRIPT_TITLE}: could not save settings: {exc}")


from PySide6.QtCore import QUrl, Qt  # noqa: E402
from PySide6.QtGui import QColor, QDesktopServices, QIcon  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


def find_icon() -> QIcon | None:
    """The app icon, when it is next to this script or inside the packaged app."""
    here = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    for candidate in (here / "AppIcon.icns", here / "installer" / "AppIcon.icns"):
        if candidate.is_file():
            return QIcon(str(candidate))
    return None


class _StatusLine:
    """Shows short messages in the label beside the buttons."""

    def __init__(self, label: QLabel) -> None:
        self._label = label

    def showMessage(self, text: str) -> None:  # noqa: N802 - Qt-style name
        self._label.setText(text)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(window_title())
        icon = find_icon()
        if icon is not None:
            self.setWindowIcon(icon)
        self.resize(860, 900)
        self._build_ui(icon)
        self.status_bar = _StatusLine(self.status_label)
        self.status_bar.showMessage("Choose a shots folder to begin.")
        self._apply_settings(load_settings())
        self._center_on_screen()

    def _center_on_screen(self) -> None:
        screen = self.screen()
        if screen is not None:
            area = screen.availableGeometry()
            self.move(area.center() - self.rect().center())

    # ------------------------------------------------------------------ UI

    @staticmethod
    def _heading(text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(HEADING_STYLE)
        return label

    @staticmethod
    def _hint(text: str, style: str = HINT_STYLE) -> QLabel:
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(style)
        return label

    def _build_ui(self, icon: QIcon | None) -> None:
        central = QWidget()
        central.setStyleSheet(WINDOW_STYLE)
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(18, 14, 18, 12)
        root_layout.setSpacing(8)

        root_layout.addLayout(self._build_header(icon))

        # The settings scroll, so every explanation fits on a smaller screen;
        # the results and the buttons stay in view below them.
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setSpacing(6)
        settings_layout.setContentsMargins(0, 0, 10, 0)
        self._build_source_section(settings_layout)
        self._build_shots_section(settings_layout)
        self._build_template_section(settings_layout)
        self._build_options_section(settings_layout)
        settings_layout.addStretch(1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(settings_widget)
        root_layout.addWidget(scroll, stretch=3)

        root_layout.addWidget(self._heading("RESULTS"))
        root_layout.addWidget(self._build_results(), stretch=1)
        root_layout.addLayout(self._build_button_row())

    def _build_header(self, icon: QIcon | None) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)
        if icon is not None:
            picture = QLabel()
            picture.setPixmap(icon.pixmap(40, 40))
            picture.setFixedSize(40, 40)
            row.addWidget(picture)
        titles = QVBoxLayout()
        titles.setSpacing(0)
        name = QLabel(SCRIPT_TITLE)
        name.setStyleSheet("font-size: 17px; font-weight: bold;")
        sub = QLabel("One comp per shot, with the L1 clip loaded and the frame range set.")
        sub.setStyleSheet(HINT_STYLE)
        titles.addWidget(name)
        titles.addWidget(sub)
        row.addLayout(titles)
        row.addStretch(1)
        return row

    def _build_source_section(self, layout: QVBoxLayout) -> None:
        layout.addWidget(self._heading("1  SHOTS FOLDER"))
        row = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Parent folder containing your shot subfolders…")
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self.browse_folder)
        row.addWidget(self.path_edit, stretch=1)
        row.addWidget(browse_btn)
        layout.addLayout(row)
        layout.addWidget(self._hint(
            "The folder that holds one folder per shot, e.g. Shots with ltx_sh010, "
            "ltx_sh020 … inside. Each shot folder has a source folder with its L1 clip."
        ))

    def _build_shots_section(self, layout: QVBoxLayout) -> None:
        layout.addWidget(self._heading("2  COMPS TO PUBLISH"))
        buttons = QHBoxLayout()
        scan_btn = QPushButton("Scan folder")
        scan_btn.setObjectName("smallButton")
        scan_btn.setToolTip("List the shots again (uses the folder name filter under More options).")
        scan_btn.clicked.connect(self.scan_shots)
        all_btn = QPushButton("All")
        all_btn.setObjectName("smallButton")
        all_btn.clicked.connect(lambda: self._tick_all(True))
        none_btn = QPushButton("None")
        none_btn.setObjectName("smallButton")
        none_btn.clicked.connect(lambda: self._tick_all(False))
        new_btn = QPushButton("Only without a comp")
        new_btn.setObjectName("smallButton")
        new_btn.setToolTip("Tick only the shots that do not have this version's comp yet.")
        new_btn.clicked.connect(self._tick_new_only)
        buttons.addWidget(scan_btn)
        buttons.addStretch(1)
        buttons.addWidget(all_btn)
        buttons.addWidget(none_btn)
        buttons.addWidget(new_btn)
        layout.addLayout(buttons)

        self.shot_list = QListWidget()
        self.shot_list.setFixedHeight(120)
        self.shot_list.setToolTip(
            "Only ticked shots get a comp. Shots that already have this version's comp start unticked."
        )
        layout.addWidget(self.shot_list)

    def _build_template_section(self, layout: QVBoxLayout) -> None:
        layout.addWidget(self._heading("3  TEMPLATE"))
        row = QHBoxLayout()
        self.template_edit = QLineEdit(str(DEFAULT_TEMPLATE))
        template_browse_btn = QPushButton("Browse…")
        template_browse_btn.clicked.connect(self.browse_template)
        reset_btn = QPushButton("Use default")
        reset_btn.setToolTip(f"Go back to {DEFAULT_TEMPLATE}")
        reset_btn.clicked.connect(lambda: self.template_edit.setText(str(DEFAULT_TEMPLATE)))
        row.addWidget(self.template_edit, stretch=1)
        row.addWidget(template_browse_btn)
        row.addWidget(reset_btn)
        layout.addLayout(row)
        layout.addWidget(self._hint(
            "The comp every new comp is copied from. It carries your saved Fusion layout "
            "(e.g. Mid Flow Vertical), frame format, frame rate, bit depth and path mapping. "
            "To change them, re-save this template in Fusion. No template yet? Publish or "
            "Preview offers to create a starter one."
        ))

    def _build_options_section(self, layout: QVBoxLayout) -> None:
        layout.addWidget(self._heading("4  OPTIONS"))
        grid = QGridLayout()
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(10)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        def cell(widget: QWidget, hint: str, hint_style: str = HINT_STYLE) -> QWidget:
            box = QWidget()
            col = QVBoxLayout(box)
            col.setContentsMargins(0, 0, 0, 0)
            col.setSpacing(2)
            col.addWidget(widget)
            col.addWidget(self._hint(hint, hint_style))
            return box

        def labelled(text: str, field: QWidget) -> QWidget:
            row = QWidget()
            h = QHBoxLayout(row)
            h.setContentsMargins(0, 0, 0, 0)
            h.addWidget(QLabel(text))
            h.addWidget(field, stretch=1)
            return row

        self.loader_check = QCheckBox("Load the L1 clip and set the range")
        grid.addWidget(cell(
            self.loader_check,
            "Finds the shot's L1 clip in its source folder: a movie, or an image sequence (exr, dpx, "
            "tif, jpg, png) in the <shot>_L1 folder there. The render and working ranges are set to its length.",
        ), 0, 0)

        self.tag_combo = QComboBox()
        self.tag_combo.setEditable(True)
        self.tag_combo.addItem("Auto")
        grid.addWidget(cell(
            labelled("Clip colour tag", self.tag_combo),
            "Only matters when a shot has several L1 clips, like _L1_709 and _L1_flat. Auto uses "
            "the plain _L1 clip, else the only clip, else the 709 one.",
        ), 0, 1)

        self.ref_check = QCheckBox("Also load the reference clip (_ref)")
        grid.addWidget(cell(
            self.ref_check,
            "Looks anywhere inside the shot folder, usually at the root of source, for <shot>_ref.mov "
            "(or an image sequence ending _ref). It goes in as a second Loader and never changes the range.",
        ), 1, 0)

        self.version_edit = QLineEdit("v001")
        self.version_edit.setMaximumWidth(110)
        grid.addWidget(cell(
            labelled("Version tag", self.version_edit),
            "Added to the shot name: ltx_sh120 becomes ltx_sh120_v001.comp. Use v002 for a new "
            "version beside the old comp. Empty means no version.",
        ), 1, 1)

        self.overwrite_check = QCheckBox("Replace comps that already exist")
        grid.addWidget(cell(
            self.overwrite_check,
            "Off keeps your work safe: a shot that already has this version's comp is left as it "
            "is. On replaces it with a fresh comp and your work in it is lost. Always starts off.",
            WARNING_STYLE,
        ), 2, 0)
        layout.addLayout(grid)

        # The less-used options, folded away.
        self.more_button = QToolButton()
        self.more_button.setText("More options: folder name filter, file extension, folders inside folders")
        self.more_button.setCheckable(True)
        self.more_button.setArrowType(Qt.ArrowType.RightArrow)
        self.more_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.more_button.toggled.connect(self._toggle_more)
        layout.addWidget(self.more_button)

        self.more_box = QWidget()
        more = QVBoxLayout(self.more_box)
        more.setContentsMargins(0, 0, 0, 0)
        more.setSpacing(8)

        self.pattern_edit = QLineEdit("*")
        more.addWidget(labelled("Folder name filter", self.pattern_edit))
        more.addWidget(self._hint(
            "Only folders whose name matches get a comp. * means any characters, so a single * "
            "means every folder. ltx_sh* means names starting with ltx_sh; *_010 means names ending "
            "in _010; sh0?0 uses ? for any one character."
        ))
        self.ext_edit = QLineEdit(".comp")
        self.ext_edit.setMaximumWidth(200)
        more.addWidget(labelled("File extension", self.ext_edit))
        more.addWidget(self._hint("The end of the comp's file name. Leave it as .comp for Fusion."))
        self.recursive_check = QCheckBox("Include folders inside folders")
        more.addWidget(self.recursive_check)
        more.addWidget(self._hint(
            "Off: only the folders directly inside your shots folder get a comp. On: every folder at "
            "any depth does, including source folders, so leave it off for a normal shots folder."
        ))
        self.more_box.setVisible(False)
        layout.addWidget(self.more_box)

    def _toggle_more(self, open_: bool) -> None:
        self.more_button.setArrowType(Qt.ArrowType.DownArrow if open_ else Qt.ArrowType.RightArrow)
        self.more_box.setVisible(open_)

    def _build_results(self) -> QWidget:
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Status", "Comp", "Clips"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setMinimumHeight(120)
        self.table.setToolTip("Double-click a row to reveal that folder in the Finder.")
        self.table.doubleClicked.connect(self.reveal_selected_row)
        return self.table

    def _build_button_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 6, 0, 0)

        self.preview_btn = QPushButton("Preview")
        self.preview_btn.setToolTip("Show what would happen without writing any files.")
        self.preview_btn.clicked.connect(lambda: self.run(dry_run=True))

        self.status_label = QLabel("")
        self.status_label.setStyleSheet(HINT_STYLE)

        # Cancel until the window has written something, Close after that.
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.close)

        self.publish_btn = QPushButton("Publish")
        self.publish_btn.setObjectName("mainButton")
        self.publish_btn.setDefault(True)
        self.publish_btn.setToolTip("Write the comp files to disk.")
        self.publish_btn.clicked.connect(lambda: self.run(dry_run=False))

        row.addWidget(self.preview_btn)
        row.addSpacing(10)
        row.addWidget(self.status_label, stretch=1)
        row.addWidget(self.cancel_btn)
        row.addWidget(self.publish_btn)
        return row

    # ------------------------------------------------------------ settings

    def _apply_settings(self, settings: dict) -> None:
        self.path_edit.setText(settings["source_folder"])
        template = settings["template"]
        if not template or Path(template) == SYSTEM_TEMPLATE:
            template = str(DEFAULT_TEMPLATE)   # empty, or the old system-wide default
        self.template_edit.setText(template)
        self.recursive_check.setChecked(settings["recursive"])
        self.pattern_edit.setText(settings["pattern"])
        self.ext_edit.setText(settings["extension"])
        self.version_edit.setText(settings["version_tag"])
        self.loader_check.setChecked(settings["add_loader"])
        self.ref_check.setChecked(settings["add_ref"])
        self.tag_combo.setCurrentText(settings["clip_tag"] or "Auto")
        # Show the folded options when they hold something other than the defaults.
        if settings["recursive"] or settings["pattern"] != "*" or settings["extension"] != ".comp":
            self.more_button.setChecked(True)
        if settings["source_folder"]:
            self.scan_shots()
            self.status_bar.showMessage("Settings from last time restored.")

    def _current_settings(self) -> dict:
        return {
            "source_folder": self.path_edit.text().strip(),
            "template": self.template_edit.text().strip(),
            "recursive": self.recursive_check.isChecked(),
            "pattern": self.pattern_edit.text().strip() or "*",
            "extension": self.ext_edit.text().strip() or ".comp",
            "version_tag": self.version_edit.text().strip(),
            "add_loader": self.loader_check.isChecked(),
            "clip_tag": self._clip_tag(),
            "add_ref": self.ref_check.isChecked(),
        }

    def _clip_tag(self) -> str:
        text = self.tag_combo.currentText().strip()
        return "" if text.lower() == "auto" else text

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt method name
        save_settings(self._current_settings())
        super().closeEvent(event)

    # ------------------------------------------------------------- actions

    def browse_folder(self) -> None:
        start_dir = self.path_edit.text().strip() or str(Path.home())
        directory = QFileDialog.getExistingDirectory(self, "Select Shots Folder", start_dir)
        if directory:
            self.path_edit.setText(directory)
            self.scan_shots()

    # --------------------------------------------------------------- shots

    def _comp_options(self) -> tuple[str, str]:
        extension = self.ext_edit.text().strip() or ".comp"
        if not extension.startswith("."):
            extension = f".{extension}"
        return self.version_edit.text().strip(), extension

    def scan_shots(self) -> None:
        """List the shot folders with a tick box; shots with a comp start unticked."""
        self.shot_list.clear()
        root = self._resolved_root()
        if root is None:
            return
        version, extension = self._comp_options()
        try:
            folders = find_target_folders(
                root, self.recursive_check.isChecked(), self.pattern_edit.text().strip() or "*"
            )
        except OSError as exc:
            self.status_bar.showMessage(f"Could not read the folder: {exc}")
            return

        tags: set[str] = set()
        for folder in folders:
            has_comp = comp_path_for(folder, version, extension).exists()
            item = QListWidgetItem(folder.name + ("   (comp exists)" if has_comp else ""))
            item.setData(Qt.ItemDataRole.UserRole, folder.name)
            item.setData(Qt.ItemDataRole.UserRole + 1, has_comp)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked if has_comp else Qt.CheckState.Checked)
            if has_comp:
                item.setForeground(QColor(STATUS_COLORS["skipped"]))
            self.shot_list.addItem(item)
            try:
                tags.update(tag for _, tag in find_clips(folder) if tag)
            except OSError:
                pass

        current = self.tag_combo.currentText()
        self.tag_combo.clear()
        self.tag_combo.addItem("Auto")
        self.tag_combo.addItems(sorted(tags))
        self.tag_combo.setCurrentText(current or "Auto")
        self.status_bar.showMessage(f"{len(folders)} shot folder(s) found.")

    def _tick_all(self, ticked: bool) -> None:
        state = Qt.CheckState.Checked if ticked else Qt.CheckState.Unchecked
        for i in range(self.shot_list.count()):
            self.shot_list.item(i).setCheckState(state)

    def _tick_new_only(self) -> None:
        for i in range(self.shot_list.count()):
            item = self.shot_list.item(i)
            has_comp = item.data(Qt.ItemDataRole.UserRole + 1)
            item.setCheckState(Qt.CheckState.Unchecked if has_comp else Qt.CheckState.Checked)

    def _ticked_shots(self) -> set[str]:
        return {
            self.shot_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.shot_list.count())
            if self.shot_list.item(i).checkState() == Qt.CheckState.Checked
        }

    def browse_template(self) -> None:
        start_dir = self.template_edit.text().strip() or str(Path.home())
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Template Comp", start_dir, "Fusion Comp (*.comp);;All Files (*)"
        )
        if file_path:
            self.template_edit.setText(file_path)

    def reveal_selected_row(self, index) -> None:
        path_item = self.table.item(index.row(), 1)
        if path_item is None:
            return
        path = Path(path_item.data(Qt.ItemDataRole.UserRole) or path_item.text())
        target = path.parent if path.parent.exists() else path
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))

    def _resolved_root(self, show_error: bool = False) -> Path | None:
        text = self.path_edit.text().strip()
        if not text:
            if show_error:
                QMessageBox.warning(
                    self, f"{window_title()}: No Folder Selected", "Please choose a shots folder first."
                )
            return None

        root = Path(text).expanduser()
        if not root.is_dir():
            if show_error:
                QMessageBox.critical(
                    self, f"{window_title()}: Invalid Folder", f"'{root}' is not a valid directory."
                )
            return None
        return root

    def _offer_starter_template(self, template: Path) -> bool:
        """The template is missing: offer to create a starter one. True if there is one now."""
        answer = QMessageBox.question(
            self,
            f"{window_title()}: No Template Yet",
            f"There is no template comp at:\n{template}\n\n"
            "Every new comp is copied from the template. Create a starter template there now?\n\n"
            "It is a plain comp (frames 1001 to 1100) that uses Fusion's default layout and "
            "settings. To make it yours later, open it in Fusion, set up your layout and "
            "preferences, and save it over the same file.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return False
        try:
            _engine.create_starter_template(template)
        except OSError as exc:
            QMessageBox.critical(self, f"{window_title()}: Could Not Create", str(exc))
            return False
        self.status_bar.showMessage(f"Starter template created: {template}")
        return True

    def run(self, dry_run: bool) -> None:
        root = self._resolved_root(show_error=True)
        if root is None:
            return
        save_settings(self._current_settings())

        pattern = self.pattern_edit.text().strip() or "*"
        version, extension = self._comp_options()

        if self.shot_list.count() == 0:
            self.scan_shots()
        shots = self._ticked_shots()
        if not shots:
            QMessageBox.information(
                self, window_title(), "No comps are ticked. Tick the shots to publish."
            )
            return

        template = Path(self.template_edit.text().strip() or str(DEFAULT_TEMPLATE)).expanduser()
        if not template.is_file() and not self._offer_starter_template(template):
            return

        try:
            summary = publish_comps(
                root=root,
                recursive=self.recursive_check.isChecked(),
                overwrite=self.overwrite_check.isChecked(),
                dry_run=dry_run,
                pattern=pattern,
                version=version,
                extension=extension,
                template=template,
                add_loader=self.loader_check.isChecked(),
                clip_tag=self._clip_tag(),
                only=shots,
                add_ref=self.ref_check.isChecked(),
            )
        except ValueError as exc:   # an option that is not plain file-name text
            QMessageBox.warning(self, f"{window_title()}: Check Your Options", str(exc))
            return
        except Exception as exc:  # noqa: BLE001 - surface any unexpected failure to the user
            QMessageBox.critical(self, f"{window_title()}: Unexpected Error", str(exc))
            return

        self._populate_table(summary, dry_run=dry_run)
        if not dry_run and (summary.created or summary.overwritten):
            self.cancel_btn.setText("Close")   # it can no longer cancel anything

    # -------------------------------------------------------------- output

    def _short_path(self, path: Path) -> str:
        """The path from the shots folder (shot/shot_v001.comp), or the full path."""
        root = self._resolved_root()
        try:
            return str(path.relative_to(root)) if root else str(path)
        except ValueError:
            return str(path)

    def _populate_table(self, summary: PublishSummary, dry_run: bool) -> None:
        created_label = "Would create" if dry_run else "Created"
        overwritten_label = "Would overwrite" if dry_run else "Overwritten"

        entries: list[tuple[str, Path, str, str | None]] = []
        entries += [(created_label, p, STATUS_COLORS["created"], None) for p in summary.created]
        entries += [(overwritten_label, p, STATUS_COLORS["overwritten"], None) for p in summary.overwritten]
        entries += [("Skipped (exists)", p, STATUS_COLORS["skipped"], None) for p in summary.skipped]
        entries += [("Error", p, STATUS_COLORS["error"], msg) for p, msg in summary.errored]
        entries.sort(key=lambda e: str(e[1]))

        self.table.setRowCount(len(entries))
        for row, (status, path, color, tooltip) in enumerate(entries):
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor(color))
            path_item = QTableWidgetItem(self._short_path(path))
            path_item.setData(Qt.ItemDataRole.UserRole, str(path))   # full path, for reveal
            path_item.setToolTip(str(path))
            if tooltip:
                status_item.setToolTip(tooltip)
                path_item.setToolTip(tooltip)
            self.table.setItem(row, 0, status_item)
            self.table.setItem(row, 1, path_item)
            self.table.setItem(row, 2, QTableWidgetItem(summary.notes.get(path, "")))

        total_written = len(summary.created) + len(summary.overwritten)
        verb = "would be written" if dry_run else "written"
        if entries:
            message = (
                f"{total_written} comp file(s) {verb}, "
                f"{len(summary.skipped)} skipped, {len(summary.errored)} error(s)."
            )
        else:
            message = "No matching subfolders found."
        self.status_bar.showMessage(message)
        if not dry_run:
            self.scan_shots()
            self.status_bar.showMessage(message)


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Qt's built-in "Fusion" widget style, unrelated to Blackmagic Fusion
    app.setApplicationName(SCRIPT_TITLE)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
