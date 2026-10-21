"""DRF permission stubs for SADE roles (PASO 4)."""
from __future__ import annotations

from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.usuarios.roles import (
    ADMINISTRADOR_TECNICO,
    ALL_ROLES,
    ANALISTA_TERRITORIAL,
    AUDITOR,
    ROLE_CAPABILITIES,
)


def user_roles(user) -> set[str]:
    """Resolve roles from Django groups and optional user.sade_roles."""
    if user is None or not getattr(user, "is_authenticated", False):
        return set()
    if getattr(user, "is_superuser", False):
        return set(ALL_ROLES)
    roles: set[str] = set()
    extra = getattr(user, "sade_roles", None)
    if extra:
        roles.update(extra)
    if hasattr(user, "groups"):
        roles.update(user.groups.values_list("name", flat=True))
    return roles


def has_capability(user, capability: str) -> bool:
    roles = user_roles(user)
    for role in roles:
        if capability in ROLE_CAPABILITIES.get(role, frozenset()):
            return True
    return False


class HasSadeRole(BasePermission):
    """Require at least one SADE role (or staff/superuser)."""

    message = "Se requiere un rol SADE (Administrador Técnico / Analista Territorial / Auditor)."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True
        return bool(user_roles(user) & set(ALL_ROLES))


class CanExecuteEscenario(BasePermission):
    """Execute / re-execute — Analista or Administrador."""

    message = "Se requiere rol Analista Territorial o Administrador Técnico."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return HasSadeRole().has_permission(request, view)
        return has_capability(request.user, "execute") or getattr(
            request.user, "is_staff", False
        )


class CanAuditRead(BasePermission):
    """Read scenarios / maps / sensitivity — any SADE role including Auditor."""

    def has_permission(self, request, view):
        return has_capability(request.user, "audit_read") or getattr(
            request.user, "is_staff", False
        ) or getattr(request.user, "is_superuser", False)


# Convenience exports
__all__ = [
    "HasSadeRole",
    "CanExecuteEscenario",
    "CanAuditRead",
    "user_roles",
    "has_capability",
    "ADMINISTRADOR_TECNICO",
    "ANALISTA_TERRITORIAL",
    "AUDITOR",
]
