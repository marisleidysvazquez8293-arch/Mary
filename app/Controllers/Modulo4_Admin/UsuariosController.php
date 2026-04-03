<?php
namespace App\Controllers\Modulo4_Admin;
use App\Controllers\BaseController;
/** Gestión CRUD de usuarios del sistema */
class UsuariosController extends BaseController {
    public function index(): string { return $this->render('Modulo4_Admin/usuarios', ['pageTitle' => 'Usuarios']); }
    public function nuevo(): string { return $this->render('Modulo4_Admin/usuario_form', ['pageTitle' => 'Nuevo Usuario']); }
    public function crear() { /* TODO: Módulo 4 */ }
    public function editar(int $id): string { return $this->render('Modulo4_Admin/usuario_form', ['pageTitle' => 'Editar Usuario', 'id' => $id]); }
    public function actualizar(int $id) { /* TODO: Módulo 4 */ }
    public function eliminar(int $id) { /* TODO: Módulo 4 — soft delete */ }
}
