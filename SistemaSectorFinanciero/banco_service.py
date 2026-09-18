"""
==================================================================
 SERVICIO CENTRAL DEL BANCO
==================================================================
 Orquesta las operaciones del core bancario. En este modulo se
 conectan los patrones trabajados por semana:

  - SEMANA 1 (Singleton) : ConfigManager, Database, LoggerService,
                           FraudDetector  (instancias unicas).
  - SEMANA 2 (Factory Method): creacion de cuentas.
  - SEMANA 3 (Abstract Factory): familia de objetos por CANAL
                                 (operacion, notificacion, auditoria).
  - SEMANA 4 (Builder)   : prestamos e inversiones (en app.py).
==================================================================
"""

from datetime import datetime

from config_manager import config
from database import Database
from logger import logger
from fraud_detector import detector_fraude
from factory_method import obtener_fabrica
from abstract_factory import obtener_fabrica_canal


class BancoService:
    """Capa de aplicacion que usa los patrones de cada semana."""

    # ------------------------------------------------------------------
    # SEMANA 2 - Factory Method  (crear cuenta)
    # ------------------------------------------------------------------
    def crear_cuenta(self, cliente_id, tipo, saldo_inicial, canal):
        """
        Usa el FACTORY METHOD (semana 2): obtiene la fabrica concreta
        según el tipo y deja que el método plantilla registre la cuenta.
        """
        fabrica = obtener_fabrica(tipo)          # elige la fabrica concreta
        numero, cuenta = fabrica.registrar_cuenta(cliente_id, None, saldo_inicial, canal)
        logger.evento("CREAR_CUENTA", f"tipo={tipo} numero={numero} canal={canal}")
        return numero, cuenta

    # ------------------------------------------------------------------
    # SEMANA 1 + SEMANA 3 - procesar una operacion (transaccion)
    # ------------------------------------------------------------------
    def procesar_transaccion(self, cuenta, tipo, monto, cuenta_destino, canal, cliente):
        """Proceso completo de una operacion multicanal en tiempo real.

        1) ABSTRACT FACTORY (semana 3): arma la familia de artefactos
           del canal elegido (operacion + notificacion + auditoria).
        2) SINGLETON FraudDetector (semana 1): supervisa en tiempo real.
        3) Persistencia usando componentes de la familia del canal.
        """
        # ---- SEMANA 3: fabrica del canal elegido ----
        fabrica_canal = obtener_fabrica_canal(canal)
        operacion = fabrica_canal.crear_operacion(tipo, monto)
        notificacion = fabrica_canal.crear_notificacion()
        auditoria = fabrica_canal.crear_auditoria()
        # ---------------------------------------------

        auditoria.registrar(operacion.describir())

        # ---- SEMANA 1: motor de fraude (singleton) ----
        decision, motivo, _nivel = detector_fraude.analizar(
            cuenta, tipo, monto, cuenta_destino, cliente
        )
        # -----------------------------------------------

        if decision == "BLOQUEAR":
            estado = "BLOQUEADA"
            self._registrar_operacion(cuenta, tipo, monto, cuenta_destino, canal, estado)
            mensaje = notificacion.enviar(f"Operacion BLOQUEADA: {motivo}")
            return {"ok": False, "mensaje": mensaje, "motivo": motivo}

        estado = "APROBADA"
        # Ajuste de saldos según el tipo de operacion.
        if tipo == "RETIRO":
            self._ajustar_saldo(cuenta, -monto)
        elif tipo == "DEPOSITO":
            self._ajustar_saldo(cuenta, monto)
        elif tipo == "TRANSFERENCIA":
            self._ajustar_saldo(cuenta, -monto)
            self._ajustar_saldo_destino(cuenta_destino, monto)

        self._registrar_operacion(cuenta, tipo, monto, cuenta_destino, canal, estado)
        logger.evento("TRANSACCION", f"{tipo} {monto:.2f} canal={canal} estado={estado}")
        mensaje = notificacion.enviar(
            f"Transaccion {tipo} de {monto:.2f} registrada con exito."
        )
        return {"ok": True, "mensaje": mensaje, "motivo": None}

    # ------------------------------------------------------------------
    def _registrar_operacion(self, cuenta, tipo, monto, destino, canal, estado):
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Database().ejecutar(
            "INSERT INTO transacciones(cuenta_id, numero_cuenta, tipo, monto, cuenta_destino, canal, estado, fecha) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (cuenta["id"], cuenta["numero"], tipo, monto, destino, canal, estado, fecha),
        )

    def _ajustar_saldo(self, cuenta, delta):
        if not isinstance(cuenta, dict):
            cuenta = dict(cuenta)  # sqlite3.Row no permite asignacion
        nuevo = cuenta["saldo"] + delta
        Database().ejecutar(
            "UPDATE cuentas SET saldo = ? WHERE id = ?", (nuevo, cuenta["id"])
        )
        cuenta["saldo"] = nuevo

    def _ajustar_saldo_destino(self, numero_destino, monto):
        destino = Database().consulta_una(
            "SELECT * FROM cuentas WHERE numero = ?", (numero_destino,)
        )
        if destino:
            self._ajustar_saldo(destino, monto)

    # ------------------------------------------------------------------
    # Consultas para la interfaz grafica
    # ------------------------------------------------------------------
    # `cliente_id` = None significa ADMIN (ve todo). Con un valor,
    # el usuario CLIENTE solo ve su propia informacion (aislamiento).
    # ------------------------------------------------------------------
    def resumen_dashboard(self, cliente_id=None):
        db = Database()
        params = [cliente_id] if cliente_id else []
        cond_cliente = " WHERE c.cliente_id = ?" if cliente_id else ""

        total_clientes = (1 if cliente_id else
                          db.consulta_una("SELECT COUNT(*) n FROM clientes")["n"])
        total_cuentas = db.consulta_una(
            "SELECT COUNT(*) n FROM cuentas c" + cond_cliente, params
        )["n"]
        saldo_total = db.consulta_una(
            "SELECT COALESCE(SUM(c.saldo),0) s FROM cuentas c" + cond_cliente, params
        )["s"]
        transacciones = db.consulta_una(
            "SELECT COUNT(*) n FROM transacciones t "
            "LEFT JOIN cuentas c ON c.id = t.cuenta_id" + cond_cliente, params
        )["n"]
        alertas = db.consultar(
            "SELECT a.* FROM alertas_fraude a "
            "LEFT JOIN cuentas c ON c.id = a.cuenta_id" + cond_cliente +
            " ORDER BY a.fecha DESC",
            params,
        )
        alertas_pendientes = sum(1 for a in alertas if a["estado"] == "NO_REVISADA")
        prestamos = db.consultar(
            "SELECT * FROM prestamos p" + cond_cliente.replace("c.", "p.") +
            " ORDER BY p.fecha DESC",
            params,
        )
        inversiones = db.consultar(
            "SELECT * FROM inversiones i" + cond_cliente.replace("c.", "i.") +
            " ORDER BY i.fecha DESC",
            params,
        )
        return {
            "total_clientes": total_clientes,
            "total_cuentas": total_cuentas,
            "saldo_total": saldo_total,
            "transacciones": transacciones,
            "alertas": alertas[:5],
            "alertas_pendientes": alertas_pendientes,
            "prestamos": prestamos,
            "inversiones": inversiones,
        }

    def listar_clientes(self, cliente_id=None):
        if cliente_id:
            return Database().consultar(
                "SELECT * FROM clientes WHERE id = ? ORDER BY id", (cliente_id,)
            )
        return Database().consultar("SELECT * FROM clientes ORDER BY id")

    def listar_cuentas(self, cliente_id=None):
        sql = ("SELECT c.*, cl.nombre AS nombre_cliente FROM cuentas c "
               "LEFT JOIN clientes cl ON cl.id = c.cliente_id")
        parametros = []
        if cliente_id:
            sql += " WHERE c.cliente_id = ?"
            parametros.append(cliente_id)
        sql += " ORDER BY c.id"
        return Database().consultar(sql, parametros)

    def listar_transacciones(self, cliente_id=None):
        sql = ("SELECT t.*, cl.nombre AS nombre_cliente FROM transacciones t "
               "LEFT JOIN cuentas c ON c.id = t.cuenta_id "
               "LEFT JOIN clientes cl ON cl.id = c.cliente_id")
        parametros = []
        if cliente_id:
            sql += " WHERE c.cliente_id = ?"
            parametros.append(cliente_id)
        sql += " ORDER BY t.id DESC"
        return Database().consultar(sql, parametros)

    def listar_prestamos(self, cliente_id=None):
        sql = ("SELECT p.*, cl.nombre AS nombre_cliente FROM prestamos p "
               "LEFT JOIN clientes cl ON cl.id = p.cliente_id")
        parametros = []
        if cliente_id:
            sql += " WHERE p.cliente_id = ?"
            parametros.append(cliente_id)
        sql += " ORDER BY p.id DESC"
        return Database().consultar(sql, parametros)

    def listar_inversiones(self, cliente_id=None):
        sql = ("SELECT i.*, cl.nombre AS nombre_cliente FROM inversiones i "
               "LEFT JOIN clientes cl ON cl.id = i.cliente_id")
        parametros = []
        if cliente_id:
            sql += " WHERE i.cliente_id = ?"
            parametros.append(cliente_id)
        sql += " ORDER BY i.id DESC"
        return Database().consultar(sql, parametros)


banco_service = BancoService()