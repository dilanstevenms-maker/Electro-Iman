import math


MU_0 = 4 * math.pi * 1e-7  # Permeabilidad magnética del vacío en T*m/A
COEF_TEMP_COBRE = 0.00393  # Coeficiente de temperatura del cobre puro a 20°C

def calcular_espiras_por_metro(diametro_con_esmalte_mm):
    if diametro_con_esmalte_mm <= 0:
        raise ValueError("El diámetro del cable debe ser mayor a 0.")
    
    diametro_m = diametro_con_esmalte_mm / 1000.0
    return 1.0 / diametro_m

def calcular_corriente(campo_b_teslas, espiras_por_metro):

    if espiras_por_metro <= 0:
        raise ValueError("El número de espiras (n) debe ser positivo.")
    
    # I = B / (μ_0 * n)
    corriente = campo_b_teslas / (MU_0 * espiras_por_metro)
    return corriente

def ajustar_resistencia_temperatura(resistencia_20c, temp_operacion_c=60):

    return resistencia_20c * (1 + COEF_TEMP_COBRE * (temp_operacion_c - 20))

def calcular_potencia_disipada(corriente_amp, resistencia_ohm):

    return (corriente_amp ** 2) * resistencia_ohm

def calcular_resistencia_total(resistencia_por_metro, diametro_carrete_m, total_espiras):

    longitud_por_vuelta = math.pi * diametro_carrete_m
    longitud_total_cable = longitud_por_vuelta * total_espiras
    
    return resistencia_por_metro * longitud_total_cable