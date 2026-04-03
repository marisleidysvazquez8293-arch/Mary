<?php
namespace App\Controllers\Modulo7_Herramientas;
use App\Controllers\BaseController;
/**
 * HerramientasController — Módulo 7: Herramientas Comunitarias
 * RAMA: modulo/herramientas | RESPONSABLE: Estudiante 7
 * Implementar: repositorio de software/datasets, subida, búsqueda, descarga, licencias
 */
class HerramientasController extends BaseController {
    public function index(): string { return $this->render('Modulo7_Herramientas/index', ['pageTitle' => 'Herramientas Comunitarias']); }
    public function software(): string { return $this->render('Modulo7_Herramientas/software', ['pageTitle' => 'Software']); }
    public function datasets(): string { return $this->render('Modulo7_Herramientas/datasets', ['pageTitle' => 'Datasets']); }
    public function subir() { /* TODO: Módulo 7 — archivos + metadatos */ }
}
