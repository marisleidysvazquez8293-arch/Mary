-- Esquema de Base de Datos para UDG-Proyectos

CREATE DATABASE IF NOT EXISTS udg_proyectos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE udg_proyectos;

-- 1. TABLAS DE CATÁLOGOS BASE
CREATE TABLE IF NOT EXISTS roles (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(255) NULL
);

CREATE TABLE IF NOT EXISTS areas (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(255) NULL
);

CREATE TABLE IF NOT EXISTS tipos_proyecto (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

-- 2. TABLA DE USUARIOS
CREATE TABLE IF NOT EXISTS usuarios (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol_id INT UNSIGNED NOT NULL,
    estatus ENUM('activo', 'inactivo') DEFAULT 'activo',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rol_id) REFERENCES roles(id) 
);

-- 3. PROYECTOS PRINCIPALES
CREATE TABLE IF NOT EXISTS proyectos (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    resumen TEXT NOT NULL,
    palabras_clave VARCHAR(255) NOT NULL,
    area_id INT UNSIGNED NOT NULL,
    tipo_id INT UNSIGNED NOT NULL,
    autor_id INT UNSIGNED NOT NULL,
    asesor_id INT UNSIGNED NULL,
    estatus ENUM('borrador','enviado','asignado','en_revision','correcciones','aprobado','rechazado','publicado') DEFAULT 'borrador',
    identificador_unico VARCHAR(50) UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (area_id) REFERENCES areas(id) ,
    FOREIGN KEY (tipo_id) REFERENCES tipos_proyecto(id) ,
    FOREIGN KEY (autor_id) REFERENCES usuarios(id) ,
    FOREIGN KEY (asesor_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

-- 4. ARCHIVOS Y VERSIONES
CREATE TABLE IF NOT EXISTS versiones (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    proyecto_id INT UNSIGNED NOT NULL,
    numero_version INT NOT NULL DEFAULT 1,
    descripcion TEXT NULL,
    usuario_id INT UNSIGNED NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) 
);

CREATE TABLE IF NOT EXISTS archivos_proyecto (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    proyecto_id INT UNSIGNED NOT NULL,
    version_id INT UNSIGNED NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta VARCHAR(255) NOT NULL,
    tipo_mime VARCHAR(50) NOT NULL,
    tamano_bytes INT UNSIGNED NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE,
    FOREIGN KEY (version_id) REFERENCES versiones(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS borradores (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    proyecto_id INT UNSIGNED NOT NULL,
    datos_json JSON NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE
);

-- 5. FLUJO DE EVALUACIÓN
CREATE TABLE IF NOT EXISTS asignaciones (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    proyecto_id INT UNSIGNED NOT NULL,
    evaluador_id INT UNSIGNED NOT NULL,
    fecha_asignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    estatus ENUM('pendiente', 'en_revision', 'completada') DEFAULT 'pendiente',
    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE,
    FOREIGN KEY (evaluador_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS revisiones (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    asignacion_id INT UNSIGNED NOT NULL,
    dictamen ENUM('aprobado', 'rechazado', 'correcciones') NOT NULL,
    notas TEXT NULL,
    fecha_revision DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asignacion_id) REFERENCES asignaciones(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comentarios (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    revision_id INT UNSIGNED NOT NULL,
    archivo_id INT UNSIGNED NULL,
    texto TEXT NOT NULL,
    evaluador_id INT UNSIGNED NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (revision_id) REFERENCES revisiones(id) ON DELETE CASCADE,
    FOREIGN KEY (archivo_id) REFERENCES archivos_proyecto(id) ON DELETE SET NULL,
    FOREIGN KEY (evaluador_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS historial_flujo (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    proyecto_id INT UNSIGNED NOT NULL,
    estado_anterior VARCHAR(50) NOT NULL,
    estado_nuevo VARCHAR(50) NOT NULL,
    usuario_id INT UNSIGNED NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- 6. NOTIFICACIONES
CREATE TABLE IF NOT EXISTS notificaciones (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT UNSIGNED NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    mensaje TEXT NOT NULL,
    tipo ENUM('sistema', 'proyecto', 'evaluacion') DEFAULT 'sistema',
    leida BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS config_notif (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT UNSIGNED NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    canal ENUM('email', 'interna', 'ambas') DEFAULT 'ambas',
    activa BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- 7. SEEDS: DATOS INICIALES
INSERT IGNORE INTO roles (id, nombre, descripcion) VALUES
(1, 'superadmin', 'Control total del sistema'),
(2, 'admin', 'Gestor de usuarios e información'),
(3, 'coordinador', 'Asigna evaluadores y supervisa comité'),
(4, 'evaluador', 'Dictaminador de tesis y proyectos'),
(5, 'estudiante', 'Autor principal de los proyectos'),
(6, 'publico', 'Miembro con acceso al repositorio');

INSERT IGNORE INTO areas (id, nombre) VALUES
(1, 'Ingeniería en Computación'),
(2, 'Informática'),
(3, 'Ingeniería Biomédica');

INSERT IGNORE INTO tipos_proyecto (id, nombre) VALUES
(1, 'Tesis'),
(2, 'Protocolo'),
(3, 'Proyecto Modular');

-- Usuario admin
INSERT IGNORE INTO usuarios (nombre, apellidos, correo, password_hash, rol_id, estatus) VALUES 
('Admin', 'Principal', 'admin@udg.mx', '$2y$10$wN/cW4I7d1dDWeY/bXoUge1BwJ7M7d5L1M.L8lWbH6O.6x.dJmHeC', 1, 'activo');
