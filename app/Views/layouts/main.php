<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="<?= $metaDescription ?? 'Sistema de Seguimiento de Proyectos y Tesis — Universidad de Guadalajara' ?>">
    <title><?= esc($pageTitle ?? 'UDG-Proyectos') ?></title>

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">

    <!-- CSS del sistema -->
    <link href="<?= base_url('assets/css/app.css') ?>" rel="stylesheet">

    <!-- CSS del módulo actual (opcional) -->
    <?php if (isset($moduleCSS)): ?>
    <link href="<?= base_url('assets/css/modules/' . $moduleCSS) ?>" rel="stylesheet">
    <?php endif; ?>
</head>
<body class="udg-body <?= esc($bodyClass ?? '') ?>">

    <!-- ====== NAVBAR ====== -->
    <?= view('partials/navbar') ?>

    <!-- ====== ALERTS / MENSAJES FLASH ====== -->
    <?= view('partials/alerts') ?>

    <!-- ====== CONTENIDO PRINCIPAL ====== -->
    <main class="udg-main">
        <?= view($content_view, $this->data ?? []) ?>
    </main>

    <!-- ====== FOOTER ====== -->
    <?= view('partials/footer') ?>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <!-- JS global del sistema -->
    <script src="<?= base_url('assets/js/app.js') ?>"></script>

    <!-- JS del módulo actual (opcional) -->
    <?php if (isset($moduleJS)): ?>
    <script src="<?= base_url('assets/js/modules/' . $moduleJS) ?>"></script>
    <?php endif; ?>
</body>
</html>
