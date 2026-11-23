"""Modelos de datos para el diseño y optimización de electroimanes."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Cable:
    """Representa las especificaciones técnicas de un conductor de cobre esmaltado AWG."""

    id_calibre: int
    diametro_cobre_mm: float
    diametro_con_esmalte_mm: float
    area_seccion_transversal_mm2: float
    resistencia_ohm_por_metro: float
    corriente_max_amp: float
    masa_kg_por_km: float
    temp_max_aislante_c: int = 155

    @classmethod
    def desde_diccionario(cls, datos: dict[str, Any]) -> "Cable":
        """Crea una instancia de Cable a partir de un diccionario devuelto por SQL o memoria."""
        return cls(
            id_calibre=int(datos["id_calibre"]),
            diametro_cobre_mm=float(datos["diametro_cobre_mm"]),
            diametro_con_esmalte_mm=float(datos["diametro_con_esmalte_mm"]),
            area_seccion_transversal_mm2=float(datos["area_seccion_transversal_mm2"]),
            resistencia_ohm_por_metro=float(datos["resistencia_ohm_por_metro"]),
            corriente_max_amp=float(datos["corriente_max_amp"]),
            masa_kg_por_km=float(datos["masa_kg_por_km"]),
            temp_max_aislante_c=int(datos.get("temp_max_aislante_c", 155)),
        )

    def a_diccionario(self) -> dict[str, Any]:
        """Convierte la instancia en un diccionario estándar."""
        return {
            "id_calibre": self.id_calibre,
            "diametro_cobre_mm": self.diametro_cobre_mm,
            "diametro_con_esmalte_mm": self.diametro_con_esmalte_mm,
            "area_seccion_transversal_mm2": self.area_seccion_transversal_mm2,
            "resistencia_ohm_por_metro": self.resistencia_ohm_por_metro,
            "corriente_max_amp": self.corriente_max_amp,
            "masa_kg_por_km": self.masa_kg_por_km,
            "temp_max_aislante_c": self.temp_max_aislante_c,
        }

    @property
    def nombre_calibre(self) -> str:
        """Etiqueta estandarizada del calibre (ej. AWG 18)."""
        return f"AWG {self.id_calibre}"


@dataclass
class ParametrosEntrada:
    """Parámetros de diseño geométrico y magnético ingresados por el usuario."""

    campo_b_teslas: float
    longitud_m: float
    diametro_carrete_m: float
    espesor_max_m: float
    temp_operacion_c: float = 60.0
    permeabilidad_relativa: float = 1.0  # 1.0 para núcleo de aire; >1 para ferromagnético


@dataclass
class ResultadoSolenoide:
    """Resultado detallado de la configuración calculada para el electroimán."""

    cable_seleccionado: Cable
    corriente_necesaria_amp: float
    numero_espiras_total: int
    potencia_disipada_watts: float

    # Parámetros geométricos y eléctricos ampliados
    capas: int = 1
    espiras_por_capa: int = 0
    longitud_alambre_m: float = 0.0
    masa_alambre_kg: float = 0.0
    resistencia_operacion_ohm: float = 0.0
    voltaje_necesario_volt: float = 0.0
    densidad_corriente_a_mm2: float = 0.0
    campo_b_teslas: float = 0.0
    diametro_medio_m: float = 0.0
    fuerza_atraccion_estimada_n: float = 0.0
    fuerza_atraccion_estimada_kgf: float = 0.0
    porcentaje_capacidad_termica: float = 0.0
    temp_operacion_c: float = 60.0
    es_viable: bool = True
    mensajes_advertencia: list[str] = field(default_factory=list)

    @property
    def margen_seguridad_termico_amp(self) -> float:
        """Diferencia entre corriente máxima permitida y la corriente requerida."""
        return self.cable_seleccionado.corriente_max_amp - self.corriente_necesaria_amp

    def imprimir_resumen(self):
        """Imprime un resumen de ingeniería en consola para compatibilidad con CLI."""
        print("Configuración del solenoide:")
        print(f"  Calibre AWG: {self.cable_seleccionado.id_calibre}")
        print(f"  Número de espiras: {self.numero_espiras_total} ({self.capas} capas)")
        print(f"  Corriente requerida: {self.corriente_necesaria_amp:.2f} A (Máx: {self.cable_seleccionado.corriente_max_amp:.2f} A)")
        print(f"  Voltaje estimado: {self.voltaje_necesario_volt:.2f} V")
        print(f"  Resistencia ({self.temp_operacion_c:.0f}°C): {self.resistencia_operacion_ohm:.3f} Ω")
        print(f"  Energía disipada (Calor): {self.potencia_disipada_watts:.2f} W")
        print(f"  Longitud de conductor: {self.longitud_alambre_m:.2f} m ({self.masa_alambre_kg * 1000:.1f} g)")
        if self.fuerza_atraccion_estimada_n > 0:
            print(f"  Fuerza estimada en cara polar: {self.fuerza_atraccion_estimada_n:.2f} N ({self.fuerza_atraccion_estimada_kgf:.2f} kgf)")
