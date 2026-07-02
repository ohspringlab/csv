"""
Configuration dialog for managing piece nomenclature.
Allows adding, removing, and reordering piece names.
"""

import json
import os

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QLineEdit, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class NomenclatureDialog(QDialog):
    """Dialog for editing the piece_names list in nomenclature.json."""

    def __init__(self, nomenclature_path: str, parent=None):
        super().__init__(parent)
        self.nomenclature_path = nomenclature_path
        self.piece_names = []
        self._load_nomenclature()
        self._init_ui()
        self._populate_list()

    def _load_nomenclature(self):
        """Load piece names from JSON file."""
        if os.path.exists(self.nomenclature_path):
            try:
                with open(self.nomenclature_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.piece_names = data.get("piece_names", [])
            except Exception as e:
                QMessageBox.warning(self, "Erreur",
                    f"Impossible de lire la nomenclature:\n{e}")
                self.piece_names = []
        else:
            self.piece_names = []

    def _init_ui(self):
        self.setWindowTitle("Configuration de la Nomenclature")
        self.setMinimumSize(440, 580)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #080E1C;
                border: 1px solid rgba(56,189,248,0.22);
                border-radius: 14px;
            }
            QLabel#title {
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 13pt;
                font-weight: 800;
                color: #E2E8F0;
            }
            QLabel#desc {
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 9pt;
                color: #64748B;
            }
            QListWidget {
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 10pt;
                border: 1px solid rgba(56,189,248,0.22);
                border-radius: 10px;
                background: rgba(15,31,61,0.80);
                padding: 4px;
                color: #CBD5E1;
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
            QLineEdit {
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 10pt;
                border: 1px solid rgba(56,189,248,0.28);
                border-radius: 8px;
                padding: 7px 12px;
                background: rgba(15,31,61,0.80);
                color: #E2E8F0;
            }
            QLineEdit:focus {
                border-color: #38BDF8;
                background: rgba(15,31,61,0.95);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        # ── Header band ───────────────────────────────────────────────
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #0F1F3D, stop:0.5 #0D1A36, stop:1 #0F1F3D);
                border: 1px solid rgba(56,189,248,0.28);
                border-radius: 10px;
            }
        """)
        header.setFixedHeight(64)
        hlay = QVBoxLayout(header)
        hlay.setContentsMargins(16, 8, 16, 8)

        title = QLabel("⚙  Nomenclature des pièces")
        title.setObjectName("title")
        title.setStyleSheet(
            "font-family:'Segoe UI',Arial,sans-serif; font-size:13pt;"
            "font-weight:800; color:#E2E8F0; background:transparent; border:none;"
        )
        hlay.addWidget(title)

        desc = QLabel("Ordre des colonnes dans le tableau")
        desc.setStyleSheet(
            "font-family:'Segoe UI',Arial,sans-serif; font-size:9pt;"
            "color:#64748B; background:transparent; border:none;"
        )
        hlay.addWidget(desc)
        layout.addWidget(header)

        # ── Instruction ───────────────────────────────────────────────
        tip = QLabel("Glisser-déposer pour réordonner  •  Double-cliquer pour renommer")
        tip.setStyleSheet(
            "font-family:'Segoe UI',Arial,sans-serif;"
            "font-size:8pt; color:#334155; font-style:italic;"
        )
        layout.addWidget(tip)

        # ── List widget ───────────────────────────────────────────────
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        layout.addWidget(self.list_widget)

        # ── Add row ───────────────────────────────────────────────────
        add_layout = QHBoxLayout()
        self.new_name_input = QLineEdit()
        self.new_name_input.setPlaceholderText("Nouveau nom de piece...")
        self.new_name_input.returnPressed.connect(self._add_piece)
        add_layout.addWidget(self.new_name_input)

        add_btn = QPushButton("＋ Ajouter")
        add_btn.setFixedWidth(120)
        add_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #0F766E, stop:1 #14B8A6);
                color: #FFF;
                border: 1px solid rgba(56,189,248,0.30);
                border-radius: 8px;
                padding: 7px 14px;
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 10pt; font-weight: 700;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #14B8A6, stop:1 #2DD4BF);
            }
            QPushButton:pressed { opacity: 0.85; }
        """)
        add_btn.clicked.connect(self._add_piece)
        add_layout.addWidget(add_btn)
        layout.addLayout(add_layout)

        # ── Action buttons ────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        def make_action_btn(label, grad_start, grad_end, slot):
            b = QPushButton(label)
            b.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 {grad_start}, stop:1 {grad_end});
                    color: #FFF;
                    border: 1px solid rgba(255,255,255,0.18);
                    border-radius: 8px;
                    padding: 7px 14px;
                    font-family: "Segoe UI", Arial, sans-serif;
                    font-size: 10pt; font-weight: 700;
                }}
                QPushButton:hover {{
                    border-color: rgba(255,255,255,0.45);
                    filter: brightness(1.12);
                }}
                QPushButton:pressed {{ opacity: 0.85; }}
            """)
            b.clicked.connect(slot)
            return b

        btn_layout.addWidget(make_action_btn(
            "✕ Supprimer", "#7F1D1D", "#DC2626", self._remove_piece))
        btn_layout.addWidget(make_action_btn(
            "↑ Monter",    "#1E3A8A", "#3B82F6", self._move_up))
        btn_layout.addWidget(make_action_btn(
            "↓ Descendre", "#1E3A8A", "#3B82F6", self._move_down))
        layout.addLayout(btn_layout)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: rgba(56,189,248,0.18); margin: 6px 0;")
        layout.addWidget(sep)

        # ── Save / Cancel ─────────────────────────────────────────────
        bottom = QHBoxLayout()
        bottom.setSpacing(10)
        bottom.addStretch()

        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: rgba(100,116,139,0.28);
                color: #94A3B8;
                border: 1px solid rgba(100,116,139,0.35);
                border-radius: 8px;
                padding: 7px 22px;
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 10pt; font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(100,116,139,0.45);
                color: #CBD5E1;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        bottom.addWidget(cancel_btn)

        save_btn = QPushButton("💾  Sauvegarder")
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #1D4ED8, stop:1 #7C3AED);
                color: #FFF;
                border: 1px solid rgba(56,189,248,0.35);
                border-radius: 8px;
                padding: 7px 26px;
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 10pt; font-weight: 800;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #3B82F6, stop:1 #8B5CF6);
                border-color: rgba(56,189,248,0.60);
            }
            QPushButton:pressed { opacity: 0.85; }
        """)
        save_btn.clicked.connect(self._save_and_accept)
        bottom.addWidget(save_btn)
        layout.addLayout(bottom)

    def _populate_list(self):
        """Fill the list widget with current piece names."""
        self.list_widget.clear()
        for name in self.piece_names:
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.list_widget.addItem(item)

    def _add_piece(self):
        """Add a new piece name from the input field."""
        name = self.new_name_input.text().strip()
        if not name:
            return
        # Check for duplicate
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).text().strip() == name:
                QMessageBox.information(self, "Doublon",
                    f"'{name}' existe déjà dans la liste.")
                return
        item = QListWidgetItem(name)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.list_widget.addItem(item)
        self.new_name_input.clear()
        # Select the new item
        self.list_widget.setCurrentItem(item)

    def _remove_piece(self):
        """Remove the selected piece from the list."""
        current_row = self.list_widget.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "Sélection requise",
                "Veuillez sélectionner une pièce à supprimer.")
            return
        item = self.list_widget.item(current_row)
        reply = QMessageBox.question(
            self, "Confirmer la suppression",
            f"Supprimer '{item.text()}' de la nomenclature?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.list_widget.takeItem(current_row)

    def _move_up(self):
        """Move the selected item one position up."""
        current_row = self.list_widget.currentRow()
        if current_row <= 0:
            return
        item = self.list_widget.takeItem(current_row)
        self.list_widget.insertItem(current_row - 1, item)
        self.list_widget.setCurrentRow(current_row - 1)

    def _move_down(self):
        """Move the selected item one position down."""
        current_row = self.list_widget.currentRow()
        if current_row < 0 or current_row >= self.list_widget.count() - 1:
            return
        item = self.list_widget.takeItem(current_row)
        self.list_widget.insertItem(current_row + 1, item)
        self.list_widget.setCurrentRow(current_row + 1)

    def _get_current_names(self) -> list:
        """Collect all piece names from the list widget."""
        names = []
        for i in range(self.list_widget.count()):
            text = self.list_widget.item(i).text().strip()
            if text:
                names.append(text)
        return names

    def _save_and_accept(self):
        """Save nomenclature to JSON and close dialog."""
        names = self._get_current_names()
        if not names:
            QMessageBox.warning(self, "Liste vide",
                "La nomenclature ne peut pas être vide.")
            return

        # Load existing JSON to preserve other keys
        existing = {}
        if os.path.exists(self.nomenclature_path):
            try:
                with open(self.nomenclature_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                pass

        existing["piece_names"] = names

        try:
            os.makedirs(os.path.dirname(self.nomenclature_path), exist_ok=True)
            with open(self.nomenclature_path, "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
            self.piece_names = names
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erreur de sauvegarde",
                f"Impossible de sauvegarder la nomenclature:\n{e}")

    def get_piece_names(self) -> list:
        """Return the (potentially modified) piece names after dialog closes."""
        return self.piece_names
