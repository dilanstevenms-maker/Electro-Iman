"""Widgets visuales con efecto Glassmorphism para métricas, tarjetas y estados."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPaintEvent
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from interfaz.styles import CosmicColors, aplicar_resplandor_neon, aplicar_sombra_glass


class GlassCard(QFrame):
    """Contenedor base con efecto de vidrio esmerilado translúcido."""

    def __init__(self, parent: QWidget | None = None, subtle: bool = False):
        super().__init__(parent)
        self.setObjectName("GlassCardSubtle" if subtle else "GlassCard")
        aplicar_sombra_glass(self, blur=22, y_offset=6)


class GlassHeroCard(QFrame):
    """Tarjeta destacada ('Hero Card') con resplandor perimetral neón para el resultado ideal."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("GlassCardHero")
        aplicar_resplandor_neon(self, blur=30, color_glow=QColor(0, 245, 160, 65))


class GlassMetricCard(QFrame):
    """Tarjeta compacta para destacar una métrica individual de ingeniería."""

    def __init__(
        self,
        titulo: str,
        valor_inicial: str = "--",
        unidad: str = "",
        icono: str = "⚡",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setObjectName("GlassCardSubtle")
        self.setMinimumHeight(86)
        aplicar_sombra_glass(self, blur=14, y_offset=4, color_sombra=QColor(0, 0, 0, 70))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        # Header de la métrica (Icono + Título)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)

        self.lbl_icono = QLabel(icono)
        self.lbl_icono.setStyleSheet("font-size: 14px; background: transparent;")

        self.lbl_titulo = QLabel(titulo)
        self.lbl_titulo.setStyleSheet(
            f"color: {CosmicColors.TEXT_SECONDARY}; font-size: 11px; "
            "font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; background: transparent;"
        )

        header_layout.addWidget(self.lbl_icono)
        header_layout.addWidget(self.lbl_titulo)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Valor + Unidad
        val_layout = QHBoxLayout()
        val_layout.setSpacing(4)
        val_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBaseline)

        self.lbl_valor = QLabel(valor_inicial)
        self.lbl_valor.setStyleSheet(
            f"color: {CosmicColors.ACCENT_MINT}; font-size: 20px; "
            "font-weight: 700; background: transparent;"
        )

        self.lbl_unidad = QLabel(unidad)
        self.lbl_unidad.setStyleSheet(
            f"color: {CosmicColors.TEXT_MUTED}; font-size: 12px; font-weight: 600; background: transparent;"
        )

        val_layout.addWidget(self.lbl_valor)
        val_layout.addWidget(self.lbl_unidad)
        val_layout.addStretch()
        layout.addLayout(val_layout)

    def set_valor(self, nuevo_valor: str, color_custom: str | None = None):
        """Actualiza el texto y color del valor principal."""
        self.lbl_valor.setText(nuevo_valor)
        color = color_custom or CosmicColors.ACCENT_MINT
        self.lbl_valor.setStyleSheet(
            f"color: {color}; font-size: 20px; font-weight: 700; background: transparent;"
        )


class StatusBadge(QFrame):
    """Píldora de estado con indicador LED luminoso y texto."""

    def __init__(self, texto: str = "Listo", estado: str = "ok", parent: QWidget | None = None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 12, 4)
        layout.setSpacing(8)

        self.led = QLabel("●")
        self.lbl_texto = QLabel(texto)
        self.lbl_texto.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))

        layout.addWidget(self.led)
        layout.addWidget(self.lbl_texto)

        self.set_estado(texto, estado)

    def set_estado(self, texto: str, estado: str = "ok"):
        """Actualiza el estado visual: 'ok' (verde), 'advertencia' (amarillo), 'error' (rojo), 'info' (cian)."""
        self.lbl_texto.setText(texto)

        colores = {
            "ok": (CosmicColors.STATUS_SUCCESS, "rgba(0, 245, 160, 0.14)"),
            "advertencia": (CosmicColors.STATUS_WARNING, "rgba(255, 184, 0, 0.16)"),
            "error": (CosmicColors.STATUS_DANGER, "rgba(255, 69, 103, 0.18)"),
            "info": (CosmicColors.STATUS_INFO, "rgba(0, 217, 245, 0.14)"),
        }
        color_texto, color_bg = colores.get(estado, colores["ok"])

        self.led.setStyleSheet(f"color: {color_texto}; font-size: 11px; background: transparent;")
        self.lbl_texto.setStyleSheet(f"color: {color_texto}; background: transparent;")
        self.setStyleSheet(
            f"background-color: {color_bg}; border: 1px solid {color_texto}; "
            "border-radius: 12px;"
        )


class ThermalSafetyBar(QWidget):
    """Barra de utilización térmica que cambia de color dinámicamente."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        header = QHBoxLayout()
        self.lbl_titulo = QLabel("Factor de Carga Térmica (I / I_máx):")
        self.lbl_titulo.setStyleSheet(f"color: {CosmicColors.TEXT_SECONDARY}; font-size: 11px; font-weight: 600;")
        self.lbl_porcentaje = QLabel("0.0%")
        self.lbl_porcentaje.setStyleSheet(f"color: {CosmicColors.ACCENT_MINT}; font-size: 11px; font-weight: 700;")

        header.addWidget(self.lbl_titulo)
        header.addStretch()
        header.addWidget(self.lbl_porcentaje)
        layout.addLayout(header)

        self.barra = QProgressBar()
        self.barra.setRange(0, 100)
        self.barra.setValue(0)
        self.barra.setTextVisible(False)
        self.barra.setFixedHeight(10)
        layout.addWidget(self.barra)

    def set_porcentaje(self, porcentaje: float):
        """Actualiza el porcentaje y aplica el color correspondiente."""
        clamped = max(0, min(100, int(porcentaje)))
        self.barra.setValue(clamped)
        self.lbl_porcentaje.setText(f"{porcentaje:.1f}%")

        if porcentaje < 60.0:
            color = CosmicColors.ACCENT_MINT
        elif porcentaje < 85.0:
            color = CosmicColors.ACCENT_CYAN
        elif porcentaje <= 100.0:
            color = CosmicColors.STATUS_WARNING
        else:
            color = CosmicColors.STATUS_DANGER

        self.lbl_porcentaje.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 700;")
        self.barra.setStyleSheet(f"""
            QProgressBar {{
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid {CosmicColors.GLASS_BORDER};
                border-radius: 5px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)

