from __future__ import annotations

import os
import shutil
import tomllib
from dataclasses import dataclass
from pathlib import Path

from .domain.contracts import AppError


@dataclass(frozen=True)
class Settings:
    data_root: Path
    install_path: Path | None = None
    source2viewer: Path | None = None
    settle_seconds: float = 10.0
    scan_seconds: float = 60.0
    poll_seconds: float = 2.0
    reserve_bytes: int = 256 * 1024 * 1024
    worker_timeout: float = 300.0

    @classmethod
    def load(cls, data_root: str | None = None, config_path: str | None = None, **overrides) -> Settings:
        config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
        config = Path(config_path) if config_path else config_home / "cs-demo-analyzer/config.toml"
        values = tomllib.loads(config.read_text()) if config.is_file() else {}
        chosen = data_root or os.environ.get("CSDA_DATA_ROOT") or values.pop("data_root", None)
        # pop even when a higher-priority override wins
        values.pop("data_root", None)
        if chosen is None:
            chosen = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "cs-demo-analyzer"
        path = Path(chosen).expanduser()
        if not path.is_absolute():
            raise AppError("INVALID_CONFIG", "Data root must be an absolute path", "configuration")
        for key, value in overrides.items():
            if value is not None:
                values[key] = value
        for key in ("install_path", "source2viewer"):
            if values.get(key):
                values[key] = Path(values[key]).expanduser().resolve()
        result = cls(data_root=path.resolve(), **values)
        if min(result.settle_seconds, result.scan_seconds, result.poll_seconds, result.reserve_bytes, result.worker_timeout) < 0 or result.poll_seconds == 0 or result.scan_seconds == 0:
            raise AppError("INVALID_CONFIG", "Timing and reserve settings must be non-negative, scan/poll positive", "configuration")
        return result

    def prepare(self) -> None:
        self.data_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        for name in ("raw", "datasets", "staging", "assets", "logs"):
            (self.data_root / name).mkdir(exist_ok=True, mode=0o700)

    def check_space(self, source_bytes: int, *, copying: bool) -> None:
        # Space for raw snapshot (when copying), an intentionally conservative
        # derived-data allowance of one input size, and an untouched reserve.
        required = source_bytes * (2 if copying else 1) + self.reserve_bytes
        free = shutil.disk_usage(self.data_root).free
        if free < required:
            raise AppError("DISK_FULL", f"Data root needs {required:,} free bytes; {free:,} available", "snapshot" if copying else "parse", True)
