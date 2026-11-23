"""Fórmulas físicas para el cálculo electromagnético y térmico de solenoides."""

import math

# Constantes físicas fundamentales
MU_0: float = 4.0 * math.pi * 1e-7  # Permeabilidad magnética del vacío en T·m/A
COEF_TEMP_COBRE: float = 0.00393    # Coeficiente de variación térmica del cobre a 20°C (1/°C)
GRAVEDAD_ESTANDAR: float = 9.80665  # m/s²


def calcular_espiras_por_metro(diametro_con_esmalte_mm: float) -> float:
    """Calcula la densidad lineal de espiras en una sola capa continua."""
    if diametro_con_esmalte_mm <= 0:
        raise ValueError("El diámetro del cable debe ser mayor a 0.")
    diametro_m = diametro_con_esmalte_mm / 1000.0
    return 1.0 / diametro_m


def calcular_corriente(
    campo_b_teslas: float,
    espiras_por_metro: float,
    permeabilidad_relativa: float = 1.0,
) -> float:
    """Calcula la corriente eléctrica requerida para generar el campo B en el centro.

    Fórmula: I = B / (μ_0 * μ_r * n)
    """
    if espiras_por_metro <= 0:
        raise ValueError("El número efectivo de espiras por metro debe ser positivo.")
    if permeabilidad_relativa <= 0:
        raise ValueError("La permeabilidad relativa debe ser mayor a 0.")

    mu_total = MU_0 * permeabilidad_relativa
    return campo_b_teslas / (mu_total * espiras_por_metro)


def ajustar_resistencia_temperatura(
    resistencia_20c: float,
    temp_operacion_c: float = 60.0,
) -> float:
    """Ajusta la resistencia eléctrica del cobre a la temperatura de operación.

    Fórmula: R(T) = R_20 * (1 + α * (T - 20))
    """
    return resistencia_20c * (1.0 + COEF_TEMP_COBRE * (temp_operacion_c - 20.0))


def calcular_potencia_disipada(corriente_amp: float, resistencia_ohm: float) -> float:
    """Calcula la potencia disipada por efecto Joule en Watts (P = I^2 * R)."""
    return (corriente_amp ** 2) * resistencia_ohm


def calcular_voltaje(corriente_amp: float, resistencia_ohm: float) -> float:
    """Calcula la tensión continua (DC) requerida según la ley de Ohm (V = I * R)."""
    return corriente_amp * resistencia_ohm


def calcular_resistencia_total(
    resistencia_por_metro: float,
    diametro_carrete_m: float,
    total_espiras: int,
) -> float:
    """Calcula la resistencia a 20°C considerando la longitud del alambre enrollado."""
    longitud_total = calcular_longitud_alambre(diametro_carrete_m, total_espiras)
    return resistencia_por_metro * longitud_total


def calcular_longitud_alambre(diametro_medio_m: float, total_espiras: int) -> float:
    """Calcula la longitud total de alambre de cobre en metros."""
    perimetro_medio = math.pi * diametro_medio_m
    return perimetro_medio * total_espiras


def calcular_densidad_corriente(corriente_amp: float, area_mm2: float) -> float:
    """Calcula la densidad de corriente en A/mm²."""
    if area_mm2 <= 0:
        return 0.0
    return corriente_amp / area_mm2


def calcular_fuerza_polar_teorica(campo_b_teslas: float, diametro_carrete_m: float) -> float:
    """Calcula la fuerza de atracción teórica máxima en la cara polar (en Newtons).

    F = (B² * A) / (2 * μ_0)
    donde A = π * (D/2)²
    """
    radio = diametro_carrete_m / 2.0
    area_m2 = math.pi * (radio ** 2)
    return ((campo_b_teslas ** 2) * area_m2) / (2.0 * MU_0)
