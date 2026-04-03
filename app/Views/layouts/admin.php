<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= esc($pageTitle ?? 'Admin — UDG-Proyectos') ?></title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
    <link href="<?= base_url('assets/css/app.css') ?>" rel="stylesheet">
</head>
<body class="udg-body bg-light">
    <?= view('partials/navbar') ?>
    <?= view('partials/alerts') ?>
    
    <div class="container-fluid">
        <div class="row min-vh-100">
            <!-- Sidebar Admin -->
            <nav class="col-md-3 col-lg-2 d-md-block bg-udg-dark text-white sidebar collapse">
                <div class="position-sticky pt-3">
                    <ul class="nav flex-column gap-2 p-2">
                        <li class="nav-item">
                            <a class="nav-link text-white" href="<?= base_url('dashboard') ?>">
                                <i class="bi bi-speedometer2 me-2"></i> Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link text-white" href="<?= base_url('admin/usuarios') ?>">
                                <i class="bi bi-people me-2"></i> Usuarios
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link text-white" href="<?= base_url('admin/roles') ?>">
                                <i class="bi bi-shield-lock me-2"></i> Roles
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link text-white" href="<?= base_url('admin/configuracion') ?>">
                                <i class="bi bi-gear me-2"></i> Configuración
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 py-4">
                <?= view($content_view, $this->data ?? []) ?>
            </main>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="<?= base_url('assets/js/app.js') ?>"></script>
</body>
</html>
