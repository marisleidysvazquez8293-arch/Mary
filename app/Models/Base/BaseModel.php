<?php

namespace App\Models\Base;

use CodeIgniter\Model;

/**
 * BaseModel — Modelo base para todos los módulos de UDG-Proyectos
 * 
 * Extiende el Model de CI4 y agrega:
 * - Timestamps automáticos (created_at / updated_at)
 * - Soft deletes (deleted_at)
 * - Métodos utilitarios comunes
 * - Paginación estandarizada
 * 
 * Todos los modelos del sistema DEBEN extender este BaseModel.
 */
abstract class BaseModel extends Model
{
    // Formato de fechas estándar del sistema
    protected $dateFormat  = 'datetime';
    protected $createdField = 'created_at';
    protected $updatedField = 'updated_at';
    protected $deletedField = 'deleted_at';

    // Protección de asignación masiva desactivada (cada modelo define $allowedFields)
    protected $allowCallbacks = true;

    // Paginación por defecto
    protected int $defaultPerPage = 15;

    // ----------------------------------------------------------------
    // Métodos utilitarios comunes
    // ----------------------------------------------------------------

    /**
     * Obtener todos los registros activos (no eliminados)
     */
    public function getActivos(int $limit = 0, int $offset = 0): array
    {
        return $this->findAll($limit, $offset);
    }

    /**
     * Buscar por campo exacto
     */
    public function buscarPor(string $campo, mixed $valor): array
    {
        return $this->where($campo, $valor)->findAll();
    }

    /**
     * Verificar si un registro existe
     */
    public function existe(int $id): bool
    {
        return $this->find($id) !== null;
    }

    /**
     * Actualización parcial segura (solo campos permitidos)
     */
    public function actualizarCampos(int $id, array $datos): bool
    {
        $datosFiltrados = array_intersect_key($datos, array_flip($this->allowedFields));
        return $this->update($id, $datosFiltrados);
    }

    /**
     * Paginación estandarizada para todas las vistas
     * 
     * @return array ['data' => [...], 'pager' => Pager, 'total' => int]
     */
    public function paginar(int $perPage = 0, array $where = []): array
    {
        $perPage = $perPage ?: $this->defaultPerPage;

        $builder = $this->builder();
        if (! empty($where)) {
            $builder->where($where);
        }

        $total = $this->countAllResults(false);
        $data  = $this->paginate($perPage);
        $pager = $this->pager;

        return compact('data', 'pager', 'total');
    }

    /**
     * Log de actividad — registra en tabla system_logs
     * Llamar desde controladores cuando sea necesario.
     */
    public function registrarLog(int $userId, string $accion, string $tabla, int $registroId): void
    {
        $db = \Config\Database::connect();
        $db->table('system_logs')->insert([
            'usuario_id'  => $userId,
            'accion'      => $accion,
            'tabla'       => $tabla,
            'registro_id' => $registroId,
            'ip'          => \Config\Services::request()->getIPAddress(),
            'created_at'  => date('Y-m-d H:i:s'),
        ]);
    }
}
