<?php

if (! function_exists('estatus_badge')) {
    /**
        * Genera un badge de Bootstrap con colores estándar para el sistema
        * según el nombre del estatus.
        */
    function estatus_badge(string $estatus): string
    {
        $estatusLimpiado = strtolower(trim($estatus));
        
        $colores = [
            'borrador'   => 'secondary',
            'enviado'    => 'primary',
            'asignado'   => 'info',
            'en_revision'=> 'warning',
            'aprobado'   => 'success',
            'rechazado'  => 'danger',
            'publicado'  => 'dark',
            'activo'     => 'success',
            'inactivo'   => 'secondary',
        ];

        $color = $colores[$estatusLimpiado] ?? 'secondary';
        $texto = ucfirst($estatusLimpiado);
        
        // Transformar guiones bajos en espacios para mostrar
        $texto = str_replace('_', ' ', $texto);

        return "<span class=\"badge bg-{$color}\">{$texto}</span>";
    }
}

if (! function_exists('format_bytes')) {
    /**
        * Formatea un tamaño en bytes a KB, MB, GB...
        */
    function format_bytes(int $bytes, int $precision = 2): string
    {
        $units = ['B', 'KB', 'MB', 'GB', 'TB'];

        $bytes = max($bytes, 0);
        $pow = floor(($bytes ? log($bytes) : 0) / log(1024));
        $pow = min($pow, count($units) - 1);

        $bytes /= (1 << (10 * $pow));

        return round($bytes, $precision) . ' ' . $units[$pow];
    }
}
