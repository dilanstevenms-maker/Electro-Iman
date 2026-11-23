"""Capa de abstracción de datos para el catálogo de calibres de alambre AWG.

Permite conectar bases de datos SQL externas (ej. MySQL Server) y proporciona
un modo de respaldo (fallback) con catálogo en memoria para garantizar que la
interfaz gráfica siempre sea completamente funcional.
"""

from typing import Any, Optional
import math

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_DISPONIBLE = True
except ImportError:
    MYSQL_DISPONIBLE = False
    MySQLError = Exception

from src.db.datos_catalogo import CATALOGO_AWG_DEFAULT
from src.modelos import Cable


class DatabaseManager:
    """Gestor de acceso y abstracción a la base de datos SQL de calibres AWG."""

    _instancia: Optional["DatabaseManager"] = None

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "WLSn321R",
        database: str = "electroiman_db",
        auto_conectar: bool = True,
    ):
        self.config: dict[str, Any] = {
            "host": host,
            "port": int(port),
            "user": user,
            "password": password,
            "database": database,
            "connect_timeout": 3,
        }
        self._conectado_sql: bool = False
        self._ultimo_error: Optional[str] = None
        self._modo_fallback: bool = True

        # Catálogo local de respaldo precargado
        self._cache_calibres: list[Cable] = [
            Cable.desde_diccionario(datos) for datos in CATALOGO_AWG_DEFAULT
        ]

        if auto_conectar:
            self.conectar()

    @classmethod
    def obtener_instancia(cls, **kwargs) -> "DatabaseManager":
        """Patrón Singleton para compartir la conexión en toda la UI."""
        if cls._instancia is None:
            cls._instancia = cls(**kwargs)
        return cls._instancia

    @property
    def conectado_a_sql(self) -> bool:
        """Indica si hay conexión activa y verificada con el servidor SQL."""
        return self._conectado_sql

    @property
    def modo_actual(self) -> str:
        """Devuelve una descripción legible del origen de datos activo."""
        if self._conectado_sql:
            return f"MySQL ({self.config['host']}:{self.config['port']}/{self.config['database']})"
        return "Caché Local / Modo Contingencia (41 Calibres AWG)"

    @property
    def ultimo_error(self) -> Optional[str]:
        """Último mensaje de error devuelto por el conector SQL."""
        return self._ultimo_error

    def conectar(self, nueva_config: Optional[dict[str, Any]] = None) -> bool:
        """Establece conexión con el motor SQL. Si falla, activa el modo fallback."""
        if nueva_config:
            self.config.update(nueva_config)

        if not MYSQL_DISPONIBLE:
            self._conectado_sql = False
            self._modo_fallback = True
            self._ultimo_error = "El módulo 'mysql-connector-python' no está instalado."
            return False

        try:
            conexion = mysql.connector.connect(**self.config)
            if conexion.is_connected():
                self._conectado_sql = True
                self._modo_fallback = False
                self._ultimo_error = None
                conexion.close()
                # Sincronizamos la caché con la BD real
                self._sincronizar_desde_sql()
                return True
        except MySQLError as exc:
            self._conectado_sql = False
            self._modo_fallback = True
            self._ultimo_error = str(exc)
        except Exception as exc:  # pylint: disable=broad-except
            self._conectado_sql = False
            self._modo_fallback = True
            self._ultimo_error = f"Error inesperado: {exc}"

        return False

    def probar_conexion(self, config_prueba: Optional[dict[str, Any]] = None) -> tuple[bool, str]:
        """Realiza una prueba aislada de conexión sin alterar el estado actual."""
        if not MYSQL_DISPONIBLE:
            return False, "mysql-connector-python no está instalado en este entorno de Python."

        cfg = dict(self.config)
        if config_prueba:
            cfg.update(config_prueba)

        try:
            conn = mysql.connector.connect(**cfg)
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM catalogo_cables_awg;")
                total = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                return True, f"Conexión exitosa. Se encontraron {total} calibres en MySQL."
        except MySQLError as e:
            return False, f"Fallo de conexión SQL: {e}"
        except Exception as e:
            return False, f"Error al probar conexión: {e}"

        return False, "No se pudo establecer la conexión."

    def _sincronizar_desde_sql(self) -> None:
        """Carga en memoria los calibres desde la tabla SQL."""
        cables_sql = self._consultar_sql_directo("SELECT * FROM catalogo_cables_awg ORDER BY id_calibre ASC;")
        if cables_sql:
            self._cache_calibres = [Cable.desde_diccionario(f) for f in cables_sql]

    def _consultar_sql_directo(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        """Ejecuta una consulta SQL segura con retorno tipo diccionario."""
        if not self._conectado_sql or not MYSQL_DISPONIBLE:
            return []

        try:
            conexion = mysql.connector.connect(**self.config)
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(query, params)
            filas = cursor.fetchall()
            cursor.close()
            conexion.close()
            return filas
        except Exception as e:
            self._ultimo_error = str(e)
            return []

    def obtener_calibres(
        self,
        filtro_texto: str = "",
        calibre_min: Optional[int] = None,
        calibre_max: Optional[int] = None,
        corriente_min: Optional[float] = None,
    ) -> list[Cable]:
        """Obtiene la lista de calibres con filtros estructurados.

        Si la base de datos SQL está conectada, ejecuta la consulta SQL.
        Si está en modo contingencia, aplica los mismos filtros en memoria.
        """
        # Si estamos conectados a SQL, podemos consultar la BD
        if self._conectado_sql:
            condiciones = []
            parametros = []

            if calibre_min is not None:
                condiciones.append("id_calibre >= %s")
                parametros.append(calibre_min)

            if calibre_max is not None:
                condiciones.append("id_calibre <= %s")
                parametros.append(calibre_max)

            if corriente_min is not None and corriente_min > 0:
                condiciones.append("corriente_max_amp >= %s")
                parametros.append(corriente_min)

            if filtro_texto.strip():
                limpio = filtro_texto.strip().lower().replace("awg", "").strip()
                if limpio.isdigit():
                    condiciones.append("id_calibre = %s")
                    parametros.append(int(limpio))

            where_str = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
            query = f"SELECT * FROM catalogo_cables_awg {where_str} ORDER BY id_calibre ASC;"
            filas = self._consultar_sql_directo(query, tuple(parametros))
            if filas:
                return [Cable.desde_diccionario(f) for f in filas]

        # Modo fallback o filtrado local
        resultado = list(self._cache_calibres)

        if calibre_min is not None:
            resultado = [c for c in resultado if c.id_calibre >= calibre_min]

        if calibre_max is not None:
            resultado = [c for c in resultado if c.id_calibre <= calibre_max]

        if corriente_min is not None and corriente_min > 0:
            resultado = [c for c in resultado if c.corriente_max_amp >= corriente_min]

        if filtro_texto.strip():
            texto = filtro_texto.strip().lower().replace("awg", "").strip()
            if texto.isdigit():
                num = int(texto)
                resultado = [c for c in resultado if c.id_calibre == num]
            else:
                # Búsqueda difusa por número o características
                resultado = [
                    c for c in resultado
                    if str(c.id_calibre).startswith(texto) or texto in f"awg {c.id_calibre}"
                ]

        return resultado

    def obtener_calibre_por_id(self, id_calibre: int) -> Optional[Cable]:
        """Busca un calibre específico por su número AWG."""
        if self._conectado_sql:
            filas = self._consultar_sql_directo(
                "SELECT * FROM catalogo_cables_awg WHERE id_calibre = %s LIMIT 1;",
                (id_calibre,),
            )
            if filas:
                return Cable.desde_diccionario(filas[0])

        for c in self._cache_calibres:
            if c.id_calibre == id_calibre:
                return c
        return None

    def consultar_compatibilidad(
        self,
        id_calibre: int,
        corriente_requerida_amp: float,
        temp_operacion_c: float = 60.0,
    ) -> dict[str, Any]:
        """Evalúa si un calibre soporta de forma segura la corriente y temperatura dadas.

        Devuelve un reporte detallado con estado térmico y factores de seguridad.
        """
        cable = self.obtener_calibre_por_id(id_calibre)
        if not cable:
            return {
                "es_compatible": False,
                "nivel": "desconocido",
                "mensaje": f"Calibre AWG {id_calibre} no encontrado en el catálogo.",
                "porcentaje_carga": 0.0,
                "margen_amperios": 0.0,
            }

        if corriente_requerida_amp <= 0:
            return {
                "es_compatible": True,
                "nivel": "optimo",
                "mensaje": "Corriente nula o despreciable.",
                "porcentaje_carga": 0.0,
                "margen_amperios": cable.corriente_max_amp,
            }

        porcentaje = (corriente_requerida_amp / cable.corriente_max_amp) * 100.0
        margen = cable.corriente_max_amp - corriente_requerida_amp
        temp_ok = temp_operacion_c <= cable.temp_max_aislante_c

        if not temp_ok:
            return {
                "es_compatible": False,
                "nivel": "critico_temperatura",
                "mensaje": f"Temperatura {temp_operacion_c}°C excede la clase térmica del barniz ({cable.temp_max_aislante_c}°C).",
                "porcentaje_carga": porcentaje,
                "margen_amperios": margen,
                "cable": cable,
            }

        if corriente_requerida_amp > cable.corriente_max_amp:
            return {
                "es_compatible": False,
                "nivel": "sobrecarga",
                "mensaje": f"Sobrecarga de corriente: requiere {corriente_requerida_amp:.2f} A, máximo admisible {cable.corriente_max_amp:.2f} A.",
                "porcentaje_carga": porcentaje,
                "margen_amperios": margen,
                "cable": cable,
            }

        if porcentaje > 85.0:
            nivel = "precaucion"
            mensaje = f"Operación cerca del límite térmico ({porcentaje:.1f}% de capacidad nominal)."
        elif porcentaje > 50.0:
            nivel = "adecuado"
            mensaje = f"Operación nominal equilibrada ({porcentaje:.1f}% de carga)."
        else:
            nivel = "optimo"
            mensaje = f"Excelente margen de seguridad ({porcentaje:.1f}% de carga, margen {margen:.2f} A)."

        return {
            "es_compatible": True,
            "nivel": nivel,
            "mensaje": mensaje,
            "porcentaje_carga": porcentaje,
            "margen_amperios": margen,
            "cable": cable,
        }

    def obtener_resumen_estado(self) -> dict[str, Any]:
        """Provee información del estado de la capa de datos para la barra de estado de la UI."""
        total = len(self._cache_calibres)
        return {
            "conectado": self._conectado_sql,
            "modo": self.modo_actual,
            "total_calibres": total,
            "host": self.config.get("host", ""),
            "puerto": self.config.get("port", 3306),
            "base_datos": self.config.get("database", ""),
            "error": self._ultimo_error,
        }

