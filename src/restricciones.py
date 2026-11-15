import math

from src.errores import GeometriaInvalidaError, RestriccionTermicaError
from src.modelos import Cable


def validar_entradas(campo_b_teslas, longitud_m, diametro_carrete_m, espesor_max_m):
    if campo_b_teslas <= 0:
        raise ValueError("El campo magnético debe ser mayor a 0 T.")
    if longitud_m <= 0 or diametro_carrete_m <= 0 or espesor_max_m <= 0:
        raise GeometriaInvalidaError(
            "Longitud, diámetro del carrete y espesor disponible deben ser mayores a 0."
        )


def espiras_por_capa(cable: Cable, longitud_m: float) -> int:
    return math.floor(longitud_m * 1000 / cable.diametro_con_esmalte_mm + 1e-9)


def capas_maximas(cable: Cable, espesor_max_m: float) -> int:
    return math.floor(espesor_max_m * 1000 / cable.diametro_con_esmalte_mm + 1e-9)


def cabe_en_geometria(cable: Cable, longitud_m: float, espesor_max_m: float) -> bool:
    return espiras_por_capa(cable, longitud_m) >= 1 and capas_maximas(cable, espesor_max_m) >= 1


def verificar_restricciones_termicas(cable: Cable, corriente_amp: float, temp_operacion_c: float):
    """Lanza RestriccionTermicaError si el diseño no es seguro para este cable."""
    if corriente_amp > cable.corriente_max_amp:
        raise RestriccionTermicaError(
            f"AWG {cable.id_calibre}: {corriente_amp:.2f} A supera el máximo de "
            f"{cable.corriente_max_amp:.2f} A."
        )
    if temp_operacion_c > cable.temp_max_aislante_c:
        raise RestriccionTermicaError(
            f"AWG {cable.id_calibre}: {temp_operacion_c} °C supera la clase térmica "
            f"del esmalte ({cable.temp_max_aislante_c} °C)."
        )