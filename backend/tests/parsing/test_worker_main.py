"""Behavior tests for the isolated worker's stdin/stdout protocol.

The worker is launched exactly as the coordinator launches it. These assert the
observable contract: stdout is one WorkerResult JSON line, failures carry a
structured ErrorResponse, and the process exits non-zero on failure. No real
demo is parsed.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from cs_demo_analyzer.domain.contracts import WorkerResult

WORKER = [sys.executable, "-m", "cs_demo_analyzer.worker.main"]


def _run(payload: bytes) -> subprocess.CompletedProcess:
    return subprocess.run(WORKER, input=payload, capture_output=True, timeout=120)


def _result(process: subprocess.CompletedProcess) -> WorkerResult:
    lines = process.stdout.decode("utf-8").splitlines()
    assert len(lines) == 1, f"expected one stdout line, got {len(lines)}"
    return WorkerResult.model_validate_json(lines[0])


def test_empty_stdin_reports_protocol_error():
    process = _run(b"")
    assert process.returncode != 0
    result = _result(process)
    assert result.error is not None
    assert result.error.code == "WORKER_PROTOCOL"
    assert result.manifest_path is None


def test_malformed_request_reports_protocol_error():
    process = _run(b"{not json}\n")
    assert process.returncode != 0
    assert _result(process).error.code == "WORKER_PROTOCOL"


def test_missing_input_reports_structured_error(tmp_path):
    request = {
        "protocol_version": 1,
        "job_id": "job-1",
        "generation_id": "gen-1",
        "demo_id": "demo-1",
        "input_path": str(tmp_path / "missing.dem"),
        "output_dir": str(tmp_path / "out"),
        "profile": "foundation-v1",
    }
    process = _run(json.dumps(request).encode() + b"\n")
    assert process.returncode != 0
    error = _result(process).error
    assert error is not None
    assert error.code == "SOURCE_MISSING"
    assert error.stage == "parse"
    assert error.retryable is True


def test_invalid_demo_reports_invalid_demo(tmp_path):
    bad = tmp_path / "bad.dem"
    bad.write_bytes(b"not a PBDEMS2 demo" * 4)
    request = {
        "protocol_version": 1,
        "job_id": "job-1",
        "generation_id": "gen-1",
        "demo_id": "demo-1",
        "input_path": str(bad),
        "output_dir": str(tmp_path / "out"),
        "profile": "foundation-v1",
    }
    process = _run(json.dumps(request).encode() + b"\n")
    assert process.returncode != 0
    error = _result(process).error
    assert error is not None
    assert error.code in {"INVALID_DEMO", "PARSE_FAILED"}


@pytest.mark.parametrize("payload", [b"", b"{}\n"])
def test_worker_never_emits_extra_stdout(payload: bytes):
    process = _run(payload)
    assert process.stdout.decode("utf-8").count("\n") == 1
