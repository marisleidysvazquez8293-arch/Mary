<?php

namespace App\Database\Migrations;

use CodeIgniter\Database\Migration;

/**
 * Migración 001 — Catálogos base del sistema
 * 
 * Crea las tablas:
 *   - roles
 *   - permisos
 *   - roles_permisos
 *   - areas
 *   - tipos_proyecto
 * 
 * EJECUTAR PRIMERO: estas tablas tienen las dependencias base.
 */
class Catalogos extends Migration
{
    public function up(): void
    {
        // ----- ROLES -----
        $this->forge->addField([
            'id'          => ['type' => 'INT', 'unsigned' => true, 'auto_increment' => true],
            'nombre'      => ['type' => 'VARCHAR', 'constraint' => 50, 'unique' => true],
            'descripcion' => ['type' => 'VARCHAR', 'constraint' => 200, 'null' => true],
            'created_at'  => ['type' => 'DATETIME', 'null' => true],
            'updated_at'  => ['type' => 'DATETIME', 'null' => true],
        ]);
        $this->forge->addKey('id', true);
        $this->forge->createTable('roles');

        // ----- PERMISOS -----
        $this->forge->addField([
            'id'          => ['type' => 'INT', 'unsigned' => true, 'auto_increment' => true],
            'nombre'      => ['type' => 'VARCHAR', 'constraint' => 100, 'unique' => true],
            'descripcion' => ['type' => 'VARCHAR', 'constraint' => 200, 'null' => true],
        ]);
        $this->forge->addKey('id', true);
        $this->forge->createTable('permisos');

        // ----- ROLES_PERMISOS (tabla pivote) -----
        $this->forge->addField([
            'rol_id'     => ['type' => 'INT', 'unsigned' => true],
            'permiso_id' => ['type' => 'INT', 'unsigned' => true],
        ]);
        $this->forge->addKey(['rol_id', 'permiso_id'], true);
        $this->forge->addForeignKey('rol_id',     'roles',    'id', 'CASCADE', 'CASCADE');
        $this->forge->addForeignKey('permiso_id', 'permisos', 'id', 'CASCADE', 'CASCADE');
        $this->forge->createTable('roles_permisos');

        // ----- ÁREAS DE CONOCIMIENTO -----
        $this->forge->addField([
            'id'          => ['type' => 'INT', 'unsigned' => true, 'auto_increment' => true],
            'nombre'      => ['type' => 'VARCHAR', 'constraint' => 150],
            'descripcion' => ['type' => 'TEXT', 'null' => true],
            'activa'      => ['type' => 'TINYINT', 'constraint' => 1, 'default' => 1],
        ]);
        $this->forge->addKey('id', true);
        $this->forge->createTable('areas');

        // ----- TIPOS DE PROYECTO -----
        $this->forge->addField([
            'id'     => ['type' => 'INT', 'unsigned' => true, 'auto_increment' => true],
            'nombre' => ['type' => 'VARCHAR', 'constraint' => 100],
        ]);
        $this->forge->addKey('id', true);
        $this->forge->createTable('tipos_proyecto');
    }

    public function down(): void
    {
        $this->forge->dropTable('roles_permisos', true);
        $this->forge->dropTable('permisos', true);
        $this->forge->dropTable('roles', true);
        $this->forge->dropTable('areas', true);
        $this->forge->dropTable('tipos_proyecto', true);
    }
}
