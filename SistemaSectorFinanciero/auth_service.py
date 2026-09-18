"""
==================================================================
 AUTENTICACION Y ROLES
==================================================================
 Define los usuarios del sistema y sus roles:

  - ADMIN   : administra el sistema, ve toda la informacion y
              gestiona los usuarios (activar/desactivar, roles).
  - CLIENTE : entra con su propio usuario y solo ve/opera SU
              cartera (sus cuentas, transacciones, prestamos,
              inversiones y alertas).

 Nota: tambien es Singleton (semana 1) como el resto de servicios,
 para que la política de acceso sea única en todos los canales.
==================================================================
"""

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from singleton import SingletonMeta
from database import Database
from logger import logger
from kyc_aml_service import servicio_cumplimiento


class AuthService(metaclass=SingletonMeta):
    """Gestion de cuentas de acceso, login y usuarios."""

    # ------------------------------------------------------------------
    # LOGIN
    # ------------------------------------------------------------------
    def autenticar(self, username, password):
        """Valida credenciales.

        Devuelve (usuario, codigo):
          - usuario: fila sqlite3.Row o None
          - código: 'OK', 'USUARIO_NO_EXISTE', 'INACTIVO' o 'CLAVE_INCORRECTA'
        """
        fila = Database().consulta_una(
            "SELECT * FROM usuarios WHERE username = ?", (username,)
        )
        if fila is None:
            return None, "USUARIO_NO_EXISTE"
        if not fila["activo"]:
            return None, "INACTIVO"
        if not check_password_hash(fila["password_hash"], password):
            return None, "CLAVE_INCORRECTA"
        return fila, "OK"

    def inicializar_session(self, fila_usuario):
        """Carga en la sesión los datos del usuario autenticado."""
        nombre = fila_usuario["username"]
        if fila_usuario["cliente_id"]:
            cliente = Database().consulta_una(
                "SELECT nombre FROM clientes WHERE id = ?",
                (fila_usuario["cliente_id"],),
            )
            if cliente:
                nombre = cliente["nombre"]
        return {
            "usuario_id": fila_usuario["id"],
            "username": fila_usuario["username"],
            "nombre": nombre,
            "rol": fila_usuario["rol"],
            "cliente_id": fila_usuario["cliente_id"],
        }

    # ------------------------------------------------------------------
    # REGISTRO PÚBLICO DE UN CLIENTE (se crea su ficha + su usuario)
    # ------------------------------------------------------------------
    def registrar_cliente_nuevo(self, datos_ficha, username, password):
        """Registra la ficha financiera (KYC/AML) y crea el usuario CLIENTE."""
        db = Database()
        if db.consulta_una("SELECT id FROM usuarios WHERE username = ?", (username,)):
            raise ValueError("El nombre de usuario ya esta en uso")

        # 1) Crear la ficha financiera aplicando KYC/AML.
        _kyc, _aml, cliente_id = servicio_cumplimiento.registrar_cliente(datos_ficha)

        # 2) Crear el usuario de acceso vinculado a esa ficha.
        db.ejecutar(
            "INSERT INTO usuarios(username, password_hash, rol, cliente_id, activo, creado) "
            "VALUES (?,?,?,?,1,?)",
            (
                username,
                generate_password_hash(password),
                "CLIENTE",
                cliente_id,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        logger.info(f"[AUTH] Usuario {username} ok, vinculado a la ficha {cliente_id}")
        return cliente_id

    # ------------------------------------------------------------------
    # GESTION (solo ADMIN)
    # ------------------------------------------------------------------
    def crear_usuario(self, username, password, rol, cliente_id=None):
        """El admin crea usuarios (ADMIN o CLIENTE) manualmente."""
        db = Database()
        if db.consulta_una("SELECT id FROM usuarios WHERE username = ?", (username,)):
            raise ValueError("El nombre de usuario ya esta en uso")
        db.ejecutar(
            "INSERT INTO usuarios(username, password_hash, rol, cliente_id, activo, creado) "
            "VALUES (?,?,?,?,1,?)",
            (
                username,
                generate_password_hash(password),
                rol,
                cliente_id,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        logger.info(f"[AUTH] Admin creo usuario {username} con rol {rol}")

    def listar_usuarios(self):
        return Database().consultar(
            "SELECT u.*, c.nombre AS nombre_cliente FROM usuarios u "
            "LEFT JOIN clientes c ON c.id = u.cliente_id ORDER BY u.id"
        )

    def cambiar_estado(self, usuario_id, activo):
        Database().ejecutar(
            "UPDATE usuarios SET activo = ? WHERE id = ?",
            (1 if activo else 0, int(usuario_id)),
        )

    def cambiar_rol(self, usuario_id, rol):
        if rol not in ("ADMIN", "CLIENTE"):
            raise ValueError("Rol invalido")
        Database().ejecutar(
            "UPDATE usuarios SET rol = ? WHERE id = ?", (rol, int(usuario_id))
        )


auth_service = AuthService()