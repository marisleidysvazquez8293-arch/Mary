<?php

namespace App\Filters;

use CodeIgniter\Filters\FilterInterface;
use CodeIgniter\HTTP\RequestInterface;
use CodeIgniter\HTTP\ResponseInterface;

/**
 * AuthFilter — Verifica que el usuario tenga sesión activa.
 * 
 * Si no hay sesión activa redirige a: /auth/login
 * 
 * Uso en Routes.php:
 *   ['filter' => 'auth']
 */
class AuthFilter implements FilterInterface
{
    public function before(RequestInterface $request, $arguments = null)
    {
        if (! session()->get('isLoggedIn')) {
            // Guardar la URL intentada para redirigir después del login
            session()->set('redirect_url', current_url());
            return redirect()->to(base_url('auth/login'))
                             ->with('error', 'Debes iniciar sesión para continuar.');
        }
    }

    public function after(RequestInterface $request, ResponseInterface $response, $arguments = null)
    {
        // No se necesita acción post-respuesta
    }
}
