"""Diálogo modal para la configuración y diagnóstico de la conexión SQL externa."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from interfaz.styles import CosmicColors, aplicar_sombra_glass
from src.db.database_manager import DatabaseManager


class DatabaseConfigDialog(QDialog):
    """Permite al equipo técnico configurar o probar la conexión con el servidor MySQL."""

    conexionActualizada = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Capa de Datos SQL (MySQL)")
        self.setFixedSize(520, 560)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.db_manager = DatabaseManager.obtener_instancia()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        # Header
        lbl_titulo = QLabel("Conexión con Base de Datos MySQL")
        lbl_titulo.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {CosmicColors.TEXT_PRIMARY};"
        )
        lbl_desc = QLabel(
            "Configura los parámetros para conectar el catálogo de calibres AWG "
            "almacenado en tu servidor MySQL (puerto por defecto: 3306)."
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet(f"color: {CosmicColors.TEXT_SECONDARY}; font-size: 12px;")

        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_desc)

        # Formulario
        form_layout = QFormLayout()
        form_layout.setSpacing(12)

        self.txt_host = QLineEdit(str(self.db_manager.config.get("host", "localhost")))
        self.spin_puerto = QSpinBox()
        self.spin_puerto.setRange(1, 65535)
        self.spin_puerto.setValue(int(self.db_manager.config.get("port", 3306)))

        self.txt_user = QLineEdit(str(self.db_manager.config.get("user", "root")))
        self.txt_pass = QLineEdit(str(self.db_manager.config.get("password", "")))
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)

        self.txt_db = QLineEdit(str(self.db_manager.config.get("database", "electroiman_db")))

        form_layout.addRow(QLabel("Host / Servidor:"), self.txt_host)
        form_layout.addRow(QLabel("Puerto TCP:"), self.spin_puerto)
        form_layout.addRow(QLabel("Usuario:"), self.txt_user)
        form_layout.addRow(QLabel("Contraseña:"), self.txt_pass)
        form_layout.addRow(QLabel("Base de Datos:"), self.txt_db)

        layout.addLayout(form_layout)

        # Consola de diagnóstico
        lbl_consola = QLabel("Diagnóstico de Conexión:")
        lbl_consola.setStyleSheet(f"font-weight: 600; color: {CosmicColors.TEXT_SECONDARY};")
        layout.addWidget(lbl_consola)

        self.txt_consola = QTextEdit()
        self.txt_consola.setReadOnly(True)
        self.txt_consola.setFixedHeight(110)
        self.txt_consola.setStyleSheet(
            "background-color: rgba(10, 8, 20, 0.9); border: 1px solid rgba(255, 255, 255, 0.1); "
            "border-radius: 8px; font-family: 'Consolas', monospace; font-size: 11px; padding: 6px;"
        )
        estado = self.db_manager.obtener_resumen_estado()
        self.txt_consola.setText(
            f"Estado actual: {estado['modo']}\n"
            f"Calibres en memoria: {estado['total_calibres']}\n"
            f"Conexión activa: {'Sí' if estado['conectado'] else 'No (Modo Contingencia)'}"
        )
        layout.addWidget(self.txt_consola)

        # Botones de Acción
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_probar = QPushButton("🔍 Probar Conexión")
        self.btn_probar.setObjectName("BtnSecondary")
        self.btn_probar.clicked.connect(self._on_probar_conexion)

        self.btn_guardar = QPushButton("💾 Guardar y Conectar")
        self.btn_guardar.setObjectName("BtnPrimary")
        self.btn_guardar.clicked.connect(self._on_guardar_conectar)

        self.btn_cancelar = QPushButton("Cerrar")
        self.btn_cancelar.setObjectName("BtnGhost")
        self.btn_cancelar.clicked.connect(self.close)

        btn_layout.addWidget(self.btn_probar)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addWidget(self.btn_guardar)

        layout.addLayout(btn_layout)

    def _obtener_config_form(self) -> dict:
        return {
            "host": self.txt_host.text().strip(),
            "port": self.spin_puerto.value(),
            "user": self.txt_user.text().strip(),
            "password": self.txt_pass.text(),
            "database": self.txt_db.text().strip(),
        }

    def _on_probar_conexion(self):
        cfg = self._obtener_config_form()
        self.txt_consola.append("\n[Prueba] Intentando conectar a MySQL Server...")
        exito, msg = self.db_manager.probar_conexion(cfg)
        if exito:
            self.txt_consola.append(f"🟢 ÉXITO: {msg}")
        else:
            self.txt_consola.append(f"🔴 ERROR: {msg}")

    def _on_guardar_conectar(self):
        cfg = self._obtener_config_form()
        self.txt_consola.append("\n[Conexión] Aplicando nueva configuración...")
        conectado = self.db_manager.conectar(cfg)
        if conectado:
            self.txt_consola.append("🟢 Conexión establecida con MySQL exitosamente.")
            self.conexionActualizada.emit()
            self.accept()
        else:
            self.txt_consola.append(
                f"🟡 No se pudo conectar a MySQL: {self.db_manager.ultimo_error}\n"
                "Permaneciendo en modo contingencia (fallback con catálogo precargado)."
            )
            self.conexionActualizada.emit()

