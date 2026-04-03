<?php

/**
 * app_helper.php — Funciones globales del sistema UDG-Proyectos
 * 
 * Cargado automáticamente en BaseController.
 * Disponible en toda la aplicación.
 */

if (! function_exists('estatus_badge')) {
    /**
     * Retorna un badge HTML Bootstrap con el color correcto según el estatus del proyecto.
     */
    function estatus_badge(string $estatus): string
    {
        $map = [
            'borrador'     => ['secondary', 'Borrador'],
            'enviado'      => ['primary',   'Enviado'],
            'en_revision'  => ['info',      'En Revisión'],
            'correcciones' => ['warning',   'Con Correcciones'],
            'aprobado'     => ['success',   'Aprobado'],
            'rechazado'    => ['danger',    'Rechazado'],
            'publicado'    => ['dark',      'Publicado'],
        ];

        [$color, $label] = $map[$estatus] ?? ['secondary', ucfirst($estatus)];
        return "<span class=\"badge bg-{$color}\">{$label}</span>";
    }
}

if (! function_exists('nombre_completo')) {
    /**
     * Construye el nombre completo de un usuario a partir de un array.
     */
    function nombre_completo(array $usuario, bool $invertido = false): string
    {
        $nombre    = trim($usuario['nombre'] ?? '');
        $paterno   = trim($usuario['apellido_paterno'] ?? '');
        $materno   = trim($usuario['apellido_materno'] ?? '');

        if ($invertido) {
            return trim("{$paterno} {$materno}, {$nombre}");
        }
        return trim("{$nombre} {$paterno} {$materno}");
    }
}

if (! function_exists('formato_tamano')) {
    /**
     * Convierte bytes a formato legible (KB, MB, GB).
     */
    function formato_tamano(int $bytes): string
    {
        if ($bytes >= 1073741824) {
            return round($bytes / 1073741824, 2) . ' GB';
        }
        if ($bytes >= 1048576) {
            return round($bytes / 1048576, 2) . ' MB';
        }
        if ($bytes >= 1024) {
            return round($bytes / 1024, 2) . ' KB';
        }
        return $bytes . ' bytes';
    }
}

if (! function_exists('fecha_legible')) {
    /**
     * Formatea una fecha en español (ej: "15 de marzo de 2024").
     */
    function fecha_legible(string $fecha, bool $conHora = false): string
    {
        $meses = [
            1 => 'enero', 2 => 'febrero', 3 => 'marzo', 4 => 'abril',
            5 => 'mayo', 6 => 'junio', 7 => 'julio', 8 => 'agosto',
            9 => 'septiembre', 10 => 'octubre', 11 => 'noviembre', 12 => 'diciembre',
        ];

        $ts  = strtotime($fecha);
        $dia = date('j', $ts);
        $mes = $meses[(int)date('n', $ts)];
        $anio = date('Y', $ts);
        $hora = $conHora ? ' a las ' . date('H:i', $ts) : '';

        return "{$dia} de {$mes} de {$anio}{$hora}";
    }
}

if (! function_exists('truncar_texto')) {
    /**
     * Truncar texto largo con puntos suspensivos.
     */
    function truncar_texto(string $texto, int $longitud = 150): string
    {
        if (mb_strlen($texto) <= $longitud) {
            return $texto;
        }
        return mb_substr($texto, 0, $longitud) . '…';
    }
}

if (! function_exists('is_role')) {
    /**
     * Verificar si el usuario actual tiene un rol específico (en vistas).
     */
    function is_role(string|array $roles): bool
    {
        $userRole = session()->get('user_role') ?? 'publico';
        if (is_array($roles)) {
            return in_array($userRole, $roles);
        }
        return $userRole === $roles;
    }
}

if (! function_exists('csrf_field_html')) {
    /**
     * Genera el campo CSRF oculto para formularios.
     * Equivalente a csrf_field() pero con nombre personalizado.
     */
    function csrf_field_html(): string
    {
        $token = csrf_token();
        $hash  = csrf_hash();
        return "<input type=\"hidden\" name=\"{$token}\" value=\"{$hash}\">";
    }
}
