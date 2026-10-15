"""Isolated parser child: one JSON request in, one WorkerResult JSON out.

Launched by the coordinator as ``python -m cs_demo_analyzer.worker.main`` in its
own session with stdin closed after the request. stdout carries exactly one
``WorkerResult`` JSON object plus a newline; stderr carries bounded diagnostics.
The child never logs player names or private data. On any failure it emits a
structured ``ErrorResponse`` and exits non-zero.
"""

from __future__ import annotations

import ctypes
import errno
import os
import signal
import sys
from pathlib import Path

from ..domain.contracts import AppError, ErrorResponse, ExtractionRequest, WorkerResult

_MAX_MESSAGE = 2000
_PR_SET_PDEATHSIG = 1


class _ProtocolError(Exception):
    """The request on stdin was absent or not an ExtractionRequest."""


def _install_parent_death_signal() -> None:
    """Ask Linux to SIGTERM this child when its parent dies.

    Set as early as possible; the caller re-checks liveness afterwards to close
    the race where the parent died before the signal was installed.
    """
    if not sys.platform.startswith("linux"):
        return
    try:
        libc = ctypes.CDLL("libc.so.6", use_errno=True)
        libc.prctl(_PR_SET_PDEATHSIG, signal.SIGTERM, 0, 0, 0)
    except Exception:  # pragma: no cover - best-effort hardening only
        pass


def _read_request() -> ExtractionRequest:
    raw = sys.stdin.buffer.read()
    if not raw.strip():
        raise _ProtocolError("no extraction request received on stdin")
    line = raw.split(b"\n", 1)[0]
    try:
        return ExtractionRequest.model_validate_json(line)
    except ValueError as exc:
        raise _ProtocolError("stdin is not a valid extraction request") from exc


def _bound(message: str) -> str:
    text = message.strip() or "unknown error"
    return text if len(text) <= _MAX_MESSAGE else text[: _MAX_MESSAGE - 3] + "..."


def _error_from(exc: BaseException) -> ErrorResponse:
    if isinstance(exc, AppError):
        return ErrorResponse(code=exc.code, message=_bound(exc.message), stage=exc.stage, retryable=exc.retryable)
    if isinstance(exc, OSError) and exc.errno == errno.ENOSPC:
        return ErrorResponse(code="DISK_FULL", message="No space left while extracting", stage="parse", retryable=True)
    if isinstance(exc, MemoryError):
        return ErrorResponse(code="RESOURCE_LIMIT", message="Out of memory during extraction", stage="parse", retryable=True)
    return ErrorResponse(
        code="PARSE_FAILED",
        message=_bound(f"{type(exc).__name__}: {exc}"),
        stage="parse",
    )


def _emit(result: WorkerResult) -> None:
    sys.stdout.buffer.write(result.model_dump_json().encode("utf-8") + b"\n")
    sys.stdout.buffer.flush()


def _fail(error: ErrorResponse) -> int:
    _emit(WorkerResult(error=error))
    print(f"parser failed: {error.code} ({error.stage})", file=sys.stderr, flush=True)
    return 1


def main() -> int:
    _install_parent_death_signal()
    try:
        request = _read_request()
    except _ProtocolError as exc:
        return _fail(ErrorResponse(code="WORKER_PROTOCOL", message=_bound(str(exc)), stage="parse"))

    if request.parent_pid is not None and os.getppid() != request.parent_pid:
        print("parent process is gone; aborting before extraction", file=sys.stderr, flush=True)
        return 1

    try:
        from ..parsing.awpy_adapter import MANIFEST_NAME, extract

        extract(request)
    except Exception as exc:  # every failure must be reported structurally
        return _fail(_error_from(exc))

    _emit(WorkerResult(manifest_path=str(Path(request.output_dir) / MANIFEST_NAME)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
