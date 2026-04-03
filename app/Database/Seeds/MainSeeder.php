<?php

namespace App\Database\Seeds;

use CodeIgniter\Database\Seeder;

/**
 * Seed principal — Carga todos los seeders en orden correcto.
 * 
 * Ejecutar con:
 *   php spark db:seed MainSeeder
 */
class MainSeeder extends Seeder
{
    public function run(): void
    {
        $this->call('RolesSeeder');
        $this->call('CatalogosSeeder');
        $this->call('AdminSeeder');
    }
}
