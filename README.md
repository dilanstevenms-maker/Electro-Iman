# Diseño Computacional de un Electroimán

Proyecto en Python para determinar los parámetros óptimos en la construcción de un electroimán (solenoide)[cite: 7]. 

El algoritmo utiliza una búsqueda heurística para evaluar combinaciones de calibres de cable AWG, aplicando restricciones térmicas para descartar automáticamente los diseños que superen el límite de seguridad por efecto Joule[cite: 8, 10, 11].

## Características
A partir del campo magnético deseado y el espacio disponible, el sistema calcula[cite: 7]:
- Calibre del cable AWG
- Número de espiras
- Corriente eléctrica necesaria
- Energía disipada en forma de calor

## Estructura del proyecto
- data/: Scripts SQL para la creación de la base de datos de cables[cite: 4].
- src/: Lógica matemática, ecuaciones físicas, modelos y optimizador[cite: 4].
- interfaz/: Interacción con el usuario mediante consola[cite: 4].

## Instalación y ejecución
1. Clonar el repositorio.
2. Instalar las dependencias: `pip install -r requirements.txt`.
3. Ejecutar el script `data/esquema_db.sql` en MySQL Workbench para levantar los datos.
4. Ajustar las credenciales locales en `src/db/conexion.py`.

## Autores
Carolina Molina y Dilan Muñoz
Universidad Sergio Arboleda - Ciencias de la Computación e IA