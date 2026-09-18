"""
==================================================================
 SEMANA 1 - PATRON SINGLETON (aplicacion: DETECCION DE FRAUDE)
==================================================================
 FraudDetector es el motor UNICO de deteccion de fraude en tiempo
 real. Como es Singleton, todas los canales (WEB, MOVIL, CAJERO,
 SUCURSAL) reportan contra el mismo motor y las reglas son
 compartidas y consistentes.

 Reglas actuales (reglas de negocio parametricas via ConfigManager):
   1. Montos que superan los limites por tipo de operacion.
   2. Trasferencia hacia una cuenta inexistente.
   3. Negocio sospechoso (AML = ALTO) que opera por encima del umbral.

 ==== LUGAR DONDE SE TRABAJA EL PATRON (SEMANA 1) ====
 - `metaclass=SingletonMeta` -> un solo motor de fraude.
 - El modulo services/banco.py lo invoca en cada transaccion.
==================================================================
"""

from datetime import datetime

from singleton import SingletonMeta
from config_manager import config
from logger import logger


class FraudDetector(metaclass=SingletonMeta):
    """Unico motor de deteccion de fraude del banco."""

    def __init__(self):
        # Solo se inicializa una vez (Singleton).
        self._limites = {
            "DEPOSITO": config.obtener("limite_deposito") or 8000,
            "RETIRO": config.obtener("limite_retiro") or 5000,
            "TRANSFERENCIA": config.obtener("limite_transferencia") or 10000,
        }
        self._monto_gran_operacion = config.obtener("monto_gran_operacion") or 20000

    # ------------------------------------------------------------------
    def analizar(self, cuenta, tipo, monto, cuenta_destino, cliente=None):
        """Evalua una operacion en tiempo real.

        Devuelve una tupla: (decision, motivo, nivel)
        donde decision puede ser 'APROBAR' o 'BLOQUEAR'.
        """
        limite = self._limites.get(tipo, 0)
        motivo = None
        nivel = "BAJO"

        # Regla 1: monto sobre el limite para su tipo de operacion.
        if monto > limite:
            motivo = f"Monto {monto:.2f} excede el limite de {tipo} ({limite:.2f})"
            nivel = "ALTO"

        # Regla 2: transferencia a una cuenta destino inexistente.
        if tipo == "TRANSFERENCIA" and cuenta_destino and not self._existe_cuenta(cuenta_destino):
            motivo = f"Cuenta destino inexistente o invalida: {cuenta_destino}"
            nivel = "MEDIO"

        # Regla 3: cliente con riesgo AML alto realizando operaciones
        #          grandes (indicador de lavado de activos).
        if cliente and cliente["aml_riesgo"] == "ALTO":
            if monto >= self._monto_gran_operacion * config.obtener("tasa_riesgo"):
                motivo = f"Cliente riesgo AML alto con operacion grande: {monto:.2f}"
                nivel = "CRITICO"

        if motivo:
            logger.advertir(f"[FRAUDE] {nivel} - {motivo}")
            self._registrar_alerta(cuenta, motivo, nivel)
            return "BLOQUEAR", motivo, nivel

        logger.info(f"[FRAUDE] Operacion supervisada sin anomalias: {tipo} {monto:.2f}")
        return "APROBAR", None, nivel

    # ------------------------------------------------------------------
    def _existe_cuenta(self, numero):
        from database import Database

        fila = Database().consulta_una(
            "SELECT id FROM cuentas WHERE numero = ?", (numero,)
        )
        return fila is not None

    def _registrar_alerta(self, cuenta, motivo, nivel):
        """Persiste la alerta para el panel de la interfaz grafica."""
        from database import Database

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Database().ejecutar(
            "INSERT INTO alertas_fraude(cuenta_id, motivo, nivel, fecha) VALUES (?,?,?,?)",
            (cuenta["id"] if cuenta else None, motivo, nivel, fecha),
        )

    # ------------------------------------------------------------------
    def listar_alertas(self, cliente_id=None):
        """Alertas del banco; si cliente_id llega, solo las de ese cliente."""
        from database import Database

        sql = ("SELECT a.* FROM alertas_fraude a "
               "LEFT JOIN cuentas c ON c.id = a.cuenta_id")
        parametros = []
        if cliente_id:
            sql += " WHERE c.cliente_id = ?"
            parametros.append(cliente_id)
        sql += " ORDER BY a.fecha DESC"
        return Database().consultar(sql, parametros)


detector_fraude = FraudDetector()