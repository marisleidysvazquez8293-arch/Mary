<?php
namespace App\Controllers\Modulo4_Admin;
use App\Controllers\BaseController;
/**
 * AdminController — Módulo 4: Administración
 * RAMA: modulo/administracion | RESPONSABLE: Estudiante 4
 * Implementar: gestión usuarios, roles, config, logs, respaldos, asignación evaluadores
 */
class AdminController extends BaseController {
    public function index(): string {
        return $this->render('Modulo4_Admin/index', ['pageTitle' => 'Panel de Administración']);
    }
}
