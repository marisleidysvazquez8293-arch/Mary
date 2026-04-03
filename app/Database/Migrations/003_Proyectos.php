<?php

namespace App\Database\Migrations;

use CodeIgniter\Database\Migration;

/**
 * Migración 003 — Proyectos, Archivos, Versiones y Borradores
 * 
 * DEPENDE DE: 001_Catalogos, 002_Usuarios
 */
class Proyectos extends Migration
{
    public function up(): void
    {
        // ----- PROYECTOS -----
        $this->forge->addField([
            'id'                  => ['type' => 'INT', 'unsigned' => true, 'auto_increment' => true],
            'identificador_unico' => ['type' => 'VARCHAR', 'constraint' => 30, 'unique' => true],
            'titulo'              => ['type' => 'VARCHAR', 'constraint' => 500],
            'resumen'             => ['type' => 'TEXT'],
            'palabras_clave'      => ['type' => 'VARCHAR', 'constraint' => 500, 'null' => true],
            'area_id'             => ['type' => 'INT', 'unsigned' => true, 'null' => true],
            'tipo_id'             => ['type' => 'INT', 'unsigned' => true, 'null' => true],
            'autor_id'            => ['type' => 'INT', 'unsigned' => true],
            'asesor_id'           => ['type' => 'INT', 'unsigned' => true, 'null' => true],
            'estatus'             => ['type' => 'ENUM',
                                      'constraint' => ['borrador','enviado','en_revision','correcciones','aprobado','rechazado','publicado'],
                                      'default' => 'borrador'],
            'anio_generacion'     => ['type' => 'YEAR', 'null' => true],
            'institucion'         => ['type' => 'VARCHAR', 'constraint' => 200, 'default' => 'Universidad de Guadalajara'],
            'departamento'        => ['type' => 'VARCHAR', 'constraint' => 200, 'null' => true],
            'url_repositorio'     => ['type' => 'VARCHAR', 'constraint' => 500, 'null' => true],
            'doi'                 => ['type' => 'VARCHAR', 'constraint' => 200, 'null' => true],
            'visitas'             => ['type' => 'INT', 'unsigned' => true, 'default' => 0],
            'descargas'           => ['type' => 'INT', 'unsigned' => true, 'default' => 0],
            'created_at'          => ['type' => 'DATETIME', 'null' => true],
            'updated_at'          => ['type' => 'DATETIME', 'null' => true],
            'deleted_at'          => ['type' => 'DATETIME', 'null' => true],
        ]);
        $this->forge->addKey('id', true);
        $this->forge->addKey('estatus');
        $this->forge->addKey('autor_id');
        $this->forge->addForeignKey('autor_id', 'usuarios', 'id', 'CASCADE', 'CASCADE');
        $this->forge->addForeignKey('area_id',  'areas',    'id', 'SET NULL', 'SET NULL');
        $this->forge->addForeignKey('tipo_id',  'tipos_proyecto', 'id', 'SET NULL', 'SET NULL');
        $this->forge->createTable('proyectos');

        // ----- ARCHIVOS DEL PROYECTO -----
        $this->forge->addField([
            'id'               => ['type' => 'INT', 'unsigned' => true, 'auto_increment' => true],
            'proyecto_id'      => ['type' => 'INT', 'unsigned' => true],
            'nombre_original'  => ['type' => 'VARCHAR', 'constraint' => 255],
            'ruta'             => ['type' => 'VARCHAR', 'constraint' => 500],
            'tipo_mime'        => ['type' => 'VARCHAR', 'constraint' => 100],
            'tamano_bytes'     => ['type' => 'BIGINT', 'unsigned' => true],
            'version'          => ['type' => 'TINYINT', 'unsigned' => true, 'default' => 1],
            'es_principal'     => ['type' => 'TINYINT', 'constraint' => 1, 'default' => 0],
            'created_at'       => ['type' => 'DATETIME', 'null' => true],
        ]);
        $this->forge->addKey('id', true);
        $this->forge->addKey('proyecto_id');
        $this->forge->addForeignKey('proyecto_id', 'proyectos', 'id', 'CASCADE', 'CASCADE');
        $this->forge->createTable('archivos_proyecto');

        // ----- VERSIONES -----
        $this->forge->addField([
            'id'           => ['type' => 'INT', 'unsigned' => true, 'auto_increment' => true],
            'proyecto_id'  => ['type' => 'INT', 'unsigned' => true],
            'numero'       => ['type' => 'TINYINT', 'unsigned' => true],
            'descripcion'  => ['type' => 'TEXT', 'null' => true],
            'usuario_id'   => ['type' => 'INT', 'unsigned' => true],
            'created_at'   => ['type' => 'DATETIME', 'null' => true],
        ]);
        $this->forge->addKey('id', true);
        $this->forge->addForeignKey('proyecto_id', 'proyectos', 'id', 'CASCADE', 'CASCADE');
        $this->forge->addForeignKey('usuario_id',  'usuarios',  'id', 'CASCADE', 'CASCADE');
        $this->forge->createTable('versiones');

        // ----- BORRADORES -----
        $this->forge->addField([
            'id'          => ['type' => 'INT', 'unsigned' => true, 'auto_increment' => true],
            'proyecto_id' => ['type' => 'INT', 'unsigned' => true, 'unique' => true],
            'datos_json'  => ['type' => 'JSON'],
            'updated_at'  => ['type' => 'DATETIME', 'null' => true],
        ]);
        $this->forge->addKey('id', true);
        $this->forge->addForeignKey('proyecto_id', 'proyectos', 'id', 'CASCADE', 'CASCADE');
        $this->forge->createTable('borradores');

        // ----- HISTORIAL DE FLUJO -----
        $this->forge->addField([
            'id'               => ['type' => 'INT', 'unsigned' => true, 'auto_increment' => true],
            'proyecto_id'      => ['type' => 'INT', 'unsigned' => true],
            'estado_anterior'  => ['type' => 'VARCHAR', 'constraint' => 50],
            'estado_nuevo'     => ['type' => 'VARCHAR', 'constraint' => 50],
            'usuario_id'       => ['type' => 'INT', 'unsigned' => true],
            'nota'             => ['type' => 'TEXT', 'null' => true],
            'created_at'       => ['type' => 'DATETIME', 'null' => true],
        ]);
        $this->forge->addKey('id', true);
        $this->forge->addKey('proyecto_id');
        $this->forge->addForeignKey('proyecto_id', 'proyectos', 'id', 'CASCADE', 'CASCADE');
        $this->forge->addForeignKey('usuario_id',  'usuarios',  'id', 'CASCADE', 'CASCADE');
        $this->forge->createTable('historial_flujo');
    }

    public function down(): void
    {
        $this->forge->dropTable('historial_flujo',   true);
        $this->forge->dropTable('borradores',        true);
        $this->forge->dropTable('versiones',         true);
        $this->forge->dropTable('archivos_proyecto', true);
        $this->forge->dropTable('proyectos',         true);
    }
}
