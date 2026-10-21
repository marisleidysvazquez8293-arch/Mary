"""
Servicios multicriterio SADE.

Reexporta AHPService / CLPService para:

    from apps.multicriterio.services import AHPService
"""
from apps.multicriterio.services.ahp_service import (
    DEFAULT_CR_THRESHOLD,
    DEFAULT_PANEL_INCONSISTENT_PCT,
    AHPResult,
    AHPService,
    PanelConsistencyReport,
    SAATY_RI,
)
from apps.multicriterio.services.clp_service import (
    CLASS_LABELS,
    DEFAULT_BREAKS,
    CLPResult,
    CLPService,
    CandidatePolygon,
    SuitabilityClass,
)

__all__ = [
    "AHPService",
    "AHPResult",
    "PanelConsistencyReport",
    "SAATY_RI",
    "DEFAULT_CR_THRESHOLD",
    "DEFAULT_PANEL_INCONSISTENT_PCT",
    "CLPService",
    "CLPResult",
    "SuitabilityClass",
    "CLASS_LABELS",
    "CandidatePolygon",
    "DEFAULT_BREAKS",
]
