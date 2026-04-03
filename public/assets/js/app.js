/**
 * UDG-Proyectos: JavaScript global
 * app.js — Funciones disponibles en todas las páginas
 */

(function () {
  'use strict';

  // ==========================================================
  // 1. Notificaciones — polling AJAX cada 60 seg
  // ==========================================================
  function checkNotifications() {
    const bell = document.getElementById('notifBell');
    if (!bell) return;

    fetch(BASE_URL + 'notificaciones/api/no-leidas', {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (!data) return;
        const badge = document.getElementById('notifCount');
        if (badge) {
          const count = data.data?.count ?? 0;
          badge.textContent = count > 99 ? '99+' : count;
          badge.classList.toggle('d-none', count === 0);
        }
      })
      .catch(() => {/* silencioso */});
  }

  // ==========================================================
  // 2. Confirmación de acciones peligrosas
  // ==========================================================
  function initConfirmActions() {
    document.querySelectorAll('[data-confirm]').forEach(el => {
      el.addEventListener('click', function (e) {
        const msg = this.dataset.confirm || '¿Estás seguro?';
        if (!confirm(msg)) e.preventDefault();
      });
    });
  }

  // ==========================================================
  // 3. Auto-cierre de alertas flash (5 seg)
  // ==========================================================
  function autoCloseAlerts() {
    document.querySelectorAll('.alert.fade.show').forEach(alert => {
      setTimeout(() => {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        if (bsAlert) bsAlert.close();
      }, 5000);
    });
  }

  // ==========================================================
  // 4. Resaltar enlace activo en el navbar
  // ==========================================================
  function highlightActiveNav() {
    const path = window.location.pathname;
    document.querySelectorAll('.udg-navbar .nav-link').forEach(link => {
      const href = link.getAttribute('href');
      if (href && path.startsWith(href.replace(BASE_URL, '/'))) {
        link.classList.add('active');
      }
    });
  }

  // ==========================================================
  // 5. Tooltips Bootstrap (inicializar globalmente)
  // ==========================================================
  function initTooltips() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
      bootstrap.Tooltip.getOrCreateInstance(el);
    });
  }

  // ==========================================================
  // 6. Helpers AJAX globales
  // ==========================================================

  /**
   * Obtener token CSRF del meta tag o de un input oculto
   */
  window.getCsrfToken = function () {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return { name: meta.name, value: meta.content };
    const input = document.querySelector('input[name^="csrf_"]');
    if (input) return { name: input.name, value: input.value };
    return null;
  };

  /**
   * POST JSON con CSRF automático
   */
  window.postJSON = function (url, datos) {
    const csrf = window.getCsrfToken();
    const body = csrf ? { ...datos, [csrf.name]: csrf.value } : datos;
    return fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: JSON.stringify(body),
    }).then(r => r.json());
  };

  // ==========================================================
  // INIT
  // ==========================================================
  document.addEventListener('DOMContentLoaded', () => {
    initConfirmActions();
    autoCloseAlerts();
    highlightActiveNav();
    initTooltips();

    // Notificaciones solo si hay usuario logueado (el elemento existe)
    if (document.getElementById('notifBell')) {
      checkNotifications();
      setInterval(checkNotifications, 60000);
    }
  });

})();
