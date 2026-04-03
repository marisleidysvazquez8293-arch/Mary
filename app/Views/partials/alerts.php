<?php
/**
 * partials/alerts.php — Mensajes flash estandarizados
 * 
 * Tipos soportados: success, error, warning, info
 * Se usan con: redirect()->with('success', 'Mensaje')
 *              redirect()->with('errors', ['campo' => 'Error'])
 */
$tipos = [
    'success' => ['bg-success', 'bi-check-circle-fill'],
    'error'   => ['bg-danger',  'bi-x-circle-fill'],
    'warning' => ['bg-warning text-dark', 'bi-exclamation-triangle-fill'],
    'info'    => ['bg-info text-dark',    'bi-info-circle-fill'],
];
?>

<div class="udg-alerts-container" role="alert" aria-live="polite">
    <div class="container-xl">

        <?php foreach ($tipos as $tipo => [$cls, $icon]): ?>
            <?php if ($msg = session()->getFlashdata($tipo)): ?>
                <div class="alert <?= $cls ?> alert-dismissible d-flex align-items-center gap-2 fade show shadow-sm" id="alert-<?= $tipo ?>">
                    <i class="bi <?= $icon ?> flex-shrink-0"></i>
                    <span><?= esc($msg) ?></span>
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
                </div>
            <?php endif; ?>
        <?php endforeach; ?>

        <!-- Errores de validación (array) -->
        <?php if ($errors = session()->getFlashdata('errors')): ?>
            <div class="alert bg-danger alert-dismissible fade show shadow-sm">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                <strong>Corrige los siguientes errores:</strong>
                <ul class="mb-0 mt-1 ps-3">
                    <?php foreach ((array)$errors as $error): ?>
                        <li><?= esc($error) ?></li>
                    <?php endforeach; ?>
                </ul>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
            </div>
        <?php endif; ?>

    </div>
</div>
