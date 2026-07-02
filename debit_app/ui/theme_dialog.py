"""
Theme dialog for desktop visual customization.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


DEFAULT_THEME = {
    "primary": "#38BDF8",
    "secondary": "#7C3AED",
    "font_color": "#E2E8F0",
    "table_font_color": "#0F172A",
    "font_family": "modern",
    "button_style": "gradient",
    "hover_effect": "lift",
    "radius": 12,
    "animation": True,
}

FONT_OPTIONS = {
    "modern": ("Moderne / Modern", '"Segoe UI", Arial, sans-serif'),
    "classic": ("Classique / Classic", 'Georgia, "Times New Roman", serif'),
    "rounded": ("Arrondie / Rounded", '"Trebuchet MS", "Segoe UI", sans-serif'),
    "mono": ("Mono", '"Courier New", monospace'),
}

BUTTON_STYLE_OPTIONS = {
    "gradient": "Dégradé / Gradient",
    "solid": "Uni / Solid",
    "outline": "Contour / Outline",
}

HOVER_OPTIONS = {
    "lift": "Lever / Lift",
    "glow": "Lueur / Glow",
    "zoom": "Zoom",
    "none": "Aucun / None",
}


def normalized_theme(theme: dict | None) -> dict:
    data = DEFAULT_THEME.copy()
    if theme:
        data.update({k: v for k, v in theme.items() if k in data})
    return data


class ColorButton(QPushButton):
    def __init__(self, label: str, color: str, parent=None):
        super().__init__(label, parent)
        self._color = color
        self.clicked.connect(self._choose_color)
        self._sync_style()

    @property
    def color(self) -> str:
        return self._color

    def set_color(self, color: str):
        self._color = color
        self._sync_style()

    def _choose_color(self):
        chosen = QColorDialog.getColor(QColor(self._color), self, self.text())
        if chosen.isValid():
            self.set_color(chosen.name().upper())

    def _sync_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                color: #FFFFFF;
                border: 1px solid rgba(255,255,255,0.35);
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 800;
            }}
        """)


class ThemeDialog(QDialog):
    def __init__(self, theme: dict | None = None, parent=None):
        super().__init__(parent)
        self.theme = normalized_theme(theme)
        self.setWindowTitle("Éditeur de thème")
        self.setMinimumWidth(460)
        self.setModal(True)
        self._init_ui()

    def _init_ui(self):
        self.setStyleSheet("""
            QDialog { background: #080E1C; }
            QLabel {
                color: #CBD5E1;
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 10pt;
            }
            QLabel#title {
                color: #E2E8F0;
                font-size: 15pt;
                font-weight: 900;
            }
            QComboBox, QSpinBox {
                background: rgba(15,31,61,0.90);
                color: #E2E8F0;
                border: 1px solid rgba(56,189,248,0.28);
                border-radius: 8px;
                padding: 6px 10px;
            }
            QCheckBox { color: #CBD5E1; spacing: 8px; }
            QPushButton#save {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #1D4ED8, stop:1 #7C3AED);
                color: #FFFFFF;
                border: 1px solid rgba(56,189,248,0.35);
                border-radius: 8px;
                padding: 8px 24px;
                font-weight: 800;
            }
            QPushButton#plain {
                background: rgba(100,116,139,0.28);
                color: #CBD5E1;
                border: 1px solid rgba(100,116,139,0.35);
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: 700;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        title = QLabel("🎨  Éditeur de thème")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Ajustez les couleurs, polices, boutons et effets du bureau.")
        subtitle.setStyleSheet("color:#64748B;")
        layout.addWidget(subtitle)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form.setVerticalSpacing(12)

        self.primary_btn = ColorButton("Couleur favorite", self.theme["primary"])
        self.secondary_btn = ColorButton("Couleur d'accent", self.theme["secondary"])
        self.font_color_btn = ColorButton("Couleur du texte", self.theme["font_color"])
        self.table_font_btn = ColorButton("Texte du tableau", self.theme["table_font_color"])

        form.addRow("Couleur favorite", self.primary_btn)
        form.addRow("Couleur d'accent", self.secondary_btn)
        form.addRow("Couleur du texte", self.font_color_btn)
        form.addRow("Texte du tableau", self.table_font_btn)

        self.font_combo = self._combo(FONT_OPTIONS, self.theme["font_family"])
        self.button_combo = self._combo(BUTTON_STYLE_OPTIONS, self.theme["button_style"])
        self.hover_combo = self._combo(HOVER_OPTIONS, self.theme["hover_effect"])
        form.addRow("Style de police", self.font_combo)
        form.addRow("Style des boutons", self.button_combo)
        form.addRow("Effet au survol", self.hover_combo)

        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(4, 28)
        self.radius_spin.setValue(int(self.theme["radius"]))
        self.radius_spin.setSuffix(" px")
        form.addRow("Arrondi", self.radius_spin)

        self.animation_check = QCheckBox("Activer les animations")
        self.animation_check.setChecked(bool(self.theme["animation"]))
        form.addRow("Animations", self.animation_check)

        form_widget = QWidget()
        form_widget.setLayout(form)
        layout.addWidget(form_widget)

        actions = QHBoxLayout()
        reset_btn = QPushButton("Réinitialiser")
        reset_btn.setObjectName("plain")
        reset_btn.clicked.connect(self._reset)
        actions.addWidget(reset_btn)
        actions.addStretch()

        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("plain")
        cancel_btn.clicked.connect(self.reject)
        actions.addWidget(cancel_btn)

        save_btn = QPushButton("Sauvegarder")
        save_btn.setObjectName("save")
        save_btn.clicked.connect(self.accept)
        actions.addWidget(save_btn)
        layout.addLayout(actions)

    def _combo(self, options: dict, current: str) -> QComboBox:
        combo = QComboBox()
        for key, label in options.items():
            text = label[0] if isinstance(label, tuple) else label
            combo.addItem(text, key)
        idx = combo.findData(current)
        combo.setCurrentIndex(max(0, idx))
        return combo

    def _reset(self):
        self.theme = DEFAULT_THEME.copy()
        self.primary_btn.set_color(self.theme["primary"])
        self.secondary_btn.set_color(self.theme["secondary"])
        self.font_color_btn.set_color(self.theme["font_color"])
        self.table_font_btn.set_color(self.theme["table_font_color"])
        self.font_combo.setCurrentIndex(self.font_combo.findData(self.theme["font_family"]))
        self.button_combo.setCurrentIndex(self.button_combo.findData(self.theme["button_style"]))
        self.hover_combo.setCurrentIndex(self.hover_combo.findData(self.theme["hover_effect"]))
        self.radius_spin.setValue(int(self.theme["radius"]))
        self.animation_check.setChecked(bool(self.theme["animation"]))

    def selected_theme(self) -> dict:
        return {
            "primary": self.primary_btn.color,
            "secondary": self.secondary_btn.color,
            "font_color": self.font_color_btn.color,
            "table_font_color": self.table_font_btn.color,
            "font_family": self.font_combo.currentData(),
            "button_style": self.button_combo.currentData(),
            "hover_effect": self.hover_combo.currentData(),
            "radius": self.radius_spin.value(),
            "animation": self.animation_check.isChecked(),
        }
