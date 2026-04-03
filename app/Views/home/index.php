<div class="container py-5">
    <div class="row align-items-center justify-content-center text-center">
        <div class="col-lg-8">
            <h1 class="display-4 fw-bold text-udg-blue mb-4">Bienvenido a UDG-<span class="text-udg-gold">Proyectos</span></h1>
            <p class="lead mb-5" style="color: var(--clr-muted)">La plataforma integral para el seguimiento, evaluación y publicación de proyectos y tesis de la Universidad de Guadalajara.</p>
            
            <div class="d-grid gap-3 d-sm-flex justify-content-sm-center mb-5">
                <?php if(session()->get('isLoggedIn')): ?>
                    <a href="<?= base_url('dashboard') ?>" class="btn btn-primary btn-lg px-4 gap-3">Ir a mi Panel</a>
                <?php else: ?>
                    <a href="<?= base_url('auth/login') ?>" class="btn btn-primary btn-lg px-4 gap-3">Iniciar Sesión</a>
                    <a href="<?= base_url('auth/registro') ?>" class="btn btn-outline-primary btn-lg px-4">Registrarse</a>
                <?php endif; ?>
            </div>

            <div class="row g-4 text-start">
                <div class="col-md-4">
                    <div class="udg-card h-100 text-center">
                        <i class="bi bi-journal-text fs-1 text-udg-blue mb-3"></i>
                        <h5>Gestión de Proyectos</h5>
                        <p class="text-muted small">Registra, edita y envía tus proyectos para evaluación de forma sencilla y estructurada.</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="udg-card h-100 text-center">
                        <i class="bi bi-check2-circle fs-1 text-udg-blue mb-3"></i>
                        <h5>Evaluación Transparente</h5>
                        <p class="text-muted small">Seguimiento en tiempo real del estatus de revisión y dictamen por parte del comité evaluador.</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="udg-card h-100 text-center">
                        <i class="bi bi-globe fs-1 text-udg-blue mb-3"></i>
                        <h5>Repositorio Público</h5>
                        <p class="text-muted small">Consulta proyectos y tesis terminados compartidos por la comunidad universitaria.</p>
                        <a href="<?= base_url('repositorio') ?>" class="btn btn-sm btn-outline-secondary mt-2">Explorar</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
