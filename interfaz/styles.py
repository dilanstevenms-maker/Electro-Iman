"""Hojas de estilo QSS avanzadas y paleta de colores para el tema Glassmorphism Cósmico.

Diseñado con fondos semitransparentes, bordes translúcidos de 1px, acentos en
verde menta brillante y cian eléctrico, y jerarquía visual de alta fidelidad.
"""

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QWidget


class CosmicColors:
    """Paleta de colores para el diseño Glassmorphism Cósmico."""

    # Tonos Base Oscuros / Cósmicos
    BG_MAIN_DARK = "#090A15"
    BG_SECONDARY_DARK = "#120E26"
    BG_TERTIARY_DARK = "#1A1338"

    # Vidrio esmerilado (Glass containers)
    GLASS_BG = "rgba(23, 18, 44, 0.72)"
    GLASS_BG_HOVER = "rgba(33, 26, 60, 0.82)"
    GLASS_BG_LIGHT = "rgba(255, 255, 255, 0.04)"
    GLASS_BG_ACTIVE = "rgba(42, 33, 76, 0.90)"

    # Bordes translúcidos
    GLASS_BORDER = "rgba(255, 255, 255, 0.12)"
    GLASS_BORDER_LIGHT = "rgba(255, 255, 255, 0.20)"
    GLASS_BORDER_GLOW = "rgba(0, 245, 160, 0.45)"
    GLASS_BORDER_CYAN = "rgba(0, 217, 245, 0.50)"

    # Acentos de Interacción
    ACCENT_MINT = "#00F5A0"       # Verde menta brillante
    ACCENT_CYAN = "#00D9F5"       # Cian eléctrico
    ACCENT_MINT_HOVER = "#24FFB1"
    ACCENT_CYAN_HOVER = "#30E3FF"
    ACCENT_GRADIENT_START = "#00F5A0"
    ACCENT_GRADIENT_END = "#00D9F5"

    # Estados
    STATUS_SUCCESS = "#00F5A0"
    STATUS_WARNING = "#FFB800"
    STATUS_DANGER = "#FF4567"
    STATUS_INFO = "#00D9F5"

    # Tipografía
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#A2A8C8"
    TEXT_MUTED = "#6B7294"
    TEXT_DARK = "#070B14"         # Para botones primarios con fondo brillante


def aplicar_sombra_glass(
    widget: QWidget,
    blur: int = 24,
    y_offset: int = 8,
    color_sombra: QColor = QColor(0, 0, 0, 110),
) -> QGraphicsDropShadowEffect:
    """Aplica una sombra suave y difusa característica del efecto de vidrio elevado."""
    sombra = QGraphicsDropShadowEffect(widget)
    sombra.setBlurRadius(blur)
    sombra.setYOffset(y_offset)
    sombra.setXOffset(0)
    sombra.setColor(color_sombra)
    widget.setGraphicsEffect(sombra)
    return sombra


def aplicar_resplandor_neon(
    widget: QWidget,
    blur: int = 28,
    color_glow: QColor = QColor(0, 245, 160, 80),
) -> QGraphicsDropShadowEffect:
    """Aplica un resplandor perimetral sutil en verde menta / cian para tarjetas destacadas."""
    sombra = QGraphicsDropShadowEffect(widget)
    sombra.setBlurRadius(blur)
    sombra.setYOffset(0)
    sombra.setXOffset(0)
    sombra.setColor(color_glow)
    widget.setGraphicsEffect(sombra)
    return sombra


# Hoja de estilo global en formato QSS
STYLESHEET_GLOBAL = f"""
/* ====================================================================
   ESTILO GLOBAL GLASSMORPHISM CÓSMICO
   ==================================================================== */

QMainWindow {{
    background: qlineargradient(
        spread: pad,
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 {CosmicColors.BG_MAIN_DARK},
        stop: 0.45 {CosmicColors.BG_SECONDARY_DARK},
        stop: 1.0 {CosmicColors.BG_TERTIARY_DARK}
    );
    color: {CosmicColors.TEXT_PRIMARY};
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
}}

QWidget {{
    color: {CosmicColors.TEXT_PRIMARY};
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
    font-size: 13px;
}}

/* Tooltips */
QToolTip {{
    background-color: rgba(18, 14, 38, 0.95);
    color: {CosmicColors.TEXT_PRIMARY};
    border: 1px solid {CosmicColors.GLASS_BORDER_LIGHT};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}

/* ====================================================================
   PESTAÑAS DE NAVEGACIÓN (QTabWidget)
   ==================================================================== */

QTabWidget::pane {{
    border: none;
    background: transparent;
}}

QTabBar::tab {{
    background: rgba(255, 255, 255, 0.04);
    color: {CosmicColors.TEXT_SECONDARY};
    border: 1px solid {CosmicColors.GLASS_BORDER};
    border-bottom: none;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    padding: 10px 24px;
    margin-right: 6px;
    font-weight: 600;
    font-size: 13px;
}}

QTabBar::tab:hover {{
    background: rgba(255, 255, 255, 0.08);
    color: {CosmicColors.TEXT_PRIMARY};
    border-color: {CosmicColors.GLASS_BORDER_LIGHT};
}}

QTabBar::tab:selected {{
    background: qlineargradient(
        spread: pad,
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 rgba(0, 245, 160, 0.18),
        stop: 1 rgba(0, 217, 245, 0.18)
    );
    color: {CosmicColors.ACCENT_MINT};
    border: 1px solid {CosmicColors.ACCENT_MINT};
    border-bottom: 2px solid {CosmicColors.ACCENT_CYAN};
}}

/* ====================================================================
   TARJETAS Y PANELES (Glass Cards)
   ==================================================================== */

QFrame#GlassCard {{
    background-color: {CosmicColors.GLASS_BG};
    border: 1px solid {CosmicColors.GLASS_BORDER};
    border-radius: 16px;
}}

QFrame#GlassCardHero {{
    background-color: rgba(26, 20, 52, 0.78);
    border: 1px solid rgba(0, 245, 160, 0.35);
    border-radius: 18px;
}}

QFrame#GlassCardSubtle {{
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
}}

/* ====================================================================
   BOTONES
   ==================================================================== */

QPushButton#BtnPrimary {{
    background: qlineargradient(
        spread: pad,
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 {CosmicColors.ACCENT_GRADIENT_START},
        stop: 1 {CosmicColors.ACCENT_GRADIENT_END}
    );
    color: {CosmicColors.TEXT_DARK};
    font-weight: 700;
    font-size: 13px;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
}}

QPushButton#BtnPrimary:hover {{
    background: qlineargradient(
        spread: pad,
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 {CosmicColors.ACCENT_MINT_HOVER},
        stop: 1 {CosmicColors.ACCENT_CYAN_HOVER}
    );
}}

QPushButton#BtnPrimary:pressed {{
    background-color: #00c07d;
    padding-top: 11px;
    padding-bottom: 9px;
}}

QPushButton#BtnSecondary {{
    background-color: rgba(255, 255, 255, 0.06);
    color: {CosmicColors.TEXT_PRIMARY};
    border: 1px solid {CosmicColors.GLASS_BORDER};
    border-radius: 10px;
    padding: 8px 16px;
    font-weight: 600;
}}

QPushButton#BtnSecondary:hover {{
    background-color: rgba(255, 255, 255, 0.12);
    border-color: {CosmicColors.GLASS_BORDER_LIGHT};
    color: {CosmicColors.ACCENT_MINT};
}}

QPushButton#BtnSecondary:pressed {{
    background-color: rgba(255, 255, 255, 0.04);
}}

QPushButton#BtnGhost {{
    background: transparent;
    color: {CosmicColors.TEXT_SECONDARY};
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 6px 12px;
}}

QPushButton#BtnGhost:hover {{
    background: rgba(255, 255, 255, 0.06);
    color: {CosmicColors.ACCENT_CYAN};
    border-color: {CosmicColors.GLASS_BORDER};
}}

/* ====================================================================
   SLIDERS (Deslizadores con estilo Neón)
   ==================================================================== */

QSlider::groove:horizontal {{
    height: 6px;
    background: rgba(255, 255, 255, 0.12);
    border-radius: 3px;
}}

QSlider::sub-page:horizontal {{
    background: qlineargradient(
        spread: pad,
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 {CosmicColors.ACCENT_MINT},
        stop: 1 {CosmicColors.ACCENT_CYAN}
    );
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: #FFFFFF;
    border: 2px solid {CosmicColors.ACCENT_MINT};
    width: 18px;
    margin-top: -6px;
    margin-bottom: -6px;
    border-radius: 9px;
}}

QSlider::handle:horizontal:hover {{
    background: {CosmicColors.ACCENT_MINT};
    border: 2px solid #FFFFFF;
    box-shadow: 0 0 10px {CosmicColors.ACCENT_MINT};
}}

QSlider::handle:horizontal:pressed {{
    background: {CosmicColors.ACCENT_CYAN};
    border: 2px solid #FFFFFF;
}}

/* ====================================================================
   CAMPOS DE ENTRADA Y SPINBOXES
   ==================================================================== */

QLineEdit, QDoubleSpinBox, QSpinBox {{
    background-color: rgba(18, 14, 38, 0.85);
    color: {CosmicColors.TEXT_PRIMARY};
    border: 1px solid {CosmicColors.GLASS_BORDER};
    border-radius: 8px;
    padding: 6px 10px;
    selection-background-color: {CosmicColors.ACCENT_MINT};
    selection-color: {CosmicColors.TEXT_DARK};
    font-weight: 600;
}}

QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {{
    border: 1px solid {CosmicColors.ACCENT_MINT};
    background-color: rgba(24, 18, 50, 0.95);
}}

QDoubleSpinBox::up-button, QSpinBox::up-button,
QDoubleSpinBox::down-button, QSpinBox::down-button {{
    background: rgba(255, 255, 255, 0.05);
    border: none;
    width: 16px;
    border-radius: 4px;
}}

QDoubleSpinBox::up-button:hover, QSpinBox::up-button:hover,
QDoubleSpinBox::down-button:hover, QSpinBox::down-button:hover {{
    background: rgba(0, 245, 160, 0.25);
}}

/* ====================================================================
   MENÚS DESPLEGABLES (QComboBox)
   ==================================================================== */

QComboBox {{
    background-color: rgba(18, 14, 38, 0.85);
    color: {CosmicColors.TEXT_PRIMARY};
    border: 1px solid {CosmicColors.GLASS_BORDER};
    border-radius: 8px;
    padding: 6px 12px;
    font-weight: 600;
}}

QComboBox:hover {{
    border-color: {CosmicColors.GLASS_BORDER_LIGHT};
}}

QComboBox:focus {{
    border: 1px solid {CosmicColors.ACCENT_CYAN};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: rgba(15, 11, 32, 0.98);
    color: {CosmicColors.TEXT_PRIMARY};
    border: 1px solid {CosmicColors.GLASS_BORDER};
    border-radius: 8px;
    padding: 4px;
    selection-background-color: rgba(0, 245, 160, 0.25);
    selection-color: {CosmicColors.ACCENT_MINT};
}}

/* ====================================================================
   TABLAS (QTableWidget)
   ==================================================================== */

QTableWidget {{
    background-color: rgba(18, 14, 38, 0.65);
    alternate-background-color: rgba(28, 22, 54, 0.45);
    color: {CosmicColors.TEXT_PRIMARY};
    border: 1px solid {CosmicColors.GLASS_BORDER};
    border-radius: 12px;
    gridline-color: rgba(255, 255, 255, 0.06);
    selection-background-color: rgba(0, 245, 160, 0.22);
    selection-color: {CosmicColors.ACCENT_MINT};
}}

QHeaderView::section {{
    background-color: rgba(25, 20, 50, 0.90);
    color: {CosmicColors.TEXT_SECONDARY};
    border: none;
    border-bottom: 1px solid {CosmicColors.GLASS_BORDER};
    padding: 8px 10px;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QHeaderView::section:hover {{
    color: {CosmicColors.ACCENT_MINT};
}}

/* ====================================================================
   BARRAS DE DESPLAZAMIENTO (QScrollBar)
   ==================================================================== */

QScrollBar:vertical {{
    background: rgba(255, 255, 255, 0.02);
    width: 8px;
    margin: 0;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background: rgba(255, 255, 255, 0.18);
    border-radius: 4px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {CosmicColors.ACCENT_MINT};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* ====================================================================
   BARRAS DE PROGRESO (QProgressBar)
   ==================================================================== */

QProgressBar {{
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid {CosmicColors.GLASS_BORDER};
    border-radius: 6px;
    height: 12px;
    text-align: center;
    color: {CosmicColors.TEXT_PRIMARY};
    font-size: 10px;
    font-weight: bold;
}}

QProgressBar::chunk {{
    background: qlineargradient(
        spread: pad,
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 {CosmicColors.ACCENT_MINT},
        stop: 1 {CosmicColors.ACCENT_CYAN}
    );
    border-radius: 5px;
}}
"""

