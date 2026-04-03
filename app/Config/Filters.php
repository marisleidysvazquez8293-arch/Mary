<?php

namespace Config;

use CodeIgniter\Config\BaseConfig;

class Filters extends BaseConfig
{
    /**
     * Aliases para los filtros del sistema.
     * Permite usar nombre corto en Routes.php: ['filter' => 'auth']
     */
    public array $aliases = [
        'csrf'     => \CodeIgniter\Filters\CSRF::class,
        'toolbar'  => \CodeIgniter\Filters\DebugToolbar::class,
        'honeypot' => \CodeIgniter\Filters\Honeypot::class,
        'auth'     => \App\Filters\AuthFilter::class,
        'role'     => \App\Filters\RoleFilter::class,
        'guest'    => \App\Filters\GuestFilter::class,
    ];

    /**
     * Filtros aplicados globalmente a TODAS las rutas.
     */
    public array $globals = [
        'before' => [
            'csrf' => ['except' => ['api/*']],
        ],
        'after' => [
            'toolbar',
        ],
    ];

    public array $methods = [];

    /**
     * Filtros por ruta — se definen aquí o en Routes.php con ['filter' => '...']
     */
    public array $filters = [
        'auth' => [
            'before' => [
                'dashboard',
                'envio/*',
                'aprobacion/*',
                'notificaciones/*',
                'portafolio/*',
                'herramientas/*',
                'social/*',
            ],
        ],
        'role:admin,superadmin' => [
            'before' => ['admin/*'],
        ],
        'role:evaluador,coordinador,admin,superadmin' => [
            'before' => ['aprobacion/*'],
        ],
        'guest' => [
            'before' => ['auth/login', 'auth/registro'],
        ],
    ];
}
