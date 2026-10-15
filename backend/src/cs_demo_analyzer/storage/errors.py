"""Storage-layer exceptions.

They subclass the domain ``AppError`` so the coordinator's existing error
translation keeps working and the UI receives stable codes.
"""

from __future__ import annotations

from ..domain.contracts import AppError


class StorageError(AppError):
    def __init__(
        self,
        message: str,
        *,
        code: str = "INTERNAL_ERROR",
        stage: str = "storage",
        retryable: bool = False,
    ) -> None:
        super().__init__(code=code, message=message, stage=stage, retryable=retryable)


class CatalogError(StorageError):
    def __init__(self, message: str, *, code: str = "INTERNAL_ERROR", retryable: bool = False) -> None:
        super().__init__(message, code=code, stage="catalog", retryable=retryable)


class ArtifactInvalid(StorageError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="ARTIFACT_INVALID", stage="publish")
