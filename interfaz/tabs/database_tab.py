"""Pestaña de consulta, filtrado e inspección de calibres AWG vinculada a la capa SQL."""

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from interfaz.styles import CosmicColors
from interfaz.widgets.glass_cards import GlassCard, StatusBadge
from src.db.database_manager import DatabaseManager
from src.modelos import Cable


class DatabaseTab(QWidget):
    """Pestaña para visualizar y filtrar el catálogo SQL de calibres y evaluar compatibilidad."""

    solicitarConfigSQL = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.db_manager = DatabaseManager.obtener_instancia()
        self.calibre_seleccionado: Optional[Cable] = None

        self._init_ui()
        self.recargar_calibres()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(8)

        # Columna Izquierda: Tabla y Filtros SQL
        col_tabla = self._crear_panel_tabla()
        splitter.addWidget(col_tabla)

        # Columna Derecha: Inspector de Calibre y Compatibilidad
        col_inspector = self._crear_panel_inspector()
        splitter.addWidget(col_inspector)

        splitter.setSizes([750, 400])
        main_layout.addWidget(splitter)

    # -------------------------------------------------------------------------
    # PANEL DE TABLA Y FILTROS
    # -------------------------------------------------------------------------
    def _crear_panel_tabla() -> QWidget:
        pass  # se define abajo con self

    def _crear_panel_tabla(self) -> QWidget:
        contenedor = GlassCard()
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # Header con Buscador y Botón de Conexión
        header = QHBoxLayout()
        header.setSpacing(12)

        lbl_titulo = QLabel("📚 Catálogo SQL de Calibres AWG")
        lbl_titulo.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {CosmicColors.TEXT_PRIMARY};"
        )
        header.addWidget(lbl_titulo)
        header.addStretch()

        self.btn_config_sql = QPushButton("⚙️ Conexión MySQL...")
        self.btn_config_sql.setObjectName("BtnSecondary")
        self.btn_config_sql.clicked.connect(self.solicitarConfigSQL.emit)
        header.addWidget(self.btn_config_sql)

        layout.addLayout(header)

        # Barra de Búsqueda y Filtros Rápidos
        search_bar = QHBoxLayout()
        search_bar.setSpacing(8)

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("🔍 Filtrar por número AWG (ej. 14, 22)...")
        self.txt_buscar.textChanged.connect(self.recargar_calibres)
        search_bar.addWidget(self.txt_buscar, stretch=1)

        self.btn_filtro_todos = QPushButton("Todos")
        self.btn_filtro_todos.setObjectName("BtnSecondary")
        self.btn_filtro_todos.clicked.connect(lambda: self._aplicar_filtro_rango(None, None))

        self.btn_filtro_gruesos = QPushButton("Gruesos (0-14)")
        self.btn_filtro_gruesos.setObjectName("BtnSecondary")
        self.btn_filtro_gruesos.clicked.connect(lambda: self._aplicar_filtro_rango(0, 14))

        self.btn_filtro_medios = QPushButton("Medios (15-28)")
        self.btn_filtro_medios.setObjectName("BtnSecondary")
        self.btn_filtro_medios.clicked.connect(lambda: self._aplicar_filtro_rango(15, 28))

        self.btn_filtro_finos = QPushButton("Finos (29-40)")
        self.btn_filtro_finos.setObjectName("BtnSecondary")
        self.btn_filtro_finos.clicked.connect(lambda: self._aplicar_filtro_rango(29, 40))

        search_bar.addWidget(self.btn_filtro_todos)
        search_bar.addWidget(self.btn_filtro_gruesos)
        search_bar.addWidget(self.btn_filtro_medios)
        search_bar.addWidget(self.btn_filtro_finos)

        layout.addLayout(search_bar)

        # Tabla de Datos
        self.tabla = QTableWidget(0, 8)
        self.tabla.setHorizontalHeaderLabels([
            "AWG",
            "Ø Cobre (mm)",
            "Ø Esmalte (mm)",
            "Área (mm²)",
            "Resistencia (Ω/m)",
            "Corriente Máx (A)",
            "Masa (kg/km)",
            "Temp Máx (°C)",
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.itemSelectionChanged.connect(self._on_fila_seleccionada)
        layout.addWidget(self.tabla)

        # Barra inferior de estado de registros
        status_layout = QHBoxLayout()
        self.lbl_contador = QLabel("Cargando catálogo...")
        self.lbl_contador.setStyleSheet(f"color: {CosmicColors.TEXT_MUTED}; font-size: 11px;")
        self.lbl_origen = QLabel(self.db_manager.modo_actual)
        self.lbl_origen.setStyleSheet(f"color: {CosmicColors.ACCENT_CYAN}; font-size: 11px; font-weight: 600;")

        status_layout.addWidget(self.lbl_contador)
        status_layout.addStretch()
        status_layout.addWidget(self.lbl_origen)
        layout.addLayout(status_layout)

        return contenedor

    # -------------------------------------------------------------------------
    # PANEL DE INSPECCIÓN Y COMPATIBILIDAD
    # -------------------------------------------------------------------------
    def _crear_panel_inspector(self) -> QWidget:
        contenedor = GlassCard()
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # Título
        lbl_titulo = QLabel("🔬 Inspector de Compatibilidad")
        lbl_titulo.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {CosmicColors.TEXT_PRIMARY};"
        )
        layout.addWidget(lbl_titulo)

        # Ficha del Calibre Seleccionado
        card_ficha = GlassCard(subtle=True)
        ficha_layout = QVBoxLayout(card_ficha)
        ficha_layout.setContentsMargins(14, 12, 14, 12)
        ficha_layout.setSpacing(8)

        self.lbl_inspector_calibre = QLabel("Selecciona un calibre")
        self.lbl_inspector_calibre.setStyleSheet(
            f"font-size: 22px; font-weight: 800; color: {CosmicColors.ACCENT_MINT};"
        )
        ficha_layout.addWidget(self.lbl_inspector_calibre)

        grid_specs = QGridLayout()
        grid_specs.setSpacing(6)

        self.lbl_spec_diam_cobre = QLabel("--")
        self.lbl_spec_diam_esmalte = QLabel("--")
        self.lbl_spec_area = QLabel("--")
        self.lbl_spec_resistencia = QLabel("--")
        self.lbl_spec_corriente_max = QLabel("--")
        self.lbl_spec_clase_termica = QLabel("--")

        def _formato_label(txt):
            lbl = QLabel(txt)
            lbl.setStyleSheet(f"color: {CosmicColors.TEXT_SECONDARY}; font-size: 11px; font-weight: 600;")
            return lbl

        grid_specs.addWidget(_formato_label("Ø Cobre:"), 0, 0)
        grid_specs.addWidget(self.lbl_spec_diam_cobre, 0, 1)
        grid_specs.addWidget(_formato_label("Ø Esmalte:"), 1, 0)
        grid_specs.addWidget(self.lbl_spec_diam_esmalte, 1, 1)
        grid_specs.addWidget(_formato_label("Área Sección:"), 2, 0)
        grid_specs.addWidget(self.lbl_spec_area, 2, 1)
        grid_specs.addWidget(_formato_label("Resistencia 20°C:"), 3, 0)
        grid_specs.addWidget(self.lbl_spec_resistencia, 3, 1)
        grid_specs.addWidget(_formato_label("Corriente Máx:"), 4, 0)
        grid_specs.addWidget(self.lbl_spec_corriente_max, 4, 1)
        grid_specs.addWidget(_formato_label("Clase Térmica:"), 5, 0)
        grid_specs.addWidget(self.lbl_spec_clase_termica, 5, 1)

        ficha_layout.addLayout(grid_specs)
        layout.addWidget(card_ficha)

        # Módulo de Evaluación de Compatibilidad
        lbl_sub = QLabel("Evaluar Condiciones de Carga:")
        lbl_sub.setStyleSheet(f"color: {CosmicColors.TEXT_SECONDARY}; font-size: 12px; font-weight: 700;")
        layout.addWidget(lbl_sub)

        form_comp = QVBoxLayout()
        form_comp.setSpacing(8)

        # Input de Corriente
        i_layout = QHBoxLayout()
        lbl_i = QLabel("Corriente Requerida (A):")
        lbl_i.setStyleSheet(f"color: {CosmicColors.TEXT_PRIMARY}; font-size: 12px;")
        self.spin_test_i = QDoubleSpinBox()
        self.spin_test_i.setRange(0.01, 200.0)
        self.spin_test_i.setValue(5.0)
        self.spin_test_i.setSuffix(" A")
        self.spin_test_i.valueChanged.connect(self._evaluar_compatibilidad)
        i_layout.addWidget(lbl_i)
        i_layout.addStretch()
        i_layout.addWidget(self.spin_test_i)
        form_comp.addLayout(i_layout)

        # Input de Temperatura
        t_layout = QHBoxLayout()
        lbl_t = QLabel("Temperatura de Trabajo (°C):")
        lbl_t.setStyleSheet(f"color: {CosmicColors.TEXT_PRIMARY}; font-size: 12px;")
        self.spin_test_t = QSpinBox()
        self.spin_test_t.setRange(20, 220)
        self.spin_test_t.setValue(60)
        self.spin_test_t.setSuffix(" °C")
        self.spin_test_t.valueChanged.connect(self._evaluar_compatibilidad)
        t_layout.addWidget(lbl_t)
        t_layout.addStretch()
        t_layout.addWidget(self.spin_test_t)
        form_comp.addLayout(t_layout)

        layout.addLayout(form_comp)

        # Resultado de Compatibilidad
        self.badge_compatibilidad = StatusBadge("Selecciona un calibre", "info")
        layout.addWidget(self.badge_compatibilidad)

        self.lbl_diagnostico = QLabel(
            "Mueve los parámetros de prueba para verificar si el conductor "
            "soporta las condiciones térmicas sin degradarse."
        )
        self.lbl_diagnostico.setWordWrap(True)
        self.lbl_diagnostico.setStyleSheet(
            f"color: {CosmicColors.TEXT_SECONDARY}; font-size: 11px; "
            "background: rgba(255, 255, 255, 0.03); border-radius: 8px; padding: 10px;"
        )
        layout.addWidget(self.lbl_diagnostico)

        layout.addStretch()
        return contenedor

    # -------------------------------------------------------------------------
    # ACCIONES Y CARGA DE DATOS
    # -------------------------------------------------------------------------
    def _aplicar_filtro_rango(self, min_val: Optional[int], max_val: Optional[int]):
        self._filtro_min = min_val
        self._filtro_max = max_val
        self.recargar_calibres()

    def recargar_calibres(self):
        """Consulta calibres a través de DatabaseManager con los filtros aplicados."""
        texto = self.txt_buscar.text().strip()
        min_c = getattr(self, "_filtro_min", None)
        max_c = getattr(self, "_filtro_max", None)

        calibres = self.db_manager.obtener_calibres(
            filtro_texto=texto,
            calibre_min=min_c,
            calibre_max=max_c,
        )

        self._cables_en_tabla = calibres
        self.tabla.setRowCount(len(calibres))
        self.lbl_contador.setText(f"Mostrando {len(calibres)} de {len(self.db_manager.obtener_calibres())} calibres AWG")
        self.lbl_origen.setText(self.db_manager.modo_actual)

        for fila, c in enumerate(calibres):
            items = [
                QTableWidgetItem(f"AWG {c.id_calibre}"),
                QTableWidgetItem(f"{c.diametro_cobre_mm:.3f}"),
                QTableWidgetItem(f"{c.diametro_con_esmalte_mm:.3f}"),
                QTableWidgetItem(f"{c.area_seccion_transversal_mm2:.3f}"),
                QTableWidgetItem(f"{c.resistencia_ohm_por_metro:.5f}"),
                QTableWidgetItem(f"{c.corriente_max_amp:.2f}"),
                QTableWidgetItem(f"{c.masa_kg_por_km:.2f}"),
                QTableWidgetItem(f"{c.temp_max_aislante_c} °C"),
            ]
            for col, itm in enumerate(items):
                itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla.setItem(fila, col, itm)

        if calibres and not self.calibre_seleccionado:
            self.tabla.selectRow(0)

    def _on_fila_seleccionada(self):
        items = self.tabla.selectedItems()
        if not items:
            return
        row = self.tabla.currentRow()
        if 0 <= row < len(self._cables_en_tabla):
            cable = self._cables_en_tabla[row]
            self.calibre_seleccionado = cable
            self._actualizar_inspector(cable)

    def _actualizar_inspector(self, c: Cable):
        self.lbl_inspector_calibre.setText(f"AWG {c.id_calibre}")
        self.lbl_spec_diam_cobre.setText(f"{c.diametro_cobre_mm:.3f} mm")
        self.lbl_spec_diam_esmalte.setText(f"{c.diametro_con_esmalte_mm:.3f} mm")
        self.lbl_spec_area.setText(f"{c.area_seccion_transversal_mm2:.3f} mm²")
        self.lbl_spec_resistencia.setText(f"{c.resistencia_ohm_por_metro:.5f} Ω/m")
        self.lbl_spec_corriente_max.setText(f"{c.corriente_max_amp:.2f} A")
        self.lbl_spec_clase_termica.setText(f"Clase {c.temp_max_aislante_c} °C")

        self._evaluar_compatibilidad()

    def _evaluar_compatibilidad(self):
        if not self.calibre_seleccionado:
            return

        corriente = self.spin_test_i.value()
        temp = self.spin_test_t.value()

        # Invocamos la capa estructurada de DatabaseManager
        reporte = self.db_manager.consultar_compatibilidad(
            id_calibre=self.calibre_seleccionado.id_calibre,
            corriente_requerida_amp=corriente,
            temp_operacion_c=float(temp),
        )

        es_comp = reporte["es_compatible"]
        nivel = reporte["nivel"]
        porcentaje = reporte["porcentaje_carga"]
        margen = reporte["margen_amperios"]
        msg = reporte["mensaje"]

        if nivel in ("optimo", "adecuado"):
            self.badge_compatibilidad.set_estado("Totalmente Compatible", "ok")
        elif nivel == "precaucion":
            self.badge_compatibilidad.set_estado("Precaución Térmica", "advertencia")
        else:
            self.badge_compatibilidad.set_estado("Incompatible / Peligro", "error")

        diagnostico = (
            f"• Factor de carga: {porcentaje:.1f} % de capacidad nominal\n"
            f"• Margen disponible: {margen:+.2f} A\n"
            f"• Diagnóstico: {msg}"
        )
        self.lbl_diagnostico.setText(diagnostico)

