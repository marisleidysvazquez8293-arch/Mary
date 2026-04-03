<?php

namespace App\Controllers;

use CodeIgniter\Controller;
use CodeIgniter\HTTP\CLIRequest;
use CodeIgniter\HTTP\IncomingRequest;
use CodeIgniter\HTTP\RequestInterface;
use CodeIgniter\HTTP\ResponseInterface;
use Psr\Log\LoggerInterface;

/**
 * BaseController — Controlador base de UDG-Proyectos
 * 
 * Todos los controladores del sistema DEBEN extender este BaseController.
 * 
 * Proporciona:
 * - Helpers cargados globalmente
 * - Datos comunes de sesión para las vistas
 * - Método de respuesta JSON para APIs internas
 * - Método de redirección con mensaje flash
 */
abstract class BaseController extends Controller
{
    protected CLIRequest|IncomingRequest $request;

    // Datos disponibles en TODAS las vistas del sistema
    protected array $viewData = [];

    // Helpers cargados automáticamente en todo el sistema
    protected $helpers = ['url', 'form', 'app', 'file', 'format'];

    public function initController(
        RequestInterface $request,
        ResponseInterface $response,
        LoggerInterface $logger
    ): void {
        parent::initController($request, $response, $logger);

        // Cargar datos de sesión para las vistas
        $this->viewData = [
            'isLoggedIn'  => session()->get('isLoggedIn') ?? false,
            'currentUser' => session()->get('user') ?? null,
            'userRole'    => session()->get('user_role') ?? 'publico',
            'userId'      => session()->get('user_id') ?? null,
            'pageTitle'   => 'UDG-Proyectos',
        ];
    }

    // ----------------------------------------------------------------
    // Métodos utilitarios para todos los controladores
    // ----------------------------------------------------------------

    /**
     * Renderizar una vista con el layout principal.
     * 
     * @param string $view     Ruta de la vista (relativa a app/Views/)
     * @param array  $data     Datos adicionales para la vista
     * @param string $layout   Layout a usar (main|auth|admin)
     */
    protected function render(
        string $view,
        array $data = [],
        string $layout = 'main'
    ): string {
        $data = array_merge($this->viewData, $data);
        $data['content_view'] = $view;

        return view("layouts/{$layout}", $data);
    }

    /**
     * Respuesta JSON estándar para endpoints AJAX
     */
    protected function jsonResponse(
        bool $success,
        string $message = '',
        array $data = [],
        int $statusCode = 200
    ): \CodeIgniter\HTTP\Response {
        return $this->response
            ->setStatusCode($statusCode)
            ->setJSON([
                'success' => $success,
                'message' => $message,
                'data'    => $data,
            ]);
    }

    /**
     * Redireccionar con mensaje flash estandarizado
     * 
     * @param string $to   Ruta destino (nombre de ruta o URL)
     * @param string $type success|error|warning|info
     */
    protected function redirectWithMessage(
        string $to,
        string $type,
        string $message
    ): \CodeIgniter\HTTP\RedirectResponse {
        return redirect()->to(base_url($to))->with($type, $message);
    }

    /**
     * Obtener datos del usuario actual de la sesión
     */
    protected function getCurrentUser(): ?array
    {
        return session()->get('user');
    }

    /**
     * Obtener ID del usuario actual
     */
    protected function getCurrentUserId(): ?int
    {
        return session()->get('user_id');
    }

    /**
     * Verificar si el usuario actual tiene un rol específico
     */
    protected function hasRole(string|array $roles): bool
    {
        $userRole = session()->get('user_role');
        if (is_array($roles)) {
            return in_array($userRole, $roles);
        }
        return $userRole === $roles;
    }
}
