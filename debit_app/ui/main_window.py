"""
Main application window for Gestionnaire de Débit - Meubles.
"""

import os
import sys
import json
import shutil

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFileDialog, QMessageBox, QStatusBar, QToolBar,
    QScrollArea, QFrame, QSizePolicy, QApplication, QSpacerItem
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QFont, QColor, QLinearGradient, QPalette

from core.parser import parse_csv_file, FILE_COLORS
from core.transformer import transform
from core.exporter import export_excel, export_csv
from ui.table_view import CutListTable
from ui.config_dialog import NomenclatureDialog
from ui.theme_dialog import ThemeDialog, DEFAULT_THEME, FONT_OPTIONS, normalized_theme
from ui.animated_widgets import AnimatedBackground, HeroHeader, GradientAccentBar, LegendCard


def _get_config_path() -> str:
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "config", "nomenclature.json")


def _get_theme_path() -> str:
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "config", "theme.json")


def _get_preferences_path() -> str:
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "config", "preferences.json")


def _get_bundled_config_path() -> str:
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS  # type: ignore
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "config", "nomenclature.json")


DEFAULT_PIECE_NAMES = [
    "DOS", "PIGNON (L)", "PIGNON (R)", "DESSUS/DESSOUS",
    "TAB FIXE", "TAB AJUST", "Front Stretcher", "Rear Stretcher",
    "Drw Stretcher", "Front Toe", "Side Toe", "Drw Bottom",
    "Drw L Side", "Drw R Side", "Drw Front", "Drw Back",
    "Door", "Door(L)", "Door(R)", "Drawer", "Stile", "Toe Skin"
]

TRANSLATIONS = {
    "fr": {
        "window_title": "Gestionnaire de Débit — Meubles",
        "app_title": "Gestionnaire de Débit",
        "app_subtitle": "Import CSV  ·  aperçu trié  ·  export Excel / CSV",
        "file_menu": "  Fichier  ",
        "config_menu": "  Configuration  ",
        "help_menu": "  Aide  ",
        "import_menu": "  Importer CSV...",
        "export_excel_menu": "  Exporter Excel...",
        "export_csv_menu": "  Exporter CSV...",
        "clear_menu": "  Effacer tout",
        "quit_menu": "  Quitter",
        "nomenclature_menu": "  Nomenclature...",
        "theme_menu": "  Thème...",
        "language_menu": "  Langue: Français",
        "about_menu": "  A propos...",
        "import_btn": "＋  Importer CSV",
        "clear_btn": "✕  Effacer tout",
        "excel_btn": "⬇  Excel",
        "csv_btn": "⬇  CSV",
        "nomenclature_btn": "⚙  Nomenclature",
        "theme_btn": "🎨  Thème",
        "language_btn": "🌐  Français",
        "loaded_files": "📁  FICHIERS CHARGÉS",
        "no_files": "Aucun fichier chargé — utilisez  ＋ Importer CSV",
        "status_empty": "●  Prêt  |  Aucun fichier chargé",
        "status_loaded": "●  {files} fichier(s) chargé(s)   |   {cabinets} meuble(s) affichés",
        "cabinet": "MEUBLE",
        "qty": "Qté",
        "dimensions": "Dimensions",
        "theme_saved_title": "Thème sauvegardé",
        "theme_saved_msg": "Le thème du bureau a été mis à jour.",
        "language_saved_title": "Langue mise à jour",
        "language_saved_msg": "La langue du bureau est maintenant le français.",
    },
    "en": {
        "window_title": "Cut List Manager — Cabinets",
        "app_title": "Cut List Manager",
        "app_subtitle": "CSV import  ·  sorted preview  ·  Excel / CSV export",
        "file_menu": "  File  ",
        "config_menu": "  Configuration  ",
        "help_menu": "  Help  ",
        "import_menu": "  Import CSV...",
        "export_excel_menu": "  Export Excel...",
        "export_csv_menu": "  Export CSV...",
        "clear_menu": "  Clear all",
        "quit_menu": "  Quit",
        "nomenclature_menu": "  Nomenclature...",
        "theme_menu": "  Theme...",
        "language_menu": "  Language: English",
        "about_menu": "  About...",
        "import_btn": "＋  Import CSV",
        "clear_btn": "✕  Clear all",
        "excel_btn": "⬇  Excel",
        "csv_btn": "⬇  CSV",
        "nomenclature_btn": "⚙  Nomenclature",
        "theme_btn": "🎨  Theme",
        "language_btn": "🌐  English",
        "loaded_files": "📁  LOADED FILES",
        "no_files": "No file loaded — use  ＋ Import CSV",
        "status_empty": "●  Ready  |  No file loaded",
        "status_loaded": "●  {files} file(s) loaded   |   {cabinets} cabinet(s) shown",
        "cabinet": "CABINET",
        "qty": "Qty",
        "dimensions": "Dimensions",
        "theme_saved_title": "Theme saved",
        "theme_saved_msg": "The desktop theme has been updated.",
        "language_saved_title": "Language updated",
        "language_saved_msg": "Desktop language is now English.",
    },
}

# Toolbar button styles by type
BTN_IMPORT  = "background-color:#27AE60; border-color:rgba(255,255,255,0.3);"
BTN_CLEAR   = "background-color:#C0392B; border-color:rgba(255,255,255,0.3);"
BTN_EXCEL   = "background-color:#1E7E34; border-color:rgba(255,255,255,0.3);"
BTN_CSV     = "background-color:#17A589; border-color:rgba(255,255,255,0.3);"
BTN_CONFIG  = "background-color:#8E44AD; border-color:rgba(255,255,255,0.3);"

TOOLBAR_BTN_BASE = """
    QToolButton {{
        {extra}
        color: #FFFFFF;
        border: 1px solid rgba(255,255,255,0.25);
        border-radius: 6px;
        padding: 6px 16px;
        font-size: 10pt;
        font-weight: 700;
    }}
    QToolButton:hover {{
        filter: brightness(1.15);
        border-color: rgba(255,255,255,0.55);
    }}
    QToolButton:pressed {{
        filter: brightness(0.85);
    }}
"""


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestionnaire de Débit — Meubles")
        self.setMinimumSize(1100, 660)
        self.resize(1450, 780)

        self.config_path = _get_config_path()
        self.theme_path = _get_theme_path()
        self.preferences_path = _get_preferences_path()
        self.piece_names = self._load_piece_names()
        self.theme = self._load_theme()
        self.language = self._load_language()
        self._toolbar_buttons = []
        self._toolbar_button_refs = {}
        self._actions = {}

        self.imported_files: list = []
        self.all_rows: list = []
        self.pivot_data: list = []

        self._init_ui()
        self._update_status()

    def _apply_window_style(self):
        """Apply gradient accent line under toolbar via window palette."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #080E1C;
            }
        """)

    def resizeEvent(self, event):
        """Keep toolbar accent bar positioned just below the toolbar."""
        super().resizeEvent(event)
        self._reposition_accent()

    def showEvent(self, event):
        super().showEvent(event)
        self._reposition_accent()

    def _reposition_accent(self):
        if not hasattr(self, '_toolbar_accent'):
            return
        from PyQt6.QtWidgets import QToolBar
        toolbars = self.findChildren(QToolBar)
        if toolbars:
            geo = toolbars[0].geometry()
            self._toolbar_accent.setGeometry(
                geo.x(), geo.y() + geo.height(),
                geo.width(), 3
            )
            self._toolbar_accent.raise_()

    # ── Nomenclature ──────────────────────────────────────────────────

    def _load_piece_names(self) -> list:
        bundled_config = _get_bundled_config_path()
        if not os.path.exists(self.config_path) and bundled_config != self.config_path:
            try:
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                shutil.copyfile(bundled_config, self.config_path)
            except Exception:
                pass

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                names = data.get("piece_names", [])
                if names:
                    return names
            except Exception:
                pass
        return DEFAULT_PIECE_NAMES[:]

    # ── Theme ────────────────────────────────────────────────────────

    def _load_theme(self) -> dict:
        if os.path.exists(self.theme_path):
            try:
                with open(self.theme_path, "r", encoding="utf-8") as f:
                    return normalized_theme(json.load(f))
            except Exception:
                pass
        return DEFAULT_THEME.copy()

    def _save_theme(self):
        try:
            os.makedirs(os.path.dirname(self.theme_path), exist_ok=True)
            with open(self.theme_path, "w", encoding="utf-8") as f:
                json.dump(self.theme, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(
                self, "Erreur",
                f"Impossible de sauvegarder le thème:\n{e}"
            )

    def _load_language(self) -> str:
        if os.path.exists(self.preferences_path):
            try:
                with open(self.preferences_path, "r", encoding="utf-8") as f:
                    language = json.load(f).get("language", "fr")
                if language in TRANSLATIONS:
                    return language
            except Exception:
                pass
        return "fr"

    def _save_language(self):
        try:
            os.makedirs(os.path.dirname(self.preferences_path), exist_ok=True)
            with open(self.preferences_path, "w", encoding="utf-8") as f:
                json.dump({"language": self.language}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(
                self, "Erreur",
                f"Impossible de sauvegarder la langue:\n{e}"
            )

    def _tr(self, key: str) -> str:
        return TRANSLATIONS.get(self.language, TRANSLATIONS["fr"]).get(key, key)

    def _table_labels(self) -> dict:
        return {
            "cabinet": self._tr("cabinet"),
            "qty": self._tr("qty"),
            "dimensions": self._tr("dimensions"),
        }

    def _button_qss(self) -> str:
        primary = self.theme["primary"]
        secondary = self.theme["secondary"]
        radius = max(4, int(self.theme["radius"]) - 4)
        font_family = FONT_OPTIONS[self.theme["font_family"]][1]

        if self.theme["button_style"] == "solid":
            bg = primary
            hover_bg = secondary
            color = "#FFFFFF"
            border = primary
        elif self.theme["button_style"] == "outline":
            bg = "transparent"
            hover_bg = "rgba(255,255,255,0.08)"
            color = primary
            border = primary
        else:
            bg = (
                f"qlineargradient(x1:0,y1:0,x2:1,y2:0, "
                f"stop:0 {primary}, stop:1 {secondary})"
            )
            hover_bg = (
                f"qlineargradient(x1:0,y1:0,x2:1,y2:0, "
                f"stop:0 {secondary}, stop:1 {primary})"
            )
            color = "#FFFFFF"
            border = "rgba(255,255,255,0.24)"

        hover_border = border
        if self.theme["animation"] and self.theme["hover_effect"] != "none":
            hover_border = primary if self.theme["hover_effect"] == "glow" else "rgba(255,255,255,0.70)"

        return f"""
            QToolButton {{
                background: {bg};
                color: {color};
                border: 1px solid {border};
                border-radius: {radius}px;
                padding: 7px 18px;
                font-family: {font_family};
                font-size: 10pt;
                font-weight: 800;
                min-width: 110px;
            }}
            QToolButton:hover {{
                background: {hover_bg};
                border-color: {hover_border};
            }}
            QToolButton:pressed {{
                background: {secondary};
            }}
        """

    def _apply_theme(self):
        primary = self.theme["primary"]
        font_color = self.theme["font_color"]
        radius = self.theme["radius"]
        font_family = FONT_OPTIONS[self.theme["font_family"]][1]

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #080E1C;
                color: {font_color};
                font-family: {font_family};
            }}
            QMenuBar {{
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #0F1F3D, stop:1 #080E1C);
                color: {font_color};
                border-bottom: 2px solid {primary};
                font-family: {font_family};
                font-weight: 700;
            }}
            QMenuBar::item:selected {{
                background-color: rgba(255,255,255,0.08);
                color: {primary};
            }}
            QMenu {{
                background-color: #0F1F3D;
                color: {font_color};
                border: 1px solid {primary};
                border-radius: {radius}px;
            }}
            QMenu::item:selected {{
                background: rgba(255,255,255,0.08);
                color: {primary};
            }}
            QStatusBar {{
                background: #080E1C;
                color: {font_color};
                border-top: 2px solid {primary};
                font-family: {font_family};
            }}
        """)

        if hasattr(self, "table"):
            self.table.set_theme(self.theme)
        if hasattr(self, "status_label"):
            self.status_label.setStyleSheet(
                f"color:{primary}; font-size:9pt; padding:0 4px; "
                f"font-weight:700; font-family:{font_family};"
            )
        if hasattr(self, "legend_frame"):
            self.legend_frame.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 rgba(15,31,61,210),
                        stop:0.5 rgba(10,22,40,195),
                        stop:1 rgba(15,31,61,210));
                    border: 1px solid {primary};
                    border-radius: {radius}px;
                }}
            """)
        if hasattr(self, "legend_title"):
            self.legend_title.setStyleSheet(
                f"font-size:8pt; font-weight:800; color:{primary}; "
                f"letter-spacing:1.5px; background:transparent; border:none; "
                f"font-family:{font_family};"
            )
        for btn in getattr(self, "_toolbar_buttons", []):
            btn.setStyleSheet(self._button_qss())
        if hasattr(self, "legend_inner"):
            self._refresh_legend_items()

    def _apply_language(self):
        self.setWindowTitle(self._tr("window_title"))

        menu_refs = getattr(self, "_menus", {})
        if menu_refs:
            menu_refs["file"].setTitle(self._tr("file_menu"))
            menu_refs["config"].setTitle(self._tr("config_menu"))
            menu_refs["help"].setTitle(self._tr("help_menu"))

        for key, action in getattr(self, "_actions", {}).items():
            action.setText(self._tr(key))

        button_refs = getattr(self, "_toolbar_button_refs", {})
        button_map = {
            "import": "import_btn",
            "clear": "clear_btn",
            "excel": "excel_btn",
            "csv": "csv_btn",
            "nomenclature": "nomenclature_btn",
            "theme": "theme_btn",
            "language": "language_btn",
        }
        for key, label_key in button_map.items():
            if key in button_refs:
                button_refs[key].setText(self._tr(label_key))

        if hasattr(self, "hero"):
            self.hero.title = self._tr("app_title")
            self.hero.subtitle = self._tr("app_subtitle")
            self.hero.update()
        if hasattr(self, "legend_title"):
            self.legend_title.setText(self._tr("loaded_files"))
        if hasattr(self, "table"):
            self.table.set_labels(self._table_labels())
        self._refresh_legend_items()
        self._update_status()

    # ── UI Construction ───────────────────────────────────────────────

    def _init_ui(self):
        self._build_menu_bar()
        self._build_toolbar()
        self._build_central_widget()
        self._build_status_bar()
        self._apply_theme()
        self._apply_language()

    def _build_menu_bar(self):
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        fichier_menu = menubar.addMenu(self._tr("file_menu"))

        act_import = QAction(self._tr("import_menu"), self)
        act_import.setShortcut("Ctrl+O")
        act_import.triggered.connect(self.action_import_csv)
        fichier_menu.addAction(act_import)
        self._actions["import_menu"] = act_import

        fichier_menu.addSeparator()

        act_export_xl = QAction(self._tr("export_excel_menu"), self)
        act_export_xl.setShortcut("Ctrl+E")
        act_export_xl.triggered.connect(self.action_export_excel)
        fichier_menu.addAction(act_export_xl)
        self._actions["export_excel_menu"] = act_export_xl

        act_export_csv = QAction(self._tr("export_csv_menu"), self)
        act_export_csv.setShortcut("Ctrl+Shift+E")
        act_export_csv.triggered.connect(self.action_export_csv)
        fichier_menu.addAction(act_export_csv)
        self._actions["export_csv_menu"] = act_export_csv

        fichier_menu.addSeparator()

        act_clear = QAction(self._tr("clear_menu"), self)
        act_clear.setShortcut("Ctrl+Shift+D")
        act_clear.triggered.connect(self.action_clear)
        fichier_menu.addAction(act_clear)
        self._actions["clear_menu"] = act_clear

        fichier_menu.addSeparator()

        act_quit = QAction(self._tr("quit_menu"), self)
        act_quit.setShortcut("Ctrl+Q")
        act_quit.triggered.connect(QApplication.instance().quit)
        fichier_menu.addAction(act_quit)
        self._actions["quit_menu"] = act_quit

        config_menu = menubar.addMenu(self._tr("config_menu"))
        act_nomenclature = QAction(self._tr("nomenclature_menu"), self)
        act_nomenclature.triggered.connect(self.action_open_nomenclature)
        config_menu.addAction(act_nomenclature)
        self._actions["nomenclature_menu"] = act_nomenclature

        act_theme = QAction(self._tr("theme_menu"), self)
        act_theme.triggered.connect(self.action_open_theme)
        config_menu.addAction(act_theme)
        self._actions["theme_menu"] = act_theme

        act_language = QAction(self._tr("language_menu"), self)
        act_language.triggered.connect(self.action_toggle_language)
        config_menu.addAction(act_language)
        self._actions["language_menu"] = act_language

        aide_menu = menubar.addMenu(self._tr("help_menu"))
        act_about = QAction(self._tr("about_menu"), self)
        act_about.triggered.connect(self.action_about)
        aide_menu.addAction(act_about)
        self._actions["about_menu"] = act_about
        self._menus = {
            "file": fichier_menu,
            "config": config_menu,
            "help": aide_menu,
        }

    def _build_toolbar(self):
        toolbar = QToolBar("Barre d'outils")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.addToolBar(toolbar)

        toolbar.setStyleSheet("""
            QToolBar {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #0F1F3D, stop:1 #080E1C);
                border: none;
                spacing: 8px;
                padding: 7px 10px 9px 10px;
            }
            QToolBar::separator {
                width: 1px;
                background: rgba(56,189,248,0.20);
                margin: 5px 8px;
            }
        """)

        def add_btn(key, label, slot, gradient, tooltip):
            from PyQt6.QtWidgets import QToolButton
            btn = QToolButton()
            btn.setText(label)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(self._button_qss())
            btn.clicked.connect(slot)
            toolbar.addWidget(btn)
            self._toolbar_buttons.append(btn)
            self._toolbar_button_refs[key] = btn

        IMPORT_GRAD = "stop:0 #0F766E, stop:1 #14B8A6"
        CLEAR_GRAD  = "stop:0 #9B1C1C, stop:1 #DC2626"
        EXCEL_GRAD  = "stop:0 #1D4ED8, stop:1 #2563EB"
        CSV_GRAD    = "stop:0 #0F766E, stop:1 #0D9488"
        CONFIG_GRAD = "stop:0 #5B21B6, stop:1 #7C3AED"

        add_btn("import", self._tr("import_btn"),  self.action_import_csv,        IMPORT_GRAD,
                "Importer un ou plusieurs fichiers CSV (Ctrl+O)")
        toolbar.addSeparator()
        add_btn("clear", self._tr("clear_btn"),   self.action_clear,             CLEAR_GRAD,
                "Effacer toutes les données importées")
        toolbar.addSeparator()
        add_btn("excel", self._tr("excel_btn"),          self.action_export_excel,      EXCEL_GRAD,
                "Exporter vers un fichier Excel (.xlsx) (Ctrl+E)")
        add_btn("csv", self._tr("csv_btn"),            self.action_export_csv,        CSV_GRAD,
                "Exporter vers un fichier CSV (Ctrl+Shift+E)")
        toolbar.addSeparator()
        add_btn("nomenclature", self._tr("nomenclature_btn"),   self.action_open_nomenclature, CONFIG_GRAD,
                "Configurer les noms de pièces")
        add_btn("theme", self._tr("theme_btn"),          self.action_open_theme,         CONFIG_GRAD,
                "Personnaliser couleurs, police, boutons et effets")
        add_btn("language", self._tr("language_btn"),    self.action_toggle_language,    CONFIG_GRAD,
                "Changer la langue / Change language")

        # Animated rainbow accent line below toolbar
        self._toolbar_accent = GradientAccentBar(height=3, parent=self)
        self._toolbar_accent.show()

    def _build_central_widget(self):
        # ── Animated background fills the central area ────────────────
        self._anim_bg = AnimatedBackground()
        self.setCentralWidget(self._anim_bg)

        root_layout = QVBoxLayout(self._anim_bg)
        root_layout.setContentsMargins(12, 12, 12, 10)
        root_layout.setSpacing(10)

        # ── Hero header ───────────────────────────────────────────────
        self.hero = HeroHeader(
            title=self._tr("app_title"),
            subtitle=self._tr("app_subtitle"),
            badge="Woodshop Tool",
        )
        self.hero.setFixedHeight(118)
        root_layout.addWidget(self.hero)

        # ── Gradient accent bar (web-style rainbow strip) ─────────────
        self._accent_bar = GradientAccentBar(height=3)
        root_layout.addWidget(self._accent_bar)

        # ── Legend panel ──────────────────────────────────────────────
        self.legend_frame = QFrame()
        self.legend_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.legend_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 rgba(15,31,61,200),
                    stop:0.5 rgba(10,22,40,190),
                    stop:1 rgba(15,31,61,200));
                border: 1px solid rgba(56,189,248,0.22);
                border-radius: 10px;
            }
        """)
        self.legend_frame.setFixedHeight(48)
        legend_outer = QHBoxLayout(self.legend_frame)
        legend_outer.setContentsMargins(14, 6, 14, 6)
        legend_outer.setSpacing(10)

        self.legend_title = QLabel(self._tr("loaded_files"))
        self.legend_title.setStyleSheet(
            "font-size:8pt; font-weight:800; color:#38BDF8;"
            "letter-spacing:1.5px; background:transparent; border:none;"
        )
        legend_outer.addWidget(self.legend_title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: rgba(56,189,248,0.20); margin: 5px 4px;")
        legend_outer.addWidget(sep)

        self.legend_inner = QHBoxLayout()
        self.legend_inner.setSpacing(10)
        legend_outer.addLayout(self.legend_inner)
        legend_outer.addStretch()
        self._refresh_legend_items()
        root_layout.addWidget(self.legend_frame)

        # ── Table ─────────────────────────────────────────────────────
        self.table = CutListTable()
        root_layout.addWidget(self.table)

    def _build_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_label = QLabel()
        self.status_label.setStyleSheet(
            "color: #38BDF8; font-size: 9pt; padding: 0 4px; font-weight: 600;"
        )
        self.status_bar.addWidget(self.status_label)

        ver_label = QLabel("v1.0  |  Gestionnaire de Débit")
        ver_label.setStyleSheet("color: #334155; font-size: 8pt; padding: 0 10px;")
        self.status_bar.addPermanentWidget(ver_label)

    # ── Legend ────────────────────────────────────────────────────────

    def _refresh_legend_items(self):
        # Clear old items
        while self.legend_inner.count():
            item = self.legend_inner.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.imported_files:
            lbl = QLabel(self._tr("no_files"))
            lbl.setStyleSheet(
                "color:#334155; font-style:italic; font-size:9pt;"
                "background:transparent; border:none;"
            )
            self.legend_inner.addWidget(lbl)
        else:
            for filepath, color_hex in self.imported_files:
                fname_short = os.path.splitext(os.path.basename(filepath))[0]
                card = LegendCard(fname_short, color_hex)
                self.legend_inner.addWidget(card)

    # ── Status ────────────────────────────────────────────────────────

    def _update_status(self):
        num_files = len(self.imported_files)
        num_cabinets = len(self.pivot_data)
        if num_files == 0:
            self.status_label.setText(self._tr("status_empty"))
        else:
            self.status_label.setText(
                self._tr("status_loaded").format(
                    files=num_files,
                    cabinets=num_cabinets,
                )
            )

    # ── Actions ───────────────────────────────────────────────────────

    def action_import_csv(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Importer des fichiers CSV", "",
            "Fichiers CSV (*.csv);;Tous les fichiers (*.*)"
        )
        if not paths:
            return

        errors = []
        for path in paths:
            already_imported = [f for f, _ in self.imported_files]
            if path in already_imported:
                continue
            color_idx = len(self.imported_files)
            color = FILE_COLORS[color_idx % len(FILE_COLORS)]
            try:
                rows = parse_csv_file(path, source_color=color)
                self.all_rows.extend(rows)
                self.imported_files.append((path, color))
            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {e}")

        if errors:
            QMessageBox.warning(
                self, "Erreurs d'importation",
                "Certains fichiers n'ont pas pu être importés:\n\n" +
                "\n".join(errors)
            )

        if self.imported_files:
            self._refresh_table()
            self._refresh_legend_items()
            self._update_status()

    def action_clear(self):
        if not self.imported_files:
            return
        reply = QMessageBox.question(
            self, "Effacer tout",
            "Supprimer toutes les données importées?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.imported_files.clear()
            self.all_rows.clear()
            self.pivot_data.clear()
            self.table.clear_data()
            self._refresh_legend_items()
            self._update_status()

    def action_export_excel(self):
        if not self.pivot_data:
            QMessageBox.information(self, "Aucune donnée",
                "Importez d'abord des fichiers CSV.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter vers Excel", "liste_de_debit.xlsx",
            "Fichiers Excel (*.xlsx)"
        )
        if not path:
            return
        try:
            export_excel(self.pivot_data, self.piece_names, path)
            QMessageBox.information(self, "Exportation réussie",
                f"Fichier Excel sauvegardé :\n{path}")
        except ImportError as e:
            QMessageBox.critical(self, "Module manquant", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Erreur d'exportation", str(e))

    def action_export_csv(self):
        if not self.pivot_data:
            QMessageBox.information(self, "Aucune donnée",
                "Importez d'abord des fichiers CSV.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter vers CSV", "liste_de_debit.csv",
            "Fichiers CSV (*.csv)"
        )
        if not path:
            return
        try:
            export_csv(self.pivot_data, self.piece_names, path)
            QMessageBox.information(self, "Exportation réussie",
                f"Fichier CSV sauvegardé :\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur d'exportation", str(e))

    def action_open_nomenclature(self):
        dialog = NomenclatureDialog(self.config_path, parent=self)
        if dialog.exec():
            self.piece_names = self._load_piece_names()
            if self.all_rows:
                self._refresh_table()
            QMessageBox.information(self, "Nomenclature sauvegardée",
                "La nomenclature a été mise à jour.")

    def action_open_theme(self):
        dialog = ThemeDialog(self.theme, parent=self)
        if dialog.exec():
            self.theme = dialog.selected_theme()
            self._save_theme()
            self._apply_theme()
            QMessageBox.information(self, self._tr("theme_saved_title"),
                self._tr("theme_saved_msg"))

    def action_toggle_language(self):
        self.language = "en" if self.language == "fr" else "fr"
        self._save_language()
        self._apply_language()
        QMessageBox.information(self, self._tr("language_saved_title"),
            self._tr("language_saved_msg"))

    def action_about(self):
        QMessageBox.about(
            self, "A propos — Gestionnaire de Débit",
            "<b style='font-size:13pt;'>Gestionnaire de Débit - Meubles</b><br><br>"
            "Outil de gestion des listes de débit pour menuiserie.<br><br>"
            "• Importez des fichiers CSV de listes de coupe<br>"
            "• Visualisez les données triées par meuble<br>"
            "• Exportez vers Excel (avec couleurs) ou CSV<br>"
            "• Configurez la nomenclature des pièces<br><br>"
            "<i>Format CSV : qty, largeur, longueur, pièce, meuble, description, couleur</i><br><br>"
            "<small>v1.0</small>"
        )

    # ── Table refresh ─────────────────────────────────────────────────

    def _refresh_table(self):
        self.pivot_data = transform(self.all_rows, self.piece_names)
        self.table.set_labels(self._table_labels())
        self.table.load_data(self.pivot_data, self.piece_names)
        self._update_status()
