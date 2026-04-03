<?php

namespace App\Filters;

use CodeIgniter\Filters\FilterInterface;
use CodeIgniter\HTTP\RequestInterface;
use CodeIgniter\HTTP\ResponseInterface;

/**
 * RoleFilter — Verifica que el usuario tenga el rol requerido (RBAC).
 * 
 * Uso en Routes.php:
 *   ['filter' => 'role:admin,superadmin']
 *   ['filter' => 'role:evaluador,coordinador']
 * 
 * Los roles se pasan como argumento separado por comas.
 */
class RoleFilter implements FilterInterface
{
    public function before(RequestInterface $request, $arguments = null)
    {
        // Asegurar que hay sesión activa primero
        if (! session()->get('isLoggedIn')) {
            return redirect()->to(base_url('auth/login'))
                             ->with('error', 'Debes iniciar sesión para continuar.');
        }

        // Si no se especificaron roles, solo verificar sesión
        if (empty($arguments)) {
            return;
        }

        // Obtener rol del usuario de la sesión
        $userRole = session()->get('user_role');

        // Verificar si el rol del usuario está en la lista permitida
        if (! in_array($userRole, $arguments)) {
            return redirect()->to(base_url('dashboard'))
                             ->with('warning', 'No tienes permisos para acceder a esa sección.');
        }
    }

    public function after(RequestInterface $request, ResponseInterface $response, $arguments = null)
    {
        // No se necesita acción post-respuesta
    }
}
