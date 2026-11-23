"""Pruebas unitarias para la interfaz gráfica PyQt6 y componentes Glassmorphism."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Forzamos modo offscreen para entornos sin monitor o headless CI
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication

from interfaz.dialogs.db_config_dialog import DatabaseConfigDialog
from interfaz.gui_main import ElectroimanMainWindow
from interfaz.styles import CosmicColors, STYLESHEET_GLOBAL
from interfaz.tabs.database_tab import DatabaseTab
from interfaz.tabs.simulator_tab import SimulatorTab
from interfaz.widgets.glass_cards import GlassMetricCard, StatusBadge, ThermalSafetyBar
from interfaz.widgets.glass_slider import GlassParamSlider

_APP = None


def get_qapp():
    global _APP
    if _APP is None:
        _APP = QApplication.instance() or QApplication(sys.argv)
    return _APP


class TestInterfazPyQt6(unittest.TestCase):
    """Verifica que la UI Glassmorphism se construya y responda de forma fluida."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()

    def test_stylesheet_compilacion(self):
        self.assertIn("QMainWindow", STYLESHEET_GLOBAL)
        self.assertIn(CosmicColors.ACCENT_MINT, STYLESHEET_GLOBAL)
        self.assertIn(CosmicColors.ACCENT_CYAN, STYLESHEET_GLOBAL)

    def test_glass_param_slider(self):
        slider = GlassParamSlider(
            titulo="Campo B",
            simbolo="B",
            unidad="T",
            min_val=0.001,
            max_val=0.05,
            val_default=0.01,
            paso=0.001,
            decimales=3,
        )
        self.assertAlmostEqual(slider.valor(), 0.01, places=3)
        slider.set_valor(0.025)
        self.assertAlmostEqual(slider.valor(), 0.025, places=3)

    def test_thermal_safety_bar(self):
        bar = ThermalSafetyBar()
        bar.set_porcentaje(45.0)
        self.assertEqual(bar.barra.value(), 45)
        bar.set_porcentaje(92.0)
        self.assertEqual(bar.barra.value(), 92)

    def test_status_badge(self):
        badge = StatusBadge("OK", "ok")
        self.assertEqual(badge.lbl_texto.text(), "OK")
        badge.set_estado("Alerta", "advertencia")
        self.assertEqual(badge.lbl_texto.text(), "Alerta")

    def test_ventana_principal_creacion(self):
        ventana = ElectroimanMainWindow()
        self.assertIsNotNone(ventana.tab_simulador)
        self.assertIsNotNone(ventana.tab_database)

        # Debe tener calculado el óptimo inicial
        res = ventana.tab_simulador.resultado_actual
        self.assertIsNotNone(res)
        self.assertEqual(res.cable_seleccionado.id_calibre, 5)

        # Probar cambio de slider
        ventana.tab_simulador.slider_longitud.set_valor(120.0)
        ventana.tab_simulador.calcular_optimo()
        self.assertIsNotNone(ventana.tab_simulador.resultado_actual)

    def test_dialogo_configuracion_db(self):
        dlg = DatabaseConfigDialog()
        cfg = dlg._obtener_config_form()
        self.assertIn("host", cfg)
        self.assertIn("port", cfg)
        self.assertIn("database", cfg)


if __name__ == "__main__":
    unittest.main()

