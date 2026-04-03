<?php

namespace App\Controllers\Modulo1_Envio;

use App\Controllers\BaseController;

/**
 * EnvioController — Módulo 1: Envío de Proyectos
 * 
 * RAMA: modulo/envio
 * RESPONSABLE: Estudiante 1
 * 
 * Este archivo es el stub/esqueleto base.
 * El equipo del Módulo 1 debe implementar todos los métodos.
 * 
 * Funcionalidades a implementar:
 *   - Formulario multi-paso de envío con metadatos
 *   - Subida de archivos (PDF, DOCX, ZIP, MP4)
 *   - Guardado como borrador (autoguardado con JS)
 *   - Manejo de hasta 10 versiones por proyecto
 *   - Generación de identificador único al confirmar
 *   - Vista de mis proyectos con historial de versiones
 */
class EnvioController extends BaseController
{
    /** GET /envio — Lista de proyectos del estudiante */
    public function index(): string
    {
        // TODO: Módulo 1 — Cargar proyectos del $this->getCurrentUserId()
        return $this->render('Modulo1_Envio/index', [
            'pageTitle' => 'Mis Proyectos',
        ]);
    }

    /** GET /envio/nuevo — Formulario de nuevo proyecto */
    public function nuevo(): string
    {
        // TODO: Módulo 1 — Formulario multi-paso, cargar catálogos (áreas, tipos)
        return $this->render('Modulo1_Envio/formulario', [
            'pageTitle' => 'Nuevo Proyecto',
        ]);
    }

    /** POST /envio/guardar — Guardar proyecto como enviado */
    public function guardar()
    {
        // TODO: Módulo 1
        // 1. Validar campos requeridos (título, resumen, área, tipo, asesor)
        // 2. Validar archivo principal subido (FileUploader)
        // 3. Insertar en proyectos con estatus='enviado'
        // 4. Disparar notificación al coordinador (EmailNotification)
        // 5. Redirigir con folio de confirmación
    }

    /** POST /envio/borrador/guardar — Guardar borrador (AJAX) */
    public function guardarBorrador()
    {
        // TODO: Módulo 1 — Guardar JSON en tabla borradores, retornar JSON
        return $this->jsonResponse(true, 'Borrador guardado');
    }

    /** GET /envio/borrador/:id */
    public function borrador(int $id): string
    {
        // TODO: Módulo 1 — Cargar borrador y prepoblar formulario
        return $this->render('Modulo1_Envio/formulario', ['pageTitle' => 'Editar Borrador']);
    }

    /** GET /envio/ver/:id */
    public function ver(int $id): string
    {
        // TODO: Módulo 1 — Ver detalle de un proyecto propio
        return $this->render('Modulo1_Envio/detalle', ['pageTitle' => 'Ver Proyecto', 'id' => $id]);
    }

    /** POST /envio/archivo/subir — Subir archivo (puede ser AJAX) */
    public function subirArchivo()
    {
        // TODO: Módulo 1 — Usar App\Libraries\FileUploader
        return $this->jsonResponse(false, 'No implementado aún');
    }

    /** DELETE /envio/archivo/:id */
    public function eliminarArchivo(int $id)
    {
        // TODO: Módulo 1 — Eliminar archivo físico + registro en BD
        return $this->jsonResponse(false, 'No implementado aún');
    }

    /** GET /envio/versiones/:id */
    public function versiones(int $id): string
    {
        // TODO: Módulo 1 — Mostrar historial de versiones (máx. 10)
        return $this->render('Modulo1_Envio/versiones', ['pageTitle' => 'Versiones', 'id' => $id]);
    }
}
