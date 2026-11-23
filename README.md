# ELECTROIMÁN STUDIO — Diseño y Optimización de Electroimanes

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6%20Glassmorphism-00F5A0.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)]()

**ELECTROIMÁN STUDIO** es una aplicación de escritorio moderna desarrollada en **Python (PyQt6)** con dirección de arte en **Glassmorphism Cósmico**. Su objetivo es determinar la combinación óptima de alambre magneto AWG (calibres 0 al 40) para la construcción de electroimanes y solenoides de alto rendimiento, optimizando el consumo energético y garantizando límites de seguridad térmica y restricciones físicas de bobinado.

---

## 🎨 Dirección de Arte y Estética (Glassmorphism Cósmico)

* **Fondo Ambiental:** Lienzo cósmico profundo renderizado con aceleración por hardware (`QPainter`), combinando degradados azul medianoche (`#090A15`), violeta oscuro (`#100C22`) y halos difusos en verde menta neón (`#00F5A0`) y púrpura cósmico.
* **Paneles de Vidrio Esmerilado:** Contenedores translúcidos con canal alfa, bordes suaves de 1 px semitransparentes (`rgba(255, 255, 255, 0.10)`) y sombras difusas de elevación.
* **Paleta de Interacción:** 
  * **Verde menta brillante (`#00F5A0`)** y **Cian eléctrico (`#00D9F5`)** para destacar botones principales, deslizadores, cursores neón, badges de estado y métricas clave.
* **Tipografía:** Tipografía limpia y moderna sans-serif (*Segoe UI / Inter*), con legibilidad y contraste óptimos.

---

## 🚀 Arquitectura y Pantallas de la Aplicación

La aplicación implementa una navegación fluida entre múltiples pantallas integradas:

```
[ Pantalla 1: Inicio Elegante ]
               │
               ▼  (INICIAR CONSULTA →)
[ Pantalla 2: Dashboard de Parámetros ] ◄──► [ Pantalla 4: Catálogo AWG (SQL) ]
               │
               ▼  (CALCULAR COMBINACIÓN)
[ Pantalla 3: Visualización de Resultados ] ──► (Volver a Parámetros)
```

### 1. Pantalla de Inicio (Bienvenida Minimalista)
* Nombre destacado: **ELECTROIMÁN STUDIO**.
* Subtítulo: *Diseño Minimalista de Electroimanes — Por Carolina Molina y Dilan Muñoz*.
* Botón central con resplandor neón: **`INICIAR CONSULTA →`**.
* Identificador de autoría superior: *Carolina Molina & Dilan Muñoz*.

### 2. Dashboard de Parámetros (Entradas de Diseño)
Tres tarjetas horizontales de vidrio esmerilado:
* **Parámetros del Solenoide:** Sliders fluidos sincronizados con cajitas de valor numérico para:
  * Longitud útil ($L$): 20 a 400 mm (por defecto 214.1 mm).
  * Diámetro interior ($D_{int}$): 5 a 100 mm (por defecto 5.0 mm).
  * Espesor máximo de bobinado ($t_{bob}$): 2 a 40 mm (por defecto 10.0 mm).
* **Material del Núcleo:** Selector de permeabilidad magnética ($\mu_r$) para núcleos de Aire ($\mu_r = 1$), Hierro Dulce Laminado ($\mu_r = 250$), Ferrita Ni-Zn ($\mu_r = 50$) o Acero al Silicio ($\mu_r = 500$).
* **Parámetros de Operación:**
  * Temperatura estimada ($T_{op}$): 20 a 120 °C (con corrección de resistividad térmica del cobre).
  * Interruptor deslizante (*Switch Toggle*) para el **Modo de Optimización**.
* Botón de acción: **`CALCULAR COMBINACIÓN`**.

### 3. Visualización de Resultados (Combinación Ideal)
* **Hero Card Principal:**
  * Calibre óptimo destacado en tipografía gigante: **`AWG 5`** con badge de validación **`★ ÓPTIMO`**.
  * Rejilla de 6 microtarjetas métricas de vidrio esmerilado:
    * 🌀 **Espiras Totales:** ej. `90 vueltas`
    * ⚡ **Corriente Requerida:** ej. `18.93 A`
    * 🔥 **Potencia Disipada (Joule):** ej. `1.74 W`
    * 🛡️ **Resistencia Eléctrica:** ej. `0.005 Ω`
    * 🔌 **Voltaje DC Requerido:** ej. `0.09 V`
    * 🧲 **Fuerza Polar Teórica:** ej. `0.00 N`
  * **Barra de Carga Térmica:** Barra de progreso dinámico ($I / I_{máx}$) en verde menta neón.
* **Panel Lateral de Alternativas Compatibles:**
  * Tabla con el ranking de los calibres viables evaluados (`AWG 11`, `AWG 13`, `AWG 15`) indicando espiras, capas y caída de tensión.
* Botón de navegación: **`Volver a Parámetros`**.

### 4. Catálogo de Calibres AWG (Capa de Datos SQL)
* Tabla dinámica de 6 columnas con los 41 calibres AWG del catálogo.
* Filtros rápidos: Gruesos (0-14), Medios (15-28) y Finos (29-40).
* Indicador de conexión con el motor SQL: `[●] MySQL Offline (base de datos local - adapter)`.

---

## 📁 Estructura del Proyecto

```text
Electro-Iman/
├── main.py                     # Punto de entrada principal (High-DPI y carga de estilos)
├── ui.py                       # Componentes POO, widgets de vidrio y pantallas de la GUI
├── logica.py                   # Lógica de cálculo (dummy/placeholder y motor físico real)
├── styles.qss                  # Hoja de estilos Qt Style Sheets (Glassmorphism Cósmico)
├── requirements.txt            # Dependencias del proyecto
├── README.md                   # Documentación oficial
├── data/
│   └── esquema.sql             # Script SQL de inicialización en MySQL
├── interfaz/
│   ├── cli.py                  # Modo interactivo clásico para terminal
│   └── styles.qss              # Estilos del subpaquete
├── src/
│   ├── db/
│   │   ├── database_manager.py # Capa de abstracción SQL desacoplada (MySQL + Fallback)
│   │   └── datos_catalogo.py   # Catálogo estandarizado de los 41 calibres AWG
│   ├── fisica.py               # Fórmulas de Biot-Savart, Ohm, Joule y variación térmica
│   ├── modelos.py              # Modelos Cable, ParametrosEntrada y ResultadoSolenoide
│   ├── optimizador.py          # Búsqueda heurística y ranking de combinaciones viables
│   └── errores.py              # Excepciones personalizadas
└── test/
    ├── test_fisica.py          # 12 pruebas unitarias de cálculo y optimización
    └── test_interfaz.py        # 6 pruebas unitarias de renderizado PyQt6
```

---

## ⚙️ Instalación y Requisitos

### Requisitos Previos
* **Python 3.10 o superior** (probado en Python 3.10, 3.11, 3.12, 3.13 y 3.14).
* Servidor MySQL Server 8.0+ (opcional, cuenta con modo fallback automático con los 41 calibres cargados).

### 1. Clonar el repositorio
```bash
git clone https://github.com/dilanstevenms-maker/Electro-Iman.git
cd Electro-Iman
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

---

## 💻 Ejecución

### Modo Interfaz Gráfica (Glassmorphism Studio)
```bash
python main.py
```

### Modo Terminal Clásico (CLI)
```bash
python main.py --cli
```

### Ejecutar Pruebas Unitarias
```bash
python test/test_fisica.py
python test/test_interfaz.py
```

---

## 👥 Autores

* **Carolina Molina**
* **Dilan Muñoz**

**Universidad Sergio Arboleda**  
Ciencias de la Computación e Inteligencia Artificial
