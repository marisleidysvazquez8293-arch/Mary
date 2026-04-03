<?php
namespace App\Controllers\Modulo4_Admin;
use App\Controllers\BaseController;
/** Configuración general del sistema */
class ConfigController extends BaseController {
    public function index(): string { return $this->render('Modulo4_Admin/config', ['pageTitle' => 'Configuración']); }
    public function guardar() { /* TODO: Módulo 4 */ }
}
