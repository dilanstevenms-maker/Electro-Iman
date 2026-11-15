import mysql.connector
from mysql.connector import Error

def conectar_db():
    """Establece la conexión con la base de datos MySQL local."""
    try:
        conexion = mysql.connector.connect(
            user='root',
            password='WLSn321R',
            host='localhost',
            port=3306,
            database='electroiman_db' 
        )
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error crítico al conectar a MySQL: {e}")
        return None

def obtener_catalogo_cables():
    conexion = conectar_db()
    if not conexion:
        return []

    try:
        # El parámetro dictionary=True es clave para no lidiar con índices numéricos
        cursor = conexion.cursor(dictionary=True)
        
        # catálogo ordenado del más grueso al más delgado
        consulta = "SELECT * FROM catalogo_cables_awg ORDER BY id_calibre ASC;"
        cursor.execute(consulta)
        
        cables = cursor.fetchall()
        return cables
        
    except Error as e:
        print(f"Error al consultar el catálogo de cables: {e}")
        return []
        
    finally:
        # Siempre debemos cerrar la conexión al terminar de traer los datos
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()


if __name__ == '__main__':
    print("Probando conexión a la base de datos...\n")
    catalogo = obtener_catalogo_cables()
    
    if catalogo:
        print(f"¡Conexión exitosa! Se han cargado {len(catalogo)} calibres AWG.")
        print("Ejemplo del primer registro (Calibre 0):")
        print(catalogo[0])
    else:
        print("No se pudieron cargar los datos. Revisa tus credenciales o Workbench.")