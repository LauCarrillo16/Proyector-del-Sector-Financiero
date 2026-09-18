# Semana 3 — Patrón ABSTRACT FACTORY

## 1. ¿Qué es el patrón Abstract Factory?

Es un patrón de diseño **creacional** que crea **familias de objetos
relacionados** sin que el cliente sepa las clases concretas. Garantiza que todos
los objetos creados pertenezcan a la **misma familia**.

**¿Por qué en un banco?** El banco opera por **múltiples canales**: Web, Móvil,
Cajero y Sucursal. Cada canal necesita un *conjunto* de artefactos que van
juntos: la operación, la notificación y la auditoría. Si cada canal creara sus
objetos por separado, podríamos mezclar una operación de Cajero con una
notificación de Web (error). El Abstract Factory garantiza que, al elegir el
canal, **toda la familia es de ese canal**.

---

## 2. ¿Dónde está en el código?

Archivo: **`abstract_factory.py`**

| Pieza del patrón | Código |
|---|---|
| Fábrica abstracta | `FabricaAbstractaCanal` |
| Fábricas concretas | `FabricaWeb`, `FabricaMovil`, `FabricaCajero`, `FabricaSucursal` |
| Producto 1 | `OperacionCanal` (`OperacionWeb`, `OperacionMovil`, `OperacionCajero`, `OperacionSucursal`) |
| Producto 2 | `NotificacionCanal` (`NotificacionWeb`, `NotificacionMovil`, `NotificacionCajero`, `NotificacionSucursal`) |
| Producto 3 | `AuditoriaCanal` (`AuditoriaWeb`, `AuditoriaMovil`, `AuditoriaCajero`, `AuditoriaSucursal`) |
| Selector | `obtener_fabrica_canal(canal)` |

### Código clave

Fábrica abstracta (contrato de la familia):
```python
class FabricaAbstractaCanal(ABC):
    @abstractmethod
    def crear_operacion(self, tipo, monto): ...
    @abstractmethod
    def crear_notificacion(self): ...
    @abstractmethod
    def crear_auditoria(self): ...
```

Una fábrica concreta (familia del canal Web):
```python
class FabricaWeb(FabricaAbstractaCanal):
    def crear_operacion(self, tipo, monto):  return OperacionWeb(tipo, monto)
    def crear_notificacion(self):            return NotificacionWeb()
    def crear_auditoria(self):               return AuditoriaWeb()
```

Uso desde el servicio (`banco_service.py`):
```python
fabrica = obtener_fabrica_canal(canal)
operacion    = fabrica.crear_operacion(tipo, monto)
notificacion = fabrica.crear_notificacion()
auditoria    = fabrica.crear_auditoria()
```

La cabecera del archivo indica: `SEMANA 3 - PATRON ABSTRACT FACTORY`.

---

## 3. ¿Qué hace dentro del sistema?

Cuando el usuario opera por un canal (Web, Móvil, Cajero o Sucursal):

1. `obtener_fabrica_canal(canal)` devuelve la fábrica de ese canal.
2. La fábrica crea la **familia completa y consistente**:
   - **Operación**: con un folio propio del canal (por ejemplo `W-DEPOSITO-…`,
     `M-TRANSFERENCIA-…`) y su entorno de seguridad.
   - **Notificación**: correo (Web), push + SMS (Móvil), comprobante impreso
     (Cajero) o entrega por asesor (Sucursal).
   - **Auditoría**: deja trazabilidad etiquetada por canal.
3. Nunca se mezcla una operación de un canal con la notificación de otro.

Si mañana se agrega un canal nuevo, solo se crea una nueva fábrica concreta sin
tocar el resto del código.

---

## 4. Funciones de la página relacionadas

| Página | Cómo se ve el patrón en uso |
|---|---|
| **Transacciones** (`/transacciones`) | Al elegir el canal, se arma la familia completa de ese canal para registrar la operación. |
| **Cuentas** (`/cuentas`) | Al elegir el canal de apertura, la cuenta queda asociada a la familia de ese canal. |

---

## 5. Cómo probarlo desde el front

1. Ve a **Transacciones** y haz un depósito por canal **WEB** → la notificación
   será por correo.
2. Haz otro por canal **MOVIL** → la notificación será push + SMS.
3. Haz otro por **CAJERO** → será un comprobante impreso.
4. Haz otro por **SUCURSAL** → lo entrega un asesor.

Cada canal produce su propia familia de notificación/auditoría → eso es el
Abstract Factory.

---

## 6. Estructura del patrón

```
FabricaAbstractaCanal (fábrica abstracta)
   │ crear_operacion / crear_notificacion / crear_auditoria
   ├── FabricaWeb       → OperacionWeb      + NotificacionWeb      + AuditoriaWeb
   ├── FabricaMovil     → OperacionMovil    + NotificacionMovil    + AuditoriaMovil
   ├── FabricaCajero    → OperacionCajero   + NotificacionCajero   + AuditoriaCajero
   └── FabricaSucursal  → OperacionSucursal + NotificacionSucursal + AuditoriaSucursal

Cada fila es una FAMILIA completa y consistente de un canal.
```
