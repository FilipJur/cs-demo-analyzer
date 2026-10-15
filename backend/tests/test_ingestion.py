import hashlib
from pathlib import Path

import pytest

from cs_demo_analyzer.config import Settings
from cs_demo_analyzer.domain.contracts import AppError, Fingerprint, Observation
from cs_demo_analyzer.ingestion.service import IngestionService, snapshot_source
from cs_demo_analyzer.storage.catalog import Catalog


def observe(path):
    return Observation(path=str(path), fingerprint=Fingerprint.from_path(path))


def settle(service, path):
    result = None
    for _ in range(3):
        result = service.consider(observe(path))
    return result


@pytest.fixture
def ingest(tmp_path):
    settings = Settings(tmp_path / "data", settle_seconds=0, reserve_bytes=0)
    settings.prepare()
    catalog = Catalog(settings.data_root)
    yield settings, catalog, IngestionService(settings, catalog)
    catalog.close()


def test_raw_preservation_duplicate_content_and_source_revision(ingest, tmp_path):
    settings, catalog, service = ingest
    source = tmp_path / "one.dem"
    original = b"PBDEMS2\0" + b"first revision"
    source.write_bytes(original)
    first = settle(service, source)
    assert first == hashlib.sha256(original).hexdigest()
    copy = tmp_path / "copy.dem"
    copy.write_bytes(original)
    assert settle(service, copy) == first
    assert len(catalog.list_demos()) == 1
    assert len(catalog.list_jobs()) == 1
    replacement = b"PBDEMS2\0" + b"completed later revision"
    source.write_bytes(replacement)
    assert service.consider(observe(source)) is None
    assert catalog.get_source(str(source)).demo_id is None
    second = settle(service, source)
    assert second != first
    assert Path(catalog.get_demo(first).raw_path).read_bytes() == original
    assert Path(catalog.get_demo(second).raw_path).read_bytes() == replacement
    assert source.read_bytes() == replacement


def test_early_sidecar_does_not_bypass_settling_and_late_sidecar_is_preserved(ingest, tmp_path):
    settings, catalog, service = ingest
    source = tmp_path / "match.dem"
    source.write_bytes(b"PBDEMS2\0body")
    sidecar = tmp_path / "match.dem.info"
    sidecar.write_bytes(b"early")
    assert service.consider(observe(source)) is None
    assert catalog.list_demos() == []
    demo_id = settle(service, source)
    sidecar.write_bytes(b"late metadata")
    service.consider(observe(source))
    files = (settings.data_root / "raw" / demo_id / "sidecars").glob("*.info")
    assert {p.read_bytes() for p in files} == {b"early", b"late metadata"}
    assert len(catalog.list_demos()) == 1


def test_compressed_and_invalid_files_report_errors_without_raw_publication(ingest, tmp_path):
    settings, catalog, service = ingest
    compressed = tmp_path / "match.dem.gz"
    compressed.write_bytes(b"gzip data")
    settle(service, compressed)
    assert catalog.get_source(str(compressed)).error.code == "UNSUPPORTED_COMPRESSED"
    invalid = tmp_path / "wrong.dem"
    invalid.write_bytes(b"HL2DEMO\0old")
    settle(service, invalid)
    assert catalog.get_source(str(invalid)).error.code == "INVALID_DEMO"
    assert catalog.list_demos() == []


def test_changed_observation_cannot_be_copied(ingest, tmp_path):
    settings, _, _ = ingest
    source = tmp_path / "changed.dem"
    source.write_bytes(b"PBDEMS2\0first")
    observation = observe(source)
    source.write_bytes(b"PBDEMS2\0replacement")
    with pytest.raises(AppError) as failure:
        snapshot_source(observation, settings)
    assert failure.value.code == "SOURCE_UNSTABLE"
    assert list((settings.data_root / "raw").iterdir()) == []


def test_restart_repairs_a_partially_published_optional_sidecar(ingest, tmp_path):
    settings, catalog, service = ingest
    source = tmp_path / "sidecar.dem"
    source.write_bytes(b"PBDEMS2\0body")
    metadata = b"complete optional match metadata"
    Path(str(source) + ".info").write_bytes(metadata)
    demo_id = settle(service, source)
    stored = next((settings.data_root / "raw" / demo_id / "sidecars").glob("*.info"))
    stored.chmod(0o600)
    stored.write_bytes(b"partial")
    restarted = IngestionService(settings, catalog)
    restarted.consider(observe(source))
    assert stored.read_bytes() == metadata
    assert catalog.get_source(str(source)).demo_id == demo_id
