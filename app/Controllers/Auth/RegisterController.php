<?php

namespace App\Controllers\Auth;

use App\Controllers\BaseController;
use App\Models\UserModel;
use App\Models\RoleModel;

/**
 * RegisterController — Registro de nuevos usuarios
 * 
 * Rutas manejadas:
 *   GET  /auth/registro → Formulario de registro
 *   POST /auth/registro → Procesar registro
 */
class RegisterController extends BaseController
{
    protected UserModel $userModel;
    protected RoleModel $roleModel;

    public function __construct()
    {
        $this->userModel = new UserModel();
        $this->roleModel = new RoleModel();
    }

    /**
     * GET /auth/registro
     */
    public function index(): string
    {
        return $this->render('auth/registro', [
            'pageTitle' => 'Crear Cuenta — UDG-Proyectos',
        ], 'auth');
    }

    /**
     * POST /auth/registro
     */
    public function procesar()
    {
        if (! $this->validate([
            'nombre'              => 'required|min_length[2]|max_length[100]',
            'apellido_paterno'    => 'required|min_length[2]|max_length[100]',
            'apellido_materno'    => 'permit_empty|max_length[100]',
            'correo'              => 'required|valid_email|is_unique[usuarios.correo]',
            'numero_control'      => 'required|min_length[6]|max_length[20]',
            'password'            => 'required|min_length[8]',
            'password_confirm'    => 'required|matches[password]',
        ], [
            'correo' => ['is_unique' => 'Este correo ya está registrado.'],
            'password_confirm' => ['matches' => 'Las contraseñas no coinciden.'],
        ])) {
            return redirect()->back()
                             ->withInput()
                             ->with('errors', $this->validator->getErrors());
        }

        // Rol por defecto: estudiante
        $rolEstudiante = $this->roleModel->getRolPorNombre('estudiante');

        $datos = [
            'nombre'           => trim($this->request->getPost('nombre')),
            'apellido_paterno' => trim($this->request->getPost('apellido_paterno')),
            'apellido_materno' => trim($this->request->getPost('apellido_materno') ?? ''),
            'correo'           => strtolower(trim($this->request->getPost('correo'))),
            'numero_control'   => trim($this->request->getPost('numero_control')),
            'password_hash'    => $this->request->getPost('password'), // Se hasheará en el modelo
            'rol_id'           => $rolEstudiante['id'] ?? 5,
            'estatus'          => 'activo',
        ];

        if (! $this->userModel->insert($datos)) {
            return redirect()->back()
                             ->withInput()
                             ->with('error', 'Error al crear la cuenta. Intenta de nuevo.');
        }

        // Enviar email de bienvenida
        $emailLib = new \App\Libraries\EmailNotification();
        $emailLib->enviarBienvenida($datos['correo'], $datos['nombre']);

        return redirect()->to(base_url('auth/login'))
                         ->with('success', '¡Cuenta creada! Ya puedes iniciar sesión.');
    }
}
