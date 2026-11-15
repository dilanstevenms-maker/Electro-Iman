# Diseño Computacional de un Electroimán

Herramienta de software desarrollada en Python para determinar los parámetros óptimos en la construcción de un electroimán (solenoide con núcleo de aire). 

Mediante un enfoque de búsqueda heurística, el algoritmo evalúa múltiples combinaciones de calibres de cable AWG almacenados en MySQL, descartando automáticamente los diseños que no caben físicamente en el carrete o que superan el límite de seguridad térmico por efecto Joule.

---

## Características

* **Búsqueda heurística y optimización:** Evalúa sistemáticamente los calibres del catálogo AWG y configuraciones de capas para minimizar la potencia disipada en calor ($P = I^2 R$).
* **Restricciones físicas y térmicas:** Comprueba que la corriente requerida no supere el amperaje máximo del conductor y que la temperatura de operación no degrade el aislamiento térmico del barniz.
* **Sesión interactiva continua:** Permite realizar múltiples consultas consecutivas y ajustar parámetros en caso de error o inviabilidad física sin reiniciar el programa.
* **Cálculo detallado de resultados:**
  * Calibre óptimo del cable AWG.
  * Número exacto de espiras y capas.
  * Corriente eléctrica necesaria (Amperios).
  * Potencia disipada en forma de calor (Watts).

---

## Estructura del Proyecto

```text
Electro-Iman/
├── data/
│   └── esquema.sql          # Creación de BD 'electroiman_db' y catálogo AWG (0 al 40)
├── interfaz/
│   └── cli.py               # Menú interactivo por consola y formateo de resultados
├── src/
│   ├── db/
│   │   └── conexion.py      # Conexión con MySQL y consulta del catálogo
│   ├── errores.py           # Excepciones personalizadas (geométricas, térmicas, etc.)
│   ├── fisica.py            # Fórmulas de campo magnético, resistencia y calor Joule
│   ├── modelos.py           # Dataclasses de Cable y ResultadoSolenoide
│   ├── optimizador.py       # Algoritmo heurístico de optimización
│   └── restricciones.py     # Validaciones de espacio geométrico y límites de corriente
├── test/
│   └── test_fisica.py       # Pruebas unitarias
├── main.py                  # Punto de entrada principal de la aplicación
├── requirements.txt         # Dependencias del proyecto
└── README.md
```

---

## Requisitos e Instalación

### 1. Requisitos Previos
* Python 3.10 o superior.
* MySQL Server (v8.0 o superior) y MySQL Workbench instalados y en ejecución (puerto por defecto: `3306`).

### 2. Clonar el repositorio
```bash
git clone https://github.com/dilanstevenms-maker/Electro-Iman.git
cd Electro-Iman
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar la Base de Datos
1. Abre **MySQL Workbench** y conéctate a tu servidor local.
2. Abre y ejecuta el script [`data/esquema.sql`](data/esquema.sql). Esto creará la base de datos `electroiman_db` y cargará los 41 calibres AWG en la tabla `catalogo_cables_awg`.
3. Verifica o ajusta tus credenciales locales (usuario, contraseña y puerto) en [`src/db/conexion.py`](src/db/conexion.py):
   ```python
   conexion = mysql.connector.connect(
       user='root',
       password='TU_CONTRASENA',
       host='localhost',
       port=3306,
       database='electroiman_db'
   )
   ```

### 5. Verificar la conexión a MySQL (Opcional)
Puedes comprobar rápidamente que la base de datos responda ejecutando:
```bash
python src/db/conexion.py
```
*(Deberás ver el mensaje de confirmación con los 41 registros cargados).*

---

## Guía de Uso

Inicia la aplicación ejecutando:
```bash
python main.py
```

### Parámetros de Entrada Solicitados

| Parámetro | Unidad | Rango Típico Sugerido | Descripción |
| :--- | :---: | :---: | :--- |
| **Campo magnético deseado** | **T (Teslas)** | `0.001` - `0.03` T | Campo magnético objetivo en el centro del solenoide. |
| **Longitud del solenoide** | **mm** | `50` - `300` mm | Largo del carrete o tubo donde se enrollará el cable. |
| **Diámetro del carrete** | **mm** | `10` - `50` mm | Diámetro interior del carrete. |
| **Espesor máximo de bobinado** | **mm** | `5` - `25` mm | Altura disponible para apilar capas de conductor. |

> **Nota:** Puedes usar punto (`.`) o coma (`,`) para los decimales. Si deseas cancelar en cualquier momento, puedes escribir `salir` o `q`.

### Ejemplo de Salida

```text
=============================================
   Diseño computacional de un electroimán
=============================================
Campo magnético deseado (T): 0.01
Longitud del solenoide (mm): 100
Diámetro del carrete (mm): 20
Espesor máximo de bobinado (mm): 10

---------------------------------------------
Configuracion del solenoide:
Calibre AWG: 5
Número de espiras: 42
Corriente requerida: 18.95 A
Energía disipada (Calor): 1.66 W
---------------------------------------------

¿Deseas realizar otra consulta? (s/n) [s]:
```

---

## Autores

* **Carolina Molina**
* **Dilan Muñoz**

**Universidad Sergio Arboleda**  
Ciencias de la Computación e Inteligencia Artificial