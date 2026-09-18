# Semana 2 — Patrón FACTORY METHOD

## 1. ¿Qué es el patrón Factory Method?

Es un patrón de diseño **creacional** que define un **método (función) para crear
objetos**, pero delega a las **subclases concretas** la decisión de *qué clase*
instanciar.

La clase base sabe *qué pasos seguir* (el método plantilla), pero cada fábrica
concreta decide *qué objeto crear*.

**¿Por qué en un banco?** Hay varios tipos de cuenta (Ahorro, Corriente,
Inversión). En vez de crearlas "a mano" en el código del front, cada tipo tiene
su propia fábrica que decide qué clase de cuenta construir.

---

## 2. ¿Dónde está en el código?

Archivo: **`factory_method.py`**

| Pieza del patrón | Código |
|---|---|
| Producto (base) | `Cuenta` |
| Productos concretos | `CuentaAhorro`, `CuentaCorriente`, `CuentaInversion` |
| Creador abstracto | `FabricaCuentas` (con el método plantilla `registrar_cuenta()`) |
| Creadores concretos | `FabricaCuentaAhorro`, `FabricaCuentaCorriente`, `FabricaCuentaInversion` |
| Selector | `obtener_fabrica(tipo)` |

### Código clave

Creador abstracto con el método plantilla:
```python
class FabricaCuentas(ABC):
    def registrar_cuenta(self, cliente_id, numero, saldo_inicial, canal):
        cuenta = self.crear_cuenta(cliente_id, saldo_inicial, canal)  # FACTORY METHOD
        numero_final = numero or self.generar_numero(cuenta)
        cuenta.registrar_en_db(numero_final)
        return numero_final, cuenta

    @abstractmethod
    def crear_cuenta(self, cliente_id, saldo_inicial, canal):  # decide la subclase
        pass
```

Una fábrica concreta:
```python
class FabricaCuentaAhorro(FabricaCuentas):
    def crear_cuenta(self, cliente_id, saldo_inicial, canal):
        return CuentaAhorro(cliente_id, saldo_inicial, canal)
```

El front nunca instancia la cuenta; solo pide la fábrica:
```python
fabrica = obtener_fabrica(tipo)          # elige la fábrica según el tipo
numero, cuenta = fabrica.registrar_cuenta(...)
```

La cabecera del archivo indica: `SEMANA 2 - PATRON FACTORY METHOD`.

---

## 3. ¿Qué hace dentro del sistema?

Cuando se abre una cuenta nueva:

1. El usuario elige el **tipo de cuenta** (Ahorro, Corriente o Inversión).
2. `obtener_fabrica(tipo)` devuelve la fábrica concreta correspondiente.
3. La fábrica llama al **factory method** `crear_cuenta()` que crea la clase
   correcta (`CuentaAhorro`, `CuentaCorriente` o `CuentaInversion`).
4. El método plantilla `registrar_cuenta()` hace los pasos comunes: genera el
   **número de cuenta** con su prefijo (`AHO-`, `CTE-`, `INV-`) y la **guarda en
   la base de datos**.

Así, si mañana se agrega un nuevo tipo de cuenta, solo se crea una nueva fábrica
sin tocar el código existente (abierto a extensión, cerrado a modificación).

---

## 4. Funciones de la página relacionadas

| Página | Cómo se ve el patrón en uso |
|---|---|
| **Cuentas** (`/cuentas`) | Al elegir el tipo y dar clic en "Crear cuenta", se dispara la fábrica correspondiente. |

---

## 5. Cómo probarlo desde el front

1. Entra (por ejemplo `maria / 1234`) y ve a **Cuentas**.
2. Crea una cuenta tipo **AHORRO**: verás que el número empieza por `AHO-`.
3. Crea una tipo **CORRIENTE**: el número empieza por `CTE-`.
4. Crea una tipo **INVERSION**: el número empieza por `INV-`.

Cada prefijo lo decide la fábrica concreta → eso es el Factory Method.

---

## 6. Estructura del patrón

```
FabricaCuentas (creador abstracto)      Cuenta (producto)
   │ registrar_cuenta()                     │
   │ crear_cuenta()  <- abstracto           ├── CuentaAhorro      (AHO-)
   ├── FabricaCuentaAhorro  --------------> ├── CuentaCorriente   (CTE-)
   ├── FabricaCuentaCorriente -----------> └── CuentaInversion   (INV-)
   └── FabricaCuentaInversion ----------->
```
