<div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="h3 mb-0 text-udg-blue">Panel de Administración</h2>
    </div>

    <div class="row g-4">
        <div class="col-md-3">
            <div class="udg-card bg-primary text-white text-center">
                <i class="bi bi-people-fill fs-1 d-block mb-2"></i>
                <h5 class="mb-0">Usuarios</h5>
                <a href="<?= base_url('admin/usuarios') ?>" class="text-white small text-decoration-underline mt-2 d-inline-block">Gestionar</a>
            </div>
        </div>
        <div class="col-md-3">
            <div class="udg-card bg-success text-white text-center">
                <i class="bi bi-shield-lock-fill fs-1 d-block mb-2"></i>
                <h5 class="mb-0">Roles</h5>
                <a href="<?= base_url('admin/roles') ?>" class="text-white small text-decoration-underline mt-2 d-inline-block">Gestionar</a>
            </div>
        </div>
        <div class="col-md-3">
            <div class="udg-card bg-warning text-dark text-center">
                <i class="bi bi-gear-fill fs-1 d-block mb-2"></i>
                <h5 class="mb-0">Configuración</h5>
                <a href="<?= base_url('admin/configuracion') ?>" class="text-dark small text-decoration-underline mt-2 d-inline-block">Ver</a>
            </div>
        </div>
        <div class="col-md-3">
            <div class="udg-card bg-secondary text-white text-center">
                <i class="bi bi-pie-chart-fill fs-1 d-block mb-2"></i>
                <h5 class="mb-0">Reportes</h5>
                <a href="#" class="text-white small text-decoration-underline mt-2 d-inline-block">Generar</a>
            </div>
        </div>
    </div>
</div>
