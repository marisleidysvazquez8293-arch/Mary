<?php

namespace App\Database\Seeds;

use CodeIgniter\Database\Seeder;

/**
 * AdminSeeder — Crea el usuario superadmin inicial del sistema
 * 
 * IMPORTANTE: Cambia la contraseña inmediatamente después del primer login.
 * Credenciales por defecto:
 *   Email:    admin@udg.mx
 *   Password: Admin2024!
 */
class AdminSeeder extends Seeder
{
    public function run(): void
    {
        // Obtener ID del rol superadmin
        $rol = $this->db->table('roles')->where('nombre', 'superadmin')->get()->getRowArray();
        if (! $rol) {
            echo "  ✗ ERROR: Ejecuta RolesSeeder primero.\n";
            return;
        }

        $admin = [
            'nombre'           => 'Administrador',
            'apellido_paterno' => 'UDG',
            'apellido_materno' => 'Proyectos',
            'correo'           => 'admin@udg.mx',
            'password_hash'    => password_hash('Admin2024!', PASSWORD_BCRYPT, ['cost' => 12]),
            'rol_id'           => $rol['id'],
            'estatus'          => 'activo',
            'created_at'       => date('Y-m-d H:i:s'),
            'updated_at'       => date('Y-m-d H:i:s'),
        ];

        // Verificar que no exista antes de insertar
        $existe = $this->db->table('usuarios')->where('correo', 'admin@udg.mx')->get()->getNumRows();
        if ($existe === 0) {
            $this->db->table('usuarios')->insert($admin);
            echo "  ✓ Superadmin creado: admin@udg.mx / Admin2024!\n";
            echo "  ⚠  CAMBIA LA CONTRASEÑA DESPUÉS DEL PRIMER LOGIN\n";
        } else {
            echo "  ! Superadmin ya existe, se omitió.\n";
        }
    }
}
