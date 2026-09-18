# Documentación del Sistema Bancario Core

La documentación detallada está separada en un archivo por cada semana del
proyecto progresivo. En la interfaz gráfica **no se muestran los patrones**:
estos viven en el código con comentarios `SEMANA X - PATRON`.

## Documentación semanal

| Semana | Patrón | Documento |
|---|---|---|
| 1 | Singleton | [Semana_1_Singleton.md](documentacion/Semana_1_Singleton.md) |
| 2 | Factory Method | [Semana_2_Factory_Method.md](documentacion/Semana_2_Factory_Method.md) |
| 3 | Abstract Factory | [Semana_3_Abstract_Factory.md](documentacion/Semana_3_Abstract_Factory.md) |
| 4 | Builder | [Semana_4_Builder.md](documentacion/Semana_4_Builder.md) |

Cada archivo explica el patrón trabajado, dónde está en el código, qué hace
dentro del sistema, las páginas relacionadas y cómo probarlo.

---

# Anexo — Funciones de la página (resumen general)

| Página | Quién la usa | Qué hace |
|---|---|---|
| **Login** (`/login`) | Todos | Ingreso con usuario y contraseña. |
| **Registro** (`/registro`) | Público | Abre ficha de cliente (KYC/AML automático) + credenciales. |
| **Dashboard** (`/`) | Todos | Contadores, alertas pendientes, últimos préstamos e inversiones. |
| **Mi ficha / Clientes** (`/clientes`) | Todos | Ficha financiera con KYC y riesgo AML. |
| **Cuentas** (`/cuentas`) | Todos | Crear y listar cuentas. (Semana 2 + 3) |
| **Transacciones** (`/transacciones`) | Todos | Depósitos, retiros y transferencias con fraude en tiempo real. (Semana 1 + 3) |
| **Préstamos** (`/prestamos`) | Todos | Solicitar préstamos y ver cuotas. (Semana 4) |
| **Inversiones** (`/inversiones`) | Todos | Crear inversiones por perfil de riesgo. (Semana 4) |
| **Fraude** (`/fraude`) | Todos | Alertas de fraude; marcarlas como revisadas. (Semana 1) |
| **Cumplimiento** (`/cumplimiento`) | Solo ADMIN | Tablero KYC/AML y recálculo de riesgo. |
| **Panel admin** (`/admin`) | Solo ADMIN | Crear usuarios, cambiar roles, activar/desactivar. |

**Roles:** `ADMIN` administra el sistema y ve todo; `CLIENTE` solo ve y opera su
propia cartera.
