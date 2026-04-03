<?php

namespace App\Models;

use App\Models\Base\BaseModel;

/**
 * ProjectModel — Modelo central de proyectos/tesis
 * 
 * Compartido entre múltiples módulos:
 *   - Módulo 1 (Envío): crear, editar, borradores
 *   - Módulo 2 (Aprobación): cambiar estatus, flujo
 *   - Módulo 3 (Repositorio): consulta pública
 *   - Módulo 4 (Admin): gestión general
 * 
 * ESTADOS VÁLIDOS del proyecto (flujo completo):
 *   borrador → enviado → en_revision → correcciones → aprobado → publicado
 *                                    ↘ rechazado
 */
class ProjectModel extends BaseModel
{
    protected $table         = 'proyectos';
    protected $primaryKey    = 'id';
    protected $returnType    = 'array';
    protected $useSoftDeletes = true;

    protected $allowedFields = [
        'titulo', 'resumen', 'palabras_clave',
        'area_id', 'tipo_id', 'autor_id', 'asesor_id',
        'estatus', 'identificador_unico',
        'anio_generacion', 'institucion', 'departamento',
        'url_repositorio', 'doi', 'visitas', 'descargas',
    ];

    // Estatus válidos para el flujo del sistema
    public const ESTATUS_VALIDOS = [
        'borrador',
        'enviado',
        'en_revision',
        'correcciones',
        'aprobado',
        'rechazado',
        'publicado',
    ];

    protected $beforeInsert = ['generarIdentificador'];

    // ----------------------------------------------------------------
    // CALLBACKS
    // ----------------------------------------------------------------

    /**
     * Genera identificador único tipo UDG-2024-00001
     */
    protected function generarIdentificador(array $data): array
    {
        $anio  = date('Y');
        $total = $this->countAll() + 1;
        $data['data']['identificador_unico'] = sprintf('UDG-%s-%05d', $anio, $total);
        return $data;
    }

    // ----------------------------------------------------------------
    // CONSULTAS MÓDULO 1 — Envío
    // ----------------------------------------------------------------

    /**
     * Proyectos de un estudiante específico
     */
    public function getMisProyectos(int $autorId): array
    {
        return $this->select('proyectos.*, areas.nombre as area_nombre, tipos_proyecto.nombre as tipo_nombre')
                    ->join('areas', 'areas.id = proyectos.area_id', 'left')
                    ->join('tipos_proyecto', 'tipos_proyecto.id = proyectos.tipo_id', 'left')
                    ->where('autor_id', $autorId)
                    ->orderBy('created_at', 'DESC')
                    ->findAll();
    }

    /**
     * Cambiar estatus de un proyecto (con validación de flujo)
     */
    public function cambiarEstatus(int $proyectoId, string $nuevoEstatus, int $usuarioId): bool
    {
        $proyecto = $this->find($proyectoId);
        if (! $proyecto || ! in_array($nuevoEstatus, self::ESTATUS_VALIDOS)) {
            return false;
        }

        // Registrar en historial del flujo
        $db = \Config\Database::connect();
        $db->table('historial_flujo')->insert([
            'proyecto_id'    => $proyectoId,
            'estado_anterior' => $proyecto['estatus'],
            'estado_nuevo'   => $nuevoEstatus,
            'usuario_id'     => $usuarioId,
            'created_at'     => date('Y-m-d H:i:s'),
        ]);

        return $this->update($proyectoId, ['estatus' => $nuevoEstatus]);
    }

    // ----------------------------------------------------------------
    // CONSULTAS MÓDULO 3 — Repositorio público
    // ----------------------------------------------------------------

    /**
     * Búsqueda pública con filtros
     */
    public function buscarPublico(array $filtros = [], int $perPage = 15): array
    {
        $this->select('proyectos.*, areas.nombre as area_nombre, tipos_proyecto.nombre as tipo,
                        usuarios.nombre as autor_nombre, usuarios.apellido_paterno as autor_apellido')
             ->join('areas', 'areas.id = proyectos.area_id', 'left')
             ->join('tipos_proyecto', 'tipos_proyecto.id = proyectos.tipo_id', 'left')
             ->join('usuarios', 'usuarios.id = proyectos.autor_id', 'left')
             ->where('proyectos.estatus', 'publicado');

        if (! empty($filtros['q'])) {
            $q = $filtros['q'];
            $this->groupStart()
                 ->like('proyectos.titulo', $q)
                 ->orLike('proyectos.resumen', $q)
                 ->orLike('proyectos.palabras_clave', $q)
                 ->groupEnd();
        }
        if (! empty($filtros['area'])) {
            $this->where('proyectos.area_id', $filtros['area']);
        }
        if (! empty($filtros['tipo'])) {
            $this->where('proyectos.tipo_id', $filtros['tipo']);
        }
        if (! empty($filtros['anio'])) {
            $this->where('proyectos.anio_generacion', $filtros['anio']);
        }
        if (! empty($filtros['autor'])) {
            $this->like('usuarios.nombre', $filtros['autor']);
        }

        return [
            'data'  => $this->paginate($perPage),
            'pager' => $this->pager,
            'total' => $this->countAllResults(false),
        ];
    }

    /**
     * Incrementar contador de visitas o descargas
     */
    public function incrementarContador(int $id, string $campo = 'visitas'): void
    {
        if (! in_array($campo, ['visitas', 'descargas'])) {
            return;
        }
        $this->set($campo, "$campo + 1", false)->where('id', $id)->update();
    }
}
