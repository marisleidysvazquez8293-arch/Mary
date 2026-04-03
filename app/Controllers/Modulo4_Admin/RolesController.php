<?php
namespace App\Controllers\Modulo4_Admin;
use App\Controllers\BaseController;
/** Gestión de roles y permisos RBAC */
class RolesController extends BaseController {
    public function index(): string { return $this->render('Modulo4_Admin/roles', ['pageTitle' => 'Roles y Permisos']); }
}
