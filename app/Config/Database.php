<?php

namespace Config;

use CodeIgniter\Database\Config;

class Database extends Config
{
    public string $defaultGroup = 'default';

    public array $default = [
        'DSN'          => '',
        'hostname'     => 'localhost',
        'username'     => 'root',
        'password'     => '',
        'database'     => 'udg_proyectos',
        'DBDriver'     => 'MySQLi',
        'DBPrefix'     => '',
        'pConnect'     => false,
        'DBDebug'      => true,
        'charset'      => 'utf8mb4',
        'DBCollat'     => 'utf8mb4_unicode_ci',
        'swapPre'      => '',
        'encrypt'      => false,
        'compress'     => false,
        'strictOn'     => false,
        'failover'     => [],
        'port'         => 3306,
        'numberNative' => false,
    ];

    public function __construct()
    {
        parent::__construct();

        // Sobreescribir con variables del .env si existen
        if (isset($_ENV['database.default.hostname'])) {
            $this->default['hostname'] = $_ENV['database.default.hostname'];
        }
        if (isset($_ENV['database.default.database'])) {
            $this->default['database'] = $_ENV['database.default.database'];
        }
        if (isset($_ENV['database.default.username'])) {
            $this->default['username'] = $_ENV['database.default.username'];
        }
        if (isset($_ENV['database.default.password'])) {
            $this->default['password'] = $_ENV['database.default.password'];
        }
    }
}
