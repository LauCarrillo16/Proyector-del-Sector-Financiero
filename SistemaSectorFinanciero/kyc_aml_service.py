"""
==================================================================
 CUMplimiento REGULATORIO - KYC / AML (servicio de negocio)
==================================================================
 - KYC (Know Your Customer): evaluacion del cliente a partir de sus
   datos; asigna un nivel de verificacion (NIVEL_1..NIVEL_3).
 - AML (Anti Money Laundering): calcula un puntaje de riesgo y
   clasifica al cliente como BAJO / MEDIO / ALTO. Los clientes de
   riesgo ALTO activan el escrutinio extra del FraudDetector
   (semana 1) y generan las alertas que vemos en la interfaz.

 ==== METODO USADO (SEMANA 1) ====
 - `ServicioCumplimiento` tambien es Singleton para que la evaluacion
   sea igual en todos los canales.
==================================================================
"""

from datetime import datetime

from singleton import SingletonMeta
from logger import logger


class ServicioCumplimiento(metaclass=SingletonMeta):
    """Singleton que orquesta las políticas regulatorias KYC/AML."""

    # ------------------------------------------------------------------
    def evaluar_kyc(self, fila_cliente):
        """Asigna el nivel de verificacion KYC al cliente.

        Reglas de ejemplo:
          - Identificacion tipo DNI  -> NIVEL_1 (identidad basica).
          - Identificacion tipo PAS  -> NIVEL_2 (extranjeros).
          - Con email + teléfono     -> NIVEL_3 (verificacion completa).
        """
        fila_cliente = dict(fila_cliente)
        identificacion = (fila_cliente.get("identificacion") or "").upper()
        email = fila_cliente.get("email") or ""
        telefono = fila_cliente.get("telefono") or ""

        if identificacion.startswith("DNI") and email and telefono:
            nivel = "NIVEL_3"
        elif identificacion.startswith("PAS"):
            nivel = "NIVEL_2"
        else:
            nivel = "NIVEL_1"
        return nivel

    # ------------------------------------------------------------------
    def calcular_riesgo_aml(self, fila_cliente, operaciones_recientes=0.0):
        """Puntaje de riesgo AML (0..1) y clasificacion BAJO/MEDIO/ALTO.

        Se combina el tamano de las operaciones recientes con una
        penalidad según el nivel KYC.
        """
        fila_cliente = dict(fila_cliente)
        kyc = fila_cliente.get("kyc_nivel") or "NIVEL_1"
        # KYC bajo => menos confianza => mayor peso de riesgo.
        penalidad_kyc = {"NIVEL_3": 0.15, "NIVEL_2": 0.35, "NIVEL_1": 0.5}.get(kyc, 0.5)

        monto_gran_operacion = 20000.0  # visible en config_manager
        exposicion = min(operaciones_recientes / monto_gran_operacion, 1.0)

        puntaje = 0.3 * penalidad_kyc + 0.7 * exposicion
        if puntaje >= 0.6:
            nivel = "ALTO"
        elif puntaje >= 0.35:
            nivel = "MEDIO"
        else:
            nivel = "BAJO"
        return nivel, puntaje

    # ------------------------------------------------------------------
    def registrar_cliente(self, datos):
        """Crea el cliente aplicando KYC al instante (de alto cumplimiento)."""
        from database import Database

        nivel_kyc = self.evaluar_kyc(datos)
        nivel_aml, _ = self.calcular_riesgo_aml({**datos, "kyc_nivel": nivel_kyc})
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cursor = Database().ejecutar(
                "INSERT INTO clientes(nombre, identificacion, email, telefono, ocupacion,"
                " kyc_nivel, aml_riesgo, creado) VALUES (?,?,?,?,?,?,?,?)",
                (
                    datos.get("nombre"), datos.get("identificacion"),
                    datos.get("email"), datos.get("telefono"),
                    datos.get("ocupacion"), nivel_kyc, nivel_aml, fecha,
                ),
            )
        except Exception as exc:  # identificacion duplicada, etc.
            raise ValueError(f"No se pudo registrar el cliente: {exc}")
        nuevo_id = cursor.lastrowid
        logger.info(f"[KYC/AML] Cliente registrado {datos.get('nombre')} kyc={nivel_kyc} aml={nivel_aml}")
        return nivel_kyc, nivel_aml, nuevo_id

    # ------------------------------------------------------------------
    def recalcular_clientes(self):
        """Recalcula el riesgo AML de todos los clientes (boton de la interfaz)."""
        from database import Database

        db = Database()
        clientes = db.consultar("SELECT * FROM clientes")
        for c in clientes:
            movs = db.consulta_una(
                "SELECT COALESCE(SUM(t.monto),0) AS total FROM transacciones t "
                "JOIN cuentas ON cuentas.id = t.cuenta_id "
                "JOIN clientes ON clientes.id = cuentas.cliente_id "
                "WHERE clientes.id = ?",
                (c["id"],),
            )
            nivel, _ = self.calcular_riesgo_aml(c, movs["total"])
            db.ejecutar("UPDATE clientes SET aml_riesgo = ? WHERE id = ?", (nivel, c["id"]))
        logger.info("[KYC/AML] Riesgo AML recalculado para todos los clientes")


servicio_cumplimiento = ServicioCumplimiento()