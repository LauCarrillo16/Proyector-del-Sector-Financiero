"""
==================================================================
 SEMANA 1 - PATRON SINGLETON (aplicacion: BASE DE DATOS)
==================================================================
 Database es un Singleton que abre UNA SOLA conexion SQLite y la
 comparte con toda la aplicacion. Esto evita abrir una conexion
 por cada peticion, consume menos recursos y mantiene la
 consistencia de datos entre canales.

 ==== LUGAR DONDE SE TRABAJA EL PATRON (SEMANA 1) ====
 - `metaclass=SingletonMeta` -> una unica instancia/conexion.
 - Se llama en toda la app como `Database()` y siempre es la misma.
==================================================================
"""

import sqlite3
import threading

from singleton import SingletonMeta
from config_manager import config


class Database(metaclass=SingletonMeta):
    """Conexion unica a la base de datos del banco."""

    def __init__(self):
        # SOLO se ejecuta una vez (Singleton).
        self._archivo = config.obtener("db_file") or "banco.db"
        # check_same_thread=False permite que Flask use la misma
        # conexion desde varios hilos (multicanal en tiempo real).
        self._conexion = sqlite3.connect(self._archivo, check_same_thread=False)
        self._conexion.row_factory = sqlite3.Row
        self._mutex = threading.Lock()
        self._crear_tablas()
        self._sembrar_iniciales()

    # ------------------------------------------------------------------
    # Acceso con candado para operaciones seguras en concurrencia.
    # ------------------------------------------------------------------
    def ejecutar(self, sql, parametros=()):
        """Ejecuta INSERT/UPDATE/DELETE devolviendo la fila afectada."""
        with self._mutex:
            cursor = self._conexion.cursor()
            cursor.execute(sql, parametros)
            self._conexion.commit()
            return cursor

    def consultar(self, sql, parametros=()):
        """Ejecuta SELECT y devuelve lista de filas (sqlite3.Row)."""
        with self._mutex:
            cursor = self._conexion.cursor()
            cursor.execute(sql, parametros)
            return cursor.fetchall()

    def consulta_una(self, sql, parametros=()):
        """Ejecuta SELECT devolviendo una sola fila (o None)."""
        with self._mutex:
            cursor = self._conexion.cursor()
            cursor.execute(sql, parametros)
            return cursor.fetchone()

    # ------------------------------------------------------------------
    def _crear_tablas(self):
        self.ejecutar("""
            CREATE TABLE IF NOT EXISTS clientes (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre        TEXT NOT NULL,
                identificacion TEXT NOT NULL UNIQUE,
                email         TEXT,
                telefono      TEXT,
                ocupacion     TEXT,
                kyc_nivel     TEXT DEFAULT 'PENDIENTE',
                aml_riesgo    TEXT DEFAULT 'BAJO',
                creado        TEXT
            )
        """)
        self.ejecutar("""
            CREATE TABLE IF NOT EXISTS cuentas (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                numero     TEXT UNIQUE,
                tipo       TEXT,
                saldo      REAL DEFAULT 0,
                canal      TEXT,
                fecha      TEXT
            )
        """)
        self.ejecutar("""
            CREATE TABLE IF NOT EXISTS transacciones (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                cuenta_id     INTEGER,
                numero_cuenta TEXT,
                tipo          TEXT,
                monto         REAL,
                cuenta_destino TEXT,
                canal         TEXT,
                estado        TEXT DEFAULT 'APROBADA',
                fecha         TEXT
            )
        """)
        self.ejecutar("""
            CREATE TABLE IF NOT EXISTS prestamos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id  INTEGER,
                tipo        TEXT,
                monto       REAL,
                plazo_meses INTEGER,
                tasa        REAL,
                garantia    TEXT,
                seguro      REAL,
                cuota       REAL,
                estado      TEXT DEFAULT 'ACTIVO',
                fecha       TEXT
            )
        """)
        self.ejecutar("""
            CREATE TABLE IF NOT EXISTS inversiones (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id      INTEGER,
                nombre_inversor TEXT,
                tipo            TEXT,
                monto           REAL,
                tasa            REAL,
                plazo_meses     INTEGER,
                perfil          TEXT,
                fecha           TEXT
            )
        """)
        self.ejecutar("""
            CREATE TABLE IF NOT EXISTS alertas_fraude (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                transaccion_id  INTEGER,
                cuenta_id       INTEGER,
                motivo          TEXT,
                nivel           TEXT,
                fecha           TEXT,
                estado          TEXT DEFAULT 'NO_REVISADA'
            )
        """)

        # Tabla de usuarios del sistema (autenticacion y roles).
        # rol: 'ADMIN' (administra el sistema y usuarios) o
        #      'CLIENTE' (entra y opera SU cartera financiera).
        self.ejecutar("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                rol           TEXT NOT NULL DEFAULT 'CLIENTE',
                cliente_id    INTEGER,          -- vinculo al cliente financiero
                activo        INTEGER DEFAULT 1,
                creado        TEXT
            )
        """)

    # ------------------------------------------------------------------
    def _sembrar_iniciales(self):
        """Datos de ejemplo para que la app funcione desde el primer dia."""
        if self.consulta_una("SELECT COUNT(*) AS n FROM clientes")["n"] > 0:
            return
        from datetime import datetime

        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        clientes = [
            ("Maria Perez", "DNI-44556677", "maria@correo.com", "999111222", "Contadora", "NIVEL_1", "BAJO"),
            ("Luis Gomez", "DNI-22334455", "luis@correo.com", "999333444", "Comerciante", "NIVEL_3", "ALTO"),
            ("Ana Torres", "PAS-11223344", "ana@correo.com", "999555666", "Ingeniera", "NIVEL_2", "MEDIO"),
        ]
        for c in clientes:
            self.ejecutar(
                "INSERT INTO clientes(nombre, identificacion, email, telefono, ocupacion, kyc_nivel, aml_riesgo, creado) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (*c, ahora),
            )

        self.ejecutar(
            "INSERT INTO cuentas(cliente_id, numero, tipo, saldo, canal, fecha) VALUES (1,'AHO-1001','AHORRO',25000,'WEB',?)",
            (ahora,),
        )
        self.ejecutar(
            "INSERT INTO cuentas(cliente_id, numero, tipo, saldo, canal, fecha) VALUES (2,'CTE-2002','CORRIENTE',45000,'SUCURSAL',?)",
            (ahora,),
        )
        self.ejecutar(
            "INSERT INTO cuentas(cliente_id, numero, tipo, saldo, canal, fecha) VALUES (3,'INV-3003','INVERSION',100000,'MOVIL',?)",
            (ahora,),
        )

        self.ejecutar(
            "INSERT INTO transacciones(cuenta_id, numero_cuenta, tipo, monto, cuenta_destino, canal, estado, fecha) "
            "VALUES (1,'AHO-1001','DEPOSITO',1200,'-','WEB','APROBADA',?)",
            (ahora,),
        )
        self.ejecutar(
            "INSERT INTO transacciones(cuenta_id, numero_cuenta, tipo, monto, cuenta_destino, canal, estado, fecha) "
            "VALUES (2,'CTE-2002','TRANSFERENCIA',25000,'AHO-1001','MOVIL','BLOQUEADA',?)",
            (ahora,),
        )

        # ---- Usuarios de acceso (autenticacion / roles) ----
        # Contraseñas con hash: nunca se guardan en texto plano.
        from werkzeug.security import generate_password_hash

        ids_clientes = {
            nombre: self.consulta_una(
                "SELECT id FROM clientes WHERE identificacion = ?", (identificacion,)
            )["id"]
            for nombre, identificacion in [
                ("Maria Perez", "DNI-44556677"),
                ("Luis Gomez", "DNI-22334455"),
                ("Ana Torres", "PAS-11223344"),
            ]
        }

        # Usuario administrador del sistema.
        self.ejecutar(
            "INSERT INTO usuarios(username, password_hash, rol, cliente_id, activo, creado) "
            "VALUES (?,?,?,NULL,1,?)",
            ("admin", generate_password_hash("admin123"), "ADMIN", ahora),
        )
        # Usuarios clientes vinculados a su ficha financiera.
        self.ejecutar(
            "INSERT INTO usuarios(username, password_hash, rol, cliente_id, activo, creado) "
            "VALUES (?,?,?,?,1,?)",
            ("maria", generate_password_hash("1234"), "CLIENTE", ids_clientes["Maria Perez"], ahora),
        )
        self.ejecutar(
            "INSERT INTO usuarios(username, password_hash, rol, cliente_id, activo, creado) "
            "VALUES (?,?,?,?,1,?)",
            ("luis", generate_password_hash("1234"), "CLIENTE", ids_clientes["Luis Gomez"], ahora),
        )