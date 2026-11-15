from interfaz.cli import (
    mostrar_error,
    mostrar_resultado,
    preguntar_si_continuar,
    solicitar_parametros,
)
from src.db.conexion import obtener_catalogo_cables
from src.errores import ElectroimanError
from src.modelos import Cable
from src.optimizador import optimizar_solenoide


def main():
    filas = obtener_catalogo_cables()
    if not filas:
        mostrar_error(
            "No se pudo cargar el catálogo AWG. Revisa que MySQL esté encendido "
            "(puerto 3306) y que hayas ejecutado data/esquema.sql."
        )
        return

    catalogo = [Cable.desde_diccionario(fila) for fila in filas]

    while True:
        try:
            parametros = solicitar_parametros()
            if parametros is None:
                print("\nConsulta cancelada.")
                break

            campo_b, longitud_m, diametro_m, espesor_m = parametros
            resultado = optimizar_solenoide(campo_b, longitud_m, diametro_m, espesor_m, catalogo)
            mostrar_resultado(resultado)

        except (ElectroimanError, ValueError) as e:
            mostrar_error(e)
            print("\nPuedes ajustar los parámetros para intentar con otra configuración.")

        except (KeyboardInterrupt, EOFError):
            print("\n\nSesión finalizada por el usuario.")
            break

        print()
        if not preguntar_si_continuar():
            print("\n¡Gracias por usar la herramienta! Hasta luego.\n")
            break


if __name__ == "__main__":
    main()