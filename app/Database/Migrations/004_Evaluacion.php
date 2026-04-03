<?php

namespace App\Database\Migrations;

use CodeIgniter\Database\Migration;

/**
 * Migración 004 — Evaluación y Comité
 * 
 * DEPENDE DE: 002_Usuarios, 003_Proyectos
 */
class Evaluacion extends Migration
{
    public function up(): void
    {
        // ----- ASIGNACIONES evaluador-proyecto -----
        $this->forge->addField([
            'id'               => ['type' => 'INT', 'unsigned' => true, 'auto_increment' => true],
            'proyecto_id'      => ['type' => 'INT', 'unsigned' => true],
            'evaluador_id'     => ['type' => 'INT', 'unsigned' => true],
            'asignado_por'     => ['type' => 'INT', 'unsigned' => true],
            'fecha_limite'     => ['type' => 'DATE', 'null' => true],
            'estatus'          => ['type' => 'ENUM', 'constraint' => ['pendiente','en_proceso','completada'], 'default' => 'pendiente'],
            'created_at'       => ['type' => 'DATETIME', 'null' => true],
            'updated_at'       => ['type' => 'DATETIME', 'null' => true],
        ]);
        $this->forge->addKey('id', true);
        $this->forge->addKey(['proyecto_id', 'evaluador_id']);
        $this->forge->addForeignKey('proyecto_id',  'proyectos', 'id', 'CASCADE', 'CASCADE');
        $this->forge->addForeignKey('evaluador_id', 'usuarios',  'id', 'CASCADE', 'CASCADE');
        $this->forge->addForeignKey('asignado_por', 'usuarios',  'id', 'CASCADE', 'CASCADE');
        $this->forge->createTable('asignaciones');

        // ----- REVISIONES / DICTÁMENES -----
        $this->forge->addField([
            'id'              => ['type' => 'INT', 'unsigned' => true, 'auto_increment' => true],
            'asignacion_id'   => ['type' => 'INT', 'unsigned' => true],
            'dictamen'        => ['type' => 'ENUM',
                                  'constraint' => ['aprobado','aprobado_correcciones','rechazado'],
                                  'null' => true],
            'notas_publicas'  => ['type' => 'TEXT', 'null' => true],
            'notas_privadas'  => ['type' => 'TEXT', 'null' => true],
            'fecha_dictamen'  => ['type' => 'DATETIME', 'null' => true],
            'created_at'      => ['type' => 'DATETIME', 'null' => true],
            'updated_at'      => ['type' => 'DATETIME', 'null' => true],
        ]);
        $this->forge->addKey('id', true);
        $this->forge->addForeignKey('asignacion_id', 'asignaciones', 'id', 'CASCADE', 'CASCADE');
        $this->forge->createTable('revisiones');

        // ----- COMENTARIOS sobre documentos -----
        $this->forge->addField([
            'id'            => ['type' => 'INT', 'unsigned' => true, 'auto_increment' => true],
            'revision_id'   => ['type' => 'INT', 'unsigned' => true],
            'archivo_id'    => ['type' => 'INT', 'unsigned' => true, 'null' => true],
            'evaluador_id'  => ['type' => 'INT', 'unsigned' => true],
            'texto'         => ['type' => 'TEXT'],
            'pagina_ref'    => ['type' => 'INT', 'null' => true],
            'linea_ref'     => ['type' => 'INT', 'null' => true],
            'resuelto'      => ['type' => 'TINYINT', 'constraint' => 1, 'default' => 0],
            'created_at'    => ['type' => 'DATETIME', 'null' => true],
        ]);
        $this->forge->addKey('id', true);
        $this->forge->addForeignKey('revision_id',  'revisiones',        'id', 'CASCADE', 'CASCADE');
        $this->forge->addForeignKey('archivo_id',   'archivos_proyecto', 'id', 'SET NULL', 'SET NULL');
        $this->forge->addForeignKey('evaluador_id', 'usuarios',          'id', 'CASCADE', 'CASCADE');
        $this->forge->createTable('comentarios_revision');
    }

    public function down(): void
    {
        $this->forge->dropTable('comentarios_revision', true);
        $this->forge->dropTable('revisiones',           true);
        $this->forge->dropTable('asignaciones',         true);
    }
}
