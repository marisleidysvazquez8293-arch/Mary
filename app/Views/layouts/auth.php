<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= esc($pageTitle ?? 'UDG-Proyectos') ?></title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
    <link href="<?= base_url('assets/css/app.css') ?>" rel="stylesheet">
    <link href="<?= base_url('assets/css/auth.css') ?>" rel="stylesheet">
</head>
<body class="udg-auth-body">
    <div class="udg-auth-wrapper">
        <!-- Logo -->
        <div class="udg-auth-logo text-center mb-4">
            <img src="<?= base_url('assets/images/udg-logo.png') ?>" alt="UDG" height="60" onerror="this.style.display='none'">
            <h1 class="udg-auth-title">UDG-<span>Proyectos</span></h1>
            <p class="udg-auth-subtitle">Sistema de Seguimiento de Proyectos y Tesis</p>
        </div>

        <!-- Mensajes flash -->
        <?= view('partials/alerts') ?>

        <!-- Contenido de auth (login/registro/etc) -->
        <div class="udg-auth-card card shadow-lg">
            <div class="card-body p-4 p-md-5">
                <?= view($content_view, $this->data ?? []) ?>
            </div>
        </div>

        <p class="text-center text-muted mt-3 small">
            &copy; <?= date('Y') ?> Universidad de Guadalajara. Todos los derechos reservados.
        </p>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="<?= base_url('assets/js/app.js') ?>"></script>
</body>
</html>
