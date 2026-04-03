<?php
namespace App\Controllers\Modulo5_Notificacion;
use App\Controllers\BaseController;
/**
 * NotificacionController — Módulo 5: Notificaciones
 * RAMA: modulo/notificacion | RESPONSABLE: Estudiante 5
 * Implementar: centro de notificaciones, configuración por usuario, polling AJAX no-leídas
 */
class NotificacionController extends BaseController {
    public function index(): string { return $this->render('Modulo5_Notificacion/index', ['pageTitle' => 'Mis Notificaciones']); }
    public function marcarLeida(int $id) { /* TODO: Módulo 5 */ }
    public function marcarTodas() { /* TODO: Módulo 5 */ }
    public function configuracion(): string { return $this->render('Modulo5_Notificacion/configuracion', ['pageTitle' => 'Config. Notificaciones']); }
    public function guardarConfig() { /* TODO: Módulo 5 */ }
    public function apiNoLeidas() { return $this->jsonResponse(false, 'Pendiente'); }
}
