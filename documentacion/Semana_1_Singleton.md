# Semana 1 — Patrón SINGLETON

## 1. ¿Qué es el patrón Singleton?

Es un patrón de diseño **creacional** que garantiza que una clase tenga
**una única instancia** en todo el sistema y proporciona un punto de acceso
global a ella.

**¿Por qué en un banco?** Cosas como la configuración, la conexión a la base de
datos, el logger y el motor de fraude NO deben crearse muchas veces: todos los
canales (Web, Móvil, Cajero, Sucursal) deben usar exactamente el mismo objeto.

---

## 2. ¿Dónde está en el código?

| Archivo | Clase | Qué singleton es |
|---|---|---|
| `singleton.py` | `SingletonMeta` | La metaclase base (el mecanismo del patrón) |
| `config_manager.py` | `ConfigManager` | Configuración global del banco |
| `database.py` | `Database` | Una sola conexión a SQLite |
| `logger.py` | `LoggerService` | Registro centralizado de eventos |
| `fraud_detector.py` | `FraudDetector` | Motor único de detección de fraude |
| `auth_service.py` | `AuthService` | Servicio único de login y roles |
| `kyc_aml_service.py` | `ServicioCumplimiento` | Servicio único de cumplimiento KYC/AML |

### Cómo se implementa (código clave)

`singleton.py`:
```python
class SingletonMeta(type):
    _instancias = {}            # guarda la única instancia por clase
    _lock = threading.Lock()    # seguro en concurrencia

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instancias:
            with cls._lock:
                if cls not in cls._instancias:
                    cls._instancias[cls] = super().__call__(*args, **kwargs)
        return cls._instancias[cls]
```

Cualquier clase se vuelve singleton así:
```python
class ConfigManager(metaclass=SingletonMeta):
    ...
```

Cada archivo tiene en su cabecera el comentario:
`SEMANA 1 - PATRON SINGLETON`.

---

## 3. ¿Qué hace dentro del sistema?

- **ConfigManager**: todos los módulos leen los mismos límites de operación,
  canales y umbrales de fraude. Nadie crea una copia distinta de la configuración.
- **Database**: una sola conexión a SQLite; evita abrir una conexión por cada
  petición y mantiene la consistencia entre canales.
- **LoggerService**: todos los eventos (login, cuentas, transacciones, fraude,
  builder) escriben en el mismo log ordenado.
- **FraudDetector**: un único motor que analiza cada operación en tiempo real.
  Reglas actuales:
  1. Monto sobre el límite del tipo de operación (depósito/retiro/transferencia).
  2. Transferencia a una cuenta destino inexistente.
  3. Cliente con riesgo AML ALTO moviendo montos grandes.
  Si se activa una regla, la operación se **bloquea** y se crea una **alerta**.

### Verificación de que es Singleton
```python
from config_manager import ConfigManager
a = ConfigManager()
b = ConfigManager()
print(a is b)   # True  -> misma instancia
```

---

## 4. Funciones de la página relacionadas

| Página | Cómo se ve el patrón en uso |
|---|---|
| **Todas** | Toda la app usa la misma configuración, base de datos y logger. |
| **Transacciones** (`/transacciones`) | Cada depósito, retiro o transferencia pasa por el motor de fraude (instancia única) antes de aprobarse. |
| **Fraude** (`/fraude`) | Muestra las alertas que creó ese motor único; permite marcarlas como revisadas. |
| **Login** (`/login`) y **Registro** (`/registro`) | El servicio de autenticación es único (mismas reglas para todos). |
| **Cumplimiento** (`/cumplimiento`) | El servicio KYC/AML es único y se aplica igual en todos los canales. |

---

## 5. Cómo probarlo desde el front

1. Entra como `maria / 1234` y ve a **Transacciones**.
2. Retira más de 5.000 (límite de retiro) por cualquier canal.
3. El motor de fraude la bloquea al instante.
4. Ve a **Fraude**: aparece la alerta generada por la única instancia del motor.

---

## 6. Estructura del patrón

```
SingletonMeta (metaclase)
      │
      ├── ConfigManager    (configuración)
      ├── Database         (conexión)
      ├── LoggerService    (logs)
      ├── FraudDetector    (fraude en tiempo real)
      ├── AuthService      (login/roles)
      └── ServicioCumplimiento (KYC/AML)
```
