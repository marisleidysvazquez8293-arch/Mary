"""
Usuarios / RBAC (ADM) — thin PASO 4 stubs.

Prefer django.contrib.auth User + Groups named after apps.usuarios.roles.
No custom Usuario table yet; RoleLabel documents ERS role names for admin.
"""
from django.db import models

from apps.usuarios.roles import ALL_ROLES


class RoleLabel(models.TextChoices):
    """ERS role names — use as Django Group.name values."""

    ADMINISTRADOR_TECNICO = ALL_ROLES[0], ALL_ROLES[0]
    ANALISTA_TERRITORIAL = ALL_ROLES[1], ALL_ROLES[1]
    AUDITOR = ALL_ROLES[2], ALL_ROLES[2]
