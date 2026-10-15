"""Shared fixtures for storage behavior tests.

Fixtures only; the dataset/catalog helpers live in ``support.py`` so test
modules can import them directly.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from cs_demo_analyzer.storage import Artifacts, Catalog

from .support import DatasetBuilder, Harness


@pytest.fixture
def data_root(tmp_path: Path) -> Path:
    return tmp_path / "data"


@pytest.fixture
def catalog(data_root: Path):
    instance = Catalog(data_root)
    try:
        yield instance
    finally:
        instance.close()


@pytest.fixture
def artifacts(data_root: Path) -> Artifacts:
    return Artifacts(data_root)


@pytest.fixture
def harness(catalog: Catalog, artifacts: Artifacts) -> Harness:
    return Harness(catalog, artifacts)


@pytest.fixture
def builder(tmp_path: Path) -> DatasetBuilder:
    """A staging directory outside the data root, for path-protection tests."""
    return DatasetBuilder(tmp_path / "stage")
