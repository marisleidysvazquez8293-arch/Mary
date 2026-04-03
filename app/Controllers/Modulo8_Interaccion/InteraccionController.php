<?php
namespace App\Controllers\Modulo8_Interaccion;
use App\Controllers\BaseController;
/**
 * InteraccionController — Módulo 8: Interacción Social
 * RAMA: modulo/interaccion | RESPONSABLE: Estudiante 8
 * Implementar: sistema de votos, comentarios en proyectos, ranking, donaciones (opcional)
 */
class InteraccionController extends BaseController {
    public function votar(int $proyectoId) { /* TODO: Módulo 8 — AJAX, un voto por usuario */ return $this->jsonResponse(false, 'Pendiente'); }
    public function comentar() { /* TODO: Módulo 8 — insertar comentario público */ return $this->jsonResponse(false, 'Pendiente'); }
    public function ranking(): string { return $this->render('Modulo8_Interaccion/ranking', ['pageTitle' => 'Ranking de Proyectos']); }
}
