"""
==================================================================
 SEMANA 1  |  PATRON SINGLETON
==================================================================
 Objetivo: garantizar que exista UNA SOLA instancia de clases
 criticas del sistema (configuracion, base de datos, logger y
 detector de fraude) y que todas las clases compartan la misma.

 Implementacion: metaclase `SingletonMeta` con doble chequeo y
 `threading.Lock` para que sea seguro en concurrencia
 (trabajo en tiempo real / multiples canales).

 En este modulo vive SOLO el mecanismo base del patron.
 Cada clase singleton del proyecto usa esta metaclase.
==================================================================
"""

import threading


class SingletonMeta(type):
    """Metaclase que convierte cualquier clase en un Singleton.

    Ejemplo de uso:
        class ConfigManager(metaclass=SingletonMeta):
            ...
    """

    # Diccionario que guarda la UNICA instancia de cada clase.
    _instancias = {}

    # Candado para que dos hilos no creen la instancia al mismo tiempo.
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        # Primera comprobacion rapida (sin candado) para no bloquear,
        # ya que la lectura de un dict es barata y segura.
        if cls not in cls._instancias:
            # Segunda comprobacion DENTRO del candado: si dos hilos
            # entran a la vez, solo uno crea la instancia.
            with cls._lock:
                if cls not in cls._instancias:
                    instancia = super().__call__(*args, **kwargs)
                    cls._instancias[cls] = instancia
        return cls._instancias[cls]


def es_singleton(cls) -> bool:
    """Confirmacion pedagogica de que una clase es singleton."""
    return isinstance(cls, SingletonMeta)