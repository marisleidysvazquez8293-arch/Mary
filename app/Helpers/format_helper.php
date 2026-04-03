<?php

/**
 * format_helper.php — Generación de citas académicas
 * 
 * Soporta formatos: APA 7a edición, IEEE, MLA 9a edición
 * Usado principalmente por el Módulo 3 (Repositorio).
 */

if (! function_exists('generar_cita_apa')) {
    /**
     * Generar cita en formato APA 7a edición.
     * 
     * Ejemplo:
     *   García, J. A. (2024). *Título del proyecto*. Universidad de Guadalajara.
     */
    function generar_cita_apa(array $proyecto): string
    {
        $autor  = apellido_nombre_apa($proyecto);
        $anio   = $proyecto['anio_generacion'] ?? date('Y');
        $titulo = $proyecto['titulo'] ?? '';
        $inst   = $proyecto['institucion'] ?? 'Universidad de Guadalajara';
        $folio  = $proyecto['identificador_unico'] ?? '';

        $cita = "{$autor} ({$anio}). <em>{$titulo}</em>. {$inst}.";
        if ($folio) {
            $url  = base_url("repositorio/proyecto/" . ($proyecto['id'] ?? ''));
            $cita .= " <a href=\"{$url}\">{$url}</a>";
        }
        return $cita;
    }
}

if (! function_exists('generar_cita_ieee')) {
    /**
     * Generar cita en formato IEEE.
     * 
     * Ejemplo:
     *   J. A. García, "Título del proyecto," Universidad de Guadalajara, 2024.
     */
    function generar_cita_ieee(array $proyecto): string
    {
        $autor  = iniciales_nombre_ieee($proyecto);
        $titulo = $proyecto['titulo'] ?? '';
        $inst   = $proyecto['institucion'] ?? 'Universidad de Guadalajara';
        $anio   = $proyecto['anio_generacion'] ?? date('Y');

        return "{$autor}, \"{$titulo},\" {$inst}, {$anio}.";
    }
}

if (! function_exists('generar_cita_mla')) {
    /**
     * Generar cita en formato MLA 9a edición.
     * 
     * Ejemplo:
     *   García, Juan Antonio. "Título del proyecto." Universidad de Guadalajara, 2024.
     */
    function generar_cita_mla(array $proyecto): string
    {
        $apellido = $proyecto['autor_apellido'] ?? '';
        $nombre   = $proyecto['autor_nombre'] ?? '';
        $titulo   = $proyecto['titulo'] ?? '';
        $inst     = $proyecto['institucion'] ?? 'Universidad de Guadalajara';
        $anio     = $proyecto['anio_generacion'] ?? date('Y');

        $autor = $apellido ? "{$apellido}, {$nombre}" : $nombre;
        return "{$autor}. \"{$titulo}.\" {$inst}, {$anio}.";
    }
}

// ----------------------------------------------------------------
// Funciones auxiliares internas
// ----------------------------------------------------------------

if (! function_exists('apellido_nombre_apa')) {
    function apellido_nombre_apa(array $proyecto): string
    {
        $apellido = $proyecto['autor_apellido'] ?? '';
        $nombre   = $proyecto['autor_nombre'] ?? '';

        if (! $apellido) {
            return $nombre;
        }

        // Iniciales del nombre: "Juan Antonio" → "J. A."
        $iniciales = '';
        foreach (explode(' ', $nombre) as $parte) {
            $iniciales .= strtoupper(mb_substr($parte, 0, 1)) . '. ';
        }

        return trim("{$apellido}, " . trim($iniciales));
    }
}

if (! function_exists('iniciales_nombre_ieee')) {
    function iniciales_nombre_ieee(array $proyecto): string
    {
        $nombre   = $proyecto['autor_nombre'] ?? '';
        $apellido = $proyecto['autor_apellido'] ?? '';

        $iniciales = '';
        foreach (explode(' ', $nombre) as $parte) {
            $iniciales .= strtoupper(mb_substr($parte, 0, 1)) . '. ';
        }

        return trim(trim($iniciales) . ' ' . $apellido);
    }
}
