from __future__ import annotations

from dataclasses import dataclass

from app.core.errors.codes import ErrorCode


@dataclass(slots=True)
class AppError(Exception):
    code: ErrorCode
    message: str
    target: str | None = None
    suggestion: str | None = None

    def __str__(self) -> str:
        return self.message
