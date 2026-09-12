# 🏦 Sistema Bancario Core

Sistema bancario desarrollado como un proyecto progresivo para aplicar e integrar diferentes **patrones de diseño de software**.

El sistema permite gestionar clientes, cuentas bancarias, transacciones, préstamos, inversiones, alertas de fraude, cumplimiento KYC/AML y administración de usuarios.

Los patrones de diseño se implementan directamente en el código fuente. Para mantener una interfaz gráfica limpia, **los nombres de los patrones no se muestran en las páginas del sistema**. Cada implementación se encuentra identificada mediante comentarios como:

```text
SEMANA X - PATRON
```

Este documento explica qué patrón fue trabajado cada semana, dónde se encuentra implementado y cómo participa en las funcionalidades del sistema.

---

# 📋 Funcionalidades principales

El sistema cuenta con los siguientes módulos:

* 🔐 Autenticación y registro de usuarios.
* 👥 Gestión de clientes.
* 💳 Creación y administración de cuentas bancarias.
* 💸 Depósitos, retiros y transferencias.
* 🚨 Detección de fraude en tiempo real.
* 🏦 Solicitud de préstamos.
* 📈 Creación de inversiones.
* 📋 Gestión de cumplimiento KYC/AML.
* 👨‍💼 Administración de usuarios y roles.
* 📊 Dashboard general del sistema.

---

# 🗓️ Documentación por semanas

---

# Semana 1 — Singleton

## 📌 Patrón implementado

El patrón **Singleton** garantiza que exista una única instancia compartida de un objeto crítico dentro del sistema.

Este patrón es utilizado para servicios globales que deben ser compartidos por todos los módulos, evitando la creación de múltiples instancias innecesarias.

---

## 📂 Ubicación en el código

| Archivo              | Clase                  | Función                                                 |
| -------------------- | ---------------------- | ------------------------------------------------------- |
| `singleton.py`       | `SingletonMeta`        | Metaclase thread-safe encargada de crear los Singletons |
| `config_manager.py`  | `ConfigManager`        | Gestión de la configuración global                      |
| `database.py`        | `Database`             | Conexión única a SQLite                                 |
| `logger.py`          | `LoggerService`        | Registro centralizado de eventos                        |
| `fraud_detector.py`  | `FraudDetector`        | Motor único de detección de fraude                      |
| `auth_service.py`    | `AuthService`          | Gestión única de autenticación y roles                  |
| `kyc_aml_service.py` | `ServicioCumplimiento` | Gestión centralizada de políticas KYC/AML               |

---

## ⚙️ Funcionamiento dentro del sistema

Todos los módulos comparten:

* La misma configuración.
* La misma conexión a la base de datos.
* El mismo sistema de registro de eventos.
* El mismo motor de detección de fraude.
* El mismo servicio de autenticación.
* El mismo servicio de cumplimiento KYC/AML.

El componente más importante en esta implementación es el **FraudDetector**, ya que existe una única instancia encargada de analizar las operaciones realizadas en el sistema.

Antes de aprobar una transacción, el sistema verifica condiciones como:

* Límites máximos permitidos.
* Destinos inválidos.
* Clientes con nivel de riesgo ALTO.
* Operaciones sospechosas.

Cuando se detecta una situación de riesgo, la operación puede ser bloqueada y se genera una alerta de fraude.

---

## 🖥️ Funcionalidades relacionadas

| Página               | Uso del Singleton                                                    |
| -------------------- | -------------------------------------------------------------------- |
| **Todas**            | Comparten la misma configuración, base de datos y logger             |
| **Transacciones**    | Cada depósito, retiro o transferencia pasa por el detector de fraude |
| **Fraude**           | Muestra las alertas generadas por el motor de fraude                 |
| **Login / Registro** | Utiliza el servicio único de autenticación                           |
| **Cumplimiento**     | Utiliza el servicio único de KYC/AML                                 |

<img width="1536" height="1024" alt="ChatGPT Image 12 sept 2026, 01_16_44 p m" src="https://github.com/user-attachments/assets/9dd8b8bb-fe59-469a-8cba-ccca03827132" />

---

# Semana 2 — Factory Method

## 📌 Patrón implementado

El patrón **Factory Method** permite delegar la creación de objetos a diferentes fábricas.

La clase base define el proceso general para crear un objeto, mientras que las fábricas concretas determinan qué tipo específico de objeto será creado.

---

## 📂 Ubicación en el código

| Elemento            | Implementación                                                            |
| ------------------- | ------------------------------------------------------------------------- |
| Productos           | `Cuenta`, `CuentaAhorro`, `CuentaCorriente`, `CuentaInversion`            |
| Creador abstracto   | `FabricaCuentas`                                                          |
| Método principal    | `registrar_cuenta()`                                                      |
| Fábricas concretas  | `FabricaCuentaAhorro`, `FabricaCuentaCorriente`, `FabricaCuentaInversion` |
| Selector de fábrica | `obtener_fabrica(tipo)`                                                   |
| Archivo             | `factory_method.py`                                                       |

---

## ⚙️ Funcionamiento dentro del sistema

Cuando un usuario crea una cuenta bancaria, selecciona el tipo de cuenta que desea registrar.

El sistema identifica el tipo seleccionado y utiliza la fábrica correspondiente.

Los tipos disponibles son:

* Cuenta de Ahorro.
* Cuenta Corriente.
* Cuenta de Inversión.

Cada fábrica es responsable de crear su tipo de cuenta específico.

Además, cada tipo utiliza un prefijo diferente para su identificación:

```text
AHO- → Cuenta de Ahorro
CTE- → Cuenta Corriente
INV- → Cuenta de Inversión
```

La fábrica base se encarga de los pasos comunes, como:

1. Generar el número de cuenta.
2. Crear el objeto correspondiente.
3. Guardar la información en la base de datos.

---

## 🖥️ Funcionalidades relacionadas

| Página      | Uso del Factory Method                                                             |
| ----------- | ---------------------------------------------------------------------------------- |
| **Cuentas** | Al seleccionar Ahorro, Corriente o Inversión se utiliza la fábrica correspondiente |

<img width="1536" height="1024" alt="ChatGPT Image 12 sept 2026, 01_16_44 p m" src="https://github.com/user-attachments/assets/6753fba7-19db-442b-a293-5ea5f6f0d1de" />

---

# Semana 3 — Abstract Factory

## 📌 Patrón implementado

El patrón **Abstract Factory** permite crear familias de objetos relacionados entre sí.

En este proyecto se utiliza para gestionar las diferentes familias correspondientes a los canales bancarios.

Los canales disponibles son:

* 🌐 Web.
* 📱 Móvil.
* 🏧 Cajero.
* 🏢 Sucursal.

---

## 📂 Ubicación en el código

| Elemento           | Implementación                                                   |
| ------------------ | ---------------------------------------------------------------- |
| Fábrica abstracta  | `FabricaAbstractaCanal`                                          |
| Fábricas concretas | `FabricaWeb`, `FabricaMovil`, `FabricaCajero`, `FabricaSucursal` |
| Productos          | `OperacionCanal`, `NotificacionCanal`, `AuditoriaCanal`          |
| Selector           | `obtener_fabrica_canal(canal)`                                   |
| Archivo            | `abstract_factory.py`                                            |

---

## ⚙️ Funcionamiento dentro del sistema

Cuando un usuario realiza una operación desde un canal determinado, el sistema crea una familia completa de objetos relacionados con ese canal.

Cada operación incluye:

1. Una operación bancaria.
2. Una notificación.
3. Un registro de auditoría.

Por ejemplo, dependiendo del canal utilizado, la notificación puede ser:

| Canal    | Tipo de notificación     |
| -------- | ------------------------ |
| Web      | Correo electrónico       |
| Móvil    | Notificación Push o SMS  |
| Cajero   | Comprobante impreso      |
| Sucursal | Atención mediante asesor |

Esto evita que se mezclen elementos de diferentes canales.

Por ejemplo, una operación realizada desde un cajero no debería generar una notificación correspondiente al canal web.

---

## 🖥️ Funcionalidades relacionadas

| Página            | Uso del Abstract Factory                                                        |
| ----------------- | ------------------------------------------------------------------------------- |
| **Transacciones** | Al seleccionar Web, Móvil, Cajero o Sucursal se crea la familia correspondiente |
| **Cuentas**       | La apertura de una cuenta puede quedar asociada al canal seleccionado           |

<img width="1536" height="1024" alt="ChatGPT Image 12 sept 2026, 01_22_09 p m" src="https://github.com/user-attachments/assets/2c814ff3-abf8-40c1-b6f3-c20cd072eceb" />

---

# Semana 4 — Builder

## 📌 Patrón implementado

El patrón **Builder** permite construir objetos complejos paso a paso.

Este patrón evita tener constructores demasiado grandes con muchos parámetros opcionales.

En el sistema se utiliza principalmente para:

* Préstamos.
* Inversiones.

---

# 🏦 Construcción de préstamos

## 📂 Ubicación en el código

| Elemento | Implementación     |
| -------- | ------------------ |
| Producto | `Prestamo`         |
| Builder  | `PrestamoBuilder`  |
| Director | `PrestamoDirector` |
| Archivo  | `builders.py`      |

---

## ⚙️ Funcionamiento

El Director determina la secuencia de construcción dependiendo del tipo de préstamo.

Los tipos disponibles son:

* Personal.
* Hipotecario.
* Vehicular.

Durante la construcción se agregan elementos como:

* Monto solicitado.
* Plazo.
* Tasa de interés.
* Garantía.
* Seguro.
* Cálculo de cuota mensual.

Finalmente, el préstamo construido puede ser almacenado en el sistema.

---

# 📈 Construcción de inversiones

## 📂 Ubicación en el código

| Elemento | Implementación      |
| -------- | ------------------- |
| Producto | `Inversion`         |
| Builder  | `InversionBuilder`  |
| Director | `InversionDirector` |
| Archivo  | `builders.py`       |

<img width="1535" height="1024" alt="ChatGPT Image 12 sept 2026, 01_35_52 p m" src="https://github.com/user-attachments/assets/353a3538-d8a5-4217-bc0a-5b2498c4723f" />

---

## ⚙️ Funcionamiento

La inversión se construye según el perfil de riesgo del cliente.

Los perfiles disponibles son:

* Conservador.
* Moderado.
* Agresivo.

Dependiendo del perfil, el sistema selecciona características como:

* Tipo de producto.
* Tasa estimada.
* Nivel de riesgo.
* Rentabilidad esperada.

Los productos pueden incluir:

* Plazo fijo.
* Fondo mixto.
* Bonos.

Finalmente, el sistema calcula la rentabilidad estimada de la inversión.

---

## 🖥️ Funcionalidades relacionadas

| Página          | Uso del Builder                                 |
| --------------- | ----------------------------------------------- |
| **Préstamos**   | Construye préstamos según tipo, monto y plazo   |
| **Inversiones** | Construye inversiones según el perfil de riesgo |

---

# 🖥️ Módulos del sistema

| Página                     | Ruta             | Quién puede acceder   | Función                                                    |
| -------------------------- | ---------------- | --------------------- | ---------------------------------------------------------- |
| 🔐 Login                   | `/login`         | Todos                 | Permite iniciar sesión                                     |
| 📝 Registro                | `/registro`      | Público               | Registra clientes y realiza validaciones iniciales KYC/AML |
| 📊 Dashboard               | `/`              | Usuarios autenticados | Muestra información general, alertas y movimientos         |
| 👥 Clientes                | `/clientes`      | Usuarios autenticados | Permite consultar información financiera y nivel de riesgo |
| 💳 Cuentas                 | `/cuentas`       | Usuarios autenticados | Crear y consultar cuentas bancarias                        |
| 💸 Transacciones           | `/transacciones` | Usuarios autenticados | Depósitos, retiros y transferencias                        |
| 🏦 Préstamos               | `/prestamos`     | Usuarios autenticados | Solicitud y consulta de préstamos                          |
| 📈 Inversiones             | `/inversiones`   | Usuarios autenticados | Creación y consulta de inversiones                         |
| 🚨 Fraude                  | `/fraude`        | Usuarios autenticados | Consulta y revisión de alertas de fraude                   |
| 📋 Cumplimiento            | `/cumplimiento`  | ADMIN                 | Gestión de KYC/AML y niveles de riesgo                     |
| 👨‍💼 Panel administrativo | `/admin`         | ADMIN                 | Gestión de usuarios, roles y estados                       |

---

# 👤 Roles del sistema

El sistema cuenta con dos roles principales.

## 👨‍💼 ADMIN

El administrador tiene acceso completo a las funcionalidades del sistema.

Puede:

* Administrar usuarios.
* Crear usuarios.
* Cambiar roles.
* Activar o desactivar cuentas.
* Consultar información de clientes.
* Gestionar cumplimiento KYC/AML.
* Consultar alertas de fraude.
* Acceder a los módulos administrativos.

---

## 👤 CLIENTE

El cliente tiene acceso únicamente a la información relacionada con su propia cartera.

Puede:

* Consultar su información.
* Crear cuentas.
* Realizar transacciones.
* Solicitar préstamos.
* Crear inversiones.
* Consultar sus productos financieros.

---

# 🧩 Relación entre patrones y funcionalidades

| Semana   | Patrón           | Funcionalidad principal                                 |
| -------- | ---------------- | ------------------------------------------------------- |
| Semana 1 | Singleton        | Servicios globales, autenticación y detección de fraude |
| Semana 2 | Factory Method   | Creación de diferentes tipos de cuentas                 |
| Semana 3 | Abstract Factory | Gestión de operaciones por canales bancarios            |
| Semana 4 | Builder          | Construcción paso a paso de préstamos e inversiones     |

---

# 🔄 Flujo general de una operación

Una operación dentro del sistema puede seguir el siguiente flujo:

```text
Usuario
   │
   ▼
Selecciona una funcionalidad
   │
   ▼
Selecciona canal
(Web / Móvil / Cajero / Sucursal)
   │
   ▼
Abstract Factory crea la familia del canal
   │
   ▼
Singleton FraudDetector analiza la operación
   │
   ├── Operación válida
   │       │
   │       ▼
   │   Se procesa y registra
   │
   └── Operación sospechosa
           │
           ▼
      Se bloquea y genera alerta
```

---

# 📁 Estructura relacionada con los patrones

```text
proyecto/
│
├── singleton.py
├── config_manager.py
├── database.py
├── logger.py
├── fraud_detector.py
├── auth_service.py
├── kyc_aml_service.py
│
├── factory_method.py
│
├── abstract_factory.py
│
├── builders.py
│
└── README.md
```

---

# 🎯 Objetivo del proyecto

El objetivo del Sistema Bancario Core es desarrollar progresivamente un sistema funcional que permita aplicar patrones de diseño en situaciones reales dentro de un contexto bancario.

Cada patrón se incorpora para resolver una necesidad específica:

* **Singleton:** controlar servicios únicos y compartidos.
* **Factory Method:** crear diferentes tipos de cuentas.
* **Abstract Factory:** manejar familias completas según el canal bancario.
* **Builder:** construir productos financieros complejos paso a paso.

De esta manera, los patrones no se implementan únicamente como ejemplos aislados, sino como parte del funcionamiento real del sistema.

---

# 📚 Documentación de patrones

Cada semana del proyecto incorpora un nuevo patrón de diseño.

Los patrones están documentados:

* En el código mediante comentarios.
* En este README mediante su explicación funcional.
* En las funcionalidades visibles del sistema mediante su integración.

La interfaz gráfica está enfocada en el funcionamiento del sistema bancario, mientras que la implementación de los patrones permanece organizada dentro del código fuente.

```text
SEMANA 1 - SINGLETON
SEMANA 2 - FACTORY METHOD
SEMANA 3 - ABSTRACT FACTORY
SEMANA 4 - BUILDER
```

---

## 👩‍💻 Proyecto académico

**Sistema Bancario Core**

Proyecto progresivo orientado a la aplicación práctica de patrones de diseño de software dentro de un sistema bancario.

Cada semana incorpora una nueva solución arquitectónica al sistema, permitiendo que el proyecto evolucione progresivamente mientras se aplican conceptos de diseño y programación orientada a objetos.
