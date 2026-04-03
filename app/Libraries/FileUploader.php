<?php

namespace App\Libraries;

/**
 * FileUploader — Librería centralizada para subida de archivos
 * 
 * Maneja la subida segura de archivos con:
 * - Validación de tipo MIME real (no solo extensión)
 * - Límite de tamaño por configuración
 * - Organización por proyecto y versión
 * - Máximo 10 versiones por proyecto
 * 
 * Uso:
 *   $uploader = new \App\Libraries\FileUploader();
 *   $result   = $uploader->subirArchivo($request->getFile('archivo'), $proyectoId);
 */
class FileUploader
{
    private int    $maxSizeKB;
    private array  $allowedMimes;
    private string $uploadPath;
    private int    $maxVersions;

    // MIME types permitidos (validación real)
    private const MIME_MAP = [
        'pdf'  => ['application/pdf'],
        'docx' => ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        'doc'  => ['application/msword'],
        'zip'  => ['application/zip', 'application/x-zip-compressed'],
        'mp4'  => ['video/mp4'],
    ];

    public function __construct()
    {
        $this->maxSizeKB    = (int)(getenv('upload.maxSize') ?: 512000);
        $this->maxVersions  = (int)(getenv('upload.maxVersions') ?: 10);
        $this->uploadPath   = WRITEPATH . 'uploads/projects/';
        $this->allowedMimes = $this->construirMimesPermitidos(
            getenv('upload.allowedTypes') ?: 'pdf|docx|zip|mp4'
        );
    }

    /**
     * Subir archivo para un proyecto.
     * 
     * @return array ['success' => bool, 'ruta' => string, 'error' => string]
     */
    public function subirArchivo(\CodeIgniter\HTTP\Files\UploadedFile $archivo, int $proyectoId, int $version = 1): array
    {
        // Validar que el archivo se subió correctamente
        if (! $archivo->isValid()) {
            return ['success' => false, 'error' => 'El archivo no se subió correctamente: ' . $archivo->getErrorString()];
        }

        // Validar tamaño
        if ($archivo->getSizeByUnit('kb') > $this->maxSizeKB) {
            $maxMB = round($this->maxSizeKB / 1024);
            return ['success' => false, 'error' => "El archivo excede el tamaño máximo de {$maxMB} MB."];
        }

        // Validar tipo MIME
        $mime = $archivo->getMimeType();
        if (! in_array($mime, $this->allowedMimes)) {
            return ['success' => false, 'error' => 'Tipo de archivo no permitido. Solo: PDF, DOCX, ZIP, MP4.'];
        }

        // Crear carpeta del proyecto
        $carpeta = $this->uploadPath . "proyecto_{$proyectoId}/";
        if (! is_dir($carpeta)) {
            mkdir($carpeta, 0755, true);
        }

        // Nombre seguro: proyectoID_v01_timestamp_original.ext
        $extension  = strtolower($archivo->getExtension());
        $nombreBase = pathinfo($archivo->getClientFilename(), PATHINFO_FILENAME);
        $nombreBase = preg_replace('/[^a-zA-Z0-9_-]/', '_', $nombreBase);
        $nombreFinal = sprintf('p%d_v%02d_%s_%s.%s',
            $proyectoId,
            $version,
            date('Ymd_His'),
            substr($nombreBase, 0, 30),
            $extension
        );

        // Mover archivo
        $archivo->move($carpeta, $nombreFinal);

        return [
            'success'       => true,
            'ruta'          => "proyecto_{$proyectoId}/{$nombreFinal}",
            'nombre_original' => $archivo->getClientFilename(),
            'tipo_mime'     => $mime,
            'tamano_bytes'  => $archivo->getSize(),
            'version'       => $version,
        ];
    }

    /**
     * Verificar cuántas versiones existen para un proyecto.
     * Retorna el número de la próxima versión o false si ya alcanzó el máximo.
     */
    public function getSiguienteVersion(int $proyectoId, int $versionesActuales): int|false
    {
        if ($versionesActuales >= $this->maxVersions) {
            return false;
        }
        return $versionesActuales + 1;
    }

    /**
     * Eliminar un archivo físico del servidor.
     */
    public function eliminarArchivo(string $ruta): bool
    {
        $fullPath = $this->uploadPath . $ruta;
        if (file_exists($fullPath)) {
            return unlink($fullPath);
        }
        return false;
    }

    /**
     * Obtener URL pública de descarga (pasa por controlador — no expone ruta real).
     */
    public function getUrlDescarga(int $proyectoId, int $archivoId): string
    {
        return base_url("repositorio/descargar/{$proyectoId}/{$archivoId}");
    }

    // ----------------------------------------------------------------
    // Métodos privados
    // ----------------------------------------------------------------

    private function construirMimesPermitidos(string $tipos): array
    {
        $mimes = [];
        foreach (explode('|', $tipos) as $ext) {
            $ext = strtolower(trim($ext));
            if (isset(self::MIME_MAP[$ext])) {
                $mimes = array_merge($mimes, self::MIME_MAP[$ext]);
            }
        }
        return $mimes;
    }
}
