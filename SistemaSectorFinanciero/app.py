"""
==================================================================
 APP PRINCIPAL - Sistema Bancario Core (Flask)
==================================================================
 Interfaz grafica web del proyecto progresivo de patrones de diseño.

  - Semana 1 (Singleton)  : config_manager, database, logger,
                            fraud_detector, auth_service  (instancias unicas).
  - Semana 2 (Factory Method): creacion de cuentas (ruta /cuentas).
  - Semana 3 (Abstract Factory): familia multicanal por canal
                            (ruta /transacciones -> servicio central).
  - Semana 4 (Builder)    : prestamos (ruta /prestamos) e
                            inversiones (ruta /inversiones).

 ROLES:
  - ADMIN  : administra el sistema y los usuarios / ve todo.
  - CLIENTE: entra con su usuario y solo ve y opera SU cartera.

 Rutas publicas: /login y /registro.
 Ejecutar:  python app.py   (abre http://127.0.0.1:5000)
==================================================================
"""

from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for, flash, session,
)

from config_manager import config
from database import Database
from logger import logger
from fraud_detector import detector_fraude
from banco_service import banco_service
from kyc_aml_service import servicio_cumplimiento
from auth_service import auth_service
from builders import (
    PrestamoBuilder,
    PrestamoDirector,
    InversionBuilder,
    InversionDirector,
)

app = Flask(__name__)
app.secret_key = "banco-patrones-seguridad"
app.config["TEMPLATES_AUTO_RELOAD"] = True


# =================================================================
# CONTROLES DE ACCESO (decoradores)
# =================================================================
def login_requerido(rol=None):
    """Decorador: exige sesión iniciada y, si se indica, un rol concreto."""
    def decorador(funcion):
        @wraps(funcion)
        def envoltura(*args, **kwargs):
            if "usuario_id" not in session:
                flash("Inicia sesión para entrar al sistema financiero.", "error")
                return redirect(url_for("login", siguiente=request.path))
            if rol and session.get("rol") != rol:
                flash("No tienes permisos para acceder a esta seccion.", "error")
                return redirect(url_for("inicio"))
            return funcion(*args, **kwargs)
        return envoltura
    return decorador


def ambito_cliente():
    """Devuelve el cliente_id del usuario CLIENTE o None si es ADMIN."""
    return session.get("cliente_id")


@app.context_processor
def inyectar_configuracion():
    """ConfigManager (Singleton, semana 1) disponible en todos los templates."""
    return {"config": config}


# =================================================================
# AUTENTICACION (rutas publicas)
# =================================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        usuario, codigo = auth_service.autenticar(username, password)
        if codigo == "OK":
            session.clear()
            session.update(auth_service.inicializar_session(usuario))
            logger.evento("LOGIN", f"{username} rol={session['rol']}")
            flash(f"Bienvenido, {session['nombre']}.", "ok")
            siguiente = request.form.get("siguiente") or url_for("inicio")
            return redirect(siguiente if siguiente.startswith("/") else url_for("inicio"))
        mensajes = {
            "USUARIO_NO_EXISTE": "Usuario no registrado.",
            "INACTIVO": "Cuenta desactivada. Contacta al administrador.",
            "CLAVE_INCORRECTA": "Contraseña incorrecta.",
        }
        flash(mensajes.get(codigo, "No se pudo iniciar sesión."), "error")
        return redirect(url_for("login"))
    return render_template("login.html", siguiente=request.args.get("siguiente", ""))


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        datos = {
            "nombre": request.form.get("nombre", "").strip(),
            "identificacion": request.form.get("identificacion", "").strip(),
            "email": request.form.get("email", "").strip(),
            "telefono": request.form.get("telefono", "").strip(),
            "ocupacion": request.form.get("ocupacion", "").strip(),
        }
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        try:
            auth_service.registrar_cliente_nuevo(datos, username, password)
            flash(
                "Ficha registrada con KYC/AML y usuario creado. Ya puedes iniciar sesión.",
                "ok",
            )
            return redirect(url_for("login"))
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("registro"))
    return render_template("registro.html")


@app.route("/logout")
def logout():
    logger.evento("LOGOUT", session.get("username", "anónimo"))
    session.clear()
    flash("Sesion cerrada.", "ok")
    return redirect(url_for("login"))


# =================================================================
# DASHBOARD
# =================================================================
@app.route("/")
@login_requerido()
def inicio():
    return render_template(
        "index.html",
        datos=banco_service.resumen_dashboard(cliente_id=ambito_cliente()),
    )


# =================================================================
# CLIENTES (ficha financiera; el CLIENTE solo ve la suya)
# =================================================================
@app.route("/clientes")
@login_requerido()
def clientes():
    return render_template(
        "clientes.html",
        clientes=banco_service.listar_clientes(cliente_id=ambito_cliente()),
    )


# =================================================================
# CUMPLIMIENTO (panel regulatorio KYC/AML, solo administradores)
# =================================================================
@app.route("/cumplimiento", methods=["GET", "POST"])
@login_requerido(rol="ADMIN")
def cumplimiento():
    """Panel de cumplimiento regulatorio (KYC / AML)."""
    if request.method == "POST":
        servicio_cumplimiento.recalcular_clientes()
        flash("Riesgo AML recalculado para todos los clientes", "ok")
        return redirect(url_for("cumplimiento"))
    return render_template(
        "cumplimiento.html", clientes=banco_service.listar_clientes()
    )


# =================================================================
# PANEL ADMINISTRADOR (gestion de usuarios del sistema)
# =================================================================
@app.route("/admin", methods=["GET", "POST"])
@login_requerido(rol="ADMIN")
def panel_admin():
    """El admin crea usuarios y activa/desactiva o cambia roles."""
    if request.method == "POST":
        accion = request.form.get("accion")
        try:
            if accion == "crear":
                username = request.form.get("username", "").strip()
                password = request.form.get("password", "")
                rol = request.form.get("rol", "CLIENTE")
                cliente_id = request.form.get("cliente_id") or None
                auth_service.crear_usuario(username, password, rol, cliente_id)
                flash(f"Usuario {username} creado con rol {rol}.", "ok")
            elif accion == "estado":
                auth_service.cambiar_estado(
                    request.form.get("usuario_id"),
                    request.form.get("activo") == "1",
                )
                flash("Estado del usuario actualizado.", "ok")
            elif accion == "rol":
                auth_service.cambiar_rol(
                    request.form.get("usuario_id"),
                    request.form.get("rol"),
                )
                flash("Rol del usuario actualizado.", "ok")
        except ValueError as exc:
            flash(str(exc), "error")
        return redirect(url_for("panel_admin"))

    return render_template(
        "admin_usuarios.html",
        usuarios=auth_service.listar_usuarios(),
        clientes=banco_service.listar_clientes(),
    )


# =================================================================
# CUENTAS  ->  SEMANA 2: FACTORY METHOD
# =================================================================
@app.route("/cuentas", methods=["GET", "POST"])
@login_requerido()
def cuentas():
    if request.method == "POST":
        # El CLIENTE siempre opera sobre su ficha; el ADMIN elige el cliente.
        cliente_id = int(session.get("cliente_id") or request.form.get("cliente_id"))
        tipo = request.form.get("tipo")
        saldo = float(request.form.get("saldo") or 0)
        canal = request.form.get("canal", "WEB")

        # [SEMANA 2 - FACTORY METHOD] La creacion concreta queda delegada
        # en banco_service.crear_cuenta() -> obtener_fabrica(tipo).
        numero, cuenta = banco_service.crear_cuenta(cliente_id, tipo, saldo, canal)
        flash(
            f"Cuenta {numero} creada ({cuenta.tipo}) por el canal {canal}.",
            "ok",
        )
        return redirect(url_for("cuentas"))

    return render_template(
        "cuentas.html",
        cuentas=banco_service.listar_cuentas(cliente_id=ambito_cliente()),
        clientes=banco_service.listar_clientes(),
        tipos=["AHORRO", "CORRIENTE", "INVERSION"],
        canales=config.canales(),
    )


# =================================================================
# TRANSACCIONES -> SEMANA 1 (fraude) + SEMANA 3 (abstract factory)
# =================================================================
@app.route("/transacciones", methods=["GET", "POST"])
@login_requerido()
def transacciones():
    if request.method == "POST":
        numero_cuenta = request.form.get("numero_cuenta")
        tipo = request.form.get("tipo")
        monto = float(request.form.get("monto") or 0)
        cuenta_destino = request.form.get("cuenta_destino", "").strip() or None
        canal = request.form.get("canal", "WEB")

        cuenta = Database().consulta_una(
            "SELECT * FROM cuentas WHERE numero = ?", (numero_cuenta,)
        )
        if cuenta is None:
            flash(f"Cuenta origen {numero_cuenta} no encontrada", "error")
            return redirect(url_for("transacciones"))

        # Aislamiento: un CLIENTE solo puede operar sus propias cuentas.
        if ambito_cliente() and cuenta["cliente_id"] != ambito_cliente():
            flash("Solo puedes operar con tus propias cuentas.", "error")
            return redirect(url_for("transacciones"))

        cliente = Database().consulta_una(
            "SELECT * FROM clientes WHERE id = ?", (cuenta["cliente_id"],)
        )
        if tipo == "TRANSFERENCIA" and not cuenta_destino:
            flash("Las transferencias necesitan una cuenta destino", "error")
            return redirect(url_for("transacciones"))

        # [SEMANA 1 + SEMANA 3] El servicio central:
        #   - usa el Singleton FraudDetector para supervisar en tiempo real.
        #   - usa el Abstract Factory del canal para armar la familia de objetos.
        resultado = banco_service.procesar_transaccion(
            cuenta, tipo, monto, cuenta_destino or "-", canal, cliente
        )
        flash(
            f"{'OK' if resultado['ok'] else 'BLOQUEADA'}: {resultado['mensaje']} ",
            "ok" if resultado["ok"] else "error",
        )
        return redirect(url_for("transacciones"))

    return render_template(
        "transacciones.html",
        transacciones=banco_service.listar_transacciones(cliente_id=ambito_cliente()),
        cuentas=banco_service.listar_cuentas(cliente_id=ambito_cliente()),
        tipos=["DEPOSITO", "RETIRO", "TRANSFERENCIA"],
        canales=config.canales(),
    )


# =================================================================
# PRESTAMOS  ->  SEMANA 4: BUILDER + DIRECTOR
# =================================================================
@app.route("/prestamos", methods=["GET", "POST"])
@login_requerido()
def prestamos():
    if request.method == "POST":
        cliente_id = int(session.get("cliente_id") or request.form.get("cliente_id"))
        tipo = request.form.get("tipo")
        monto = float(request.form.get("monto") or 0)
        plazo = int(request.form.get("plazo") or 12)

        director = PrestamoDirector()
        builder = PrestamoBuilder()
        # [SEMANA 4 - BUILDER] La secuencia exacta la dicta el DIRECTOR,
        # ensamblando el prestamo paso a paso.
        if tipo == "PERSONAL":
            director.prestamo_personal(builder, cliente_id, monto, plazo)
        elif tipo == "HIPOTECARIO":
            director.prestamo_hipotecario(builder, cliente_id, monto, plazo)
        else:
            director.prestamo_vehicular(builder, cliente_id, monto, plazo)

        prestamo = builder.construir()
        cuota = prestamo.registrar()
        flash(
            f"Prestamo {tipo} creado. "
            f"Cuota mensual estimada: {cuota:.2f} {config.moneda()}",
            "ok",
        )
        return redirect(url_for("prestamos"))

    return render_template(
        "prestamos.html",
        prestamos=banco_service.listar_prestamos(cliente_id=ambito_cliente()),
        clientes=banco_service.listar_clientes(),
        tipos=["PERSONAL", "HIPOTECARIO", "VEHICULAR"],
    )


# =================================================================
# INVERSIONES  ->  SEMANA 4: BUILDER + DIRECTOR
# =================================================================
@app.route("/inversiones", methods=["GET", "POST"])
@login_requerido()
def inversiones():
    if request.method == "POST":
        cliente_id = int(session.get("cliente_id") or request.form.get("cliente_id"))
        perfil = request.form.get("perfil", "MODERADO")
        monto = float(request.form.get("monto") or 0)
        meses = int(request.form.get("plazo") or 12)

        cliente = Database().consulta_una(
            "SELECT * FROM clientes WHERE id = ?", (cliente_id,)
        )
        director = InversionDirector()
        builder = InversionBuilder()
        # [SEMANA 4 - BUILDER] El director arma la inversion según el perfil.
        if perfil == "CONSERVADOR":
            director.conservador(builder, cliente_id, cliente["nombre"], monto, meses)
        elif perfil == "AGRESIVO":
            director.agresivo(builder, cliente_id, cliente["nombre"], monto, meses)
        else:
            director.moderado(builder, cliente_id, cliente["nombre"], monto, meses)

        inversion = builder.construir()
        flash(
            f"Inversion {inversion.tipo} creada. "
            f"Rentabilidad estimada: {inversion.rentabilidad():.2f} {config.moneda()}",
            "ok",
        )
        return redirect(url_for("inversiones"))

    return render_template(
        "inversiones.html",
        inversiones=banco_service.listar_inversiones(cliente_id=ambito_cliente()),
        clientes=banco_service.listar_clientes(),
        perfiles=["CONSERVADOR", "MODERADO", "AGRESIVO"],
    )


# =================================================================
# FRAUDE - panel de alertas en tiempo real (cada cliente ve las suyas)
# =================================================================
@app.route("/fraude", methods=["GET", "POST"])
@login_requerido()
def fraude():
    if request.method == "POST":
        alerta_id = request.form.get("alerta_id")
        Database().ejecutar(
            "UPDATE alertas_fraude SET estado = 'REVISADA' WHERE id = ?",
            (int(alerta_id),),
        )
        flash("Alerta de fraude marcada como revisada", "ok")
        return redirect(url_for("fraude"))
    return render_template(
        "fraude.html",
        alertas=detector_fraude.listar_alertas(cliente_id=ambito_cliente()),
    )


if __name__ == "__main__":
    print("=" * 60)
    print(" SISTEMA BANCARIO CORE - Proyecto de Patrones de Diseño")
    print(" Abre en tu navegador:  http://127.0.0.1:5000")
    print(" " * 2 + "admin/admin123  (administrador)")
    print(" " * 2 + "maria/1234  o  luis/1234  (clientes de ejemplo)")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)