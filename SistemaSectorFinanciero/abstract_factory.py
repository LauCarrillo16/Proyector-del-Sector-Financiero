"""
==================================================================
 SEMANA 3  |  PATRON ABSTRACT FACTORY
==================================================================
 Objetivo: crear FAMILIAS de objetos relacionados sin que el
 cliente sepa las clases concretas. El banco opera por MULTIPLES
 CANALES (Web, Movil, Cajero, Sucursal); cada canal necesita un
 CONJUNTO de artefactos relacionados: la operacion, la
 notificacion y la auditoria.

 Si cada canal creara sus objetos de forma suelta, podriamos
 mezclar una operacion de Cajero con una notificacion de Web.
 El Abstract Factory garantiza que, al elegir el canal, TODOS los
 artefactos pertenecen a la MISMA familia.

 Estructura clasica del patron:
   - FabricaAbstracta   : 'FabricaAbstractaCanal'
   - Fabricas concretas : 'FabricaWeb', 'FabricaMovil',
                          'FabricaCajero', 'FabricaSucursal'
   - Productos          : 'OperacionCanal', 'NotificacionCanal',
                          'AuditoriaCanal' (y sus variantes)

 ==== LUGAR DONDE SE TRABAJA EL PATRON (SEMANA 3) ====
 - Al registrar una operacion en la interfaz (ruta /transacciones):
        fabrica = obtener_fabrica_canal(canal)
        operacion   = fabrica.crear_operacion(tipo, monto)
        notificacion= fabrica.crear_notificacion()
        auditoria   = fabrica.crear_auditoria()
==================================================================
"""

import uuid
from abc import ABC, abstractmethod

from logger import logger


# =================================================================
# PRODUCTO 1: OPERACION (el registro de la operacion por canal)
# =================================================================
class OperacionCanal(ABC):
    """Producto abstracto: operacion con folio propio del canal."""

    def __init__(self, tipo, monto):
        self.tipo = tipo
        self.monto = monto
        self.canal = self._nombre_canal()

    @abstractmethod
    def _nombre_canal(self):
        pass

    @abstractmethod
    def _prefijo_folio(self):
        pass

    def generar_folio(self):
        return f"{self._prefijo_folio()}-{self.tipo}-{uuid.uuid4().hex[:6].upper()}"

    def describir(self):
        return f"[{self.canal}] Folio={self.generar_folio()} Tipo={self.tipo} Monto={self.monto:.2f}"


class OperacionWeb(OperacionCanal):
    def _nombre_canal(self): return "WEB"
    def _prefijo_folio(self): return "W"

    def describir(self):
        return super().describir() + " | Entorno: navegador con sesión SSL"


class OperacionMovil(OperacionCanal):
    def _nombre_canal(self): return "MOVIL"
    def _prefijo_folio(self): return "M"

    def describir(self):
        return super().describir() + " | Entorno: app con token OTP"


class OperacionCajero(OperacionCanal):
    def _nombre_canal(self): return "CAJERO"
    def _prefijo_folio(self): return "C"

    def describir(self):
        return super().describir() + " | Entorno: ATM con tarjeta + NIP"


class OperacionSucursal(OperacionCanal):
    def _nombre_canal(self): return "SUCURSAL"
    def _prefijo_folio(self): return "S"

    def describir(self):
        return super().describir() + " | Entorno: atencion por asesor con biometria"


# =================================================================
# PRODUCTO 2: NOTIFICACION (el medio de aviso propio del canal)
# =================================================================
class NotificacionCanal(ABC):
    """Producto abstracto: notificacion que confirma la operacion."""

    @abstractmethod
    def enviar(self, mensaje):
        """Devuelve el texto que el canal mostraria al canal."""
        pass


class NotificacionWeb(NotificacionCanal):
    def enviar(self, mensaje):
        return f"Correo electronico enviado: {mensaje}"


class NotificacionMovil(NotificacionCanal):
    def enviar(self, mensaje):
        return f"Notificacion PUSH + SMS: {mensaje}"


class NotificacionCajero(NotificacionCanal):
    def enviar(self, mensaje):
        return f"Comprobante impreso en el cajero: {mensaje}"


class NotificacionSucursal(NotificacionCanal):
    def enviar(self, mensaje):
        return f"Asesor de la sucursal entrega comprobante: {mensaje}"


# =================================================================
# PRODUCTO 3: AUDITORIA (la trazabilidad según el canal)
# =================================================================
class AuditoriaCanal(ABC):
    """Producto abstracto: deja trazabilidad de la operacion."""

    @abstractmethod
    def registrar(self, descripcion):
        pass


class AuditoriaWeb(AuditoriaCanal):
    def registrar(self, descripcion):
        logger.info(f"[AUDITORIA-WEB] {descripcion}")


class AuditoriaMovil(AuditoriaCanal):
    def registrar(self, descripcion):
        logger.info(f"[AUDITORIA-MOVIL] {descripcion}")


class AuditoriaCajero(AuditoriaCanal):
    def registrar(self, descripcion):
        logger.info(f"[AUDITORIA-CAJERO] {descripcion}")


class AuditoriaSucursal(AuditoriaCanal):
    def registrar(self, descripcion):
        logger.info(f"[AUDITORIA-SUCURSAL] {descripcion}")


# =================================================================
# FABRICA ABSTRACTA: define el contrato de cada familia
# =================================================================
class FabricaAbstractaCanal(ABC):
    """Fabrica abstracta (Semana 3). Crea una FAMILIA completa por canal."""

    @abstractmethod
    def crear_operacion(self, tipo, monto):
        pass

    @abstractmethod
    def crear_notificacion(self):
        pass

    @abstractmethod
    def crear_auditoria(self):
        pass


# =================================================================
# FABRICAS CONCRETAS: cada canal produce SU familia consistente
# =================================================================
class FabricaWeb(FabricaAbstractaCanal):
    """Familia de objetos del canal Web."""

    def crear_operacion(self, tipo, monto):
        return OperacionWeb(tipo, monto)

    def crear_notificacion(self):
        return NotificacionWeb()

    def crear_auditoria(self):
        return AuditoriaWeb()


class FabricaMovil(FabricaAbstractaCanal):
    """Familia de objetos del canal Movil."""

    def crear_operacion(self, tipo, monto):
        return OperacionMovil(tipo, monto)

    def crear_notificacion(self):
        return NotificacionMovil()

    def crear_auditoria(self):
        return AuditoriaMovil()


class FabricaCajero(FabricaAbstractaCanal):
    """Familia de objetos del canal Cajero (ATM)."""

    def crear_operacion(self, tipo, monto):
        return OperacionCajero(tipo, monto)

    def crear_notificacion(self):
        return NotificacionCajero()

    def crear_auditoria(self):
        return AuditoriaCajero()


class FabricaSucursal(FabricaAbstractaCanal):
    """Familia de objetos del canal Sucursal."""

    def crear_operacion(self, tipo, monto):
        return OperacionSucursal(tipo, monto)

    def crear_notificacion(self):
        return NotificacionSucursal()

    def crear_auditoria(self):
        return AuditoriaSucursal()


# =================================================================
# Selector publico: devuelve la fabrica adecuada según el canal.
# =================================================================
def obtener_fabrica_canal(canal):
    """Devuelve la familia de objetos correspondiente al canal (SEMANA 3)."""
    fabricas = {
        "WEB": FabricaWeb,
        "MOVIL": FabricaMovil,
        "CAJERO": FabricaCajero,
        "SUCURSAL": FabricaSucursal,
    }
    clase = fabricas.get(canal)
    if clase is None:
        raise ValueError(f"Canal desconocido: {canal}")
    return clase()