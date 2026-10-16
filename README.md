# Diseño Computacional de un Electroimán

Herramienta de software desarrollada en Python para determinar los parámetros óptimos en la construcción de un electroimán (solenoide). 

Mediante un enfoque de búsqueda heurística, el algoritmo evalúa múltiples combinaciones de calibres de cable AWG, descartando automáticamente los diseños que superan el límite de seguridad térmico por efecto Joule.

## Características
A partir del **campo magnético deseado (Teslas)** y el **espacio disponible**, el programa calcula:
- Calibre óptimo del cable AWG.
- Número exacto de espiras.
- Corriente eléctrica necesaria (Amperios).
- Energía disipada en forma de calor (Watts).

## Estructura del Proyecto
- `data/`: Scripts SQL para la creación del catálogo de cables AWG.
- `src/`: Lógica central, ecuaciones físicas, modelos de datos y algoritmo optimizador.
- `interfaz/`: Entradas de usuario y presentación de resultados en consola.

## Requisitos e Instalación
1. Clonar el repositorio:
   git clone [https://github.com/dilanstevenms-maker/Electro-Iman.git](https://github.com/dilanstevenms-maker/Electro-Iman.git)
2. Instalar las dependencias: `pip install -r requirements.txt`.
3. Ejecutar el script `data/esquema_db.sql` en MySQL Workbench para levantar los datos.
4. Ajustar las credenciales locales en `src/db/conexion.py`
## Autores
Carolina Molina y Dilan Muñoz
Universidad Sergio Arboleda - Ciencias de la Computación e IA