"""Ventana principal de la aplicación en PyQt6 con estilo Glassmorphism Cósmico."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from interfaz.dialogs.db_config_dialog import DatabaseConfigDialog
from interfaz.styles import CosmicColors, STYLESHEET_GLOBAL, aplicar_sombra_glass
from interfaz.tabs.database_tab import DatabaseTab
from interfaz.tabs.simulator_tab import SimulatorTab
from interfaz.widgets.glass_cards import StatusBadge
from src.db.database_manager import DatabaseManager


class ElectroimanMainWindow(QMainWindow):
    """Ventana principal que aloja la interfaz gráfica y coordina los módulos."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Diseño Computacional de Electroimanes — Glassmorphism Studio")
        self.resize(1200, 820)
        self.setMinimumSize(1000, 700)

        self.db_manager = DatabaseManager.obtener_instancia()

        self._init_ui()
        self._configurar_atajos()
        self.actualizar_estado_db()

    def _init_ui(self):
        # Aplicamos la hoja de estilos global
        self.setStyleSheet(STYLESHEET_GLOBAL)

        # Widget central con layout principal
        widget_central = QWidget()
        layout_central = QVBoxLayout(widget_central)
        layout_central.setContentsMargins(18, 14, 18, 12)
        layout_central.setSpacing(12)

        # Barra de Encabezado Superior (Header Glass)
        header = self._crear_header()
        layout_central.addWidget(header)

        # Pestañas Principales (TabWidget)
        self.tabs = QTabWidget()
        self.tab_simulador = SimulatorTab()
        self.tab_database = DatabaseTab()

        self.tabs.addTab(self.tab_simulador, "⚡ Simulador y Combinación Ideal")
        self.tabs.addTab(self.tab_database, "📚 Catálogo de Calibres AWG (SQL)")

        # Conectar eventos de configuración de BD desde ambas pestañas
        self.tab_simulador.solicitarConfigSQL.connect(self.abrir_dialogo_db)
        self.tab_database.solicitarConfigSQL.connect(self.abrir_dialogo_db)

        layout_central.addWidget(self.tabs, stretch=1)
        self.setCentralWidget(widget_central)

        # Barra de estado inferior
        self._crear_status_bar()

    def _crear_header(self) -> QWidget:
        header_frame = QFrame()
        header_frame.setObjectName("GlassCard")
        aplicar_sombra_glass(header_frame, blur=18, y_offset=4)

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 12, 20, 12)
        header_layout.setSpacing(16)

        # Logo e Identidad Visual
        lbl_logo = QLabel("🧲")
        lbl_logo.setStyleSheet("font-size: 28px; background: transparent;")

        titulos_layout = QVBoxLayout()
        titulos_layout.setSpacing(1)

        lbl_titulo = QLabel("ELECTROIMÁN STUDIO")
        lbl_titulo.setStyleSheet(
            f"font-size: 17px; font-weight: 800; color: {CosmicColors.TEXT_PRIMARY}; "
            f"letter-spacing: 1.5px; background: transparent;"
        )

        lbl_subtitulo = QLabel(
            "Diseño computacional, optimización heurística y restricciones térmicas en conductores AWG"
        )
        lbl_subtitulo.setStyleSheet(
            f"font-size: 11px; color: {CosmicColors.TEXT_SECONDARY}; font-weight: 500; background: transparent;"
        )

        titulos_layout.addWidget(lbl_titulo)
        titulos_layout.addWidget(lbl_subtitulo)

        header_layout.addWidget(lbl_logo)
        header_layout.addLayout(titulos_layout)
        header_layout.addStretch()

        # Indicador de estado de la Base de Datos
        self.badge_db = StatusBadge("Verificando BD...", "info")
        header_layout.addWidget(self.badge_db)

        # Botón de configuración rápida de BD
        self.btn_db_settings = QPushButton("⚙️ Ajustes SQL")
        self.btn_db_settings.setObjectName("BtnSecondary")
        self.btn_db_settings.clicked.connect(self.abrir_dialogo_db)
        header_layout.addWidget(self.btn_db_settings)

        return header_frame

    def _crear_status_bar(self):
        status = QStatusBar()
        status.setStyleSheet(
            f"color: {CosmicColors.TEXT_MUTED}; background: transparent; "
            f"border-top: 1px solid rgba(255, 255, 255, 0.06); font-size: 11px;"
        )
        self.setStatusBar(status)

        self.lbl_status_izq = QLabel("🟢 Motor heurístico listo para simulación continua.")
        self.lbl_status_izq.setStyleSheet(f"color: {CosmicColors.TEXT_SECONDARY};")
        status.addWidget(self.lbl_status_izq, stretch=1)

        self.lbl_status_der = QLabel("PyQt6 • Glassmorphism Cósmico • v2.0")
        self.lbl_status_der.setStyleSheet(f"color: {CosmicColors.TEXT_MUTED}; margin-right: 12px;")
        status.addPermanentWidget(self.lbl_status_der)

    def _configurar_atajos(self):
        # F5 o Ctrl+R para recalcular
        action_recalcular = QAction("Recalcular", self)
        action_recalcular.setShortcuts([QKeySequence("F5"), QKeySequence("Ctrl+R")])
        action_recalcular.triggered.connect(self.tab_simulador.calcular_optimo)
        self.addAction(action_recalcular)

        # Ctrl+D para configuración de BD
        action_db = QAction("Ajustes SQL", self)
        action_db.setShortcut(QKeySequence("Ctrl+D"))
        action_db.triggered.connect(self.abrir_dialogo_db)
        self.addAction(action_db)

    def abrir_dialogo_db(self):
        """Abre la ventana modal de configuración y diagnóstico SQL."""
        dialogo = DatabaseConfigDialog(self)
        dialogo.conexionActualizada.connect(self._on_conexion_db_actualizada)
        dialogo.exec()

    def _on_conexion_db_actualizada(self):
        self.actualizar_estado_db()
        self.tab_database.recargar_calibres()
        self.tab_simulador.calcular_optimo()

    def actualizar_estado_db(self):
        """Refresca el badge del header con el estado real de la conexión SQL."""
        estado = self.db_manager.obtener_resumen_estado()
        if estado["conectado"]:
            self.badge_db.set_estado(f"MySQL Online ({estado['base_datos']})", "ok")
            self.lbl_status_izq.setText(
                f"🟢 Conectado a MySQL Server ({estado['host']}:{estado['puerto']}) — "
                f"{estado['total_calibres']} calibres activos en catálogo."
            )
        else:
            self.badge_db.set_estado("Caché Local / Fallback", "advertencia")
            self.lbl_status_izq.setText(
                "🟡 Operando en modo contingencia local (catálogo precargado de 41 calibres AWG)."
            )

