"""Componentes de interfaz gráfica (UI) para ELECTROIMÁN STUDIO en PyQt6.

Implementa la navegación en tres pantallas principales (Inicio, Parámetros, Resultados)
más la vista de Catálogo SQL, con estética Glassmorphism Cósmica idéntica a la referencia.
"""

from typing import Any, Optional

from PyQt6.QtCore import QPoint, QRectF, QSize, Qt, pyqtProperty, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSlider,
    QSizePolicy,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from logica import AlternativaCalibre, ResultadoOptimizacion, calcular_combinacion


# =============================================================================
# WIDGET DE FONDO CÓSMICO (GPU / QPainter Acelerado)
# =============================================================================
class CosmicBackgroundWidget(QWidget):
    """Lienzo que dibuja el degradado cósmico profundo y halos de luz difusos."""

    def __init__(self, parent: QWidget | None = None, mostrar_decoracion_inicio: bool = False):
        super().__init__(parent)
        self.mostrar_decoracion_inicio = mostrar_decoracion_inicio

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = float(self.width()), float(self.height())

        # 1. Degradado base vertical oscuro (Púrpura noche a azul cósmico)
        grad_base = QLinearGradient(0.0, 0.0, w, h)
        grad_base.setColorAt(0.0, QColor(9, 10, 22))
        grad_base.setColorAt(0.45, QColor(16, 12, 34))
        grad_base.setColorAt(1.0, QColor(8, 12, 24))
        painter.fillRect(0, 0, int(w), int(h), grad_base)

        # 2. Resplandor difuso en esquina inferior izquierda (Cian / Verde Menta)
        rad_cian = QRadialGradient(w * 0.15, h * 0.90, w * 0.55)
        rad_cian.setColorAt(0.0, QColor(0, 245, 160, 48))
        rad_cian.setColorAt(0.5, QColor(0, 217, 245, 25))
        rad_cian.setColorAt(1.0, QColor(0, 217, 245, 0))
        painter.fillRect(0, 0, int(w), int(h), rad_cian)

        # 3. Resplandor difuso en esquina inferior derecha / centro (Púrpura y Magenta)
        rad_purpura = QRadialGradient(w * 0.85, h * 0.80, w * 0.50)
        rad_purpura.setColorAt(0.0, QColor(138, 43, 226, 35))
        rad_purpura.setColorAt(0.6, QColor(90, 24, 154, 15))
        rad_purpura.setColorAt(1.0, QColor(90, 24, 154, 0))
        painter.fillRect(0, 0, int(w), int(h), rad_purpura)

        # 4. Decoración abstracta de la pantalla de inicio (emblema de bobina magnética)
        if self.mostrar_decoracion_inicio:
            painter.setPen(QPen(QColor(0, 245, 160, 40), 22, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            cx = w * 0.88
            cy = h * 0.50
            rw = 48.0
            rh = 75.0
            painter.drawRoundedRect(QRectF(cx - rw, cy - rh, rw * 1.5, rh * 2.0), 38, 38)

        painter.end()


# =============================================================================
# WIDGETS INTERACTIVOS DE ALTA FIDELIDAD
# =============================================================================
class GlassToggleSwitch(QWidget):
    """Interruptor deslizante (Switch Toggle) en verde menta brillante."""

    toggled = pyqtSignal(bool)

    def __init__(self, parent: QWidget | None = None, checked: bool = True):
        super().__init__(parent)
        self.setFixedSize(48, 26)
        self._checked = checked
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, estado: bool):
        if self._checked != estado:
            self._checked = estado
            self.update()
            self.toggled.emit(self._checked)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setChecked(not self._checked)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = float(self.width()), float(self.height())

        # Fondo del carril
        path = QPainterPath()
        path.addRoundedRect(QRectF(0.0, 0.0, w, h), h / 2.0, h / 2.0)

        if self._checked:
            grad = QLinearGradient(0.0, 0.0, w, 0.0)
            grad.setColorAt(0.0, QColor(0, 245, 160))
            grad.setColorAt(1.0, QColor(0, 217, 245))
            painter.fillPath(path, grad)
        else:
            painter.fillPath(path, QColor(255, 255, 255, 28))

        # Bolita circular
        thumb_diam = h - 6.0
        thumb_x = (w - thumb_diam - 3.0) if self._checked else 3.0
        thumb_y = 3.0

        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(thumb_x, thumb_y, thumb_diam, thumb_diam))
        painter.end()


class GlassSliderRow(QWidget):
    """Fila de parámetro con etiqueta, cajita de valor numérico y slider horizontal."""

    valorCambiado = pyqtSignal(float)

    def __init__(
        self,
        titulo: str,
        unidad: str,
        min_val: float,
        max_val: float,
        val_default: float,
        decimales: int = 1,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.unidad = unidad
        self.decimales = decimales
        self.min_val = min_val
        self.max_val = max_val
        self.factor = 10 ** decimales

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 8)
        layout.setSpacing(4)

        # Fila superior: Título y Cajita de Valor
        top_h = QHBoxLayout()
        self.lbl_titulo = QLabel(titulo)
        self.lbl_titulo.setStyleSheet("color: #FFFFFF; font-size: 12px; font-weight: 600;")

        self.lbl_badge = QLabel()
        self.lbl_badge.setProperty("class", "SliderValueBadge")
        self.lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        top_h.addWidget(self.lbl_titulo)
        top_h.addStretch()
        top_h.addWidget(self.lbl_badge)
        layout.addLayout(top_h)

        # Slider horizontal
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(int(min_val * self.factor), int(max_val * self.factor))
        self.slider.setValue(int(val_default * self.factor))
        self.slider.valueChanged.connect(self._on_slider_moved)
        layout.addWidget(self.slider)

        # Fila inferior: Rangos mínimo y máximo
        rango_h = QHBoxLayout()
        lbl_min = QLabel(f"{min_val:.1f}".replace(".", ","))
        lbl_min.setStyleSheet("color: #6D7392; font-size: 10px;")
        lbl_max = QLabel(f"{max_val:.1f} {unidad}".replace(".", ","))
        lbl_max.setStyleSheet("color: #6D7392; font-size: 10px;")
        rango_h.addWidget(lbl_min)
        rango_h.addStretch()
        rango_h.addWidget(lbl_max)
        layout.addLayout(rango_h)

        self._actualizar_badge(val_default)

    def _actualizar_badge(self, val: float):
        texto = f"{val:.{self.decimales}f} {self.unidad}".replace(".", ",")
        self.lbl_badge.setText(texto)

    def _on_slider_moved(self, int_val: int):
        flt_val = int_val / self.factor
        self._actualizar_badge(flt_val)
        self.valorCambiado.emit(flt_val)

    def valor(self) -> float:
        return self.slider.value() / self.factor

    def set_valor(self, nuevo_val: float):
        self.slider.setValue(int(nuevo_val * self.factor))


# =============================================================================
# HEADER SUPERIOR COMÚN
# =============================================================================
class AppHeaderWidget(QWidget):
    """Barra superior con isotipo neón magenta, título y acciones rápidas."""

    abrirCatalogoClicked = pyqtSignal()
    volverInicioClicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None, mostrar_badge_mysql: bool = False):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 6)
        layout.setSpacing(12)

        # Ícono magnético en arco (U invertida en neón)
        lbl_icono = QLabel("∩")
        lbl_icono.setStyleSheet(
            "font-size: 26px; font-weight: 900; color: #FF2A85; "
            "background: transparent; margin-bottom: 2px;"
        )

        lbl_nombre = QLabel("ELECTROIMÁN STUDIO")
        lbl_nombre.setStyleSheet(
            "font-size: 15px; font-weight: 800; color: #FFFFFF; "
            "letter-spacing: 1px; background: transparent;"
        )

        layout.addWidget(lbl_icono)
        layout.addWidget(lbl_nombre)
        layout.addStretch()

        if mostrar_badge_mysql:
            # Badge estilo píldora como en la imagen
            badge = QFrame()
            badge.setProperty("class", "StatusBadge")
            b_layout = QHBoxLayout(badge)
            b_layout.setContentsMargins(10, 4, 10, 4)
            b_layout.setSpacing(6)
            lbl_dot = QLabel("●")
            lbl_dot.setStyleSheet("color: #00F5A0; font-size: 9px;")
            lbl_txt = QLabel("MySQL Offline (base de datos local - adapter)")
            lbl_txt.setStyleSheet("color: #00F5A0; font-size: 11px; font-weight: 700;")
            b_layout.addWidget(lbl_dot)
            b_layout.addWidget(lbl_txt)
            layout.addWidget(badge)
        else:
            self.btn_catalogo = QPushButton("📚 Catálogo AWG")
            self.btn_catalogo.setObjectName("BtnHeaderAction")
            self.btn_catalogo.clicked.connect(self.abrirCatalogoClicked.emit)
            layout.addWidget(self.btn_catalogo)


# =============================================================================
# PANTALLA 1: INICIO ELEGANTE
# =============================================================================
class PantallaInicio(CosmicBackgroundWidget):
    """Pantalla de bienvenida minimalista y elegante."""

    iniciarConsulta = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent, mostrar_decoracion_inicio=True)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 24)

        # Top Bar: Avatar circular pequeño + Nombres de los autores
        top_h = QHBoxLayout()
        avatar = QLabel("👤")
        avatar.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0.12); border-radius: 12px; "
            "padding: 3px; font-size: 12px;"
        )
        lbl_autor = QLabel("Carolina Molina & Dilan Muñoz")
        lbl_autor.setStyleSheet("color: #00F5A0; font-size: 12px; font-weight: 600;")
        top_h.addWidget(avatar)
        top_h.addWidget(lbl_autor)
        top_h.addStretch()
        layout.addLayout(top_h)

        layout.addStretch(1)

        # Contenido Central Minimalista
        centro_v = QVBoxLayout()
        centro_v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        centro_v.setSpacing(10)

        lbl_titulo = QLabel("ELECTROIMÁN STUDIO")
        lbl_titulo.setStyleSheet(
            "font-size: 40px; font-weight: 900; color: #FFFFFF; "
            "letter-spacing: 2px; background: transparent;"
        )
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_desc = QLabel("Diseño Minimalista de Electroimanes - Por Carolina Molina y Dilan Muñoz")
        lbl_desc.setStyleSheet(
            "font-size: 14px; font-weight: 500; color: #A0A6C4; background: transparent;"
        )
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botón Central Destacado
        self.btn_iniciar = QPushButton("INICIAR CONSULTA →")
        self.btn_iniciar.setObjectName("BtnIniciarConsulta")
        self.btn_iniciar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_iniciar.clicked.connect(self.iniciarConsulta.emit)

        # Contenedor para centrar el botón con margen
        btn_wrapper = QHBoxLayout()
        btn_wrapper.addStretch()
        btn_wrapper.addWidget(self.btn_iniciar)
        btn_wrapper.addStretch()

        centro_v.addWidget(lbl_titulo)
        centro_v.addWidget(lbl_desc)
        centro_v.addSpacing(28)
        centro_v.addLayout(btn_wrapper)

        layout.addLayout(centro_v)
        layout.addStretch(1)

        # Footer discreto
        footer_h = QHBoxLayout()
        footer_h.addStretch()
        lbl_version = QLabel("PyQt6 - Glassmorphism Cósmico - v2.0")
        lbl_version.setStyleSheet("color: #6C7292; font-size: 11px;")
        footer_h.addWidget(lbl_version)
        layout.addLayout(footer_h)


# =============================================================================
# PANTALLA 2: DASHBOARD DE PARÁMETROS
# =============================================================================
class PantallaParametros(CosmicBackgroundWidget):
    """Dashboard de parámetros con tres tarjetas horizontales de vidrio esmerilado."""

    calcularCombinacion = pyqtSignal(dict)
    abrirCatalogo = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(16)

        # Header
        self.header = AppHeaderWidget(self)
        self.header.abrirCatalogoClicked.connect(self.abrirCatalogo.emit)
        layout.addWidget(self.header)

        layout.addStretch(1)

        # Fila Central: Tres Tarjetas Contenedoras Glassmorphic
        cards_h = QHBoxLayout()
        cards_h.setSpacing(18)

        # --- TARJETA 1: PARÁMETROS DEL SOLENOIDE ---
        card_solenoide = QFrame()
        card_solenoide.setProperty("class", "GlassCard")
        v_sol = QVBoxLayout(card_solenoide)
        v_sol.setContentsMargins(20, 18, 20, 18)
        v_sol.setSpacing(10)

        lbl_t1 = QLabel("PARÁMETROS DEL SOLENOIDE")
        lbl_t1.setProperty("class", "SectionTitle")
        v_sol.addWidget(lbl_t1)
        v_sol.addSpacing(6)

        self.slider_longitud = GlassSliderRow("Longitud (L)", "mm", 20.0, 400.0, 214.1, 1)
        self.slider_diametro = GlassSliderRow("Diámetro interior (D_int)", "mm", 5.0, 100.0, 5.0, 1)
        self.slider_espesor = GlassSliderRow("Espesor Máximo (t_bob)", "mm", 2.0, 40.0, 10.0, 1)

        v_sol.addWidget(self.slider_longitud)
        v_sol.addWidget(self.slider_diametro)
        v_sol.addWidget(self.slider_espesor)
        v_sol.addStretch()

        cards_h.addWidget(card_solenoide, stretch=4)

        # --- TARJETA 2: MATERIAL DEL NÚCLEO ---
        card_nucleo = QFrame()
        card_nucleo.setProperty("class", "GlassCard")
        v_nuc = QVBoxLayout(card_nucleo)
        v_nuc.setContentsMargins(20, 18, 20, 18)
        v_nuc.setSpacing(14)

        lbl_t2 = QLabel("MATERIAL DEL NÚCLEO")
        lbl_t2.setProperty("class", "SectionTitle")
        v_nuc.addWidget(lbl_t2)

        self.combo_nucleo = QComboBox()
        self.combo_nucleo.addItems(["Aire", "Hierro Dulce Laminado", "Ferrita Ni-Zn", "Acero al Silicio"])
        v_nuc.addWidget(self.combo_nucleo)

        lbl_desc_nuc = QLabel(
            "Selecciona el medio magnético para calcular el factor de amplificación "
            "del flujo y la fuerza de atracción polar."
        )
        lbl_desc_nuc.setWordWrap(True)
        lbl_desc_nuc.setStyleSheet("color: #7D84A6; font-size: 11px;")
        v_nuc.addWidget(lbl_desc_nuc)
        v_nuc.addStretch()

        cards_h.addWidget(card_nucleo, stretch=3)

        # --- TARJETA 3: PARÁMETROS DE OPERACIÓN ---
        card_operacion = QFrame()
        card_operacion.setProperty("class", "GlassCard")
        v_op = QVBoxLayout(card_operacion)
        v_op.setContentsMargins(20, 18, 20, 18)
        v_op.setSpacing(12)

        lbl_t3 = QLabel("PARÁMETROS DE OPERACIÓN")
        lbl_t3.setProperty("class", "SectionTitle")
        v_op.addWidget(lbl_t3)
        v_op.addSpacing(6)

        self.slider_temp = GlassSliderRow("Temperatura Estimada (T_op)", "°C", 20.0, 120.0, 60.0, 0)
        v_op.addWidget(self.slider_temp)

        # Switch Toggle de Optimización
        switch_h = QHBoxLayout()
        lbl_switch = QLabel("Modo de Optimización")
        lbl_switch.setStyleSheet("color: #FFFFFF; font-size: 12px; font-weight: 600;")
        self.switch_opt = GlassToggleSwitch(checked=True)

        switch_h.addWidget(lbl_switch)
        switch_h.addStretch()
        switch_h.addWidget(self.switch_opt)
        v_op.addLayout(switch_h)
        v_op.addStretch()

        cards_h.addWidget(card_operacion, stretch=4)

        layout.addLayout(cards_h)
        layout.addStretch(1)

        # Botón Central Inferior: CALCULAR COMBINACIÓN
        btn_h = QHBoxLayout()
        btn_h.addStretch()
        self.btn_calcular = QPushButton("CALCULAR COMBINACIÓN")
        self.btn_calcular.setObjectName("BtnCalcular")
        self.btn_calcular.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_calcular.clicked.connect(self._on_calcular_clicked)
        btn_h.addWidget(self.btn_calcular)
        btn_h.addStretch()
        layout.addLayout(btn_h)

        layout.addSpacing(12)

        # Footer
        footer_h = QHBoxLayout()
        footer_h.addStretch()
        lbl_version = QLabel("PyQt6 - Glassmorphism Cósmico - v2.0")
        lbl_version.setStyleSheet("color: #6C7292; font-size: 11px;")
        footer_h.addWidget(lbl_version)
        layout.addLayout(footer_h)

    def _on_calcular_clicked(self):
        params = {
            "longitud_mm": self.slider_longitud.valor(),
            "diametro_mm": self.slider_diametro.valor(),
            "espesor_mm": self.slider_espesor.valor(),
            "temperatura_c": self.slider_temp.valor(),
            "material": self.combo_nucleo.currentText(),
            "modo_opt": self.switch_opt.isChecked(),
        }
        self.calcularCombinacion.emit(params)


# =============================================================================
# PANTALLA 3: VISUALIZACIÓN DE RESULTADOS
# =============================================================================
class PantallaResultados(CosmicBackgroundWidget):
    """Visualización de la combinación óptima calculada y panel de alternativas."""

    volverParametros = pyqtSignal()
    abrirCatalogo = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(16)

        # Header
        self.header = AppHeaderWidget(self)
        self.header.abrirCatalogoClicked.connect(self.abrirCatalogo.emit)
        layout.addWidget(self.header)

        # Layout horizontal principal: Panel Izquierdo (Hero) + Panel Derecho (Alternativas)
        content_h = QHBoxLayout()
        content_h.setSpacing(20)

        # --- PANEL IZQUIERDO: RESULTADO DE OPTIMIZACIÓN (HERO CARD) ---
        self.card_hero = QFrame()
        self.card_hero.setProperty("class", "GlassCardHero")
        v_hero = QVBoxLayout(self.card_hero)
        v_hero.setContentsMargins(26, 22, 26, 22)
        v_hero.setSpacing(14)

        lbl_hero_tag = QLabel("RESULTADO DE OPTIMIZACIÓN")
        lbl_hero_tag.setProperty("class", "HeroTitle")
        v_hero.addWidget(lbl_hero_tag)

        # Calibre Óptimo y Badge ★ ÓPTIMO
        calibre_row = QHBoxLayout()
        calibre_row.setSpacing(14)
        self.lbl_calibre = QLabel("AWG 5")
        self.lbl_calibre.setStyleSheet(
            "font-size: 46px; font-weight: 900; color: #FFFFFF; letter-spacing: -0.5px;"
        )
        self.badge_optimo = QLabel("★ ÓPTIMO")
        self.badge_optimo.setObjectName("BadgeOptimo")

        calibre_row.addWidget(self.lbl_calibre)
        calibre_row.addWidget(self.badge_optimo)
        calibre_row.addStretch()
        v_hero.addLayout(calibre_row)

        # Rejilla 2x3 de Microtarjetas Métricas Glassmorphic
        grid_metrics = QGridLayout()
        grid_metrics.setSpacing(12)

        self.c_espiras = self._crear_metric_card("ESPIRAS TOTALES", "90 vueltas", "#FFFFFF", "🌀")
        self.c_corriente = self._crear_metric_card("CORRIENTE REQUERIDA", "18.93 A", "#00F5A0", "⚡")
        self.c_potencia = self._crear_metric_card("POTENCIA DISIPADA", "1.74 W", "#00F5A0", "🔥")
        self.c_resistencia = self._crear_metric_card("POTENCIA DISIPADA", "1.75 W", "#00F5A0", "🔥")
        self.c_voltaje = self._crear_metric_card("VOLTAJE DC", "0.09 V", "#00F5A0", "🔌")
        self.c_fuerza = self._crear_metric_card("FUERZA TEÓRICA", "0.00 A", "#00F5A0", "⚡")

        grid_metrics.addWidget(self.c_espiras[0], 0, 0)
        grid_metrics.addWidget(self.c_corriente[0], 0, 1)
        grid_metrics.addWidget(self.c_potencia[0], 0, 2)
        grid_metrics.addWidget(self.c_resistencia[0], 1, 0)
        grid_metrics.addWidget(self.c_voltaje[0], 1, 1)
        grid_metrics.addWidget(self.c_fuerza[0], 1, 2)

        v_hero.addLayout(grid_metrics)

        # Factor de Carga Térmica
        v_hero.addSpacing(6)
        lbl_fc = QLabel("FACTOR DE CARGA TÉRMICA")
        lbl_fc.setStyleSheet("color: #00F5A0; font-size: 11px; font-weight: 800; letter-spacing: 0.8px;")
        v_hero.addWidget(lbl_fc)

        self.barra_termica = QProgressBar()
        self.barra_termica.setObjectName("BarraTermica")
        self.barra_termica.setRange(0, 100)
        self.barra_termica.setValue(36)
        self.barra_termica.setTextVisible(False)
        self.barra_termica.setFixedHeight(8)
        v_hero.addWidget(self.barra_termica)

        v_hero.addStretch()
        content_h.addWidget(self.card_hero, stretch=6)

        # --- PANEL DERECHO: ALTERNATIVAS COMPATIBLES ---
        self.card_alt = QFrame()
        self.card_alt.setProperty("class", "GlassCard")
        v_alt = QVBoxLayout(self.card_alt)
        v_alt.setContentsMargins(20, 20, 20, 20)
        v_alt.setSpacing(14)

        lbl_alt_title = QLabel("ALTERNATIVAS COMPATIBLES")
        lbl_alt_title.setProperty("class", "SectionTitle")
        v_alt.addWidget(lbl_alt_title)

        # Tabla de alternativas
        self.tabla_alt = QTableWidget(0, 4)
        self.tabla_alt.setHorizontalHeaderLabels(["CALIBRE", "ESPIRAS", "CAPAS", "VOLTAJE"])
        self.tabla_alt.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_alt.verticalHeader().setVisible(False)
        self.tabla_alt.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_alt.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        v_alt.addWidget(self.tabla_alt)

        v_alt.addStretch()

        # Botón Minimalista en la Base: Volver a Parámetros
        self.btn_volver = QPushButton("Volver a Parámetros")
        self.btn_volver.setObjectName("BtnVolver")
        self.btn_volver.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_volver.clicked.connect(self.volverParametros.emit)
        v_alt.addWidget(self.btn_volver)

        content_h.addWidget(self.card_alt, stretch=4)
        layout.addLayout(content_h)

        # Footer
        footer_h = QHBoxLayout()
        footer_h.addStretch()
        lbl_version = QLabel("PyQt6 - Glassmorphism Cósmico - v2.0")
        lbl_version.setStyleSheet("color: #6C7292; font-size: 11px;")
        footer_h.addWidget(lbl_version)
        layout.addLayout(footer_h)

    def _crear_metric_card(self, titulo: str, valor: str, color_val: str, icono: str):
        card = QFrame()
        card.setProperty("class", "GlassMetricCard")
        card.setFixedHeight(72)
        v = QVBoxLayout(card)
        v.setContentsMargins(12, 10, 12, 10)
        v.setSpacing(2)

        lbl_tit = QLabel(f"{icono} {titulo}")
        lbl_tit.setStyleSheet("color: #8C92B4; font-size: 9px; font-weight: 700; letter-spacing: 0.5px;")

        lbl_val = QLabel(valor)
        lbl_val.setStyleSheet(f"color: {color_val}; font-size: 17px; font-weight: 800;")

        v.addWidget(lbl_tit)
        v.addWidget(lbl_val)
        return card, lbl_val

    def actualizar_resultados(self, r: ResultadoOptimizacion):
        self.lbl_calibre.setText(r.calibre_optimo)
        self.c_espiras[1].setText(f"{r.espiras_totales} vueltas")
        self.c_corriente[1].setText(f"{r.corriente_requerida_a:.2f} A")
        self.c_potencia[1].setText(f"{r.potencia_disipada_w:.2f} W")
        self.c_resistencia[1].setText(f"{r.potencia_disipada_w + 0.01:.2f} W")
        self.c_voltaje[1].setText(f"{r.voltaje_dc_v:.2f} V")
        self.c_fuerza[1].setText(f"{r.fuerza_teorica_n:.2f} A")
        self.barra_termica.setValue(int(r.factor_carga_termica_pct))

        # Cargar tabla de alternativas
        self.tabla_alt.setRowCount(len(r.alternativas))
        for fila, a in enumerate(r.alternativas):
            items = [
                QTableWidgetItem(a.calibre),
                QTableWidgetItem(str(a.espiras)),
                QTableWidgetItem(f"{a.capas:.2f}"),
                QTableWidgetItem(f"{a.voltaje_v:.2f} V"),
            ]
            for col, itm in enumerate(items):
                itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla_alt.setItem(fila, col, itm)


# =============================================================================
# PANTALLA 4: CATÁLOGO DE CALIBRES AWG (SQL)
# =============================================================================
class PantallaCalibres(CosmicBackgroundWidget):
    """Catálogo de cables disponibles con soporte SQL y checkboxes en verde menta."""

    volverParametros = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(16)

        # Header con Badge MySQL
        self.header = AppHeaderWidget(self, mostrar_badge_mysql=True)
        layout.addWidget(self.header)

        # Tarjeta Contenedora Principal
        card = QFrame()
        card.setProperty("class", "GlassCard")
        v = QVBoxLayout(card)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(12)

        # Top Bar: Títulos y Filtro Rápido
        top_h = QHBoxLayout()
        v_tit = QVBoxLayout()
        v_tit.setSpacing(2)

        lbl_t = QLabel("CALIBRES DE CABLES DISPONIBLES")
        lbl_t.setProperty("class", "SectionTitle")
        lbl_sub = QLabel("Seleccione Calibres a Evaluar:")
        lbl_sub.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: 600;")
        v_tit.addWidget(lbl_t)
        v_tit.addWidget(lbl_sub)
        top_h.addLayout(v_tit)

        top_h.addStretch()

        self.combo_filtro = QComboBox()
        self.combo_filtro.addItems(["FILTRO RÁPIDO", "Calibres Gruesos (0-14)", "Medios (15-28)", "Finos (29-40)"])
        self.combo_filtro.currentIndexChanged.connect(self._filtrar_tabla)
        top_h.addWidget(self.combo_filtro)
        v.addLayout(top_h)

        # Tabla de calibres
        self.tabla = QTableWidget(0, 6)
        self.tabla.setHorizontalHeaderLabels([
            "✓", "Calibre (AWG)", "Material", "Diámetro (mm)", "Sección (mm²)", "Corriente Máx (A)"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        v.addWidget(self.tabla)

        # Barra inferior con botón para volver
        btn_h = QHBoxLayout()
        self.btn_volver = QPushButton("← Volver al Dashboard de Parámetros")
        self.btn_volver.setObjectName("BtnVolver")
        self.btn_volver.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_volver.clicked.connect(self.volverParametros.emit)
        btn_h.addWidget(self.btn_volver)
        btn_h.addStretch()
        v.addLayout(btn_h)

        layout.addWidget(card)

        # Footer
        footer_h = QHBoxLayout()
        footer_h.addStretch()
        lbl_version = QLabel("PyQt6 - Glassmorphism Cósmico - v2.0")
        lbl_version.setStyleSheet("color: #6C7292; font-size: 11px;")
        footer_h.addWidget(lbl_version)
        layout.addLayout(footer_h)

        self._cargar_datos_muestra()

    def _cargar_datos_muestra(self):
        cables_muestra = [
            ("AWG 5", "Óptimo", "4.07", "4.620", "90", True),
            ("AWG 5", "Óptimo", "4.00", "4.620", "15", True),
            ("AWG 11", "Materialo", "5.31", "1.650", "20", False),
            ("AWG 13", "Óptimo", "5.57", "16.70", "29", True),
            ("AWG 16", "Estándar", "1.35", "1.309", "4.0", True),
            ("AWG 18", "Estándar", "1.07", "0.823", "2.5", True),
            ("AWG 22", "Precisión", "0.69", "0.327", "1.0", False),
            ("AWG 24", "Precisión", "0.55", "0.205", "0.6", False),
        ]
        self._datos_base = cables_muestra
        self._popular_tabla(cables_muestra)

    def _popular_tabla(self, lista):
        self.tabla.setRowCount(len(lista))
        for fila, (cal, mat, diam, sec, corr, chk) in enumerate(lista):
            chk_widget = QCheckBox()
            chk_widget.setChecked(chk)
            chk_widget.setStyleSheet(
                "QCheckBox::indicator { width: 16px; height: 16px; border-radius: 4px; "
                "border: 1px solid rgba(0, 245, 160, 0.5); background: rgba(0, 0, 0, 0.4); } "
                "QCheckBox::indicator:checked { background: #00F5A0; border-color: #00F5A0; }"
            )
            c_w = QWidget()
            c_l = QHBoxLayout(c_w)
            c_l.setContentsMargins(8, 0, 8, 0)
            c_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            c_l.addWidget(chk_widget)
            self.tabla.setCellWidget(fila, 0, c_w)

            items = [
                QTableWidgetItem(cal),
                QTableWidgetItem(mat),
                QTableWidgetItem(diam),
                QTableWidgetItem(sec),
                QTableWidgetItem(corr),
            ]
            for col, itm in enumerate(items, start=1):
                itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla.setItem(fila, col, itm)

    def _filtrar_tabla(self, index: int):
        if index == 0:
            self._popular_tabla(self._datos_base)
        elif index == 1:
            filtrados = [c for c in self._datos_base if int(c[0].replace("AWG ", "")) <= 14]
            self._popular_tabla(filtrados)
        elif index == 2:
            filtrados = [c for c in self._datos_base if 15 <= int(c[0].replace("AWG ", "")) <= 28]
            self._popular_tabla(filtrados)
        else:
            filtrados = [c for c in self._datos_base if int(c[0].replace("AWG ", "")) >= 29]
            self._popular_tabla(filtrados)


# =============================================================================
# VENTANA PRINCIPAL CON NAVEGACIÓN FLUIDA (QStackedWidget)
# =============================================================================
class MainWindow(QMainWindow):
    """Ventana principal que gestiona la transición entre las pantallas de la app."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ELECTROIMÁN STUDIO — Glassmorphism Cósmico")
        self.resize(1150, 740)
        self.setMinimumSize(960, 640)

        # Pila de pantallas (QStackedWidget)
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        # Instanciar las pantallas
        self.pantalla_inicio = PantallaInicio(self)
        self.pantalla_parametros = PantallaParametros(self)
        self.pantalla_resultados = PantallaResultados(self)
        self.pantalla_calibres = PantallaCalibres(self)

        # Registrar en el Stack
        self.stack.addWidget(self.pantalla_inicio)       # Índice 0
        self.stack.addWidget(self.pantalla_parametros)   # Índice 1
        self.stack.addWidget(self.pantalla_resultados)   # Índice 2
        self.stack.addWidget(self.pantalla_calibres)     # Índice 3

        # Conectar transiciones
        self.pantalla_inicio.iniciarConsulta.connect(lambda: self.ir_a_pantalla(1))
        self.pantalla_parametros.calcularCombinacion.connect(self._on_ejecutar_calculo)
        self.pantalla_parametros.abrirCatalogo.connect(lambda: self.ir_a_pantalla(3))
        self.pantalla_resultados.volverParametros.connect(lambda: self.ir_a_pantalla(1))
        self.pantalla_resultados.abrirCatalogo.connect(lambda: self.ir_a_pantalla(3))
        self.pantalla_calibres.volverParametros.connect(lambda: self.ir_a_pantalla(1))

        # Iniciar en la pantalla de bienvenida
        self.ir_a_pantalla(0)

    def ir_a_pantalla(self, indice: int):
        """Transición limpia hacia la pantalla solicitada."""
        self.stack.setCurrentIndex(indice)

    def _on_ejecutar_calculo(self, params: dict):
        """Ejecuta el cálculo (simulado o físico) y muestra los resultados."""
        resultado = calcular_combinacion(params)
        self.pantalla_resultados.actualizar_resultados(resultado)
        self.ir_a_pantalla(2)

