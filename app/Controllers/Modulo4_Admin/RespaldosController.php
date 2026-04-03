<?php
namespace App\Controllers\Modulo4_Admin;
use App\Controllers\BaseController;
/** Respaldos de base de datos */
class RespaldosController extends BaseController {
    public function index(): string { return $this->render('Modulo4_Admin/respaldos', ['pageTitle' => 'Respaldos']); }
    public function crear() { /* TODO: Módulo 4 — usar mysqldump o similar */ }
}
