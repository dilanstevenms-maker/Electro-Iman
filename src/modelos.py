from dataclasses import dataclass
from typing import Optional

@dataclass
class Cable:
    id_calibre: int
    diametro_cobre_mm: float
    diametro_con_esmalte_mm: float
    area_seccion_transversal_mm2: float
    resistencia_ohm_por_metro: float
    corriente_max_amp: float
    masa_kg_por_km: float
    temp_max_aislante_c: int
    
    @classmethod
    def desde_diccionario(cls, datos: dict):
        """Crea una instancia de Cable a partir del diccionario devuelto por SQL."""
        return cls(**datos)

@dataclass
class ResultadoSolenoide:
    cable_seleccionado: Cable
    corriente_necesaria_amp: float
    numero_espiras_total: int
    potencia_disipada_watts: float
    
    def imprimir_resumen(self):
        print("Configuracion del solenoide:")
        print(f"Calibre AWG: {self.cable_seleccionado.id_calibre}")
        print(f"Número de espiras: {self.numero_espiras_total}")
        print(f"Corriente requerida: {self.corriente_necesaria_amp:.2f} A")
        print(f"Energía disipada (Calor): {self.potencia_disipada_watts:.2f} W")