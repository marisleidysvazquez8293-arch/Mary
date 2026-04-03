<?php

namespace App\Controllers;

use App\Controllers\BaseController;

/**
 * Home — Controlador principal y dashboard
 */
class Home extends BaseController
{
    /**
     * GET / — Página de inicio pública
     */
    public function index(): string
    {
        // Redirigir usuarios logueados al dashboard
        if (session()->get('isLoggedIn')) {
            return redirect()->to(base_url('dashboard'));
        }

        return $this->render('home/index', [
            'pageTitle' => 'UDG-Proyectos — Sistema de Tesis y Proyectos',
        ], 'main');
    }

    /**
     * GET /dashboard — Panel principal (con roles)
     */
    public function dashboard(): string
    {
        $rol = session()->get('user_role');

        // El layout del dashboard varía según el rol
        $layout = in_array($rol, ['admin', 'superadmin']) ? 'admin' : 'main';

        return $this->render("home/dashboard_{$rol}", [
            'pageTitle' => 'Dashboard — UDG-Proyectos',
        ], $layout);
    }

    /**
     * GET /acerca — Página informativa
     */
    public function acerca(): string
    {
        return $this->render('home/acerca', [
            'pageTitle' => 'Acerca del Sistema — UDG-Proyectos',
        ]);
    }
}
