"""Pestaña de simulación y cálculo de la combinación ideal de electroimán."""

from datetime import datetime
import math
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from interfaz.styles import CosmicColors
from interfaz.widgets.glass_cards import (
    GlassCard,
    GlassHeroCard,
    GlassMetricCard,
    StatusBadge,
    ThermalSafetyBar,
)
from interfaz.widgets.glass_slider import GlassParamSlider
from src.db.database_manager import DatabaseManager
from src.errores import ElectroimanError
from src.modelos import Cable, ResultadoSolenoide
from src.optimizador import evaluar_configuraciones


class SimulatorTab(QWidget):
    """Pestaña interactiva de diseño y optimización de electroimanes."""

    solicitarConfigSQL = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.db_manager = DatabaseManager.obtener_instancia()
        self.resultado_actual: Optional[ResultadoSolenoide] = None
        self.alternativas_actuales: list[ResultadoSolenoide] = []

        self._init_ui()
        # Realizamos el cálculo inicial de bienvenida
        self.calcular_optimo()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # Splitter horizontal para que el usuario pueda ajustar el ancho de los paneles
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(8)

        # Panel Izquierdo: Controles y Parámetros
        panel_izquierdo = self._crear_panel_controles()
        splitter.addWidget(panel_izquierdo)

        # Panel Derecho: Resultados, Hero Card y Alternativas
        panel_derecho = self._crear_panel_resultados()
        splitter.addWidget(panel_derecho)

        # Distribución de proporciones iniciales (42% izquierda, 58% derecha)
        splitter.setSizes([450, 650])
        main_layout.addWidget(splitter)

    # -------------------------------------------------------------------------
    # PANEL DE CONTROLES
    # -------------------------------------------------------------------------
    def _crear_panel_controles(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(4, 4, 10, 4)
        layout.setSpacing(12)

        card_controles = GlassCard()
        card_layout = QVBoxLayout(card_controles)
        card_layout.setContentsMargins(20, 18, 20, 20)
        card_layout.setSpacing(14)

        # Título del panel
        lbl_titulo = QLabel("⚙️ Parámetros de Diseño")
        lbl_titulo.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {CosmicColors.TEXT_PRIMARY};"
        )
        lbl_sub = QLabel("Ajusta los deslizadores para simular la configuración física.")
        lbl_sub.setStyleSheet(f"color: {CosmicColors.TEXT_SECONDARY}; font-size: 11px;")
        card_layout.addWidget(lbl_titulo)
        card_layout.addWidget(lbl_sub)

        # Selector de Presets Rápidos
        preset_layout = QHBoxLayout()
        lbl_preset = QLabel("Preset de fábrica:")
        lbl_preset.setStyleSheet(f"color: {CosmicColors.TEXT_SECONDARY}; font-weight: 600; font-size: 11px;")
        self.combo_presets = QComboBox()
        self.combo_presets.addItem("🎯 Personalizado", None)
        self.combo_presets.addItem("⚡ Solenoide Estándar (10 mT, 100mm)", (0.010, 100.0, 20.0, 10.0))
        self.combo_presets.addItem("🔬 Solenoide Didáctico (5 mT, 120mm)", (0.005, 120.0, 25.0, 8.0))
        self.combo_presets.addItem("🧲 Electroimán Robusto (25 mT, 80mm)", (0.025, 80.0, 18.0, 12.0))
        self.combo_presets.addItem("🔋 Actuador Compacto (15 mT, 50mm)", (0.015, 50.0, 15.0, 8.0))
        self.combo_presets.currentIndexChanged.connect(self._on_preset_seleccionado)
        preset_layout.addWidget(lbl_preset)
        preset_layout.addWidget(self.combo_presets, stretch=1)
        card_layout.addLayout(preset_layout)

        # Separador fino
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: rgba(255, 255, 255, 0.08); max-height: 1px;")
        card_layout.addWidget(sep)

        # Sliders con estilo Neón
        self.slider_campo = GlassParamSlider(
            titulo="Campo Magnético Objetivo",
            simbolo="B",
            unidad="T",
            min_val=0.001,
            max_val=0.050,
            val_default=0.010,
            paso=0.001,
            decimales=3,
            tooltip="Densidad de flujo magnético requerida en el centro del solenoide (Teslas).",
        )
        self.slider_longitud = GlassParamSlider(
            titulo="Longitud del Solenoide",
            simbolo="L",
            unidad="mm",
            min_val=20.0,
            max_val=400.0,
            val_default=100.0,
            paso=5.0,
            decimales=1,
            tooltip="Largo total del carrete o tubo donde se bobinará el conductor.",
        )
        self.slider_diametro = GlassParamSlider(
            titulo="Diámetro Interior del Carrete",
            simbolo="D_int",
            unidad="mm",
            min_val=5.0,
            max_val=100.0,
            val_default=20.0,
            paso=1.0,
            decimales=1,
            tooltip="Diámetro interior del núcleo donde inicia la primera capa de espiras.",
        )
        self.slider_espesor = GlassParamSlider(
            titulo="Espesor Máximo de Bobinado",
            simbolo="t_bob",
            unidad="mm",
            min_val=2.0,
            max_val=40.0,
            val_default=10.0,
            paso=1.0,
            decimales=1,
            tooltip="Espacio radial libre disponible para superponer capas de cable.",
        )
        self.slider_temp = GlassParamSlider(
            titulo="Temperatura de Operación Estimada",
            simbolo="T_op",
            unidad="°C",
            min_val=20.0,
            max_val=120.0,
            val_default=60.0,
            paso=5.0,
            decimales=0,
            tooltip="Temperatura de trabajo para calcular la resistencia del cobre y seguridad térmica.",
        )

        card_layout.addWidget(self.slider_campo)
        card_layout.addWidget(self.slider_longitud)
        card_layout.addWidget(self.slider_diametro)
        card_layout.addWidget(self.slider_espesor)
        card_layout.addWidget(self.slider_temp)

        # Selector de Núcleo Magnético (Permeabilidad)
        nucleo_layout = QHBoxLayout()
        lbl_nucleo = QLabel("Material del Núcleo:")
        lbl_nucleo.setStyleSheet(f"color: {CosmicColors.TEXT_SECONDARY}; font-weight: 600; font-size: 11px;")
        self.combo_nucleo = QComboBox()
        self.combo_nucleo.addItem("Aire / Vacío (μ_r = 1.0)", 1.0)
        self.combo_nucleo.addItem("Hierro Dulce Laminado (μ_r = 250.0)", 250.0)
        self.combo_nucleo.addItem("Ferrita Ni-Zn (μ_r = 50.0)", 50.0)
        self.combo_nucleo.addItem("Acero al Silicio (μ_r = 500.0)", 500.0)
        self.combo_nucleo.currentIndexChanged.connect(self._on_param_cambiado)
        nucleo_layout.addWidget(lbl_nucleo)
        nucleo_layout.addWidget(self.combo_nucleo, stretch=1)
        card_layout.addLayout(nucleo_layout)

        # Opciones de comportamiento
        self.chk_tiempo_real = QCheckBox("⚡ Optimización en tiempo real (Feedback continuo)")
        self.chk_tiempo_real.setChecked(True)
        self.chk_tiempo_real.setStyleSheet(
            f"color: {CosmicColors.TEXT_SECONDARY}; font-size: 11px; font-weight: 600; margin-top: 4px;"
        )
        card_layout.addWidget(self.chk_tiempo_real)

        # Botón Principal de Acción
        self.btn_calcular = QPushButton("⚡ CALCULAR COMBINACIÓN ÓPTIMA")
        self.btn_calcular.setObjectName("BtnPrimary")
        self.btn_calcular.setMinimumHeight(44)
        self.btn_calcular.clicked.connect(self.calcular_optimo)
        card_layout.addWidget(self.btn_calcular)

        # Conectar eventos de cambio en sliders
        self.slider_campo.valorCambiado.connect(self._on_param_cambiado)
        self.slider_longitud.valorCambiado.connect(self._on_param_cambiado)
        self.slider_diametro.valorCambiado.connect(self._on_param_cambiado)
        self.slider_espesor.valorCambiado.connect(self._on_param_cambiado)
        self.slider_temp.valorCambiado.connect(self._on_param_cambiado)

        layout.addWidget(card_controles)
        layout.addStretch()
        scroll.setWidget(contenedor)
        return scroll

    # -------------------------------------------------------------------------
    # PANEL DE RESULTADOS
    # -------------------------------------------------------------------------
    def _crear_panel_resultados(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(4, 4, 10, 4)
        layout.setSpacing(14)

        # 1. HERO CARD: COMBINACIÓN IDEAL
        self.hero_card = GlassHeroCard()
        hero_layout = QVBoxLayout(self.hero_card)
        hero_layout.setContentsMargins(24, 22, 24, 22)
        hero_layout.setSpacing(14)

        # Encabezado del Hero
        hero_header = QHBoxLayout()
        self.badge_estado = StatusBadge("Óptimo Calculado", "ok")

        lbl_hero_tag = QLabel("RESULTADO DE OPTIMIZACIÓN HEURÍSTICA")
        lbl_hero_tag.setStyleSheet(
            f"color: {CosmicColors.ACCENT_MINT}; font-size: 11px; font-weight: 800; "
            "letter-spacing: 1px; text-transform: uppercase;"
        )
        hero_header.addWidget(lbl_hero_tag)
        hero_header.addStretch()
        hero_header.addWidget(self.badge_estado)
        hero_layout.addLayout(hero_header)

        # Destacado del Calibre AWG
        calibre_row = QHBoxLayout()
        calibre_row.setSpacing(16)

        self.lbl_calibre_hero = QLabel("AWG 5")
        self.lbl_calibre_hero.setStyleSheet(
            f"font-size: 38px; font-weight: 900; color: {CosmicColors.TEXT_PRIMARY}; "
            f"letter-spacing: -0.5px;"
        )
        self.lbl_calibre_detalles = QLabel(
            "Diámetro esmalte: 4.70 mm  •  Cobre: 4.62 mm  •  Área: 16.77 mm²"
        )
        self.lbl_calibre_detalles.setStyleSheet(
            f"color: {CosmicColors.TEXT_SECONDARY}; font-size: 13px; font-weight: 500;"
        )

        calibre_info_v = QVBoxLayout()
        calibre_info_v.setSpacing(2)
        calibre_info_v.addWidget(self.lbl_calibre_hero)
        calibre_info_v.addWidget(self.lbl_calibre_detalles)

        calibre_row.addLayout(calibre_info_v, stretch=1)
        hero_layout.addLayout(calibre_row)

        # Barra de utilización térmica
        self.thermal_bar = ThermalSafetyBar()
        hero_layout.addWidget(self.thermal_bar)

        # Rejilla de Métricas Clave
        metricas_grid = QGridLayout()
        metricas_grid.setSpacing(10)

        self.card_espiras = GlassMetricCard("Espiras Totales", "--", "vueltas", "🌀")
        self.card_corriente = GlassMetricCard("Corriente Requerida", "--", "A", "⚡")
        self.card_calor = GlassMetricCard("Potencia Disipada", "--", "W", "🔥")
        self.card_voltaje = GlassMetricCard("Voltaje DC", "--", "V", "🔌")
        self.card_longitud = GlassMetricCard("Longitud Alambre", "--", "m", "📏")
        self.card_resistencia = GlassMetricCard("Resistencia (T_op)", "--", "Ω", "🛡️")
        self.card_masa = GlassMetricCard("Masa Cobre", "--", "g", "⚖️")
        self.card_fuerza = GlassMetricCard("Fuerza Teórica Cara", "--", "N", "🧲")

        metricas_grid.addWidget(self.card_espiras, 0, 0)
        metricas_grid.addWidget(self.card_corriente, 0, 1)
        metricas_grid.addWidget(self.card_calor, 0, 2)
        metricas_grid.addWidget(self.card_voltaje, 0, 3)
        metricas_grid.addWidget(self.card_longitud, 1, 0)
        metricas_grid.addWidget(self.card_resistencia, 1, 1)
        metricas_grid.addWidget(self.card_masa, 1, 2)
        metricas_grid.addWidget(self.card_fuerza, 1, 3)

        hero_layout.addLayout(metricas_grid)
        layout.addWidget(self.hero_card)

        # 2. SECCIÓN: ALTERNATIVAS VIABLES (TOP 5)
        card_alternativas = GlassCard()
        alt_layout = QVBoxLayout(card_alternativas)
        alt_layout.setContentsMargins(18, 16, 18, 16)
        alt_layout.setSpacing(10)

        alt_header = QHBoxLayout()
        lbl_alt_titulo = QLabel("📊 Alternativas Viables Evaluadas")
        lbl_alt_titulo.setStyleSheet(
            f"font-size: 14px; font-weight: 700; color: {CosmicColors.TEXT_PRIMARY};"
        )
        self.lbl_alt_count = QLabel("Mostrando opciones ordenadas por eficiencia")
        self.lbl_alt_count.setStyleSheet(f"color: {CosmicColors.TEXT_SECONDARY}; font-size: 11px;")

        alt_header.addWidget(lbl_alt_titulo)
        alt_header.addStretch()
        alt_header.addWidget(self.lbl_alt_count)
        alt_layout.addLayout(alt_header)

        # Tabla de alternativas
        self.tabla_alternativas = QTableWidget(0, 6)
        self.tabla_alternativas.setHorizontalHeaderLabels([
            "Calibre", "Espiras", "Capas", "Corriente (A)", "Potencia (W)", "Voltaje (V)"
        ])
        self.tabla_alternativas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_alternativas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_alternativas.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla_alternativas.verticalHeader().setVisible(False)
        self.tabla_alternativas.setFixedHeight(160)
        self.tabla_alternativas.itemSelectionChanged.connect(self._on_alternativa_seleccionada)
        alt_layout.addWidget(self.tabla_alternativas)

        layout.addWidget(card_alternativas)

        # 3. BARRA DE ACCIONES INFERIOR
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(10)

        self.btn_copiar = QPushButton("📋 Copiar Ficha Técnica")
        self.btn_copiar.setObjectName("BtnSecondary")
        self.btn_copiar.clicked.connect(self._copiar_reporte_portapapeles)

        self.btn_exportar = QPushButton("📄 Exportar Reporte (.txt)")
        self.btn_exportar.setObjectName("BtnSecondary")
        self.btn_exportar.clicked.connect(self._exportar_reporte_archivo)

        btn_bar.addStretch()
        btn_bar.addWidget(self.btn_copiar)
        btn_bar.addWidget(self.btn_exportar)
        layout.addLayout(btn_bar)

        layout.addStretch()
        scroll.setWidget(contenedor)
        return scroll

    # -------------------------------------------------------------------------
    # LÓGICA DE NEGOCIO Y CÁLCULOS
    # -------------------------------------------------------------------------
    def _on_param_cambiado(self):
        """Maneja el evento de actualización de cualquiera de los controles."""
        if self.chk_tiempo_real.isChecked():
            self.calcular_optimo()

    def _on_preset_seleccionado(self, index: int):
        datos = self.combo_presets.currentData()
        if datos:
            campo, long_mm, diam_mm, esp_mm = datos
            self.slider_campo.set_valor(campo)
            self.slider_longitud.set_valor(long_mm)
            self.slider_diametro.set_valor(diam_mm)
            self.slider_espesor.set_valor(esp_mm)
            self.calcular_optimo()

    def calcular_optimo(self):
        """Ejecuta la optimización heurística con los parámetros actuales."""
        campo_b = self.slider_campo.valor()
        longitud_m = self.slider_longitud.valor() / 1000.0
        diametro_m = self.slider_diametro.valor() / 1000.0
        espesor_m = self.slider_espesor.valor() / 1000.0
        temp_c = self.slider_temp.valor()
        mu_r = float(self.combo_nucleo.currentData() or 1.0)

        catalogo = self.db_manager.obtener_calibres()
        if not catalogo:
            self._mostrar_estado_error("No hay calibres cargados en la base de datos.")
            return

        try:
            mejor, viables = evaluar_configuraciones(
                campo_b_teslas=campo_b,
                longitud_m=longitud_m,
                diametro_carrete_m=diametro_m,
                espesor_max_m=espesor_m,
                catalogo=catalogo,
                temp_operacion_c=temp_c,
                permeabilidad_relativa=mu_r,
            )
            self.resultado_actual = mejor
            self.alternativas_actuales = viables
            self._mostrar_resultado_exitoso(mejor, viables)

        except ElectroimanError as err:
            self.resultado_actual = None
            self.alternativas_actuales = []
            self._mostrar_estado_error(str(err))
        except Exception as exc:  # pylint: disable=broad-except
            self.resultado_actual = None
            self.alternativas_actuales = []
            self._mostrar_estado_error(f"Error imprevisto en simulación: {exc}")

    def _mostrar_resultado_exitoso(self, res: ResultadoSolenoide, viables: list[ResultadoSolenoide]):
        self.badge_estado.set_estado("Configuración Óptima", "ok")

        c = res.cable_seleccionado
        self.lbl_calibre_hero.setText(f"AWG {c.id_calibre}")
        self.lbl_calibre_detalles.setText(
            f"Diámetro esmalte: {c.diametro_con_esmalte_mm:.3f} mm  •  "
            f"Cobre puro: {c.diametro_cobre_mm:.3f} mm  •  "
            f"Sección: {c.area_seccion_transversal_mm2:.3f} mm²  •  "
            f"Corriente máx: {c.corriente_max_amp:.1f} A"
        )

        self.thermal_bar.set_porcentaje(res.porcentaje_capacidad_termica)

        # Actualizar métricas
        self.card_espiras.set_valor(f"{res.numero_espiras_total}", f"({res.capas} capas)")
        self.card_corriente.set_valor(f"{res.corriente_necesaria_amp:.2f}", f"/ {c.corriente_max_amp:.1f} A")
        self.card_calor.set_valor(f"{res.potencia_disipada_watts:.2f}")
        self.card_voltaje.set_valor(f"{res.voltaje_necesario_volt:.2f}")
        self.card_longitud.set_valor(f"{res.longitud_alambre_m:.2f}")
        self.card_resistencia.set_valor(f"{res.resistencia_operacion_ohm:.3f}")

        masa_g = res.masa_alambre_kg * 1000.0
        if masa_g >= 1000:
            self.card_masa.set_valor(f"{res.masa_alambre_kg:.2f}", "kg")
        else:
            self.card_masa.set_valor(f"{masa_g:.1f}", "g")

        self.card_fuerza.set_valor(
            f"{res.fuerza_atraccion_estimada_n:.2f}",
            f"({res.fuerza_atraccion_estimada_kgf:.2f} kgf)"
        )

        # Llenar tabla de alternativas
        self._cargar_tabla_alternativas(viables[:8])

    def _mostrar_estado_error(self, mensaje: str):
        self.badge_estado.set_estado("Inviable", "error")
        self.lbl_calibre_hero.setText("Sin Solución Viable")
        self.lbl_calibre_detalles.setText(mensaje)
        self.thermal_bar.set_porcentaje(0.0)

        self.card_espiras.set_valor("--")
        self.card_corriente.set_valor("--")
        self.card_calor.set_valor("--")
        self.card_voltaje.set_valor("--")
        self.card_longitud.set_valor("--")
        self.card_resistencia.set_valor("--")
        self.card_masa.set_valor("--")
        self.card_fuerza.set_valor("--")

        self.tabla_alternativas.setRowCount(0)
        self.lbl_alt_count.setText("0 combinaciones viables")

    def _cargar_tabla_alternativas(self, lista: list[ResultadoSolenoide]):
        self.tabla_alternativas.setRowCount(len(lista))
        self.lbl_alt_count.setText(f"{len(self.alternativas_actuales)} viables (Top {len(lista)} en tabla)")

        for fila, item in enumerate(lista):
            cal_str = f"AWG {item.cable_seleccionado.id_calibre}"
            if fila == 0:
                cal_str += " ⭐ (Óptimo)"

            items = [
                QTableWidgetItem(cal_str),
                QTableWidgetItem(str(item.numero_espiras_total)),
                QTableWidgetItem(f"{item.capas} capas ({item.espiras_por_capa} e/c)"),
                QTableWidgetItem(f"{item.corriente_necesaria_amp:.2f} A"),
                QTableWidgetItem(f"{item.potencia_disipada_watts:.2f} W"),
                QTableWidgetItem(f"{item.voltaje_necesario_volt:.2f} V"),
            ]
            for col, itm in enumerate(items):
                itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if fila == 0:
                    itm.setForeground(Qt.GlobalColor.green)
                self.tabla_alternativas.setItem(fila, col, itm)

    def _on_alternativa_seleccionada(self):
        filas = self.tabla_alternativas.selectedItems()
        if not filas:
            return
        row = self.tabla_alternativas.currentRow()
        if 0 <= row < len(self.alternativas_actuales):
            alt = self.alternativas_actuales[row]
            # Si el usuario hace clic en una alternativa, actualizamos las tarjetas para inspeccionarla
            self._mostrar_resultado_exitoso(alt, self.alternativas_actuales)

    # -------------------------------------------------------------------------
    # EXPORTACIÓN Y REPORTES
    # -------------------------------------------------------------------------
    def _generar_texto_reporte(self) -> str:
        if not self.resultado_actual:
            return "No hay resultados calculados actualmente."

        res = self.resultado_actual
        c = res.cable_seleccionado

        return (
            "==========================================================\n"
            "   FICHA TÉCNICA - DISEÑO COMPUTACIONAL DE ELECTROIMÁN\n"
            "==========================================================\n"
            f"Fecha de cálculo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Origen de datos: {self.db_manager.modo_actual}\n\n"
            "--- PARÁMETROS OBJETIVO INGRESADOS ---\n"
            f"• Campo magnético deseado (B): {self.slider_campo.valor():.4f} T\n"
            f"• Longitud del solenoide (L):   {self.slider_longitud.valor():.1f} mm\n"
            f"• Diámetro interior carrete (D): {self.slider_diametro.valor():.1f} mm\n"
            f"• Espesor máximo bobinado (t):   {self.slider_espesor.valor():.1f} mm\n"
            f"• Temperatura de operación:    {self.slider_temp.valor():.0f} °C\n"
            f"• Núcleo magnético:             {self.combo_nucleo.currentText()}\n\n"
            "--- CONFIGURACIÓN ÓPTIMA CALCULADA ---\n"
            f"• Conductor seleccionado:       AWG {c.id_calibre}\n"
            f"• Diámetro exterior (c/esmalte): {c.diametro_con_esmalte_mm:.3f} mm\n"
            f"• Diámetro núcleo de cobre:     {c.diametro_cobre_mm:.3f} mm\n"
            f"• Número de capas:              {res.capas}\n"
            f"• Espiras por capa:             {res.espiras_por_capa}\n"
            f"• Total de espiras (N):         {res.numero_espiras_total}\n"
            f"• Corriente requerida (I):      {res.corriente_necesaria_amp:.2f} A\n"
            f"• Corriente máxima admisible:   {c.corriente_max_amp:.2f} A (Margen: {res.margen_seguridad_termico_amp:.2f} A)\n"
            f"• Carga térmica de corriente:   {res.porcentaje_capacidad_termica:.1f} %\n"
            f"• Tensión requerida (DC):       {res.voltaje_necesario_volt:.2f} V\n"
            f"• Resistencia eléctrica (T_op): {res.resistencia_operacion_ohm:.4f} Ω\n"
            f"• Potencia disipada (Calor):    {res.potencia_disipada_watts:.2f} W (Joule)\n"
            f"• Densidad de corriente (J):    {res.densidad_corriente_a_mm2:.2f} A/mm²\n"
            f"• Longitud total de alambre:    {res.longitud_alambre_m:.2f} m\n"
            f"• Masa total de alambre:        {res.masa_alambre_kg * 1000.0:.1f} g\n"
            f"• Fuerza teórica polar cara:    {res.fuerza_atraccion_estimada_n:.2f} N ({res.fuerza_atraccion_estimada_kgf:.2f} kgf)\n"
            "==========================================================\n"
        )

    def _copiar_reporte_portapapeles(self):
        texto = self._generar_texto_reporte()
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(texto)
            QMessageBox.information(
                self,
                "Ficha Técnica Copiada",
                "Los parámetros y métricas de la combinación ideal han sido copiados al portapapeles.",
            )

    def _exportar_reporte_archivo(self):
        texto = self._generar_texto_reporte()
        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Reporte Técnico",
            "reporte_electroiman.txt",
            "Archivos de Texto (*.txt);;Markdown (*.md);;Todos los archivos (*.*)",
        )
        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(texto)
                QMessageBox.information(
                    self,
                    "Reporte Exportado",
                    f"El reporte técnico se ha guardado exitosamente en:\n{ruta}",
                )
            except Exception as e:
                QMessageBox.critical(self, "Error al guardar", f"No se pudo guardar el archivo:\n{e}")

