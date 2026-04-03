<?php

namespace App\Controllers\Modulo3_Repositorio;

use App\Controllers\BaseController;
use App\Models\ProjectModel;

/**
 * RepositorioController — Módulo 3: Repositorio Público
 * 
 * RAMA: modulo/repositorio
 * RESPONSABLE: Estudiante 3
 * 
 * Funcionalidades a implementar:
 *   - Buscador con filtros (año, área, tipo, autor, palabras clave)
 *   - Vista de proyecto individual (resumen, metadatos, archivos)
 *   - Descarga de archivos (incrementa contador)
 *   - Generación de citas (APA, IEEE, MLA) — usar format_helper
 *   - Estadísticas por proyecto (visitas, descargas)
 *   - Vista pública (sin login requerido)
 */
class RepositorioController extends BaseController
{
    protected ProjectModel $projectModel;

    public function __construct()
    {
        $this->projectModel = new ProjectModel();
    }

    /** GET /repositorio — Página principal del repositorio */
    public function index(): string
    {
        // TODO: Módulo 3 — Cargar proyectos recientes/destacados
        return $this->render('Modulo3_Repositorio/index', ['pageTitle' => 'Repositorio Público']);
    }

    /** GET /repositorio/buscar */
    public function buscar(): string
    {
        // TODO: Módulo 3
        // Usar: $this->projectModel->buscarPublico($filtros)
        // Los filtros vienen por GET: q, area, tipo, anio, autor
        $filtros = $this->request->getGet(['q','area','tipo','anio','autor']);
        $result  = $this->projectModel->buscarPublico($filtros);

        return $this->render('Modulo3_Repositorio/resultados', [
            'pageTitle' => 'Resultados de búsqueda',
            'proyectos' => $result['data'],
            'pager'     => $result['pager'],
            'total'     => $result['total'],
            'filtros'   => $filtros,
        ]);
    }

    /** GET /repositorio/proyecto/:id */
    public function ver(int $id): string
    {
        // TODO: Módulo 3
        // 1. Cargar proyecto con autor y metadatos
        // 2. Incrementar contador de visitas (ProjectModel::incrementarContador)
        // 3. Cargar archivos disponibles (solo proyectos publicados)
        // 4. Generar citas en todos los formatos (format_helper)
        return $this->render('Modulo3_Repositorio/proyecto', ['pageTitle' => 'Ver Proyecto', 'id' => $id]);
    }

    /** GET /repositorio/descargar/:proyectoId/:archivoId */
    public function descargar(int $proyectoId, int $archivoId)
    {
        // TODO: Módulo 3
        // 1. Verificar que el proyecto esté publicado
        // 2. Obtener ruta del archivo (archivos_proyecto)
        // 3. Incrementar descargas (ProjectModel::incrementarContador($id, 'descargas'))
        // 4. Servir archivo con Content-Disposition: attachment
    }

    /** GET /repositorio/cita/:id — Retorna citas en JSON (AJAX) */
    public function cita(int $id)
    {
        // TODO: Módulo 3 — usar generar_cita_apa(), generar_cita_ieee(), generar_cita_mla()
        return $this->jsonResponse(false, 'No implementado aún');
    }
}
