<div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="h3 mb-0 text-udg-blue">Panel de Estudiante</h2>
        <a href="<?= base_url('envio/nuevo') ?>" class="btn btn-primary"><i class="bi bi-plus-lg me-2"></i>Nuevo Proyecto</a>
    </div>

    <div class="row g-4">
        <div class="col-md-4">
            <div class="udg-card">
                <div class="d-flex align-items-center mb-3">
                    <div class="bg-primary text-white p-2 rounded me-3">
                        <i class="bi bi-folder2-open fs-4"></i>
                    </div>
                    <h5 class="mb-0">Mis Proyectos</h5>
                </div>
                <h2 class="display-4 fw-bold">0</h2>
                <a href="<?= base_url('envio') ?>" class="text-decoration-none small">Ver todos ></a>
            </div>
        </div>
        <div class="col-md-4">
            <div class="udg-card">
                <div class="d-flex align-items-center mb-3">
                    <div class="bg-warning text-white p-2 rounded me-3">
                        <i class="bi bi-clock-history fs-4"></i>
                    </div>
                    <h5 class="mb-0">En Revisión</h5>
                </div>
                <h2 class="display-4 fw-bold">0</h2>
                <span class="text-muted small">Esperando dictamen</span>
            </div>
        </div>
        <div class="col-md-4">
            <div class="udg-card">
                <div class="d-flex align-items-center mb-3">
                    <div class="bg-success text-white p-2 rounded me-3">
                        <i class="bi bi-check-circle fs-4"></i>
                    </div>
                    <h5 class="mb-0">Aprobados</h5>
                </div>
                <h2 class="display-4 fw-bold">0</h2>
                <span class="text-muted small">Listos para repositorio</span>
            </div>
        </div>
    </div>
</div>
