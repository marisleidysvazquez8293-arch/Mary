<?php

namespace App\Database\Migrations;

use CodeIgniter\Database\Migration;

/**
 * Migración 002 — Tabla de usuarios
 * 
 * DEPENDE DE: 001_Catalogos (tabla roles)
 */
class Usuarios extends Migration
{
    public function up(): void
    {
        $this->forge->addField([
            'id'                  => ['type' => 'INT', 'unsigned' => true, 'auto_increment' => true],
            'nombre'              => ['type' => 'VARCHAR', 'constraint' => 100],
            'apellido_paterno'    => ['type' => 'VARCHAR', 'constraint' => 100],
            'apellido_materno'    => ['type' => 'VARCHAR', 'constraint' => 100, 'null' => true],
            'correo'              => ['type' => 'VARCHAR', 'constraint' => 191, 'unique' => true],
            'password_hash'       => ['type' => 'VARCHAR', 'constraint' => 255],
            'rol_id'              => ['type' => 'INT', 'unsigned' => true],
            'numero_control'      => ['type' => 'VARCHAR', 'constraint' => 30, 'null' => true],
            'carrera'             => ['type' => 'VARCHAR', 'constraint' => 150, 'null' => true],
            'semestre'            => ['type' => 'TINYINT', 'null' => true],
            'telefono'            => ['type' => 'VARCHAR', 'constraint' => 20, 'null' => true],
            'foto_perfil'         => ['type' => 'VARCHAR', 'constraint' => 255, 'null' => true],
            'bio'                 => ['type' => 'TEXT', 'null' => true],
            'token_recuperacion'  => ['type' => 'VARCHAR', 'constraint' => 100, 'null' => true],
            'token_expira'        => ['type' => 'DATETIME', 'null' => true],
            'estatus'             => ['type' => 'ENUM', 'constraint' => ['activo','inactivo','suspendido'], 'default' => 'activo'],
            'ultimo_acceso'       => ['type' => 'DATETIME', 'null' => true],
            'created_at'          => ['type' => 'DATETIME', 'null' => true],
            'updated_at'          => ['type' => 'DATETIME', 'null' => true],
            'deleted_at'          => ['type' => 'DATETIME', 'null' => true],
        ]);
        $this->forge->addKey('id', true);
        $this->forge->addKey('correo');
        $this->forge->addKey('rol_id');
        $this->forge->addForeignKey('rol_id', 'roles', 'id', 'RESTRICT', 'RESTRICT');
        $this->forge->createTable('usuarios');
    }

    public function down(): void
    {
        $this->forge->dropTable('usuarios', true);
    }
}
