<?php

namespace Config;

use CodeIgniter\Config\BaseConfig;

/**
 * Configuración de rutas para UDG-Proyectos
 * 
 * CONVENCIÓN DE RUTAS POR MÓDULO:
 *   /envio/*         → Módulo 1 — Envío de proyectos
 *   /aprobacion/*    → Módulo 2 — Flujo de aprobación / Evaluación
 *   /repositorio/*   → Módulo 3 — Repositorio público
 *   /admin/*         → Módulo 4 — Administración
 *   /notificaciones/* → Módulo 5 — Notificaciones
 *   /portafolio/*    → Módulo 6 — Portafolio estudiantil
 *   /herramientas/*  → Módulo 7 — Herramientas comunitarias
 *   /social/*        → Módulo 8 — Interacción social
 */

$routes = Services::routes();

// =============================================================
// OPCIONES GLOBALES
// =============================================================
$routes->setDefaultNamespace('App\Controllers');
$routes->setDefaultController('Home');
$routes->setDefaultMethod('index');
$routes->setTranslateURIDashes(false);
$routes->set404Override('App\Controllers\Errors\Error404::index');
$routes->setAutoRoute(false); // Seguridad: solo rutas explícitas

// =============================================================
// RUTAS PÚBLICAS (sin autenticación)
// =============================================================
$routes->get('/', 'Home::index');
$routes->get('/acerca', 'Home::acerca');

// Autenticación
$routes->group('auth', function ($routes) {
    $routes->get('login',           'Auth\LoginController::index',    ['as' => 'login']);
    $routes->post('login',          'Auth\LoginController::procesar');
    $routes->get('registro',        'Auth\RegisterController::index', ['as' => 'registro']);
    $routes->post('registro',       'Auth\RegisterController::procesar');
    $routes->get('logout',          'Auth\LoginController::logout',   ['as' => 'logout']);
    $routes->get('recuperar',       'Auth\LoginController::recuperar');
    $routes->post('recuperar',      'Auth\LoginController::enviarRecuperacion');
    $routes->get('restablecer/(:alphanum)', 'Auth\LoginController::restablecer/$1');
    $routes->post('restablecer',    'Auth\LoginController::procesarRestablecimiento');
});

// Repositorio público (accesible sin login)
$routes->group('repositorio', ['filter' => ''], function ($routes) {
    $routes->get('/',               'Modulo3_Repositorio\RepositorioController::index',   ['as' => 'repositorio']);
    $routes->get('buscar',          'Modulo3_Repositorio\RepositorioController::buscar');
    $routes->get('proyecto/(:num)', 'Modulo3_Repositorio\RepositorioController::ver/$1');
    $routes->get('descargar/(:num)/(:alphanum)', 'Modulo3_Repositorio\RepositorioController::descargar/$1/$2');
    $routes->get('cita/(:num)',     'Modulo3_Repositorio\RepositorioController::cita/$1');
});

// =============================================================
// RUTAS PROTEGIDAS — requieren sesión activa
// =============================================================
$routes->group('', ['filter' => 'auth'], function ($routes) {

    // Dashboard principal (redirige según rol)
    $routes->get('dashboard',       'Home::dashboard',               ['as' => 'dashboard']);

    // --- MÓDULO 1: Envío de proyectos ---
    $routes->group('envio', function ($routes) {
        $routes->get('/',               'Modulo1_Envio\EnvioController::index',     ['as' => 'envio.index']);
        $routes->get('nuevo',           'Modulo1_Envio\EnvioController::nuevo',     ['as' => 'envio.nuevo']);
        $routes->post('guardar',        'Modulo1_Envio\EnvioController::guardar');
        $routes->get('borrador/(:num)', 'Modulo1_Envio\EnvioController::borrador/$1');
        $routes->post('borrador/guardar','Modulo1_Envio\EnvioController::guardarBorrador');
        $routes->get('ver/(:num)',      'Modulo1_Envio\EnvioController::ver/$1');
        $routes->post('archivo/subir',  'Modulo1_Envio\EnvioController::subirArchivo');
        $routes->delete('archivo/(:num)','Modulo1_Envio\EnvioController::eliminarArchivo/$1');
        $routes->get('versiones/(:num)','Modulo1_Envio\EnvioController::versiones/$1');
    });

    // --- MÓDULO 2: Flujo de aprobación + Evaluación ---
    $routes->group('aprobacion', ['filter' => 'role:evaluador,coordinador,admin,superadmin'], function ($routes) {
        $routes->get('/',               'Modulo2_Aprobacion\AprobacionController::panel',     ['as' => 'aprobacion.panel']);
        $routes->get('asignar/(:num)',  'Modulo2_Aprobacion\AprobacionController::asignar/$1');
        $routes->post('asignar',        'Modulo2_Aprobacion\AprobacionController::procesarAsignacion');
        $routes->get('revisar/(:num)',  'Modulo2_Aprobacion\AprobacionController::revisar/$1');
        $routes->post('dictamen',       'Modulo2_Aprobacion\AprobacionController::dictamen');
        $routes->post('comentario',     'Modulo2_Aprobacion\AprobacionController::agregarComentario');
        $routes->get('historial/(:num)','Modulo2_Aprobacion\AprobacionController::historial/$1');
    });

    // --- MÓDULO 4: Administración ---
    $routes->group('admin', ['filter' => 'role:admin,superadmin'], function ($routes) {
        $routes->get('/',               'Modulo4_Admin\AdminController::index',          ['as' => 'admin.index']);
        $routes->get('usuarios',        'Modulo4_Admin\UsuariosController::index',       ['as' => 'admin.usuarios']);
        $routes->get('usuarios/nuevo',  'Modulo4_Admin\UsuariosController::nuevo');
        $routes->post('usuarios/crear', 'Modulo4_Admin\UsuariosController::crear');
        $routes->get('usuarios/(:num)', 'Modulo4_Admin\UsuariosController::editar/$1');
        $routes->post('usuarios/(:num)','Modulo4_Admin\UsuariosController::actualizar/$1');
        $routes->delete('usuarios/(:num)','Modulo4_Admin\UsuariosController::eliminar/$1');
        $routes->get('roles',           'Modulo4_Admin\RolesController::index',          ['as' => 'admin.roles']);
        $routes->get('configuracion',   'Modulo4_Admin\ConfigController::index',         ['as' => 'admin.config']);
        $routes->post('configuracion',  'Modulo4_Admin\ConfigController::guardar');
        $routes->get('logs',            'Modulo4_Admin\LogsController::index',           ['as' => 'admin.logs']);
        $routes->get('respaldos',       'Modulo4_Admin\RespaldosController::index',      ['as' => 'admin.respaldos']);
        $routes->post('respaldos/crear','Modulo4_Admin\RespaldosController::crear');
    });

    // --- MÓDULO 5: Notificaciones ---
    $routes->group('notificaciones', function ($routes) {
        $routes->get('/',               'Modulo5_Notificacion\NotificacionController::index', ['as' => 'notificaciones.index']);
        $routes->post('marcar/(:num)',  'Modulo5_Notificacion\NotificacionController::marcarLeida/$1');
        $routes->post('marcar-todas',   'Modulo5_Notificacion\NotificacionController::marcarTodas');
        $routes->get('configuracion',   'Modulo5_Notificacion\NotificacionController::configuracion');
        $routes->post('configuracion',  'Modulo5_Notificacion\NotificacionController::guardarConfig');
        $routes->get('api/no-leidas',   'Modulo5_Notificacion\NotificacionController::apiNoLeidas'); // AJAX
    });

    // --- MÓDULO 6: Portafolio estudiantil ---
    $routes->group('portafolio', function ($routes) {
        $routes->get('/',               'Modulo6_Portafolio\PortafolioController::index',  ['as' => 'portafolio.index']);
        $routes->get('(:alphanum)',     'Modulo6_Portafolio\PortafolioController::ver/$1', ['as' => 'portafolio.ver']);
        $routes->get('editar',          'Modulo6_Portafolio\PortafolioController::editar');
        $routes->post('actualizar',     'Modulo6_Portafolio\PortafolioController::actualizar');
    });

    // --- MÓDULO 7: Herramientas comunitarias ---
    $routes->group('herramientas', function ($routes) {
        $routes->get('/',               'Modulo7_Herramientas\HerramientasController::index', ['as' => 'herramientas.index']);
        $routes->get('software',        'Modulo7_Herramientas\HerramientasController::software');
        $routes->get('datasets',        'Modulo7_Herramientas\HerramientasController::datasets');
        $routes->post('subir',          'Modulo7_Herramientas\HerramientasController::subir');
    });

    // --- MÓDULO 8: Interacción social ---
    $routes->group('social', function ($routes) {
        $routes->post('votar/(:num)',   'Modulo8_Interaccion\InteraccionController::votar/$1');
        $routes->post('comentar',       'Modulo8_Interaccion\InteraccionController::comentar');
        $routes->get('ranking',         'Modulo8_Interaccion\InteraccionController::ranking', ['as' => 'social.ranking']);
    });
});
