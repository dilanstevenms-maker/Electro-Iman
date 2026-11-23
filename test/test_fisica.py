"""Pruebas unitarias para fórmulas físicas, optimizador y capa de datos."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db.database_manager import DatabaseManager
from src import fisica
from src.errores import CampoInalcanzableError, GeometriaInvalidaError
from src.modelos import Cable, ResultadoSolenoide
from src.optimizador import evaluar_configuraciones, optimizar_solenoide


class TestFisicaElectroiman(unittest.TestCase):
    """Verifica las fórmulas electromagnéticas y térmicas."""

    def test_calcular_espiras_por_metro(self):
        # Cable con diámetro de 1.0 mm -> 1000 espiras/metro
        n = fisica.calcular_espiras_por_metro(1.0)
        self.assertAlmostEqual(n, 1000.0, places=2)

    def test_calcular_corriente(self):
        # B = 0.01 T, n = 1000 espiras/m
        # I = B / (mu_0 * n)
        n = 1000.0
        campo = 0.01
        corriente = fisica.calcular_corriente(campo, n)
        esperado = campo / (fisica.MU_0 * n)
        self.assertAlmostEqual(corriente, esperado, places=3)

    def test_ajuste_temperatura_cobre(self):
        r_20 = 1.0
        r_60 = fisica.ajustar_resistencia_temperatura(r_20, 60.0)
        esperado = 1.0 * (1.0 + fisica.COEF_TEMP_COBRE * 40.0)
        self.assertAlmostEqual(r_60, esperado, places=4)

    def test_potencia_disipada_joule(self):
        p = fisica.calcular_potencia_disipada(2.0, 5.0)
        self.assertEqual(p, 20.0)  # 2^2 * 5 = 20 W

    def test_fuerza_polar_teorica(self):
        f = fisica.calcular_fuerza_polar_teorica(0.01, 0.02)
        self.assertGreater(f, 0.0)


class TestDatabaseManager(unittest.TestCase):
    """Verifica la capa de abstracción de datos y compatibilidad."""

    def setUp(self):
        self.db = DatabaseManager.obtener_instancia()

    def test_catalogo_cargado(self):
        calibres = self.db.obtener_calibres()
        self.assertEqual(len(calibres), 41)
        self.assertEqual(calibres[0].id_calibre, 0)
        self.assertEqual(calibres[-1].id_calibre, 40)

    def test_filtros_rango(self):
        gruesos = self.db.obtener_calibres(calibre_min=0, calibre_max=5)
        self.assertEqual(len(gruesos), 6)

    def test_consultar_compatibilidad_optima(self):
        # AWG 10 soporta 16 A máx. Con 5 A debe ser óptimo/adecuado
        rep = self.db.consultar_compatibilidad(10, corriente_requerida_amp=5.0, temp_operacion_c=60.0)
        self.assertTrue(rep["es_compatible"])
        self.assertIn(rep["nivel"], ("optimo", "adecuado"))

    def test_consultar_compatibilidad_sobrecarga(self):
        # AWG 20 soporta 1.6 A. Con 10 A debe fallar por sobrecarga
        rep = self.db.consultar_compatibilidad(20, corriente_requerida_amp=10.0, temp_operacion_c=60.0)
        self.assertFalse(rep["es_compatible"])
        self.assertEqual(rep["nivel"], "sobrecarga")


class TestOptimizador(unittest.TestCase):
    """Verifica el algoritmo heurístico de selección óptima."""

    def setUp(self):
        self.db = DatabaseManager.obtener_instancia()
        self.catalogo = self.db.obtener_calibres()

    def test_caso_referencia_readme(self):
        # Parámetros: B=0.01 T, L=100 mm (0.1 m), D=20 mm (0.02 m), t=10 mm (0.01 m)
        resultado = optimizar_solenoide(0.01, 0.1, 0.02, 0.01, self.catalogo)
        self.assertEqual(resultado.cable_seleccionado.id_calibre, 5)
        self.assertEqual(resultado.numero_espiras_total, 42)
        self.assertAlmostEqual(resultado.corriente_necesaria_amp, 18.95, delta=0.1)
        self.assertAlmostEqual(resultado.potencia_disipada_watts, 1.66, delta=0.1)
        self.assertEqual(resultado.capas, 2)

    def test_evaluar_alternativas(self):
        mejor, viables = evaluar_configuraciones(0.01, 0.1, 0.02, 0.01, self.catalogo)
        self.assertGreater(len(viables), 1)
        self.assertEqual(mejor, viables[0])
        # Verificar orden creciente de potencia
        for i in range(len(viables) - 1):
            self.assertLessEqual(viables[i].potencia_disipada_watts, viables[i + 1].potencia_disipada_watts)

    def test_geometria_invalida(self):
        # Carrete de tamaño microscópico donde ningún cable cabe
        with self.assertRaises(GeometriaInvalidaError):
            optimizar_solenoide(0.01, 0.0001, 0.02, 0.00001, self.catalogo)


if __name__ == "__main__":
    unittest.main()
