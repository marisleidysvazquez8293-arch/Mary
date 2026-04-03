<?php

namespace App\Filters;

use CodeIgniter\Filters\FilterInterface;
use CodeIgniter\HTTP\RequestInterface;
use CodeIgniter\HTTP\ResponseInterface;

/**
 * GuestFilter — Redirige usuarios ya autenticados al dashboard.
 * 
 * Se aplica en rutas de login y registro para evitar que
 * un usuario con sesión activa vea esas páginas.
 */
class GuestFilter implements FilterInterface
{
    public function before(RequestInterface $request, $arguments = null)
    {
        if (session()->get('isLoggedIn')) {
            return redirect()->to(base_url('dashboard'));
        }
    }

    public function after(RequestInterface $request, ResponseInterface $response, $arguments = null)
    {
        // No se necesita acción post-respuesta
    }
}
