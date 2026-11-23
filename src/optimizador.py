"""Algoritmo de optimización heurística para el diseño de electroimanes."""

import math
from typing import Optional

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

TEMP_OPERACION_DEFAULT_C = 60.0


def evaluar_configuraciones(
    campo_b_teslas: float,
    longitud_m: float,
    diametro_carrete_m: float,
    espesor_max_m: float,
    catalogo: list[Cable],
    temp_operacion_c: float = TEMP_OPERACION_DEFAULT_C,
    permeabilidad_relativa: float = 1.0,
) -> tuple[ResultadoSolenoide, list[ResultadoSolenoide]]:
    """Evalúa exhaustivamente todos los calibres y combinaciones de capas viables.

    Retorna una tupla:
      (mejor_resultado, lista_ordenada_de_alternativas_viables)
    ordenadas de menor a mayor potencia disipada por efecto Joule (calor).
    """
    validar_entradas(campo_b_teslas, longitud_m, diametro_carrete_m, espesor_max_m)

    resultados_viables: list[ResultadoSolenoide] = []
    alguno_cabe_geometricamente = False

    for cable in catalogo:
        if not cabe_en_geometria(cable, longitud_m, espesor_max_m):
            continue

        alguno_cabe_geometricamente = True
        n_por_capa = espiras_por_capa(cable, longitud_m)
        diametro_hilo_m = cable.diametro_con_esmalte_mm / 1000.0
        max_capas = capas_maximas(cable, espesor_max_m)

        for capas in range(1, max_capas + 1):
            total_espiras = n_por_capa * capas
            n_efectivo = total_espiras / longitud_m

            try:
                corriente = fisica.calcular_corriente(
                    campo_b_teslas, n_efectivo, permeabilidad_relativa
                )
            except ValueError:
                continue

            try:
                verificar_restricciones_termicas(cable, corriente, temp_operacion_c)
            except RestriccionTermicaError:
                continue  # Descartado por seguridad térmica

            # Diámetro medio efectivo del enrollamiento multicapa
            diametro_medio = diametro_carrete_m + (capas * diametro_hilo_m)

            # Longitud total y resistencia corregida
            longitud_alambre = fisica.calcular_longitud_alambre(diametro_medio, total_espiras)
            r_20c = cable.resistencia_ohm_por_metro * longitud_alambre
            r_operacion = fisica.ajustar_resistencia_temperatura(r_20c, temp_operacion_c)

            # Potencia de pérdidas Joule y tensión requerida
            potencia = fisica.calcular_potencia_disipada(corriente, r_operacion)
            voltaje = fisica.calcular_voltaje(corriente, r_operacion)
            densidad_j = fisica.calcular_densidad_corriente(
                corriente, cable.area_seccion_transversal_mm2
            )
            masa_total_kg = (cable.masa_kg_por_km / 1000.0) * longitud_alambre

            # Fuerza de atracción estimada en la cara polar
            fuerza_n = fisica.calcular_fuerza_polar_teorica(campo_b_teslas, diametro_carrete_m)
            fuerza_kgf = fuerza_n / fisica.GRAVEDAD_ESTANDAR

            porcentaje_termico = (corriente / cable.corriente_max_amp) * 100.0

            res = ResultadoSolenoide(
                cable_seleccionado=cable,
                corriente_necesaria_amp=corriente,
                numero_espiras_total=total_espiras,
                potencia_disipada_watts=potencia,
                capas=capas,
                espiras_por_capa=n_por_capa,
                longitud_alambre_m=longitud_alambre,
                masa_alambre_kg=masa_total_kg,
                resistencia_operacion_ohm=r_operacion,
                voltaje_necesario_volt=voltaje,
                densidad_corriente_a_mm2=densidad_j,
                campo_b_teslas=campo_b_teslas,
                diametro_medio_m=diametro_medio,
                fuerza_atraccion_estimada_n=fuerza_n,
                fuerza_atraccion_estimada_kgf=fuerza_kgf,
                porcentaje_capacidad_termica=porcentaje_termico,
                temp_operacion_c=temp_operacion_c,
                es_viable=True,
            )
            resultados_viables.append(res)

    if not resultados_viables:
        if not alguno_cabe_geometricamente:
            raise GeometriaInvalidaError(
                "El espacio físico disponible (longitud o espesor) es insuficiente para albergar "
                "siquiera una espira de los calibres evaluados."
            )
        raise CampoInalcanzableError(
            "Ningún calibre del catálogo puede alcanzar el campo magnético solicitado respetando "
            "los límites de corriente admisible y seguridad térmica por efecto Joule."
        )

    # Ordenar por menor potencia disipada (máxima eficiencia energética)
    resultados_viables.sort(key=lambda r: r.potencia_disipada_watts)
    return resultados_viables[0], resultados_viables


def optimizar_solenoide(
    campo_b_teslas: float,
    longitud_m: float,
    diametro_carrete_m: float,
    espesor_max_m: float,
    catalogo: list[Cable],
    temp_operacion_c: float = TEMP_OPERACION_DEFAULT_C,
    permeabilidad_relativa: float = 1.0,
) -> ResultadoSolenoide:
    """Devuelve únicamente el diseño óptimo (menor calor disipado)."""
    mejor, _ = evaluar_configuraciones(
        campo_b_teslas=campo_b_teslas,
        longitud_m=longitud_m,
        diametro_carrete_m=diametro_carrete_m,
        espesor_max_m=espesor_max_m,
        catalogo=catalogo,
        temp_operacion_c=temp_operacion_c,
        permeabilidad_relativa=permeabilidad_relativa,
    )
    return mejor
