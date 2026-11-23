"""Módulo de compatibilidad para la conexión a la base de datos MySQL.

Utiliza internamente DatabaseManager para desacoplar el acceso a datos.
"""

from src.db.database_manager import DatabaseManager


def conectar_db():
    """Mantiene compatibilidad con scripts existentes."""
    manager = DatabaseManager.obtener_instancia()
    return manager.conectado_a_sql


def obtener_catalogo_cables() -> list[dict]:
    """Obtiene el catálogo de cables como lista de diccionarios.

    Garantiza retorno de datos válidos tanto si MySQL está encendido
    como si opera en modo contingencia (fallback).
    """
    manager = DatabaseManager.obtener_instancia()
    cables = manager.obtener_calibres()
    return [c.a_diccionario() for c in cables]


if __name__ == "__main__":
    print("Probando capa de abstracción de base de datos...\n")
    manager = DatabaseManager.obtener_instancia()
    estado = manager.obtener_resumen_estado()
    print(f"Estado de conexión: {estado['modo']}")
    print(f"Total de calibres cargados: {estado['total_calibres']}")
    calibres = manager.obtener_calibres()
    if calibres:
        print(f"Primer calibre: {calibres[0].nombre_calibre} (D={calibres[0].diametro_con_esmalte_mm} mm)")
