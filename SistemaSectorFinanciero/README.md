# Sistema Bancario Core - Proyecto Progresivo de Patrones de Diseño

> **Documentación completa** (funciones de la página y relación con cada patrón):
> ver `DOCUMENTACION.md`.
> En la interfaz gráfica no se muestran los patrones; están en el código con
> comentarios `SEMANA X - PATRON`.

Sistema bancario core en **Python + Flask** con interfaz grafica web.
Modulos del negocio: gestion de cuentas, transacciones, prestamos e inversiones,
multiples canales (Web, Movil, Cajero, Sucursal), deteccion de fraude en
tiempo real y cumplimiento regulatorio (KYC / AML).

## Como ejecutar

```bash
pip install flask
python app.py
```

Abrir <http://127.0.0.1:5000> en el navegador.
En el primer arranque se crea la base `banco.db` con datos de ejemplo.

> Si quieres empezar de cero borra el archivo `banco.db` y vuelve a ejecutar.

## Roles y credenciales de demostracion

| Usuario | Clave | Rol | Que ve y hace |
|---|---|---|---|
| `admin` | `admin123` | ADMIN | Gestion global: todos los clientes, datos y alertas + panel de usuarios |
| `maria` | `1234` | CLIENTE | Solo su cartera (ficha Maria Perez) |
| `luis` | `1234` | CLIENTE | Solo su cartera (ficha Luis Gomez) |

Tambien puedes **registrarte** desde la pagina `/registro`: se crea tu ficha financiera
(KYC/AML) y un usuario CLIENTE con el que entras a operar tu propia cartera.
Las contraseñas se guardan con hash (werkzeug).

## Estructura del proyecto

| Archivo | Contenido |
|---|---|
| `app.py` | Servidor Flask y rutas de la interfaz |
| `singleton.py` | Metaclase base del Singleton (semana 1) |
| `config_manager.py` | Configuracion global (Singleton) |
| `database.py` | Conexion unica a SQLite (Singleton) |
| `logger.py` | Logger compartido (Singleton) |
| `fraud_detector.py` | Motor de fraude en tiempo real (Singleton) |
| `auth_service.py` | Login, registro y gestion de roles (Singleton) |
| `factory_method.py` | Creacion de cuentas (semana 2) |
| `abstract_factory.py` | Familias multicanal (semana 3) |
| `builders.py` | Prestamos e inversiones (semana 4) |
| `banco_service.py` | Capa de servicio que orquesta los patrones |
| `kyc_aml_service.py` | Cumplimiento regulatorio (KYC/AML) |
| `templates/`, `static/` | Interfaz grafica |

---

## Semana 1 - Singleton

**Encontrar el patron:**
- `singleton.py`: `SingletonMeta` (metaclase thread-safe con `threading.Lock`).
- `config_manager.py`: `class ConfigManager(metaclass=SingletonMeta)`.
- `database.py`: `class Database(metaclass=SingletonMeta)` (una sola conexion SQLite).
- `logger.py`: `class LoggerService(metaclass=SingletonMeta)`.
- `fraud_detector.py`: `class FraudDetector(metaclass=SingletonMeta)`.

**Como se nota en el sistema:** todos los canales y servicios llaman
`ConfigManager()`, `Database()`, `FraudDetector()`, etc., y siempre reciben la
misma instancia. En la interfaz se ve reflejado en el panel de **Fraude**, donde
el unico motor supervisa cada transaccion.

## Semana 2 - Factory Method

**Encontrar el patron:** `factory_method.py`
- Productos: `Cuenta`, `CuentaAhorro`, `CuentaCorriente`, `CuentaInversion`.
- Creador abstracto: `FabricaCuentas` con el **metodo plantilla**
  `registrar_cuenta()` que llama al metodo abstracto `crear_cuenta()`.
- Creadores concretos: `FabricaCuentaAhorro`, `FabricaCuentaCorriente`,
  `FabricaCuentaInversion`.
- Selector: `obtener_fabrica(tipo)`.

**Ruta de la interfaz:** `/cuentas`. La vista solo elige tipo; la fabrica
decide el producto.

## Semana 3 - Abstract Factory

**Encontrar el patron:** `abstract_factory.py`
- Fabrica abstracta: `FabricaAbstractaCanal` (contrato de la familia).
- Fabricas concretas por canal: `FabricaWeb`, `FabricaMovil`, `FabricaCajero`,
  `FabricaSucursal`.
- Productos por familia: `OperacionCanal`, `NotificacionCanal`, `AuditoriaCanal`
  (cada canal tiene sus variantes).
- Selector: `obtener_fabrica_canal(canal)`.

**Ruta de la interfaz:** `/transacciones` y apertura de cuentas (`/cuentas`).
Se garantiza que una operacion de Cajero nunca se mezcle con notificaciones Web,
etc.

## Semana 4 - Builder

**Encontrar el patron:** `builders.py`
- `PrestamoBuilder` (pasos encadenables: monto, plazo, tasa, garantia, seguro)
  + `PrestamoDirector` (recetas: Personal, Hipotecario, Vehicular).
- `InversionBuilder` (inversor, tipo, monto, tasa, plazo, perfil)
  + `InversionDirector` (perfiles: Conservador, Moderado, Agresivo).

**Rutas de la interfaz:** `/prestamos` y `/inversiones`.

---

### Nota para la entrega

Cada archivo contiene comentarios de cabecera tipo
`SEMANA X - PATRON` que marcan textualmente **donde** se trabaja el patron.
Revísalos antes de la presentación para explicar cada decisión de diseño.