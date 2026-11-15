def _pedir_numero(mensaje: str) -> float | None:
    while True:
        try:
            entrada = input(mensaje).strip()
            if entrada.lower() in ("salir", "exit", "q"):
                return None
            valor = float(entrada.replace(",", "."))
            if valor <= 0:
                print("  El valor debe ser mayor a 0.")
                continue
            return valor
        except ValueError:
            print("  Ingresa un número válido (o 'salir' para cancelar).")


def solicitar_parametros():
    """Devuelve (B [T], longitud [m], diámetro carrete [m], espesor máx [m]) o None si se cancela."""
    print("\n" + "=" * 45)
    print("   Diseño computacional de un electroimán")
    print("=" * 45)
    campo_b = _pedir_numero("Campo magnético deseado (T): ")
    if campo_b is None:
        return None
    longitud_mm = _pedir_numero("Longitud del solenoide (mm): ")
    if longitud_mm is None:
        return None
    diametro_mm = _pedir_numero("Diámetro del carrete (mm): ")
    if diametro_mm is None:
        return None
    espesor_mm = _pedir_numero("Espesor máximo de bobinado (mm): ")
    if espesor_mm is None:
        return None
    return campo_b, longitud_mm / 1000, diametro_mm / 1000, espesor_mm / 1000


def mostrar_resultado(resultado):
    print("\n" + "-" * 45)
    resultado.imprimir_resumen()
    print("-" * 45)


def mostrar_error(error):
    print(f"\n[Error] {error}")


def preguntar_si_continuar(mensaje: str = "¿Deseas realizar otra consulta? (s/n) [s]: ") -> bool:
    try:
        respuesta = input(mensaje).strip().lower()
        if respuesta in ("", "s", "si", "sí", "y", "yes"):
            return True
        return False
    except (KeyboardInterrupt, EOFError):
        return False