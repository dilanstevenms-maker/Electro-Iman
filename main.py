"""Punto de entrada principal para ELECTROIMÁN STUDIO."""

import os
import sys

# Garantizar que las rutas del proyecto y subdirectorio estén en sys.path
directorio_actual = os.path.dirname(os.path.abspath(__file__))
directorio_padre = os.path.dirname(directorio_actual)

for ruta in (directorio_actual, directorio_padre):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication
from ui import MainWindow


def cargar_estilos_qss(app: QApplication):
    """Carga de forma robusta la hoja de estilos styles.qss."""
    rutas_candidatas = [
        os.path.join(directorio_actual, "styles.qss"),
        os.path.join(directorio_actual, "interfaz", "styles.qss"),
        os.path.join(directorio_padre, "styles.qss"),
    ]
    for ruta in rutas_candidatas:
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    app.setStyleSheet(f.read())
                return
            except Exception as e:
                print(f"[Aviso] Error leyendo {ruta}: {e}")


def ejecutar_modo_cli():
    """Modo consola por terminal interactiva."""
    try:
        from interfaz.cli import (
            mostrar_error,
            mostrar_resultado,
            preguntar_si_continuar,
            solicitar_parametros,
        )
        from src.db.database_manager import DatabaseManager
        from src.errores import ElectroimanError
        from src.optimizador import optimizar_solenoide

        db = DatabaseManager.obtener_instancia()
        catalogo = db.obtener_calibres()
        print("Iniciando sesión interactiva por consola (modo CLI)...")
        while True:
            try:
                parametros = solicitar_parametros()
                if parametros is None:
                    break
                campo_b, longitud_m, diametro_m, espesor_m = parametros
                res = optimizar_solenoide(campo_b, longitud_m, diametro_m, espesor_m, catalogo)
                mostrar_resultado(res)
            except (ElectroimanError, ValueError) as err:
                mostrar_error(err)
            except (KeyboardInterrupt, EOFError):
                break
            if not preguntar_si_continuar():
                break
    except Exception as e:
        print(f"[Error CLI] {e}")


def main():
    if "--cli" in sys.argv:
        ejecutar_modo_cli()
        return

    app = QApplication(sys.argv)
    app.setApplicationName("ELECTROIMÁN STUDIO")
    app.setApplicationDisplayName("ELECTROIMÁN STUDIO — Diseño de Electroimanes")
    app.setOrganizationName("Carolina Molina y Dilan Muñoz")

    # Establecer tipografía predeterminada para evitar avisos de point size negativo
    app.setFont(QFont("Segoe UI", 10))

    cargar_estilos_qss(app)

    ventana = MainWindow()
    ventana.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
