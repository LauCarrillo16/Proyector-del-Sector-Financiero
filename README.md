# Sistema Bancario Core

Proyecto académico del sector financiero. Plantea el desarrollo del núcleo (core) de un sistema bancario y, como primera etapa, implementa el módulo de acceso junto con un sistema de registro y auditoría centralizado aplicando el patrón de diseño **Singleton**.

## Acerca del proyecto

Un core bancario es el software sobre el que se apoyan todas las operaciones de un banco: gestión de cuentas, transacciones, préstamos e inversiones, operando a través de múltiples canales (web, móvil, cajeros y sucursales), con detección de fraude en tiempo real y cumplimiento regulatorio (KYC/AML).

En esta etapa el desarrollo se concentra en:

- Inicio de sesión y registro de usuarios (autenticación por cookies).
- Un registro de eventos y auditoría centralizado, que es la base del control de seguridad y del cumplimiento.

Las demás funciones del banco forman parte del alcance conceptual del sistema y quedan planteadas como proyección a futuro.

## Patrón de diseño aplicado

El patrón **Singleton** se usó para el registro centralizado de eventos (clase `Logger`). Garantiza que exista una única instancia encargada de escribir la bitácora en toda la aplicación, lo que asegura un historial consistente y evita problemas cuando varias operaciones se registran al mismo tiempo. La clase maneja distintos niveles de registro: `INFO`, `WARN`, `ERROR` y `AUDIT` (este último para los eventos que exige la normativa bancaria, como accesos y registro de clientes).

## Tecnologías

- ASP.NET Core 7.0 (MVC)
- C#
- Entity Framework Core
- SQL Server

## Requisitos previos

- .NET 7 SDK
- SQL Server (Express, LocalDB o completo)
- Visual Studio 2022 (recomendado)

## Cómo ejecutarlo

1. Descarga o clona el repositorio y abre la solución `SistemaBancarioCore.sln`.

2. En `appsettings.json`, ajusta la cadena de conexión con el nombre de tu servidor de SQL Server:

   ```json
   "CadenaSQL": "Server=TU_SERVIDOR;Database=LoginDb;Trusted_Connection=True;MultipleActiveResultSets=true;Encrypt=false"
   ```

3. Crea la base de datos ejecutando la migración. En la Consola del Administrador de paquetes de Visual Studio:

   ```
   Update-Database
   ```

4. Ejecuta el proyecto (F5). La aplicación abre en la pantalla de inicio de sesión; desde ahí puedes registrar un usuario e ingresar.

Los registros de la aplicación se guardan en `bin/Debug/net7.0/Logs/`, en un archivo por día.

## Estructura del proyecto

```
SistemaBancarioCore/
├── Controllers/      Controladores (Login, Home)
├── Models/           Modelo Usuario y contexto de base de datos
├── Services/         Logger (Singleton), servicios de usuario y de archivos
├── Views/            Vistas Razor
├── Migrations/       Migraciones de Entity Framework
├── wwwroot/          Archivos estáticos (incluye las fotos de perfil)
└── appsettings.json  Configuración (cadena de conexión)
```

## Documentación

- **Semana 1 – Planteamiento del Proyecto:** introducción, problemática, justificación y objetivos del sistema.
- **Semana 2 – Aporte del Patrón Singleton:** explicación de cómo se aplicó el patrón y qué aportó al proyecto.
