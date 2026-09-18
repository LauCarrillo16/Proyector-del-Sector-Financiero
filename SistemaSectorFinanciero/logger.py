"""
==================================================================
 SEMANA 1 - PATRON SINGLETON (aplicacion: LOGGER)
==================================================================
 LoggerService es un Singleton que centraliza el registro de
 eventos. Todas las clases del banco (fabricas, builders, canales,
 deteccion de fraude) usan el MISMO logger, de modo que el log
 queda ordenado y en un solo lugar.

 ==== LUGAR DONDE SE TRABAJA EL PATRON (SEMANA 1) ====
 - `metaclass=SingletonMeta` -> una unica instancia del logger.
==================================================================
"""

import logging
import sys
from datetime import datetime

from singleton import SingletonMeta


class LoggerService(metaclass=SingletonMeta):
    """Singleton que expone un logger estandar de Python."""

    def __init__(self):
        self._logger = logging.getLogger("banco_patrones")
        if not self._logger.handlers:
            consola = logging.StreamHandler(sys.stdout)
            consola.setFormatter(
                logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
            )
            self._logger.addHandler(consola)
            self._logger.setLevel(logging.INFO)

    def info(self, mensaje):
        self._logger.info(mensaje)

    def advertir(self, mensaje):
        self._logger.warning(mensaje)

    def error(self, mensaje):
        self._logger.error(mensaje)

    def evento(self, accion, detalle):
        """Logueo de auditoria con fecha legible para el cumplimiento."""
        self.info(f"{accion} | {detalle}")


logger = LoggerService()