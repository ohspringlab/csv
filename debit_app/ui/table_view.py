"""
Custom table widget for displaying cabinet cut list data.
"""

import os
from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QLabel, QWidget, QHBoxLayout, QFrame,
    QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QBrush

from core.parser import decimal_to_fraction_str
from ui.theme_dialog import DEFAULT_THEME, FONT_OPTIONS, normalized_theme


# Cyclic accent colors for group headers (dark-theme neons)
GROUP_COLORS = [
    "#0E2A4A",  # deep teal-navy
    "#130A2E",  # deep indigo
    "#2A0E1A",  # deep rose
    "#0A2A1A",  # deep emerald
    "#2A1A06",  # deep amber
    "#1A0A2A",  # deep purple
    "#062A2A",  # deep cyan
    "#2A1206",  # deep orange
]
GROUP_ACCENTS = [
    "#38BDF8",  # sky
    "#818CF8",  # indigo
    "#F472B6",  # pink
    "#34D399",  # emerald
    "#FB923C",  # orange
    "#A78BFA",  # violet
    "#2DD4BF",  # teal
    "#F87171",  # red
]
GROUP_TEXT   = "#E2E8F0"
SUB_HDR_TEXT = "#94A3B8"
CAB_COL_BG   = "#081428"
CAB_COL_TEXT = "#38BDF8"
EMPTY_BG     = "#0A1420"


def _fmt(value) -> str:
    if value == "" or value is None:
        return ""
    if isinstance(value, float):
        return decimal_to_fraction_str(value)
    return str(value)


def _dimension_str(width, length) -> str:
    if width == "" or length == "" or width is None or length is None:
        return ""
    return f"{_fmt(width)} x {_fmt(length)}"


def _piece_entries(row_data: dict, piece_name: str) -> list:
    entries = row_data.get(f"{piece_name}_entries", [])
    if entries:
        return entries

    qty = row_data.get(f"{piece_name}_qty", "")
    if qty == "":
        return []

    return [{
        "qty": qty,
        "width": row_data.get(f"{piece_name}_w", ""),
        "length": row_data.get(f"{piece_name}_l", ""),
        "source_color": row_data.get(f"{piece_name}_color", "#FFFFFF"),
    }]


def _entries_color(entries: list, is_odd: bool) -> QColor:
    colors = {
        entry.get("source_color", "#FFFFFF")
        for entry in entries
        if entry.get("source_color")
    }
    colors.discard("#FFFFFF")

    if not colors:
        bg = QColor(EMPTY_BG if not is_odd else "#0C1A2C")
    elif len(colors) == 1:
        bg = QColor(next(iter(colors)))
    else:
        bg = QColor("#FFE8CC")

    if is_odd and bool(colors):
        h, s, v, a = bg.getHsv()
        bg.setHsv(h, min(255, s + 10), max(0, v - 12), a)

    return bg


class CutListTable(QTableWidget):
    """
    Preview table with one furniture row and two subcolumns per part:
    quantity and combined fractional dimensions.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.piece_names = []
        self.pivot_data = []
        self.theme = DEFAULT_THEME.copy()
        self.labels = {
            "cabinet": "MEUBLE",
            "qty": "Qté",
            "dimensions": "Dimensions",
        }
        self._setup_appearance()

    def _setup_appearance(self):
        primary = self.theme["primary"]
        radius = self.theme["radius"]
        font_family = FONT_OPTIONS[self.theme["font_family"]][1]
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(False)
        self.setShowGrid(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().hide()
        self.horizontalHeader().setStretchLastSection(False)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setFont(QFont(font_family.split(",")[0].strip('" '), 10))

        self.setStyleSheet(f"""
            QTableWidget {
                background-color: #0A1420;
                gridline-color: rgba(255,255,255,0.06);
                selection-background-color: {primary};
                selection-color: #FFFFFF;
                border: 1px solid {primary};
                border-radius: {radius}px;
                font-family: {font_family};
                font-size: 10pt;
                color: #CBD5E1;
            }
            QTableWidget::item { padding: 2px 5px; }
            QScrollBar:horizontal {
                background: rgba(255,255,255,0.04);
                height: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal {
                background: {primary};
                border-radius: 4px;
                min-width: 30px;
            }
            QScrollBar::handle:horizontal:hover { background: {self.theme["secondary"]}; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
            QScrollBar:vertical {
                background: rgba(255,255,255,0.04);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: {primary};
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: {self.theme["secondary"]}; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

    def set_theme(self, theme: dict):
        self.theme = normalized_theme(theme)
        self._setup_appearance()
        if self.pivot_data and self.piece_names:
            self.load_data(self.pivot_data, self.piece_names)

    def set_labels(self, labels: dict):
        self.labels = {
            "cabinet": labels.get("cabinet", self.labels["cabinet"]),
            "qty": labels.get("qty", self.labels["qty"]),
            "dimensions": labels.get("dimensions", self.labels["dimensions"]),
        }
        if self.pivot_data and self.piece_names:
            self.load_data(self.pivot_data, self.piece_names)

    def load_data(self, pivot_data: list, piece_names: list):
        self.pivot_data = pivot_data
        self.piece_names = piece_names

        self.clear()
        self.setRowCount(0)
        self.setColumnCount(0)

        if not piece_names:
            return

        total_rows = 2 + len(pivot_data)
        self.setColumnCount(1 + 2 * len(piece_names))
        self.setRowCount(total_rows)

        self._set_header_row_0()
        self._set_header_row_1()

        for row_idx, row_data in enumerate(pivot_data):
            table_row = row_idx + 2
            self._fill_data_row(table_row, row_data, row_idx % 2 == 1)

        self.setColumnWidth(0, 88)
        col = 1
        for _ in piece_names:
            self.setColumnWidth(col, 42)
            self.setColumnWidth(col + 1, 145)
            col += 2

        self.setRowHeight(0, 32)
        self.setRowHeight(1, 22)
        for row_idx, row_data in enumerate(pivot_data, start=2):
            max_lines = max(
                [1] + [len(_piece_entries(row_data, pname)) for pname in piece_names]
            )
            self.setRowHeight(row_idx, 24 * max_lines)

    def _grp_color(self, idx: int) -> str:
        return GROUP_COLORS[idx % len(GROUP_COLORS)]

    def _grp_accent(self, idx: int) -> str:
        return GROUP_ACCENTS[idx % len(GROUP_ACCENTS)]

    def _make_item(self, text: str, bg: str, fg: str = "#E2E8F0",
                   bold: bool = True, size: int = 10,
                   align=Qt.AlignmentFlag.AlignCenter,
                   editable: bool = False) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(align)
        font_family = FONT_OPTIONS[self.theme["font_family"]][1].split(",")[0].strip('" ')
        font = QFont(font_family, size)
        font.setBold(bold)
        item.setFont(font)
        item.setBackground(QBrush(QColor(bg)))
        item.setForeground(QBrush(QColor(fg)))
        if not editable:
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        return item

    def _set_header_row_0(self):
        self.setItem(0, 0,
            self._make_item(self.labels["cabinet"], CAB_COL_BG, self.theme["primary"], bold=True, size=10))

        col = 1
        for i, pname in enumerate(self.piece_names):
            bg = self._grp_color(i)
            accent = self._grp_accent(i)
            self.setItem(0, col,
                self._make_item(pname, bg, accent, bold=True, size=10))
            self.setItem(0, col + 1, self._make_item("", bg, accent))
            self.setSpan(0, col, 1, 2)
            col += 2

    def _set_header_row_1(self):
        self.setItem(1, 0, self._make_item("", self._grp_color(0), SUB_HDR_TEXT))

        col = 1
        for i in range(len(self.piece_names)):
            bg = self._grp_color(i)
            accent = self._grp_accent(i)

            for label in [self.labels["qty"], self.labels["dimensions"]]:
                self.setItem(1, col,
                    self._make_item(label, bg, SUB_HDR_TEXT, bold=True, size=9))
                col += 1

    def _fill_data_row(self, table_row: int, row_data: dict, is_odd: bool):
        cab_item = self._make_item(
            str(row_data.get("cabinet_id", "")),
            "#081428", self.theme["primary"], bold=True, size=10,
            editable=False
        )
        self.setItem(table_row, 0, cab_item)

        col = 1
        for pname in self.piece_names:
            entries = _piece_entries(row_data, pname)
            bg = _entries_color(entries, is_odd) if entries else QColor(EMPTY_BG)
            brush = QBrush(bg)
            # Decide text color: light text on dark cells, dark text on light cells
            brightness = (bg.red() * 299 + bg.green() * 587 + bg.blue() * 114) // 1000
            fg_hex = self.theme["table_font_color"] if brightness > 140 else self.theme["font_color"]

            values = [
                "\n".join(_fmt(entry.get("qty", "")) for entry in entries),
                "\n".join(
                    _dimension_str(entry.get("width", ""), entry.get("length", ""))
                    for entry in entries
                ),
            ]

            for text in values:
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setBackground(brush)
                item.setForeground(QBrush(QColor(fg_hex)))
                if text:
                    font_family = FONT_OPTIONS[self.theme["font_family"]][1].split(",")[0].strip('" ')
                    font = QFont(font_family, 10)
                    font.setBold(False)
                    item.setFont(font)
                self.setItem(table_row, col, item)
                col += 1

    def clear_data(self):
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(0)
        self.pivot_data = []
        self.piece_names = []


def build_color_legend(file_list: list) -> QWidget:
    widget = QWidget()
    widget.setStyleSheet("background: transparent;")
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(4, 2, 4, 2)
    layout.setSpacing(14)

    if not file_list:
        label = QLabel("Aucun fichier chargé")
        label.setStyleSheet("color: #334155; font-style: italic; font-size: 9pt;")
        layout.addWidget(label)
    else:
        title = QLabel("📁  Fichiers :")
        title.setStyleSheet("font-weight: 700; color: #38BDF8; font-size: 9pt;")
        layout.addWidget(title)

        for filepath, color_hex in file_list:
            swatch = QFrame()
            swatch.setFixedSize(22, 14)
            swatch.setStyleSheet(
                f"background-color:{color_hex};"
                "border:1px solid rgba(56,189,248,0.40); border-radius:7px;"
            )
            fname = os.path.splitext(os.path.basename(filepath))[0]
            lbl = QLabel(fname)
            lbl.setStyleSheet("font-size:9pt; font-weight:700; color:#CBD5E1;")
            layout.addWidget(swatch)
            layout.addWidget(lbl)

    layout.addStretch()
    return widget
