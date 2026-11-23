"""Control deslizante interactivo con sincronización numérica y estilo Glassmorphism."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from interfaz.styles import CosmicColors


class GlassParamSlider(QWidget):
    """Widget compuesto de parámetro: Título, Spinbox editable y Slider sincronizado."""

    valorCambiado = pyqtSignal(float)

    def __init__(
        self,
        titulo: str,
        simbolo: str,
        unidad: str,
        min_val: float,
        max_val: float,
        val_default: float,
        paso: float = 1.0,
        decimales: int = 2,
        tooltip: str = "",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self.paso = paso
        self.decimales = decimales
        self.escala = 10 ** decimales

        self._bloqueo_signals = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 8)
        layout.setSpacing(6)

        # Fila superior: Título y SpinBox
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)

        lbl_etiqueta = QLabel(f"{titulo} ({simbolo})")
        lbl_etiqueta.setStyleSheet(
            f"color: {CosmicColors.TEXT_PRIMARY}; font-size: 12px; font-weight: 600;"
        )
        if tooltip:
            lbl_etiqueta.setToolTip(tooltip)

        self.spin = QDoubleSpinBox()
        self.spin.setRange(min_val, max_val)
        self.spin.setSingleStep(paso)
        self.spin.setDecimals(decimales)
        self.spin.setSuffix(f" {unidad}")
        self.spin.setValue(val_default)
        self.spin.setFixedWidth(110)
        self.spin.setAlignment(Qt.AlignmentFlag.AlignRight)

        top_layout.addWidget(lbl_etiqueta)
        top_layout.addStretch()
        top_layout.addWidget(self.spin)
        layout.addLayout(top_layout)

        # Slider horizontal
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(int(min_val * self.escala), int(max_val * self.escala))
        self.slider.setSingleStep(int(paso * self.escala))
        self.slider.setPageStep(int(paso * self.escala * 5))
        self.slider.setValue(int(val_default * self.escala))
        layout.addWidget(self.slider)

        # Fila inferior: Rangos min y max
        range_layout = QHBoxLayout()
        lbl_min = QLabel(f"{min_val:.{decimales}f}")
        lbl_min.setStyleSheet(f"color: {CosmicColors.TEXT_MUTED}; font-size: 10px;")
        lbl_max = QLabel(f"{max_val:.{decimales}f} {unidad}")
        lbl_max.setStyleSheet(f"color: {CosmicColors.TEXT_MUTED}; font-size: 10px;")
        range_layout.addWidget(lbl_min)
        range_layout.addStretch()
        range_layout.addWidget(lbl_max)
        layout.addLayout(range_layout)

        # Conectar señales bidireccionales
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.spin.valueChanged.connect(self._on_spin_changed)

    def _on_slider_changed(self, int_val: int):
        if self._bloqueo_signals:
            return
        self._bloqueo_signals = True
        flt_val = int_val / self.escala
        self.spin.setValue(flt_val)
        self._bloqueo_signals = False
        self.valorCambiado.emit(flt_val)

    def _on_spin_changed(self, flt_val: float):
        if self._bloqueo_signals:
            return
        self._bloqueo_signals = True
        int_val = int(flt_val * self.escala)
        self.slider.setValue(int_val)
        self._bloqueo_signals = False
        self.valorCambiado.emit(flt_val)

    def valor(self) -> float:
        """Devuelve el valor numérico actual."""
        return float(self.spin.value())

    def set_valor(self, nuevo_valor: float):
        """Asigna un nuevo valor al parámetro."""
        clamped = max(self.min_val, min(self.max_val, nuevo_valor))
        self.spin.setValue(clamped)

