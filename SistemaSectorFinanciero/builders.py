"""
==================================================================
 SEMANA 4  |  PATRON BUILDER
==================================================================
 Objetivo: construir objetos COMPLEJOS paso a paso. Un prestamo y
 una inversion tienen muchos campos OPCIONALES (garantia, seguro,
 perfil de riesgo...). Con Constructor (Builder) la interfaz puede
 ensamblar el objeto eligiendo solo los pasos que necesita, sin
 constructores gigantes llenos de parametros.

 Estructura clasica del patron:
   - Producto    : 'Prestamo' e 'Inversion'
   - Builder     : 'PrestamoBuilder' e 'InversionBuilder'
   - Director    : 'PrestamoDirector' e 'InversionDirector'
                   (prefabrica configuraciones populares)

 ==== LUGAR DONDE SE TRABAJA EL PATRON (SEMANA 4) ====
 - Al crear un prestamo (ruta /prestamos, app.py):
       builder = PrestamoBuilder().cliente(...).monto(...).plazo(...)
       resultado = builder.construir()
 - Al crear una inversion (ruta /inversiones, app.py):
       builder = InversionBuilder().inversor(...).tipo(...)
       resultado = builder.construir()
==================================================================
"""

from datetime import datetime

from database import Database
from logger import logger


# =================================================================
# PRODUCTO 1: PRESTAMO
# =================================================================
class Prestamo:
    """Producto complejo que ensambla el PrestamoBuilder."""

    def __init__(self):
        self.cliente_id = None
        self.tipo = None
        self.monto = 0.0
        self.plazo_meses = 12
        self.tasa = 0.0
        self.garantia = None
        self.seguro = 0.0
        self.estado = "ACTIVO"
        self.fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def calcular_cuota(self):
        """Cuota fija mensual (sistema frances)."""
        if self.monto <= 0 or self.plazo_meses <= 0:
            return 0.0
        i = self.tasa / 12.0
        if i == 0:
            return self.monto / self.plazo_meses
        factor = (1 + i) ** self.plazo_meses
        return (self.monto * i * factor) / (factor - 1)

    def registrar(self):
        cuota = self.calcular_cuota()
        Database().ejecutar(
            "INSERT INTO prestamos(cliente_id, tipo, monto, plazo_meses, tasa, garantia, seguro, cuota, estado, fecha) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                self.cliente_id, self.tipo, self.monto, self.plazo_meses,
                self.tasa, self.garantia, self.seguro, cuota, self.estado, self.fecha,
            ),
        )
        logger.info(
            f"[BUILDER] Prestamo {self.tipo} creado: monto={self.monto:.2f} "
            f"plazo={self.plazo_meses}m tasa={self.tasa} cuota={cuota:.2f}"
        )
        return cuota

    def resumen(self):
        return {
            "tipo": self.tipo,
            "monto": self.monto,
            "plazo_meses": self.plazo_meses,
            "tasa": self.tasa,
            "garantia": self.garantia or "Sin garantia",
            "seguro": self.seguro,
            "cuota": self.calcular_cuota(),
        }


# =================================================================
# BUILDER 1: PRESTAMO
# =================================================================
class PrestamoBuilder:
    """Constructor del prestamo. Cada metodo devuelve `self` para
    permitir encadenar llamadas: builder.monto(..).plazo(..)."""

    def __init__(self):
        self._p = Prestamo()

    # ----- Pasos individuales del proceso de construccion -----
    def cliente(self, cliente_id):
        self._p.cliente_id = cliente_id
        return self

    def tipo(self, tipo):
        self._p.tipo = tipo
        return self

    def monto(self, monto):
        self._p.monto = monto
        return self

    def plazo(self, meses):
        self._p.plazo_meses = meses
        return self

    def tasa_interes(self, tasa):
        self._p.tasa = tasa
        return self

    def con_garantia(self, garantia):
        self._p.garantia = garantia
        return self

    def con_seguro(self, seguro):
        self._p.seguro = seguro
        return self

    # ----- Paso final: devolver el producto ensamblado -----
    def construir(self):
        if not self._p.tipo:
            raise ValueError("Debe especificar el tipo de prestamo")
        return self._p


# =================================================================
# DIRECTOR 1: PRESTAMO (recetas prefabricadas del producto)
# =================================================================
class PrestamoDirector:
    """El Director prepara la secuencia de pasos del Builder
    para generar prestamos populares sin que el usuario deba
    recordar cada parametro."""

    def prestamo_personal(self, builder, cliente_id, monto, meses):
        return (
            builder.cliente(cliente_id)
            .tipo("PERSONAL")
            .monto(monto)
            .plazo(meses)
            .tasa_interes(0.12)
            .con_seguro(monto * 0.01)
        )

    def prestamo_hipotecario(self, builder, cliente_id, monto, meses):
        return (
            builder.cliente(cliente_id)
            .tipo("HIPOTECARIO")
            .monto(monto)
            .plazo(meses)
            .tasa_interes(0.08)
            .con_garantia("Hipoteca sobre inmueble valorizado")
        )

    def prestamo_vehicular(self, builder, cliente_id, monto, meses):
        return (
            builder.cliente(cliente_id)
            .tipo("VEHICULAR")
            .monto(monto)
            .plazo(meses)
            .tasa_interes(0.10)
            .con_garantia("Prenda del vehiculo")
            .con_seguro(monto * 0.03)
        )


director_prestamos = PrestamoDirector()


# =================================================================
# PRODUCTO 2: INVERSION
# =================================================================
class Inversion:
    """Producto complejo que ensambla el InversionBuilder."""

    def __init__(self):
        self.cliente_id = None
        self.nombre_inversor = None
        self.tipo = None
        self.monto = 0.0
        self.tasa = 0.0
        self.plazo_meses = 12
        self.perfil = None
        self.fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def registro_para_db(self):
        return (
            self.cliente_id, self.nombre_inversor, self.tipo, self.monto,
            self.tasa, self.plazo_meses, self.perfil, self.fecha,
        )

    def rentabilidad(self):
        return self.monto * (self.tasa * self.plazo_meses / 12.0)


# =================================================================
# BUILDER 2: INVERSION
# =================================================================
class InversionBuilder:
    """Constructor de la inversion (encadenable, igual que el de prestamo)."""

    def __init__(self):
        self._i = Inversion()

    def inversor(self, cliente_id, nombre):
        self._i.cliente_id = cliente_id
        self._i.nombre_inversor = nombre
        return self

    def tipo(self, tipo):
        self._i.tipo = tipo
        return self

    def monto(self, monto):
        self._i.monto = monto
        return self

    def tasa(self, tasa):
        self._i.tasa = tasa
        return self

    def plazo(self, meses):
        self._i.plazo_meses = meses
        return self

    def perfil(self, perfil):
        self._i.perfil = perfil
        return self

    def construir(self):
        if not self._i.tipo or self._i.monto <= 0:
            raise ValueError("La inversion debe tener tipo y monto mayor a cero")
        Database().ejecutar(
            "INSERT INTO inversiones(cliente_id, nombre_inversor, tipo, monto, tasa, plazo_meses, perfil, fecha) "
            "VALUES (?,?,?,?,?,?,?,?)",
            self._i.registro_para_db(),
        )
        logger.info(
            f"[BUILDER] Inversion creada: tipo={self._i.tipo} monto={self._i.monto:.2f} "
            f"perfil={self._i.perfil} rentabilidad={self._i.rentabilidad():.2f}"
        )
        return self._i

    def resumen(self):
        return {
            "tipo": self._i.tipo,
            "monto": self._i.monto,
            "tasa": self._i.tasa,
            "plazo_meses": self._i.plazo_meses,
            "perfil": self._i.perfil,
            "rentabilidad": self._i.rentabilidad(),
        }


# =================================================================
# DIRECTOR 2: INVERSION (perfiles que arman la estrategia)
# =================================================================
class InversionDirector:
    """Recetas de inversion por perfil de riesgo."""

    def conservador(self, builder, cliente_id, nombre, monto, meses):
        return (
            builder.inversor(cliente_id, nombre)
            .tipo("PLAZO_FIJO")
            .monto(monto)
            .tasa(0.05)
            .plazo(meses)
            .perfil("CONSERVADOR")
        )

    def moderado(self, builder, cliente_id, nombre, monto, meses):
        return (
            builder.inversor(cliente_id, nombre)
            .tipo("FONDO_MIXTO")
            .monto(monto)
            .tasa(0.08)
            .plazo(meses)
            .perfil("MODERADO")
        )

    def agresivo(self, builder, cliente_id, nombre, monto, meses):
        return (
            builder.inversor(cliente_id, nombre)
            .tipo("BONOS_ALTO_RENDIMIENTO")
            .monto(monto)
            .tasa(0.14)
            .plazo(meses)
            .perfil("AGRESIVO")
        )


director_inversiones = InversionDirector()