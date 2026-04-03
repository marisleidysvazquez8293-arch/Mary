<?php

namespace App\Database\Seeds;

use CodeIgniter\Database\Seeder;

/**
 * RolesSeeder — Inserta los roles base del sistema RBAC
 */
class RolesSeeder extends Seeder
{
    public function run(): void
    {
        $roles = [
            ['nombre' => 'superadmin',  'descripcion' => 'Control total del sistema sin restricciones'],
            ['nombre' => 'admin',       'descripcion' => 'Gestión de usuarios, configuración y reportes'],
            ['nombre' => 'coordinador', 'descripcion' => 'Asignación de evaluadores y gestión de proyectos'],
            ['nombre' => 'evaluador',   'descripcion' => 'Revisión y dictamen de proyectos asignados'],
            ['nombre' => 'estudiante',  'descripcion' => 'Envío y seguimiento de proyectos propios'],
            ['nombre' => 'publico',     'descripcion' => 'Acceso de solo lectura al repositorio público'],
        ];

        $now = date('Y-m-d H:i:s');
        foreach ($roles as &$r) {
            $r['created_at'] = $now;
            $r['updated_at'] = $now;
        }

        $this->db->table('roles')->insertBatch($roles);
        echo "  ✓ Roles insertados: " . count($roles) . "\n";
    }
}
