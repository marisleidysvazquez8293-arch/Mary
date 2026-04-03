<?php

namespace App\Database\Migrations;

use CodeIgniter\Database\Migration;

/**
 * Migración 005 — Notificaciones y Sistema de Logs
 * 
 * DEPENDE DE: 002_Usuarios
 */
class Notificaciones extends Migration
{
    public function up(): void
    {
        // ----- NOTIFICACIONES INTERNAS -----
        $this->forge->addField([
            'id'          => ['type' => 'INT', 'unsigned' => true, 'auto_increment' => true],
            'usuario_id'  => ['type' => 'INT', 'unsigned' => true],
            'titulo'      => ['type' => 'VARCHAR', 'constraint' => 200],
            'mensaje'     => ['type' => 'TEXT'],
            'tipo'        => ['type' => 'ENUM', 'constraint' => ['info','success','warning','danger'], 'default' => 'info'],
            'url_accion'  => ['type' => 'VARCHAR', 'constraint' => 500, 'null' => true],
            'leida'       => ['type' => 'TINYINT', 'constraint' => 1, 'default' => 0],
            'created_at'  => ['type' => 'DATETIME', 'null' => true],
        ]);
        $this->forge->addKey('id', true);
        $this->forge->addKey(['usuario_id', 'leida']);
        $this->forge->addForeignKey('usuario_id', 'usuarios', 'id', 'CASCADE', 'CASCADE');
        $this->forge->createTable('notificaciones');

        // ----- CONFIGURACIÓN DE NOTIFICACIONES -----
        $this->forge->addField([
            'id'          => ['type' => 'INT', 'unsigned' => true, 'auto_increment' => true],
            'usuario_id'  => ['type' => 'INT', 'unsigned' => true],
            'tipo_evento' => ['type' => 'VARCHAR', 'constraint' => 100],
            'canal_email' => ['type' => 'TINYINT', 'constraint' => 1, 'default' => 1],
            'canal_interno'=> ['type' => 'TINYINT', 'constraint' => 1, 'default' => 1],
        ]);
        $this->forge->addKey('id', true);
        $this->forge->addKey(['usuario_id', 'tipo_evento'], false, 'udx_notif_config');
        $this->forge->addForeignKey('usuario_id', 'usuarios', 'id', 'CASCADE', 'CASCADE');
        $this->forge->createTable('config_notificaciones');

        // ----- LOGS DE SISTEMA -----
        $this->forge->addField([
            'id'          => ['type' => 'INT', 'unsigned' => true, 'auto_increment' => true],
            'usuario_id'  => ['type' => 'INT', 'unsigned' => true, 'null' => true],
            'accion'      => ['type' => 'VARCHAR', 'constraint' => 100],
            'tabla'       => ['type' => 'VARCHAR', 'constraint' => 100, 'null' => true],
            'registro_id' => ['type' => 'INT', 'unsigned' => true, 'null' => true],
            'descripcion' => ['type' => 'TEXT', 'null' => true],
            'ip'          => ['type' => 'VARCHAR', 'constraint' => 45, 'null' => true],
            'user_agent'  => ['type' => 'TEXT', 'null' => true],
            'created_at'  => ['type' => 'DATETIME', 'null' => true],
        ]);
        $this->forge->addKey('id', true);
        $this->forge->addKey('usuario_id');
        $this->forge->addKey('created_at');
        $this->forge->createTable('system_logs');
    }

    public function down(): void
    {
        $this->forge->dropTable('system_logs',          true);
        $this->forge->dropTable('config_notificaciones', true);
        $this->forge->dropTable('notificaciones',        true);
    }
}
