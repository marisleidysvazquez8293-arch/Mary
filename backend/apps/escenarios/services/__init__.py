"""
Servicios de escenarios SADE (PASO 4).

- EscenarioExecutionService: ejecución / reejecución / mapa / consulta celda
- SensitivityService: Tabla 4.3 E0–E8 + Jaccard Favorable+Óptimo
- ScenarioTraceabilityService: hash SHA-256 + ZIP reproducibilidad (RNF-002)
"""
from apps.escenarios.services.execution import (
    SENSITIVITY_IDS,
    EscenarioExecutionService,
    ExecutionOutput,
    ReexecuteOutput,
)
from apps.escenarios.services.sensitivity import (
    TABLA_43_BLOCK_PERTURBATIONS,
    SensitivityPair,
    SensitivityReport,
    SensitivityService,
)
from apps.escenarios.services.traceability import (
    SADE_SOFTWARE_VERSION,
    ScenarioTraceabilityService,
)

__all__ = [
    "EscenarioExecutionService",
    "ExecutionOutput",
    "ReexecuteOutput",
    "SensitivityService",
    "SensitivityReport",
    "SensitivityPair",
    "ScenarioTraceabilityService",
    "SADE_SOFTWARE_VERSION",
    "SENSITIVITY_IDS",
    "TABLA_43_BLOCK_PERTURBATIONS",
]
