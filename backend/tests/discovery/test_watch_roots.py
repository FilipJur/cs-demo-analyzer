"""Behaviour of root watching: notification hints, re-arming and stopping."""

from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

from cs_demo_analyzer.discovery import watcher
from cs_demo_analyzer.discovery.watcher import watch_roots
from cs_demo_analyzer.domain.contracts import RootRecord

DEMO_BYTES = b"PBDEMS2\0demo"
NOTIFY_TIMEOUT = 20.0
STOP_TIMEOUT = 20.0


class _Recorder:
    """Reconciliation hook that counts and timestamps its calls."""

    def __init__(self) -> None:
        self.calls: list[float] = []

    def __call__(self) -> None:
        self.calls.append(time.monotonic())

    @property
    def count(self) -> int:
        return len(self.calls)


@pytest.fixture
def fast_timers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Shorten watcher timing constants so tests do not wait on production delays."""
    monkeypatch.setattr(watcher, "DEBOUNCE_MS", 50)
    monkeypatch.setattr(watcher, "STEP_MS", 20)
    monkeypatch.setattr(watcher, "RUST_TIMEOUT_MS", 200)
    monkeypatch.setattr(watcher, "REARM_SECONDS", 0.2)


def _expect(condition, timeout: float = NOTIFY_TIMEOUT) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.05)
    return condition()


def _start(roots: list[RootRecord], stop_event: threading.Event, on_change) -> threading.Thread:
    thread = threading.Thread(target=watch_roots, args=(roots, stop_event, on_change), daemon=True)
    thread.start()
    return thread


def _stop(thread: threading.Thread, stop_event: threading.Event) -> None:
    stop_event.set()
    thread.join(timeout=STOP_TIMEOUT)
    assert not thread.is_alive()


def test_watch_notifies_on_new_demo_without_touching_the_root(tmp_path: Path, fast_timers: None) -> None:
    root_dir = tmp_path / "replays"
    root_dir.mkdir()
    stop_event = threading.Event()
    recorder = _Recorder()
    thread = _start([RootRecord(id=1, path=str(root_dir), recursive=True)], stop_event, recorder)
    try:
        assert _expect(lambda: recorder.count >= 1), "watcher was never armed"
        armed = recorder.count
        created: list[str] = []
        for index in range(4):
            demo = root_dir / f"match{index}.dem"
            demo.write_bytes(DEMO_BYTES)
            created.append(demo.name)
            if _expect(lambda: recorder.count > armed):
                break

        assert recorder.count > armed, "no notification for the new demo"
        assert sorted(path.name for path in root_dir.iterdir()) == sorted(created)
    finally:
        _stop(thread, stop_event)


def test_missing_root_waits_then_rearms(tmp_path: Path, fast_timers: None) -> None:
    missing = tmp_path / "not-yet"
    stop_event = threading.Event()
    recorder = _Recorder()
    thread = _start([RootRecord(id=2, path=str(missing), recursive=True)], stop_event, recorder)
    try:
        time.sleep(0.6)
        assert recorder.calls == []
        assert not missing.exists()

        missing.mkdir()
        (missing / "match.dem").write_bytes(DEMO_BYTES)

        assert _expect(lambda: recorder.count >= 1), "a root that appeared was never picked up"
        time.sleep(0.3)
        assert recorder.count <= 15, "reconciliation was called repeatedly instead of on change"
    finally:
        _stop(thread, stop_event)


def test_watch_groups_split_by_recursive_policy(tmp_path: Path) -> None:
    replays = tmp_path / "replays"
    replays.mkdir()
    csgo = tmp_path / "csgo"
    csgo.mkdir()
    groups = watcher._watch_groups(
        [
            RootRecord(id=1, path=str(replays), recursive=True),
            RootRecord(id=2, path=str(replays), recursive=False),
            RootRecord(id=3, path=str(csgo), recursive=False),
            RootRecord(id=4, path=str(tmp_path / "missing"), recursive=True),
        ]
    )

    assert [path.name for path in groups[True]] == ["replays"]
    assert [path.name for path in groups[False]] == ["csgo"]
    assert all(path.is_dir() for path in (*groups[True], *groups[False]))


def test_watch_failure_is_reported_and_retried(
    tmp_path: Path, fast_timers: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    root_dir = tmp_path / "replays"
    root_dir.mkdir()
    attempts: list[tuple] = []

    def failing_watch(*paths, **kwargs):
        attempts.append(paths)
        raise OSError("watch limit reached")
        yield  # pragma: no cover - keeps this a generator

    monkeypatch.setattr(watcher.watchfiles, "watch", failing_watch)
    stop_event = threading.Event()
    recorder = _Recorder()
    thread = _start([RootRecord(id=5, path=str(root_dir), recursive=True)], stop_event, recorder)
    try:
        assert _expect(lambda: len(attempts) >= 2), "a failed watch was not retried"
        assert recorder.count >= 2, "a failed watch was not reported to the caller"
        time.sleep(0.4)
        assert len(attempts) <= 40, "the retry loop is spinning"
    finally:
        _stop(thread, stop_event)
