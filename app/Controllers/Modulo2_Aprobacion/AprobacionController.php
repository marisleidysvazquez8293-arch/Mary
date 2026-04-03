<?php

namespace App\Controllers\Modulo2_Aprobacion;

use App\Controllers\BaseController;

/**
 * AprobacionController — Módulo 2: Flujo de Aprobación y Evaluación
 * 
 * RAMA: modulo/aprobacion
 * RESPONSABLE: Estudiante 2
 * 
 * Funcionalidades a implementar:
 *   - Panel de proyectos (pendientes / en revisión / completados)
 *   - Asignación de evaluadores por coordinador/admin
 *   - Formulario de dictamen (aprobado / correcciones / rechazado)
 *   - Comentarios sobre documentos con referencia de página/línea
 *   - Historial completo de revisiones
 *   - Evaluación colaborativa (múltiples evaluadores por proyecto)
 *   - Flujo: enviado → en_revision → correcciones|aprobado → publicado
 */
class AprobacionController extends BaseController
{
    /** GET /aprobacion — Panel principal del comité */
    public function panel(): string
    {
        // TODO: Módulo 2 — Cargar proyectos por estatus, filtrar por rol del evaluador
        return $this->render('Modulo2_Aprobacion/panel', ['pageTitle' => 'Panel de Evaluación']);
    }

    /** GET /aprobacion/asignar/:proyectoId */
    public function asignar(int $proyectoId): string
    {
        // TODO: Módulo 2 — Mostrar lista de evaluadores disponibles (UserModel::getEvaluadores())
        return $this->render('Modulo2_Aprobacion/asignar', ['pageTitle' => 'Asignar Evaluadores', 'id' => $proyectoId]);
    }

    /** POST /aprobacion/asignar */
    public function procesarAsignacion()
    {
        // TODO: Módulo 2
        // 1. Validar evaluadores seleccionados
        // 2. Insertar en tabla asignaciones
        // 3. Cambiar estatus proyecto a 'en_revision' (ProjectModel::cambiarEstatus)
        // 4. Notificar a cada evaluador por email (EmailNotification::notificarAsignacion)
    }

    /** GET /aprobacion/revisar/:asignacionId */
    public function revisar(int $asignacionId): string
    {
        // TODO: Módulo 2 — Cargar proyecto, archivos y formulario de dictamen
        return $this->render('Modulo2_Aprobacion/revisar', ['pageTitle' => 'Revisar Proyecto', 'id' => $asignacionId]);
    }

    /** POST /aprobacion/dictamen */
    public function dictamen()
    {
        // TODO: Módulo 2
        // 1. Validar dictamen (aprobado | aprobado_correcciones | rechazado)
        // 2. Insertar en revisiones
        // 3. Si todos los evaluadores emitieron dictamen → calcular resultado final
        // 4. Cambiar estatus del proyecto (ProjectModel::cambiarEstatus)
        // 5. Notificar al estudiante (EmailNotification::notificarDictamen)
    }

    /** POST /aprobacion/comentario */
    public function agregarComentario()
    {
        // TODO: Módulo 2 — Insertar en comentarios_revision (puede ser AJAX)
        return $this->jsonResponse(false, 'No implementado aún');
    }

    /** GET /aprobacion/historial/:proyectoId */
    public function historial(int $proyectoId): string
    {
        // TODO: Módulo 2 — Cargar historial_flujo del proyecto
        return $this->render('Modulo2_Aprobacion/historial', ['pageTitle' => 'Historial', 'id' => $proyectoId]);
    }
}
