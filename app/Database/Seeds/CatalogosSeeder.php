<?php

namespace App\Database\Seeds;

use CodeIgniter\Database\Seeder;

/**
 * CatalogosSeeder — Inserta áreas de conocimiento y tipos de proyecto
 */
class CatalogosSeeder extends Seeder
{
    public function run(): void
    {
        // --- Áreas de conocimiento ---
        $areas = [
            ['nombre' => 'Ingeniería de Software',          'descripcion' => 'Desarrollo, diseño y arquitectura de software'],
            ['nombre' => 'Inteligencia Artificial',          'descripcion' => 'Machine learning, redes neuronales, IA'],
            ['nombre' => 'Redes y Telecomunicaciones',       'descripcion' => 'Redes, protocolos, seguridad informática'],
            ['nombre' => 'Bases de Datos',                   'descripcion' => 'Modelado, gestión y análisis de datos'],
            ['nombre' => 'Sistemas Embebidos e IoT',         'descripcion' => 'Hardware, microcontroladores, IoT'],
            ['nombre' => 'Computación Gráfica',              'descripcion' => 'Gráficos, realidad virtual y aumentada'],
            ['nombre' => 'Ciencias de la Computación',       'descripcion' => 'Algoritmia, teoría de la computación'],
            ['nombre' => 'Gestión de Tecnologías',           'descripcion' => 'Gestión de proyectos TI, ITIL, COBIT'],
            ['nombre' => 'Bioinformática',                   'descripcion' => 'Aplicaciones computacionales en biología'],
            ['nombre' => 'Otro',                             'descripcion' => 'Área no listada anteriormente'],
        ];

        $this->db->table('areas')->insertBatch($areas);
        echo "  ✓ Áreas insertadas: " . count($areas) . "\n";

        // --- Tipos de proyecto ---
        $tipos = [
            ['nombre' => 'Tesis de Licenciatura'],
            ['nombre' => 'Proyecto de Grado'],
            ['nombre' => 'Tesis de Maestría'],
            ['nombre' => 'Tesis de Doctorado'],
            ['nombre' => 'Proyecto de Investigación'],
            ['nombre' => 'Reporte de Residencia'],
            ['nombre' => 'Artículo Académico'],
            ['nombre' => 'Prototipo / Software'],
        ];

        $this->db->table('tipos_proyecto')->insertBatch($tipos);
        echo "  ✓ Tipos de proyecto insertados: " . count($tipos) . "\n";
    }
}
