"""
==================================================================
 SEMANA 2  |  PATRON FACTORY METHOD
==================================================================
 Objetivo: delegar la CREACION de cuentas bancarias a fabricas
 especializadas. La clase base `FabricaCuentas` define el metodo
 plantilla `registrar_cuenta()` que ya sabe QUÉ pasos seguir, pero
 la decision de QUÉ objeto cUenta crear queda en cada fabrica
 concreta mediante el metodo abstracto `crear_cuenta()`.

 Estructura clasica del patron:
   - Producto           : 'Cuenta' (y sus subclases CuentaAhorro,
                           CuentaCorriente, CuentaInversion)
   - Creador (abstracto): 'FabricaCuentas'
   - Creadores concretos: 'FabricaCuentaAhorro' y compañía

 ==== LUGAR DONDE SE TRABAJA EL PATRON (SEMANA 2) ====
 - Al crear una cuenta en la interfaz (ruta /cuentas, app.py):
        fabrica = obtener_fabrica(tipo)
        resultado = fabrica.registrar_cuenta(...)
 - La logica COMMON de persistencia vive en FabricaCuentas
   (el metodo plantilla); cada fabrica solo elige la clase Cuenta.
==================================================================
"""

from abc import ABC, abstractmethod
from datetime import datetime

from database import Database
from logger import logger


# =================================================================
# 1. PRODUCTOS (la jerarquia de objetos que se crean)
# =================================================================
class Cuenta(ABC):
    """Producto base dentro del Factory Method (Semana 2)."""

    def __init__(self, cliente_id, saldo_inicial, canal):
        self.cliente_id = cliente_id
        self.saldo = saldo_inicial
        self.canal = canal
        self.tipo = self._nombre_tipo()
        self._fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @abstractmethod
    def _nombre_tipo(self):
        """Cada cuenta concreta responde su propio tipo de negocio."""
        pass

    @property
    @abstractmethod
    def prefijo_numero(self):
        """Prefijo usado al generar el numero de cuenta."""
        pass

    def registrar_en_db(self, numero):
        Database().ejecutar(
            "INSERT INTO cuentas(cliente_id, numero, tipo, saldo, canal, fecha) "
            "VALUES (?,?,?,?,?,?)",
            (self.cliente_id, numero, self.tipo, self.saldo, self.canal, self._fecha),
        )
        logger.info(f"[FACTORY] Cuenta creada: {numero} tipo={self.tipo} canal={self.canal}")
        return numero


class CuentaAhorro(Cuenta):
    """Producto concreto: cuenta de ahorro."""

    def _nombre_tipo(self):
        return "AHORRO"

    @property
    def prefijo_numero(self):
        return "AHO"


class CuentaCorriente(Cuenta):
    """Producto concreto: cuenta corriente para operar a diario."""

    def _nombre_tipo(self):
        return "CORRIENTE"

    @property
    def prefijo_numero(self):
        return "CTE"


class CuentaInversion(Cuenta):
    """Producto concreto: cuenta para inversiones."""

    def _nombre_tipo(self):
        return "INVERSION"

    @property
    def prefijo_numero(self):
        return "INV"


# =================================================================
# 2. CREADOR ABSTRACTO (define el metodo plantilla)
# =================================================================
class FabricaCuentas(ABC):
    """Creador del patron. No sabe QUE tipo de cuenta fabrica,
    pero si COMO dejarla registrada (metodo plantilla)."""

    def registrar_cuenta(self, cliente_id, numero, saldo_inicial, canal):
        """
        Metodo plantilla: pasos fijos que no cambian.
        1) Pedir a la subclase la cuenta concreta (factory method).
        2) Persistirla.
        3) Confirmar que estas activo el patron.
        """
        # ---- FACTORY METHOD: la llamada abstracta que cada subclase responde ----
        cuenta = self.crear_cuenta(cliente_id, saldo_inicial, canal)
        # ------------------------------------------------------------------------
        numero_final = numero or self.generar_numero(cuenta)
        cuenta.registrar_en_db(numero_final)
        return numero_final, cuenta

    @abstractmethod
    def crear_cuenta(self, cliente_id, saldo_inicial, canal):
        """FACTORY METHOD: cada fabrica concreta decide el producto."""
        pass

    def generar_numero(self, cuenta):
        """Numero correlativo unico por prefijo del tipo de cuenta."""
        prefijo = cuenta.prefijo_numero
        for intento in range(1, 10000):
            numero = f"{prefijo}-{1000 + intento}"
            if Database().consulta_una(
                "SELECT id FROM cuentas WHERE numero = ?", (numero,)
            ) is None:
                return numero
        raise ValueError("No se pudo generar un numero de cuenta disponible")


# =================================================================
# 3. CREADORES CONCRETOS (cada uno decide un solo producto)
# =================================================================
class FabricaCuentaAhorro(FabricaCuentas):
    """Solo sabe fabricar CuentaAhorro."""

    def crear_cuenta(self, cliente_id, saldo_inicial, canal):
        return CuentaAhorro(cliente_id, saldo_inicial, canal)


class FabricaCuentaCorriente(FabricaCuentas):
    """Solo sabe fabricar CuentaCorriente."""

    def crear_cuenta(self, cliente_id, saldo_inicial, canal):
        return CuentaCorriente(cliente_id, saldo_inicial, canal)


class FabricaCuentaInversion(FabricaCuentas):
    """Solo sabe fabricar CuentaInversion."""

    def crear_cuenta(self, cliente_id, saldo_inicial, canal):
        return CuentaInversion(cliente_id, saldo_inicial, canal)


# =================================================================
# Selector que enruta el tipo pedido en la interfaz a una fabrica.
# =================================================================
def obtener_fabrica(tipo_cuenta):
    """Devuelve la fabrica concreta según el tipo (SEMANA 2).

    El cliente de la fabrica (la interfaz) nunca instancia Cuenta
    directamente; solo pide la fabrica y esta decide el producto.
    """
    fabricas = {
        "AHORRO": FabricaCuentaAhorro,
        "CORRIENTE": FabricaCuentaCorriente,
        "INVERSION": FabricaCuentaInversion,
    }
    clase = fabricas.get(tipo_cuenta)
    if clase is None:
        raise ValueError(f"Tipo de cuenta desconocido: {tipo_cuenta}")
    return clase()