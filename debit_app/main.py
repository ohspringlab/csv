"""
Entry point for Gestionnaire de Débit - Meubles.
"""

import sys
import os

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from ui.main_window import MainWindow


STYLESHEET = """
/* ════════════════════════════════════════════
   Gestionnaire de Débit  —  Premium Dark Theme
   ════════════════════════════════════════════ */

/* ── Global reset ── */
* {
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 10pt;
    color: #CBD5E1;
}

/* ── Main window ── */
QMainWindow {
    background-color: #080E1C;
}
QWidget {
    background-color: #080E1C;
}

/* ── Menu bar ── */
QMenuBar {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #0F1F3D, stop:1 #080E1C);
    color: #CBD5E1;
    padding: 2px 0;
    font-size: 10pt;
    font-weight: 600;
    border-bottom: 2px solid #38BDF8;
}
QMenuBar::item {
    background: transparent;
    padding: 6px 16px;
    color: #CBD5E1;
    border-radius: 6px;
}
QMenuBar::item:selected {
    background-color: rgba(56,189,248,0.18);
    color: #38BDF8;
}
QMenu {
    background-color: #0F1F3D;
    border: 1px solid rgba(56,189,248,0.28);
    border-radius: 10px;
    padding: 6px 4px;
}
QMenu::item {
    padding: 8px 24px 8px 16px;
    border-radius: 6px;
    color: #CBD5E1;
}
QMenu::item:selected {
    background: rgba(56,189,248,0.15);
    color: #38BDF8;
}
QMenu::separator {
    height: 1px;
    background: rgba(56,189,248,0.14);
    margin: 5px 12px;
}

/* ── Toolbar ── */
QToolBar {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #0F1F3D, stop:1 #080E1C);
    border: none;
    border-bottom: 3px solid transparent;
    border-image: none;
    spacing: 8px;
    padding: 7px 10px;
}
QToolBar::separator {
    width: 1px;
    background: rgba(56,189,248,0.20);
    margin: 5px 8px;
}
/* Individual button colors set programmatically in main_window.py */

/* ── Status bar ── */
QStatusBar {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #0F1F3D, stop:1 #080E1C);
    color: #64748B;
    border-top: 2px solid rgba(56,189,248,0.30);
    font-size: 9pt;
    padding: 3px 10px;
}
QStatusBar QLabel { color: #64748B; }

/* ── Table ── */
QTableWidget {
    background-color: #0A1420;
    gridline-color: rgba(255,255,255,0.06);
    selection-background-color: rgba(56,189,248,0.18);
    selection-color: #38BDF8;
    border: 1px solid rgba(56,189,248,0.20);
    border-radius: 8px;
    font-size: 10pt;
    alternate-background-color: #0C1A2C;
}
QTableWidget::item { padding: 2px 4px; }
QHeaderView::section {
    background: #0F1F3D;
    color: #94A3B8;
    border: none;
    padding: 4px 8px;
    font-weight: 700;
}

/* ── Scroll bars ── */
QScrollBar:horizontal {
    background: rgba(255,255,255,0.04);
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: rgba(56,189,248,0.40);
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: rgba(56,189,248,0.70); }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QScrollBar:vertical {
    background: rgba(255,255,255,0.04);
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: rgba(56,189,248,0.40);
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: rgba(56,189,248,0.70); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Push buttons ── */
QPushButton {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #0F766E, stop:0.5 #2563EB, stop:1 #7C3AED);
    color: #FFFFFF;
    border: 1px solid rgba(56,189,248,0.28);
    border-radius: 8px;
    padding: 7px 18px;
    font-size: 10pt;
    font-weight: 700;
}
QPushButton:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #14B8A6, stop:0.5 #3B82F6, stop:1 #8B5CF6);
    border-color: rgba(56,189,248,0.55);
}
QPushButton:pressed {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #0D5B52, stop:0.5 #1D4ED8, stop:1 #6D28D9);
}
QPushButton:disabled {
    background: rgba(100,116,139,0.30);
    color: #475569;
    border-color: rgba(100,116,139,0.20);
}

/* ── Line edit ── */
QLineEdit {
    background: rgba(15,31,61,0.80);
    border: 1px solid rgba(56,189,248,0.28);
    border-radius: 8px;
    padding: 6px 10px;
    color: #E2E8F0;
    font-size: 10pt;
    selection-background-color: rgba(56,189,248,0.30);
}
QLineEdit:focus {
    border-color: #38BDF8;
    background: rgba(15,31,61,0.95);
}
QLineEdit::placeholder { color: #475569; }

/* ── List widget ── */
QListWidget {
    background: rgba(15,31,61,0.80);
    border: 1px solid rgba(56,189,248,0.22);
    border-radius: 10px;
    font-size: 10pt;
    color: #CBD5E1;
    padding: 4px;
}
QListWidget::item {
    padding: 7px 12px;
    border-radius: 6px;
    color: #CBD5E1;
}
QListWidget::item:selected {
    background: rgba(56,189,248,0.18);
    color: #38BDF8;
}
QListWidget::item:alternate {
    background: rgba(255,255,255,0.03);
}

/* ── Dialog ── */
QDialog {
    background: #080E1C;
    border: 1px solid rgba(56,189,248,0.22);
    border-radius: 14px;
}

/* ── Message box ── */
QMessageBox {
    background: #0F1F3D;
    color: #CBD5E1;
}
QMessageBox QLabel { color: #CBD5E1; }
QMessageBox QPushButton {
    min-width: 90px;
}

/* ── Frame ── */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {
    color: rgba(56,189,248,0.18);
}

/* ── Tooltip ── */
QToolTip {
    background: #0F1F3D;
    color: #CBD5E1;
    border: 1px solid rgba(56,189,248,0.35);
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 9pt;
}
"""


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark palette so native widgets inherit the theme
    from PyQt6.QtGui import QPalette, QColor
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor("#080E1C"))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor("#CBD5E1"))
    palette.setColor(QPalette.ColorRole.Base,            QColor("#0A1420"))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor("#0C1A2C"))
    palette.setColor(QPalette.ColorRole.ToolTipBase,     QColor("#0F1F3D"))
    palette.setColor(QPalette.ColorRole.ToolTipText,     QColor("#CBD5E1"))
    palette.setColor(QPalette.ColorRole.Text,            QColor("#CBD5E1"))
    palette.setColor(QPalette.ColorRole.Button,          QColor("#0F1F3D"))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor("#E2E8F0"))
    palette.setColor(QPalette.ColorRole.BrightText,      QColor("#38BDF8"))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor("#1D4ED8"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Link,            QColor("#38BDF8"))
    app.setPalette(palette)

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    app.setStyleSheet(STYLESHEET)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
