"""
Thin RBAC role constants for SADE (PASO 4).

Map to Django Group names or request.user attributes. Full Usuario/Rol
models remain deferred — use these hooks in DRF permissions.
"""

from __future__ import annotations

# Canonical role labels (ERS)
ADMINISTRADOR_TECNICO = "Administrador Técnico"
ANALISTA_TERRITORIAL = "Analista Territorial"
AUDITOR = "Auditor"

ALL_ROLES = (
    ADMINISTRADOR_TECNICO,
    ANALISTA_TERRITORIAL,
    AUDITOR,
)

# Capabilities (documentation / future fine-grained checks)
ROLE_CAPABILITIES: dict[str, frozenset[str]] = {
    ADMINISTRADOR_TECNICO: frozenset(
        {"execute", "reejecutar", "sensibilidad", "map", "audit_read", "admin"}
    ),
    ANALISTA_TERRITORIAL: frozenset(
        {"execute", "reejecutar", "sensibilidad", "map", "audit_read"}
    ),
    AUDITOR: frozenset({"map", "audit_read", "sensibilidad"}),
}
