"""
animated_widgets.py — Reusable animated Qt widgets that mirror the web version's
CSS animation effects: gradient-shift background, shimmer sweep, pulsing glow,
and a gradient accent bar.
"""

import math

from PyQt6.QtCore import QTimer, QRect, QPoint, Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import (
    QPainter, QLinearGradient, QRadialGradient, QColor, QPen,
    QBrush, QFont, QPainterPath, QGradient
)
from PyQt6.QtWidgets import QWidget, QLabel, QFrame


# ──────────────────────────────────────────────────────────────────────────────
# Animated background panel  (mirrors .stApp gradientShift + radial glows)
# ──────────────────────────────────────────────────────────────────────────────

class AnimatedBackground(QWidget):
    """
    Full-widget animated background:
    - Slow-cycling linear gradient (22 s loop)
    - Two soft radial glow blobs that drift
    """

    CYCLE_MS = 22_000   # full colour-cycle period
    TICK_MS  = 40        # ~25 fps

    def __init__(self, parent=None):
        super().__init__(parent)
        self._phase = 0.0          # 0 → 1 over CYCLE_MS
        self._blob_phase = 0.0     # separate phase for blob drift

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(self.TICK_MS)

        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)

    def _tick(self):
        self._phase      = (self._phase      + self.TICK_MS / self.CYCLE_MS) % 1.0
        self._blob_phase = (self._blob_phase + self.TICK_MS / 14_000)        % 1.0
        self.update()

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # ── Base gradient (shifts left↔right) ──────────────────────
        t = self._phase
        # ping-pong: 0→1→0
        ping = abs(2 * t - 1)

        c0 = QColor("#080E1C")
        c1 = QColor("#0F1F3D")
        c2 = QColor("#0A1628")
        c3 = QColor("#0D0A1E")

        bg = QLinearGradient(ping * w, 0, (1 - ping) * w, h)
        bg.setColorAt(0.00, c0)
        bg.setColorAt(0.35, c1)
        bg.setColorAt(0.65, c2)
        bg.setColorAt(1.00, c3)
        p.fillRect(0, 0, w, h, bg)

        # ── Radial blob 1 (sky/teal) ────────────────────────────────
        angle1 = self._blob_phase * 2 * math.pi
        bx1 = int(w * (0.08 + 0.06 * math.cos(angle1)))
        by1 = int(h * (0.12 + 0.06 * math.sin(angle1 * 0.7)))
        rad1 = int(min(w, h) * 0.38)
        blob1 = QRadialGradient(bx1, by1, rad1)
        blob1.setColorAt(0.0, QColor(56, 189, 248, 46))
        blob1.setColorAt(1.0, QColor(56, 189, 248, 0))
        p.fillRect(0, 0, w, h, blob1)

        # ── Radial blob 2 (orange/amber) ────────────────────────────
        angle2 = self._blob_phase * 2 * math.pi + math.pi
        bx2 = int(w * (0.92 + 0.05 * math.cos(angle2 * 1.3)))
        by2 = int(h * (0.06 + 0.05 * math.sin(angle2)))
        rad2 = int(min(w, h) * 0.32)
        blob2 = QRadialGradient(bx2, by2, rad2)
        blob2.setColorAt(0.0, QColor(251, 146, 60, 40))
        blob2.setColorAt(1.0, QColor(251, 146, 60, 0))
        p.fillRect(0, 0, w, h, blob2)

        # ── Radial blob 3 (violet, bottom-centre) ───────────────────
        angle3 = self._blob_phase * 2 * math.pi * 0.6
        bx3 = int(w * (0.50 + 0.04 * math.cos(angle3)))
        by3 = int(h * (0.94 + 0.03 * math.sin(angle3)))
        rad3 = int(min(w, h) * 0.30)
        blob3 = QRadialGradient(bx3, by3, rad3)
        blob3.setColorAt(0.0, QColor(167, 139, 250, 36))
        blob3.setColorAt(1.0, QColor(167, 139, 250, 0))
        p.fillRect(0, 0, w, h, blob3)

        p.end()


# ──────────────────────────────────────────────────────────────────────────────
# Hero header widget  (mirrors .app-hero with shimmer + rainbow bottom bar)
# ──────────────────────────────────────────────────────────────────────────────

class HeroHeader(QWidget):
    """
    Animated hero banner:
    - Dark glassmorphism card
    - Shimmer sweep that repeats every ~6 s
    - Gradient gradient-text title (sky → indigo → pink)
    - 5-colour bottom accent bar that also cycles
    - Pulsing live dot badge
    """

    SHIMMER_MS   = 6_000
    TICK_MS      = 35
    ACCENT_CYCLE = 5_000

    def __init__(self, title: str, subtitle: str, badge: str = "Woodshop Tool", parent=None):
        super().__init__(parent)
        self.title    = title
        self.subtitle = subtitle
        self.badge    = badge

        self._shimmer_phase = 0.0   # 0 → 1
        self._accent_phase  = 0.0   # for bottom rainbow bar
        self._dot_phase     = 0.0   # for pulsing dot

        self.setMinimumHeight(100)
        self.setSizePolicy(
            self.sizePolicy().horizontalPolicy(),
            self.sizePolicy().verticalPolicy()
        )

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(self.TICK_MS)

    def _tick(self):
        self._shimmer_phase = (self._shimmer_phase + self.TICK_MS / self.SHIMMER_MS) % 1.0
        self._accent_phase  = (self._accent_phase  + self.TICK_MS / self.ACCENT_CYCLE) % 1.0
        self._dot_phase     = (self._dot_phase     + self.TICK_MS / 2_000) % 1.0
        self.update()

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        r = 14  # corner radius

        # ── Card background ────────────────────────────────────────
        card_path = QPainterPath()
        card_path.addRoundedRect(0, 0, w, h, r, r)

        card_bg = QLinearGradient(0, 0, w, h)
        card_bg.setColorAt(0.0, QColor(15, 31, 61, 242))
        card_bg.setColorAt(0.6, QColor(17, 24, 50, 236))
        card_bg.setColorAt(1.0, QColor(10, 22, 40, 242))
        p.fillPath(card_path, card_bg)

        # ── Card border ────────────────────────────────────────────
        pen = QPen(QColor(56, 189, 248, 56), 1)
        p.setPen(pen)
        p.drawRoundedRect(1, 1, w - 2, h - 2, r, r)

        # ── Shimmer sweep ──────────────────────────────────────────
        # A diagonal highlight band that travels left→right
        sx = int((self._shimmer_phase * 2.2 - 0.2) * w)
        shimmer = QLinearGradient(sx - 120, 0, sx + 120, 0)
        shimmer.setColorAt(0.0, QColor(255, 255, 255, 0))
        shimmer.setColorAt(0.4, QColor(56, 189, 248, 24))
        shimmer.setColorAt(0.5, QColor(255, 255, 255, 32))
        shimmer.setColorAt(0.6, QColor(56, 189, 248, 24))
        shimmer.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setClipPath(card_path)
        p.fillRect(0, 0, w, h, shimmer)
        p.setClipping(False)

        # ── Rainbow bottom accent bar ──────────────────────────────
        bar_h = 4
        t = self._accent_phase
        bar = QLinearGradient(0, 0, w, 0)
        # Cycle colours by offsetting stops
        colours = [
            QColor("#38BDF8"), QColor("#818CF8"), QColor("#F472B6"),
            QColor("#FB923C"), QColor("#34D399"), QColor("#38BDF8"),
        ]
        n = len(colours) - 1
        for i, c in enumerate(colours):
            pos = ((i / n) + t) % 1.0
            bar.setColorAt(pos, c)
        p.fillRect(0, h - bar_h, w, bar_h, bar)

        # ── Badge ──────────────────────────────────────────────────
        badge_font = QFont("Segoe UI", 8, QFont.Weight.Bold)
        p.setFont(badge_font)
        badge_text = f"  ● {self.badge}  "
        fm = p.fontMetrics()
        bw = fm.horizontalAdvance(badge_text) + 16
        bh = fm.height() + 8
        bx, by = 20, 16

        # Badge pill background
        badge_path = QPainterPath()
        badge_path.addRoundedRect(bx, by, bw, bh, bh / 2, bh / 2)
        p.fillPath(badge_path, QColor(56, 189, 248, 20))
        p.setPen(QPen(QColor(56, 189, 248, 90), 1))
        p.drawPath(badge_path)

        # Dot glow pulse
        dot_alpha = int(140 + 115 * math.sin(self._dot_phase * 2 * math.pi))
        p.setPen(QPen(QColor(56, 189, 248, dot_alpha), 1))
        p.setBrush(QBrush(QColor(56, 189, 248, dot_alpha)))
        dot_x = bx + 10
        dot_y = by + bh // 2
        p.drawEllipse(dot_x, dot_y - 3, 6, 6)

        # Badge text (skip the dot char, drawn above)
        p.setPen(QColor(56, 189, 248, 210))
        p.drawText(bx + 18, by, bw, bh, Qt.AlignmentFlag.AlignVCenter, self.badge.upper())

        # ── Title with gradient text ────────────────────────────────
        title_font = QFont("Segoe UI", 20, QFont.Weight.Black)
        p.setFont(title_font)
        fm = p.fontMetrics()
        ty = by + bh + 14

        title_grad = QLinearGradient(20, ty, 20 + fm.horizontalAdvance(self.title), ty)
        title_grad.setColorAt(0.0, QColor("#E0F2FE"))
        title_grad.setColorAt(0.5, QColor("#818CF8"))
        title_grad.setColorAt(1.0, QColor("#F472B6"))
        p.setPen(QPen(QBrush(title_grad), 0))
        p.drawText(20, ty, self.title)

        # ── Subtitle ───────────────────────────────────────────────
        sub_font = QFont("Segoe UI", 10)
        sub_font.setWeight(QFont.Weight.Medium)
        p.setFont(sub_font)
        p.setPen(QColor(148, 163, 184, 210))
        sy = ty + fm.height() + 8
        p.drawText(20, sy, self.subtitle)

        p.end()

    def sizeHint(self):
        from PyQt6.QtCore import QSize
        return QSize(600, 118)


# ──────────────────────────────────────────────────────────────────────────────
# Gradient accent line  (bottom of toolbar / top of content area)
# ──────────────────────────────────────────────────────────────────────────────

class GradientAccentBar(QWidget):
    """A thin horizontal bar whose gradient cycles continuously."""

    CYCLE_MS = 5_000
    TICK_MS  = 35

    def __init__(self, height: int = 3, parent=None):
        super().__init__(parent)
        self.setFixedHeight(height)
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(self.TICK_MS)

    def _tick(self):
        self._phase = (self._phase + self.TICK_MS / self.CYCLE_MS) % 1.0
        self.update()

    def paintEvent(self, _event):
        p = QPainter(self)
        w, h = self.width(), self.height()
        t = self._phase
        grad = QLinearGradient(0, 0, w, 0)
        colours = [
            QColor("#38BDF8"), QColor("#818CF8"), QColor("#F472B6"),
            QColor("#FB923C"), QColor("#34D399"), QColor("#38BDF8"),
        ]
        n = len(colours) - 1
        for i, c in enumerate(colours):
            pos = ((i / n) + t) % 1.0
            grad.setColorAt(pos, c)
        p.fillRect(0, 0, w, h, grad)
        p.end()


# ──────────────────────────────────────────────────────────────────────────────
# Glowing legend card  (file swatch + filename with hover glow)
# ──────────────────────────────────────────────────────────────────────────────

class LegendCard(QWidget):
    """
    A single file-legend card with:
    - Colour swatch pill
    - Filename label
    - Subtle border glow that pulses on hover
    """

    TICK_MS = 40

    def __init__(self, filename: str, color_hex: str, parent=None):
        super().__init__(parent)
        self.filename  = filename
        self.color_hex = color_hex
        self._glow     = 0.0       # 0 → 1, driven by hover
        self._target   = 0.0
        self.setFixedHeight(38)
        self.setMinimumWidth(120)
        self.setCursor(Qt.CursorShape.ArrowCursor)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(self.TICK_MS)

    def _tick(self):
        delta = 0.08
        if self._glow < self._target:
            self._glow = min(self._target, self._glow + delta)
        elif self._glow > self._target:
            self._glow = max(self._target, self._glow - delta)
        if abs(self._glow - self._target) > 0.001:
            self.update()

    def enterEvent(self, _e):
        self._target = 1.0

    def leaveEvent(self, _e):
        self._target = 0.0

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        r = 10

        # Card background
        card = QPainterPath()
        card.addRoundedRect(0, 0, w, h, r, r)
        bg_alpha = int(80 + 60 * self._glow)
        p.fillPath(card, QColor(15, 31, 61, bg_alpha))

        # Glowing border
        border_alpha = int(55 + 200 * self._glow)
        pen = QPen(QColor(56, 189, 248, border_alpha), 1)
        p.setPen(pen)
        p.drawPath(card)

        # Colour swatch pill
        sw_w, sw_h = 26, 14
        sx = 10
        sy = (h - sw_h) // 2
        swatch = QPainterPath()
        swatch.addRoundedRect(sx, sy, sw_w, sw_h, sw_h / 2, sw_h / 2)
        p.fillPath(swatch, QColor(self.color_hex))
        p.setPen(QPen(QColor(56, 189, 248, 90), 1))
        p.drawPath(swatch)

        # Filename text
        font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        p.setFont(font)
        text_alpha = int(180 + 75 * self._glow)
        p.setPen(QColor(203, 213, 225, text_alpha))
        p.drawText(sx + sw_w + 8, 0, w - sx - sw_w - 18, h,
                   Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                   self.filename)

        p.end()

    def sizeHint(self):
        from PyQt6.QtCore import QSize
        fm_w = len(self.filename) * 8 + 60
        return QSize(max(120, fm_w), 38)
