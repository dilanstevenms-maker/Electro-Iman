class ElectroimanError(Exception):
    
    pass

class RestriccionTermicaError(ElectroimanError):
    def __init__(self, mensaje="El diseño supera el límite de seguridad térmico del cobre."):
        self.mensaje = mensaje
        super().__init__(self.mensaje)

class GeometriaInvalidaError(ElectroimanError):
    def __init__(self, mensaje="El espacio disponible es insuficiente para el bobinado."):
        self.mensaje = mensaje
        super().__init__(self.mensaje)

class CampoInalcanzableError(ElectroimanError):
    def __init__(self, mensaje="Ningún calibre AWG evaluado es viable para este campo magnético."):
        self.mensaje = mensaje
        super().__init__(self.mensaje)