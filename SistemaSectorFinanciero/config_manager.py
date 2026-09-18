"""
==================================================================
 SEMANA 1 - PATRON SINGLETON (aplicacion: CONFIGURACION GLOBAL)
==================================================================
 ConfigManager es EL UNICO lugar donde vive la configuracion del
 banco. No importa cuantas veces se llame `ConfigManager()`,
 siempre se devuelve la misma instancia, asi todos los canales
 comparten los mismos limites, comisiones y parametros.

 ==== LUGAR DONDE SE TRABAJA EL PATRON (SEMANA 1) ====
 - Hereda de `metaclass=SingletonMeta`  ->  instancia unica.
 - Es usado por app.py, el detector de fraude, las fabricas y
   los builders para leer parametros sin crear copias.
==================================================================
"""

from singleton import SingletonMeta


def _por_defecto():
    """Valores por defecto de la entidad bancaria."""
    import json
    import os

    origen = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(origen):
        with open(origen, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    return {}


class ConfigManager(metaclass=SingletonMeta):
    """Singleton que concentra toda la configuracion del sistema."""

    def __init__(self):
        # `__init__` solo se ejecuta UNA vez gracias a la metaclase.
        datos = _por_defecto()
        self._config = {
            "banco": datos.get("banco", "Banco Andino S.A."),
            "moneda": datos.get("moneda", "PEN"),
            "db_file": datos.get("db_file", "banco.db"),
            # Canales multicanal - usados por el Abstract Factory (Semana 3).
            "canales": datos.get("canales", ["WEB", "MOVIL", "CAJERO", "SUCURSAL"]),
            # Limites usados por el detector de fraude (tiempo real).
            "limite_deposito": datos.get("limite_deposito", 8000.0),
            "limite_retiro": datos.get("limite_retiro", 5000.0),
            "limite_transferencia": datos.get("limite_transferencia", 10000.0),
            # Umbrales AML (cumplimiento regulatorio).
            "monto_gran_operacion": datos.get("monto_gran_operacion", 20000.0),
            "tasa_riesgo": datos.get("tasa_riesgo", 0.35),
        }

    # --- Metodos de acceso -------------------------------------
    def obtener(self, clave):
        return self._config.get(clave)

    def banco(self):
        return self._config["banco"]

    def moneda(self):
        return self._config["moneda"]

    def canales(self):
        return self._config["canales"]


# Variable global conveniente: cualquiera hace `from config_manager import config`.
config = ConfigManager()