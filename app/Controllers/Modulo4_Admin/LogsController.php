<?php
namespace App\Controllers\Modulo4_Admin;
use App\Controllers\BaseController;
/** Logs de actividad del sistema */
class LogsController extends BaseController {
    public function index(): string { return $this->render('Modulo4_Admin/logs', ['pageTitle' => 'Logs del Sistema']); }
}
