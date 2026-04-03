<?php

/*
 * ---------------------------------------------------------------
 * ENTRY POINT — UDG-Proyectos
 * ---------------------------------------------------------------
 * Este archivo es el único acceso web al sistema.
 * El servidor web (Apache/Nginx) debe apuntar aquí.
 *
 * XAMPP: http://localhost/udg_proyectos/public/
 * ---------------------------------------------------------------
 */

// Ruta absoluta al directorio raíz del proyecto
define('FCPATH', __DIR__ . DIRECTORY_SEPARATOR);

// Ruta al directorio 'app'
$pathsConfig = FCPATH . '../app/Config/Paths.php';

/*
 * ---------------------------------------------------------------
 * BOOTSTRAP DE CODEIGNITER 4
 * ---------------------------------------------------------------
 */
require_once $pathsConfig;
$paths = new Config\Paths();

// Variable DEFINEPATH para el framework
define('ROOTPATH', realpath(FCPATH . '..') . DIRECTORY_SEPARATOR);

// Cargar Composer autoloader
$vendorPath = ROOTPATH . 'vendor/autoload.php';
if (file_exists($vendorPath)) {
    require_once $vendorPath;
} else {
    // Si Composer no está instalado aún, mostrar error amigable
    header('HTTP/1.1 503 Service Unavailable', true, 503);
    echo '<h1>UDG-Proyectos</h1>';
    echo '<p>Error: Las dependencias no están instaladas.</p>';
    echo '<p>Ejecuta: <code>php composer.phar install</code> en la raíz del proyecto.</p>';
    exit(1);
}

// Boot CodeIgniter
$app = Config\Services::codeigniter();
$app->initialize();
$context = is_cli() ? 'php-cli' : 'web';
$app->setContext($context);
$app->run();
