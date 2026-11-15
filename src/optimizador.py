import math

from src import fisica
from src.errores import CampoInalcanzableError, GeometriaInvalidaError, RestriccionTermicaError
from src.modelos import Cable, ResultadoSolenoide
from src.restricciones import (
    cabe_en_geometria,
    capas_maximas,
    espiras_por_capa,
    validar_entradas,
    verificar_restricciones_termicas,
)

TEMP_OPERACION_DEFAULT_C = 60


def optimizar_solenoide(
    campo_b_teslas: float,
    longitud_m: float,
    diametro_carrete_m: float,
    espesor_max_m: float,
    catalogo: list[Cable],
    temp_operacion_c: float = TEMP_OPERACION_DEFAULT_C,
) -> ResultadoSolenoide:
    """Recorre calibres y número de capas; devuelve el diseño viable de menor calor disipado."""
    validar_entradas(campo_b_teslas, longitud_m, diametro_carrete_m, espesor_max_m)

    mejor = None
    mejor_potencia = math.inf
    alguno_cabe = False

    for cable in catalogo:
        if not cabe_en_geometria(cable, longitud_m, espesor_max_m):
            continue
        alguno_cabe = True

        por_capa = espiras_por_capa(cable, longitud_m)
        d_m = cable.diametro_con_esmalte_mm / 1000.0

        for capas in range(1, capas_maximas(cable, espesor_max_m) + 1):
            total_espiras = por_capa * capas
            n_efectivo = total_espiras / longitud_m
            corriente = fisica.calcular_corriente(campo_b_teslas, n_efectivo)

            try:
                verificar_restricciones_termicas(cable, corriente, temp_operacion_c)
            except RestriccionTermicaError:
                continue  # diseño descartado por efecto Joule

            # Diámetro medio del bobinado (capas apiladas sobre el carrete)
            d_medio = diametro_carrete_m + capas * d_m
            r_20c = fisica.calcular_resistencia_total(
                cable.resistencia_ohm_por_metro, d_medio, total_espiras
            )
            r_operacion = fisica.ajustar_resistencia_temperatura(r_20c, temp_operacion_c)
            potencia = fisica.calcular_potencia_disipada(corriente, r_operacion)

            if potencia < mejor_potencia:
                mejor_potencia = potencia
                mejor = ResultadoSolenoide(
                    cable_seleccionado=cable,
                    corriente_necesaria_amp=corriente,
                    numero_espiras_total=total_espiras,
                    potencia_disipada_watts=potencia,
                )

    if mejor is None:
        if not alguno_cabe:
            raise GeometriaInvalidaError()
        raise CampoInalcanzableError()
    return mejor