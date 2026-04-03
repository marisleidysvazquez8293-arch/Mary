<?php
namespace App\Controllers\Modulo6_Portafolio;
use App\Controllers\BaseController;
/**
 * PortafolioController — Módulo 6: Portafolio Estudiantil
 * RAMA: modulo/portafolio | RESPONSABLE: Estudiante 6
 * Implementar: perfil público del estudiante, sus proyectos publicados, habilidades, logros
 */
class PortafolioController extends BaseController {
    public function index(): string { return $this->render('Modulo6_Portafolio/index', ['pageTitle' => 'Mi Portafolio']); }
    public function ver(string $username): string { return $this->render('Modulo6_Portafolio/perfil', ['pageTitle' => 'Portafolio', 'username' => $username]); }
    public function editar(): string { return $this->render('Modulo6_Portafolio/editar', ['pageTitle' => 'Editar Portafolio']); }
    public function actualizar() { /* TODO: Módulo 6 */ }
}
