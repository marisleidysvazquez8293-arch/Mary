<!-- partials/navbar.php — Barra de navegación (cambia según rol) -->
<nav class="navbar navbar-expand-lg udg-navbar sticky-top">
    <div class="container-xl">
        <!-- Logo / Marca -->
        <a class="navbar-brand udg-brand d-flex align-items-center gap-2" href="<?= base_url('/') ?>">
            <img src="<?= base_url('assets/images/udg-logo.png') ?>" alt="UDG" height="36" onerror="this.style.display='none'">
            <span>UDG<strong>Proyectos</strong></span>
        </a>

        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMain">
            <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navMain">
            <ul class="navbar-nav me-auto gap-1">
                <li class="nav-item">
                    <a class="nav-link" href="<?= base_url('repositorio') ?>">
                        <i class="bi bi-archive"></i> Repositorio
                    </a>
                </li>

                <?php if ($isLoggedIn): ?>

                    <!-- Rol: estudiante -->
                    <?php if (is_role(['estudiante'])): ?>
                    <li class="nav-item">
                        <a class="nav-link" href="<?= base_url('envio') ?>">
                            <i class="bi bi-cloud-upload"></i> Mis Proyectos
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="<?= base_url('portafolio') ?>">
                            <i class="bi bi-person-vcard"></i> Portafolio
                        </a>
                    </li>
                    <?php endif; ?>

                    <!-- Rol: evaluador -->
                    <?php if (is_role(['evaluador','coordinador'])): ?>
                    <li class="nav-item">
                        <a class="nav-link" href="<?= base_url('aprobacion') ?>">
                            <i class="bi bi-clipboard2-check"></i> Evaluación
                        </a>
                    </li>
                    <?php endif; ?>

                    <!-- Rol: admin/superadmin -->
                    <?php if (is_role(['admin','superadmin'])): ?>
                    <li class="nav-item">
                        <a class="nav-link" href="<?= base_url('admin') ?>">
                            <i class="bi bi-gear"></i> Admin
                        </a>
                    </li>
                    <?php endif; ?>

                    <!-- Todos los logeados -->
                    <li class="nav-item">
                        <a class="nav-link" href="<?= base_url('herramientas') ?>">
                            <i class="bi bi-tools"></i> Herramientas
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="<?= base_url('social/ranking') ?>">
                            <i class="bi bi-trophy"></i> Ranking
                        </a>
                    </li>

                <?php endif; ?>
            </ul>

            <!-- Lado derecho -->
            <ul class="navbar-nav align-items-center gap-2">
                <?php if ($isLoggedIn): ?>

                    <!-- Campana de notificaciones -->
                    <li class="nav-item">
                        <a class="nav-link position-relative udg-notif-btn" href="<?= base_url('notificaciones') ?>"
                           id="notifBell" title="Notificaciones">
                            <i class="bi bi-bell fs-5"></i>
                            <span class="udg-notif-badge badge rounded-pill bg-danger d-none" id="notifCount">0</span>
                        </a>
                    </li>

                    <!-- Avatar + menú usuario -->
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle d-flex align-items-center gap-2 udg-user-menu"
                           href="#" role="button" data-bs-toggle="dropdown">
                            <?php if (! empty($currentUser['foto_perfil'])): ?>
                                <img src="<?= base_url('writable/uploads/' . esc($currentUser['foto_perfil'])) ?>"
                                     class="udg-avatar" alt="avatar">
                            <?php else: ?>
                                <div class="udg-avatar udg-avatar-initials">
                                    <?= strtoupper(mb_substr($currentUser['nombre'] ?? 'U', 0, 1)) ?>
                                </div>
                            <?php endif; ?>
                            <span class="d-none d-md-inline"><?= esc($currentUser['nombre'] ?? 'Usuario') ?></span>
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end shadow">
                            <li><h6 class="dropdown-header"><?= esc(nombre_completo($currentUser)) ?></h6></li>
                            <li><span class="dropdown-item-text text-muted small"><?= esc($currentUser['rol_nombre'] ?? '') ?></span></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="<?= base_url('portafolio') ?>"><i class="bi bi-person me-2"></i>Mi Perfil</a></li>
                            <li><a class="dropdown-item" href="<?= base_url('notificaciones/configuracion') ?>"><i class="bi bi-bell me-2"></i>Notificaciones</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="<?= base_url('auth/logout') ?>"><i class="bi bi-box-arrow-right me-2"></i>Cerrar sesión</a></li>
                        </ul>
                    </li>

                <?php else: ?>
                    <li class="nav-item">
                        <a class="btn btn-outline-primary btn-sm" href="<?= base_url('auth/login') ?>">Iniciar sesión</a>
                    </li>
                    <li class="nav-item">
                        <a class="btn btn-primary btn-sm" href="<?= base_url('auth/registro') ?>">Registrarse</a>
                    </li>
                <?php endif; ?>
            </ul>
        </div>
    </div>
</nav>
