# UDG-Proyectos 🎓

> **Sistema de Seguimiento de Proyectos y Tesis**  
> Universidad de Guadalajara — Arquitectura MVC con CodeIgniter 4 + MySQL

[![PHP](https://img.shields.io/badge/PHP-8.1+-777BB4?logo=php)](https://php.net)
[![CodeIgniter](https://img.shields.io/badge/CodeIgniter-4.x-EF4223?logo=codeigniter)](https://codeigniter.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql)](https://mysql.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap)](https://getbootstrap.com)

---

## 📋 Descripción

Sistema web escalable para gestión, evaluación y publicación de proyectos/tesis académicas.
Diseñado para **5,000 estudiantes**, **200 evaluadores** y archivos de hasta **500 MB**.

## 🏗 Arquitectura

```
Capa 1 — Presentación:   HTML5 · Bootstrap 5 · JavaScript · CSS Variables
Capa 2 — Lógica:         CodeIgniter 4 · Controllers · Filters · Helpers
Capa 3 — Datos:          MySQL 8 · CI4 Models · Migrations · Seeds
```

## 📦 Módulos y Ramas Git

| Módulo | Rama | Descripción |
|--------|------|-------------|
| 1 — Envío | `modulo/envio` | Subida de proyectos, versiones, borradores |
| 2 — Aprobación | `modulo/aprobacion` | Flujo de aprobación + comité evaluador |
| 3 — Repositorio | `modulo/repositorio` | Búsqueda pública, descargas, citas |
| 4 — Admin | `modulo/administracion` | Usuarios, roles, configuración, logs |
| 5 — Notificaciones | `modulo/notificacion` | Email SMTP + centro de notificaciones |
| 6 — Portafolio | `modulo/portafolio` | Perfil estudiantil con proyectos |
| 7 — Herramientas | `modulo/herramientas` | Repositorio software/datasets |
| 8 — Interacción | `modulo/interaccion` | Votos, comentarios, ranking |

## 🚀 Instalación Local (XAMPP)

### Pre-requisitos
- XAMPP con PHP 8.1+ y MySQL 8
- Composer (o usar `composer.phar` incluido)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/udg_proyectos.git
cd udg_proyectos

# 2. Instalar dependencias PHP
php composer.phar install

# 3. Configurar entorno
cp .env.example .env
# Editar .env con tus datos de BD y SMTP

# 4. Crear la base de datos en MySQL
# CREATE DATABASE udg_proyectos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 5. Ejecutar migraciones
php spark migrate

# 6. Insertar datos iniciales
php spark db:seed MainSeeder

# 7. Acceder al sistema
# http://localhost/udg_proyectos/public/
```

### Credenciales iniciales del administrador
```
Email:    admin@udg.mx
Password: Admin2024!
⚠️  CAMBIA LA CONTRASEÑA DESPUÉS DEL PRIMER LOGIN
```

## 📁 Estructura de Carpetas

```
udg_proyectos/
├── app/
│   ├── Config/          → App, Database, Routes, Filters
│   ├── Controllers/
│   │   ├── Auth/        → Login, Register
│   │   ├── Modulo1_Envio/
│   │   ├── Modulo2_Aprobacion/
│   │   ├── Modulo3_Repositorio/
│   │   ├── Modulo4_Admin/
│   │   ├── Modulo5_Notificacion/
│   │   ├── Modulo6_Portafolio/
│   │   ├── Modulo7_Herramientas/
│   │   └── Modulo8_Interaccion/
│   ├── Models/          → UserModel, ProjectModel + por módulo
│   ├── Views/           → layouts, partials, auth, módulos
│   ├── Filters/         → AuthFilter, RoleFilter, GuestFilter
│   ├── Helpers/         → app_helper, format_helper (citas APA/IEEE/MLA)
│   ├── Libraries/       → EmailNotification, FileUploader
│   └── Database/
│       ├── Migrations/  → 001_Catalogos → 005_Notificaciones
│       └── Seeds/       → Roles, Catálogos, Admin
│
├── public/              → Web root (apuntar aquí el VirtualHost)
│   ├── index.php
│   ├── .htaccess
│   └── assets/          → css/, js/, images/
│
├── writable/            → Subidas, logs, caché (NO en Git)
├── tests/               → PHPUnit
├── docs/                → Documentación por módulo
├── .env.example         → Plantilla de variables de entorno
└── composer.json
```

## 🔐 Roles del Sistema (RBAC)

| Rol | Descripción |
|-----|-------------|
| `superadmin` | Control total |
| `admin` | Gestión de usuarios y config |
| `coordinador` | Asigna evaluadores |
| `evaluador` | Revisa y dictamina proyectos |
| `estudiante` | Envía y gestiona sus proyectos |
| `publico` | Solo lectura del repositorio |

## 🌊 Flujo del Sistema

```
Envío → Asignación → Revisión → Correcciones → Aprobación → Publicación
  borrador → enviado → en_revision → correcciones → aprobado → publicado
                                   ↘ rechazado
```

## 📐 Convenciones de Código

### Commits
```
[MOD-N] tipo: descripción breve
```
Ejemplos:
- `[MOD-1] feat: formulario multi-paso de envío`
- `[MOD-2] fix: cálculo de dictamen final`
- `[BASE] refactor: BaseModel con paginación`

### Tipos: `feat`, `fix`, `refactor`, `docs`, `test`, `style`

### Ramas
```bash
git checkout main
git pull origin main
git checkout -b modulo/envio
```

### Pull Requests
- Target: `main`
- Requiere: revisión de al menos 1 compañero
- Pasar: PHP sin errores de sintaxis

## 🛠 Comandos Útiles (php spark)

```bash
# Migraciones
php spark migrate               # Ejecutar todas
php spark migrate:rollback      # Revertir última
php spark migrate:status        # Ver estado

# Seeds
php spark db:seed MainSeeder    # Datos iniciales

# Generar archivos
php spark make:controller Nombre --module App
php spark make:model Nombre
php spark make:migration Nombre

# Servidor de desarrollo
php spark serve
```

## 📚 Documentación por Módulo

- [docs/modulos/envio.md](docs/modulos/envio.md) — Módulo 1
- [docs/modulos/aprobacion.md](docs/modulos/aprobacion.md) — Módulo 2
- [docs/modulos/repositorio.md](docs/modulos/repositorio.md) — Módulo 3
- [docs/modulos/administracion.md](docs/modulos/administracion.md) — Módulo 4
- [docs/modulos/notificacion.md](docs/modulos/notificacion.md) — Módulo 5
- [docs/modulos/portafolio.md](docs/modulos/portafolio.md) — Módulo 6
- [docs/modulos/herramientas.md](docs/modulos/herramientas.md) — Módulo 7
- [docs/modulos/interaccion.md](docs/modulos/interaccion.md) — Módulo 8

---

**Universidad de Guadalajara** · Sistema académico de proyectos y tesis · 2024
