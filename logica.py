"""Módulo de lógica y cálculo para ELECTROIMÁN STUDIO.

Contiene la definición del resultado de optimización, la función de cálculo
simulada (dummy/placeholder) y la conexión opcional con el motor físico real.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AlternativaCalibre:
    """Representa una opción secundaria viable en la búsqueda heurística."""
    calibre: str
    espiras: int
    capas: float
    voltaje_v: float


@dataclass
class ResultadoOptimizacion:
    """Modelo estructurado con las métricas calculadas para la interfaz de resultados."""
    calibre_optimo: str = "AWG 5"
    espiras_totales: int = 90
    capas: int = 2
    corriente_requerida_a: float = 18.93
    potencia_disipada_w: float = 1.74
    voltaje_dc_v: float = 0.09
    resistencia_ohm: float = 0.005
    fuerza_teorica_n: float = 0.00
    factor_carga_termica_pct: float = 35.7
    alternativas: list[AlternativaCalibre] = field(default_factory=list)


def calcular_combinacion_dummy(parametros: dict[str, Any]) -> ResultadoOptimizacion:
    """Función de cálculo simulada (dummy/placeholder).

    Actúa como placeholder interactivo con valores dinámicos coherentes
    basados en la referencia visual hasta conectar el cálculo final.
    """
    longitud_mm = float(parametros.get("longitud_mm", 214.1))
    diametro_mm = float(parametros.get("diametro_mm", 5.0))
    espesor_mm = float(parametros.get("espesor_mm", 10.0))
    temp_c = float(parametros.get("temperatura_c", 60.0))
    material = str(parametros.get("material", "Aire"))

    # Ajuste dinámico suave para que al mover los sliders los números respondan en vivo
    factor_espiras = int((longitud_mm / 2.3) * (espesor_mm / 10.0))
    espiras = max(30, min(1200, factor_espiras if factor_espiras > 0 else 90))
    corriente = round(max(0.5, 18.93 * (90.0 / espiras)), 2)
    potencia = round(max(0.1, 1.74 * (corriente / 18.93) ** 1.8), 2)
    voltaje = round(max(0.01, 0.09 * (corriente / 18.93)), 2)
    fuerza = round(0.00 if material == "Aire" else 1.25, 2)
    carga_termica = min(98.0, max(12.0, (corriente / 53.0) * 100.0))

    alternativas = [
        AlternativaCalibre(calibre="AWG 11", espiras=360, capas=4.73, voltaje_v=0.39),
        AlternativaCalibre(calibre="AWG 13", espiras=565, capas=3.02, voltaje_v=0.59),
        AlternativaCalibre(calibre="AWG 15", espiras=820, capas=2.15, voltaje_v=0.88),
    ]

    return ResultadoOptimizacion(
        calibre_optimo="AWG 5",
        espiras_totales=espiras,
        capas=2,
        corriente_requerida_a=corriente,
        potencia_disipada_w=potencia,
        voltaje_dc_v=voltaje,
        resistencia_ohm=0.005,
        fuerza_teorica_n=fuerza,
        factor_carga_termica_pct=round(carga_termica, 1),
        alternativas=alternativas,
    )


def calcular_combinacion(parametros: dict[str, Any]) -> ResultadoOptimizacion:
    """Intenta calcular con el motor físico del proyecto o conmuta a la lógica simulada."""
    try:
        from src.db.database_manager import DatabaseManager
        from src.optimizador import evaluar_configuraciones

        db = DatabaseManager.obtener_instancia()
        catalogo = db.obtener_calibres()
        if not catalogo:
            return calcular_combinacion_dummy(parametros)

        longitud_m = float(parametros.get("longitud_mm", 100.0)) / 1000.0
        diametro_m = float(parametros.get("diametro_mm", 20.0)) / 1000.0
        espesor_m = float(parametros.get("espesor_mm", 10.0)) / 1000.0
        temp_c = float(parametros.get("temperatura_c", 60.0))
        material = str(parametros.get("material", "Aire"))
        mu_r = 1.0 if "Aire" in material else (250.0 if "Hierro" in material else 50.0)

        # Campo magnético base (10 mT)
        campo_b = float(parametros.get("campo_b", 0.010))

        mejor, viables = evaluar_configuraciones(
            campo_b_teslas=campo_b,
            longitud_m=longitud_m,
            diametro_carrete_m=diametro_m,
            espesor_max_m=espesor_m,
            catalogo=catalogo,
            temp_operacion_c=temp_c,
            permeabilidad_relativa=mu_r,
        )

        alternativas = []
        for v in viables[1:4]:
            alternativas.append(
                AlternativaCalibre(
                    calibre=f"AWG {v.cable_seleccionado.id_calibre}",
                    espiras=v.numero_espiras_total,
                    capas=round(float(v.capas), 2),
                    voltaje_v=round(v.voltaje_necesario_volt, 2),
                )
            )

        return ResultadoOptimizacion(
            calibre_optimo=f"AWG {mejor.cable_seleccionado.id_calibre}",
            espiras_totales=mejor.numero_espiras_total,
            capas=mejor.capas,
            corriente_requerida_a=round(mejor.corriente_necesaria_amp, 2),
            potencia_disipada_w=round(mejor.potencia_disipada_watts, 2),
            voltaje_dc_v=round(mejor.voltaje_necesario_volt, 2),
            resistencia_ohm=round(mejor.resistencia_operacion_ohm, 4),
            fuerza_teorica_n=round(mejor.fuerza_atraccion_estimada_n, 2),
            factor_carga_termica_pct=round(mejor.porcentaje_capacidad_termica, 1),
            alternativas=alternativas,
        )

    except Exception:
        # Fallback suave garantizado a la lógica simulada
        return calcular_combinacion_dummy(parametros)

