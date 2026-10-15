"""Behaviour of demo candidate scanning."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from cs_demo_analyzer.discovery.watcher import scan_root
from cs_demo_analyzer.domain.contracts import AppError, RootRecord

DEMO_BYTES = b"PBDEMS2\0demo"


def _root(path: Path, *, recursive: bool = True, root_id: int = 7) -> RootRecord:
    return RootRecord(id=root_id, path=str(path), recursive=recursive)


def _demo(path: Path, payload: bytes = DEMO_BYTES) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return path


def _names(observations) -> list[str]:
    return [Path(observation.path).name for observation in observations]


def test_scan_reports_candidates_with_fingerprints(tmp_path: Path) -> None:
    base = tmp_path / "replays"
    _demo(base / "match.dem")
    for compression in (".gz", ".bz2", ".zst", ".zip"):
        _demo(base / f"other.dem{compression}", b"compressed")
    _demo(base / "match.dem.info", b"sidecar")
    _demo(base / "notes.txt", b"notes")
    _demo(base / "match.dem.bak", b"older")

    observations = scan_root(_root(base), tmp_path / "app-data")

    assert _names(observations) == ["match.dem", "other.dem.bz2", "other.dem.gz", "other.dem.zip", "other.dem.zst"]
    assert {observation.root_id for observation in observations} == {7}
    for observation in observations:
        info = Path(observation.path).stat()
        assert observation.fingerprint.size == info.st_size
        assert observation.fingerprint.device == info.st_dev
        assert observation.fingerprint.inode == info.st_ino
        assert observation.fingerprint.mtime_ns == info.st_mtime_ns
        assert observation.fingerprint.ctime_ns == info.st_ctime_ns


def test_scan_respects_recursive_policy(tmp_path: Path) -> None:
    base = tmp_path / "csgo"
    _demo(base / "direct.dem")
    _demo(base / "sub" / "deep" / "nested.dem")

    assert _names(scan_root(_root(base, recursive=False), tmp_path / "app-data")) == ["direct.dem"]
    assert _names(scan_root(_root(base), tmp_path / "app-data")) == ["direct.dem", "nested.dem"]


def test_scan_never_follows_symlinks(tmp_path: Path) -> None:
    base = tmp_path / "replays"
    base.mkdir()
    (base / "linked.dem").symlink_to(_demo(tmp_path / "elsewhere" / "real.dem"))
    (base / "broken.dem").symlink_to(tmp_path / "nowhere.dem")
    outside = tmp_path / "outside"
    _demo(outside / "hidden.dem")
    (base / "linked-dir").symlink_to(outside, target_is_directory=True)

    assert scan_root(_root(base), tmp_path / "app-data") == []


def test_scan_prunes_excluded_directory(tmp_path: Path) -> None:
    base = tmp_path / "replays"
    _demo(base / "kept.dem")
    app_data = tmp_path / "app-data"
    _demo(app_data / "raw" / "imported.dem")

    assert _names(scan_root(_root(base), app_data)) == ["kept.dem"]

    nested = tmp_path / "nested"
    _demo(nested / "a.dem")
    _demo(nested / "sub" / "b.dem")
    assert _names(scan_root(_root(nested), nested / "sub")) == ["a.dem"]


def test_scan_skips_root_inside_excluded_app_data(tmp_path: Path) -> None:
    app_data = tmp_path / "app-data"
    _demo(app_data / "staging" / "watched" / "x.dem")

    assert scan_root(_root(app_data / "staging" / "watched"), app_data) == []


def test_scan_missing_root_is_reported_without_creation(tmp_path: Path) -> None:
    missing = tmp_path / "gone"

    with pytest.raises(AppError) as failure:
        scan_root(_root(missing), tmp_path / "app-data")

    assert failure.value.code == "SOURCE_MISSING"
    assert failure.value.retryable is True
    assert not missing.exists()


def test_scan_rejects_root_that_is_a_file(tmp_path: Path) -> None:
    plain = _demo(tmp_path / "not-a-directory.dem")

    with pytest.raises(AppError) as failure:
        scan_root(_root(plain), tmp_path / "app-data")

    assert failure.value.code == "SOURCE_MISSING"


def test_scan_reports_unreadable_directory(tmp_path: Path) -> None:
    if os.geteuid() == 0:
        pytest.skip("directory permissions do not restrict root")
    base = tmp_path / "replays"
    locked = base / "locked"
    _demo(locked / "secret.dem")
    locked.chmod(0)
    try:
        with pytest.raises(AppError) as failure:
            scan_root(_root(base), tmp_path / "app-data")
        assert failure.value.code == "PERMISSION_DENIED"
        assert failure.value.retryable is True
    finally:
        locked.chmod(0o700)


def test_scan_skips_non_regular_files(tmp_path: Path) -> None:
    base = tmp_path / "replays"
    base.mkdir()
    os.mkfifo(base / "pipe.dem")
    (base / "empty.dem").write_bytes(b"")

    observations = scan_root(_root(base), tmp_path / "app-data")

    assert _names(observations) == ["empty.dem"]
    assert observations[0].fingerprint.size == 0
