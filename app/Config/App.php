<?php

namespace Config;

use CodeIgniter\Config\BaseConfig;

class App extends BaseConfig
{
    // --------------------------------------------------------------------
    // URL
    // --------------------------------------------------------------------
    public string $baseURL = 'http://localhost/udg_proyectos/public/';
    public string $indexPage = '';

    // --------------------------------------------------------------------
    // Localización
    // --------------------------------------------------------------------
    public string $defaultLocale    = 'es';
    public bool   $negotiateLocale  = false;
    public array  $supportedLocales = ['es', 'en'];
    public string $timezone         = 'America/Mexico_City';
    public string $charset          = 'UTF-8';

    // --------------------------------------------------------------------
    // URI
    // --------------------------------------------------------------------
    public bool $forceGlobalSecureRequests = false;
    public string $proxyIPs = '';

    // --------------------------------------------------------------------
    // Cookies
    // --------------------------------------------------------------------
    public string $cookiePrefix   = 'udg_';
    public string $cookieDomain   = '';
    public string $cookiePath     = '/';
    public bool   $cookieSecure   = false;
    public bool   $cookieHTTPOnly = false;
    public string $cookieSameSite = 'Lax';

    // --------------------------------------------------------------------
    // Seguridad
    // --------------------------------------------------------------------
    public string $salt = 'UDG-Proyectos-2024-SecretSalt!';
}
