<?php

namespace App\Models;

use App\Models\Base\BaseModel;

/**
 * UserModel — Modelo central de usuarios del sistema
 * 
 * Maneja: autenticación, perfil, roles y estado de cuenta.
 * Usado por múltiples módulos (auth, admin, portafolio).
 */
class UserModel extends BaseModel
{
    protected $table         = 'usuarios';
    protected $primaryKey    = 'id';
    protected $returnType    = 'array';
    protected $useSoftDeletes = true;

    protected $allowedFields = [
        'nombre', 'apellido_paterno', 'apellido_materno',
        'correo', 'password_hash', 'rol_id',
        'numero_control', 'carrera', 'semestre',
        'telefono', 'foto_perfil', 'bio',
        'token_recuperacion', 'token_expira',
        'estatus', 'ultimo_acceso',
    ];

    protected $validationRules = [
        'nombre'   => 'required|min_length[2]|max_length[100]',
        'correo'   => 'required|valid_email|is_unique[usuarios.correo,id,{id}]',
        'rol_id'   => 'required|integer',
    ];

    protected $validationMessages = [
        'correo' => [
            'is_unique' => 'Este correo ya está registrado en el sistema.',
        ],
    ];

    protected $beforeInsert = ['hashPassword'];
    protected $beforeUpdate = ['hashPasswordOnUpdate'];

    // ----------------------------------------------------------------
    // CALLBACKS — Hash de contraseña automático
    // ----------------------------------------------------------------

    protected function hashPassword(array $data): array
    {
        if (isset($data['data']['password_hash'])) {
            $data['data']['password_hash'] = password_hash(
                $data['data']['password_hash'],
                PASSWORD_BCRYPT,
                ['cost' => 12]
            );
        }
        return $data;
    }

    protected function hashPasswordOnUpdate(array $data): array
    {
        // Solo hash si se está actualizando la contraseña
        if (isset($data['data']['password_hash']) && ! empty($data['data']['password_hash'])) {
            $data['data']['password_hash'] = password_hash(
                $data['data']['password_hash'],
                PASSWORD_BCRYPT,
                ['cost' => 12]
            );
        } elseif (isset($data['data']['password_hash'])) {
            // Si viene vacío, eliminarlo para no borrar la contraseña existente
            unset($data['data']['password_hash']);
        }
        return $data;
    }

    // ----------------------------------------------------------------
    // AUTENTICACIÓN
    // ----------------------------------------------------------------

    /**
     * Verificar credenciales de login.
     * 
     * @return array|null Usuario encontrado o null
     */
    public function verificarCredenciales(string $correo, string $password): ?array
    {
        $usuario = $this->where('correo', $correo)
                        ->where('estatus', 'activo')
                        ->first();

        if ($usuario && password_verify($password, $usuario['password_hash'])) {
            // Actualizar último acceso
            $this->update($usuario['id'], ['ultimo_acceso' => date('Y-m-d H:i:s')]);

            // No devolver el hash en la respuesta
            unset($usuario['password_hash']);
            return $usuario;
        }

        return null;
    }

    /**
     * Obtener usuario con su nombre de rol.
     */
    public function getConRol(int $id): ?array
    {
        return $this->select('usuarios.*, roles.nombre as rol_nombre, roles.descripcion as rol_descripcion')
                    ->join('roles', 'roles.id = usuarios.rol_id')
                    ->find($id);
    }

    /**
     * Generar y guardar token de recuperación de contraseña.
     */
    public function generarTokenRecuperacion(string $correo): ?string
    {
        $usuario = $this->where('correo', $correo)->first();
        if (! $usuario) {
            return null;
        }

        $token = bin2hex(random_bytes(32));
        $this->update($usuario['id'], [
            'token_recuperacion' => $token,
            'token_expira'       => date('Y-m-d H:i:s', strtotime('+2 hours')),
        ]);

        return $token;
    }

    /**
     * Verificar token de recuperación (válido y no expirado).
     */
    public function verificarToken(string $token): ?array
    {
        return $this->where('token_recuperacion', $token)
                    ->where('token_expira >=', date('Y-m-d H:i:s'))
                    ->first();
    }

    /**
     * Obtener todos los evaluadores activos.
     */
    public function getEvaluadores(): array
    {
        return $this->select('usuarios.id, usuarios.nombre, usuarios.apellido_paterno, usuarios.correo')
                    ->join('roles', 'roles.id = usuarios.rol_id')
                    ->where('roles.nombre', 'evaluador')
                    ->where('usuarios.estatus', 'activo')
                    ->findAll();
    }
}
