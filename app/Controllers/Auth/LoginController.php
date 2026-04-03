<?php

namespace App\Controllers\Auth;

use App\Controllers\BaseController;
use App\Models\UserModel;

/**
 * LoginController — Autenticación de usuarios
 * 
 * Rutas manejadas:
 *   GET  /auth/login       → Formulario de login
 *   POST /auth/login       → Procesar login
 *   GET  /auth/logout      → Cerrar sesión
 *   GET  /auth/recuperar   → Formulario recuperación
 *   POST /auth/recuperar   → Enviar email de recuperación
 */
class LoginController extends BaseController
{
    protected UserModel $userModel;

    public function __construct()
    {
        $this->userModel = new UserModel();
    }

    /**
     * GET /auth/login — Mostrar formulario
     */
    public function index(): string
    {
        return $this->render('auth/login', [
            'pageTitle' => 'Iniciar Sesión — UDG-Proyectos',
        ], 'auth');
    }

    /**
     * POST /auth/login — Procesar credenciales
     */
    public function procesar()
    {
        // Validar campos del formulario
        if (! $this->validate([
            'correo'   => 'required|valid_email',
            'password' => 'required|min_length[6]',
        ])) {
            return redirect()->back()
                             ->withInput()
                             ->with('errors', $this->validator->getErrors());
        }

        $correo   = $this->request->getPost('correo');
        $password = $this->request->getPost('password');

        // Verificar credenciales en la base de datos
        $usuario = $this->userModel->verificarCredenciales($correo, $password);

        if (! $usuario) {
            return redirect()->back()
                             ->withInput()
                             ->with('error', 'Correo o contraseña incorrectos.');
        }

        // Verificar cuenta activa
        if ($usuario['estatus'] !== 'activo') {
            return redirect()->back()
                             ->with('error', 'Tu cuenta está desactivada. Contáctate con administración.');
        }

        // Crear sesión
        $this->crearSesion($usuario);

        // Redirigir a URL original o al dashboard
        $redirectUrl = session()->getFlashdata('redirect_url') ?? base_url('dashboard');
        return redirect()->to($redirectUrl)->with('success', '¡Bienvenido, ' . $usuario['nombre'] . '!');
    }

    /**
     * GET /auth/logout — Destruir sesión
     */
    public function logout()
    {
        session()->destroy();
        return redirect()->to(base_url('auth/login'))
                         ->with('info', 'Has cerrado sesión correctamente.');
    }

    /**
     * GET /auth/recuperar — Formulario de recuperación
     */
    public function recuperar(): string
    {
        return $this->render('auth/recuperar', [
            'pageTitle' => 'Recuperar Contraseña — UDG-Proyectos',
        ], 'auth');
    }

    /**
     * POST /auth/recuperar — Enviar email de recuperación
     */
    public function enviarRecuperacion()
    {
        if (! $this->validate(['correo' => 'required|valid_email'])) {
            return redirect()->back()->with('error', 'Ingresa un correo válido.');
        }

        $correo = $this->request->getPost('correo');
        $token  = $this->userModel->generarTokenRecuperacion($correo);

        if ($token) {
            // Enviar email (usa Library EmailNotification)
            $emailLib = new \App\Libraries\EmailNotification();
            $emailLib->enviarRecuperacion($correo, $token);
        }

        // Siempre mostrar el mismo mensaje (seguridad — no revelar si existe el correo)
        return redirect()->to(base_url('auth/login'))
                         ->with('info', 'Si el correo está registrado, recibirás instrucciones en breve.');
    }

    /**
     * GET /auth/restablecer/:token
     */
    public function restablecer(string $token): string
    {
        $usuario = $this->userModel->verificarToken($token);
        if (! $usuario) {
            return redirect()->to(base_url('auth/login'))
                             ->with('error', 'El enlace de recuperación es inválido o ha expirado.');
        }

        return $this->render('auth/restablecer', [
            'pageTitle' => 'Nueva Contraseña — UDG-Proyectos',
            'token'     => $token,
        ], 'auth');
    }

    /**
     * POST /auth/restablecer — Actualizar contraseña
     */
    public function procesarRestablecimiento()
    {
        if (! $this->validate([
            'token'            => 'required',
            'password'         => 'required|min_length[8]',
            'password_confirm' => 'required|matches[password]',
        ])) {
            return redirect()->back()->withInput()
                             ->with('errors', $this->validator->getErrors());
        }

        $token    = $this->request->getPost('token');
        $password = $this->request->getPost('password');
        $usuario  = $this->userModel->verificarToken($token);

        if (! $usuario) {
            return redirect()->to(base_url('auth/login'))
                             ->with('error', 'El enlace ha expirado. Solicita uno nuevo.');
        }

        $this->userModel->update($usuario['id'], [
            'password_hash'      => $password, // El modelo lo hasheará automáticamente
            'token_recuperacion' => null,
            'token_expira'       => null,
        ]);

        return redirect()->to(base_url('auth/login'))
                         ->with('success', 'Contraseña actualizada correctamente. Ya puedes iniciar sesión.');
    }

    // ----------------------------------------------------------------
    // Métodos privados
    // ----------------------------------------------------------------

    private function crearSesion(array $usuario): void
    {
        session()->set([
            'isLoggedIn' => true,
            'user_id'    => $usuario['id'],
            'user_role'  => $usuario['rol_nombre'] ?? 'estudiante',
            'user'       => [
                'id'               => $usuario['id'],
                'nombre'           => $usuario['nombre'],
                'apellido_paterno' => $usuario['apellido_paterno'],
                'correo'           => $usuario['correo'],
                'foto_perfil'      => $usuario['foto_perfil'] ?? null,
                'rol_id'           => $usuario['rol_id'],
                'rol_nombre'       => $usuario['rol_nombre'] ?? 'estudiante',
            ],
        ]);
    }
}
