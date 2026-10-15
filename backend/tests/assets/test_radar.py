"""Consumer-visible behaviour of the local radar slice.

Runs against a fake Source2Viewer-CLI and a fake installation in ``tmp_path``:
no CS2 install, no network and no Valve asset is needed. Fixture values mirror
the verified local Inferno extraction (``pos_x`` -2087, ``pos_y`` 3870, 4.9).
"""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

import pytest

from cs_demo_analyzer.assets.radar import RadarService

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

INFERNO = """"de_inferno"
{
	"material" "overviews/de_inferno"
	"pos_x" "-2087"
	"pos_y" "3870"
	"scale" "4.9"
	"verticalsections" { "default" { "AltitudeMax" "10000" "AltitudeMin" "-495" } }
}
"""

NUKE = """"de_nuke"
{
	"material" "overviews/de_nuke"
	"pos_x" "-3453"  "pos_y" "2887"  "scale" "7"
	"verticalsections"
	{
		"default" { "AltitudeMax" "10000" "AltitudeMin" "-495" }
		"lower" { "AltitudeMax" "-495" "AltitudeMin" "-10000" }
	}
}
"""

TOOL = '''#!{python}
import os, sys

args = sys.argv[1:]
flags = {}
index = 0
while index < len(args):
    if args[index] in ("-i", "-f", "-o") and index + 1 < len(args):
        flags[args[index]] = args[index + 1]
        index += 2
    else:
        index += 1
internal, output = flags.get("-f", ""), flags.get("-o", "")
if os.environ.get("FAKE_TOOL_LOG"):
    with open(os.environ["FAKE_TOOL_LOG"], "a") as handle:
        handle.write(internal + "\\n")
if os.environ.get("FAKE_TOOL_FAIL"):
    sys.stderr.write("simulated extraction failure\\n")
    raise SystemExit(3)
name = internal.rsplit("/", 1)[-1]
folder = "overviews" if internal.startswith("resource/overviews/") else "radars"
source_name = name if folder == "overviews" else name[: -len(".vtex_c")] + ".png"
source = os.path.join(os.environ["FAKE_TOOL_ROOT"], folder, source_name)
if not os.path.isfile(source):
    sys.stderr.write("not found in pak: " + internal + "\\n")
    raise SystemExit(1)
with open(source, "rb") as handle:
    payload = handle.read()
relative = internal if folder == "overviews" else internal[: -len(".vtex_c")] + ".png"
target = os.path.join(output, relative)
os.makedirs(os.path.dirname(target), exist_ok=True)
with open(target, "wb") as handle:
    handle.write(payload)
'''


def png(width: int = 1024, height: int = 1024) -> bytes:
    """Minimal PNG header block: enough for the signature + IHDR checks."""
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return PNG_SIGNATURE + struct.pack(">I", 13) + b"IHDR" + header + b"\x00\x00\x00\x00" * 2


class Fake:
    """Fake installation, CLI and payload tree for one test."""

    def __init__(self, tmp_path: Path) -> None:
        self.data_root = tmp_path / "app"
        self.install = tmp_path / "install"
        game = self.install / "game" / "csgo"
        game.mkdir(parents=True)
        (game / "steam.inf").write_text("ClientVersion=2000932\nPatchVersion=1.0.0.0\n", encoding="utf-8")
        (game / "pak01_dir.vpk").write_bytes(b"fake vpk payload")
        self.payloads = tmp_path / "payloads"
        (self.payloads / "overviews").mkdir(parents=True)
        (self.payloads / "radars").mkdir(parents=True)
        self.log = tmp_path / "tool.log"
        self.tool = tmp_path / "Source2Viewer-CLI"
        self.tool.write_text(TOOL.replace("{python}", sys.executable), encoding="utf-8")
        self.tool.chmod(0o755)

    def overview(self, map_name: str, text: str) -> None:
        (self.payloads / "overviews" / f"{map_name}.txt").write_text(text, encoding="utf-8")

    def radar(self, stem: str, size: int = 1024) -> None:
        (self.payloads / "radars" / f"{stem}.png").write_bytes(png(size, size))

    def service(self, **overrides) -> RadarService:
        settings = {"install_path": self.install, "executable": self.tool}
        settings.update(overrides)
        return RadarService(self.data_root, **settings)

    def calls(self) -> list[str]:
        return self.log.read_text(encoding="utf-8").split() if self.log.is_file() else []

    def cache(self, version: str = "2000932", map_name: str = "de_inferno") -> Path:
        return self.data_root / "assets" / version / map_name


@pytest.fixture
def fake(tmp_path, monkeypatch) -> Fake:
    built = Fake(tmp_path)
    monkeypatch.setenv("FAKE_TOOL_ROOT", str(built.payloads))
    monkeypatch.setenv("FAKE_TOOL_LOG", str(built.log))
    monkeypatch.delenv("FAKE_TOOL_FAIL", raising=False)
    return built


def inferno(fake: Fake) -> Fake:
    fake.overview("de_inferno", INFERNO)
    fake.radar("de_inferno_radar_psd")
    return fake


def test_extracts_caches_and_serves_from_cache_offline(fake: Fake) -> None:
    inferno(fake)
    install_before = sorted(path.relative_to(fake.install) for path in fake.install.rglob("*"))

    descriptor = fake.service().resolve("de_inferno", "2000932")

    assert descriptor.asset_id == "radar:2000932:de_inferno"
    assert (descriptor.match_status, descriptor.warning) == ("exact", None)
    assert (descriptor.width, descriptor.height) == (1024, 1024)
    assert (descriptor.pos_x, descriptor.pos_y, descriptor.scale) == (-2087.0, 3870.0, 4.9)
    assert descriptor.rotate is None and descriptor.levels == []  # not declared by this map
    assert sorted(path.name for path in fake.cache().iterdir()) == [
        "manifest.json",
        "overview.txt",
        "radar.png",
    ]
    assert (fake.cache() / "overview.txt").read_text(encoding="utf-8") == INFERNO
    assert json.loads((fake.cache() / "manifest.json").read_text(encoding="utf-8"))["pak"].endswith(
        "pak01_dir.vpk"
    )
    assert fake.service().asset_path(descriptor.asset_id) == (fake.cache() / "radar.png").resolve()
    # The installation is read-only for this slice.
    assert sorted(path.relative_to(fake.install) for path in fake.install.rglob("*")) == install_before

    calls = len(fake.calls())
    assert calls > 0
    fake.tool.unlink()

    offline = fake.service().resolve("de_inferno", "2000932")

    assert (offline.asset_id, offline.warning) == (descriptor.asset_id, None)
    assert offline.pos_x == descriptor.pos_x
    assert len(fake.calls()) == calls


def test_missing_tool_warns_and_serves_no_image(fake: Fake) -> None:
    inferno(fake)
    service = fake.service(executable=None)

    descriptor = service.resolve("de_inferno", "2000930")

    assert descriptor.asset_id is None
    assert descriptor.pos_x is None and descriptor.levels == []
    assert descriptor.match_status == "mismatch"
    assert "not provisioned" in (descriptor.warning or "")
    assert service.asset_path("radar:2000932:de_inferno") is None
    assert fake.calls() == []


def test_demo_version_match_status_is_explicit(fake: Fake) -> None:
    inferno(fake)

    mismatch = fake.service().resolve("de_inferno", "2000930")
    assert mismatch.match_status == "mismatch"
    assert mismatch.installed_client_version == "2000932" and mismatch.demo_client_version == "2000930"
    assert "2000930" in (mismatch.warning or "") and "not historical" in (mismatch.warning or "")

    unknown = fake.service().resolve("de_inferno")
    assert (unknown.match_status, unknown.demo_client_version, unknown.warning) == ("unknown", None, None)


def test_corrupt_cache_is_rebuilt_and_bad_asset_ids_are_rejected(fake: Fake) -> None:
    inferno(fake)
    service = fake.service()
    descriptor = service.resolve("de_inferno", "2000932")
    (fake.cache() / "radar.png").write_bytes(b"clobbered")
    assert service.asset_path(descriptor.asset_id) is None

    rebuilt = service.resolve("de_inferno", "2000932")

    assert (rebuilt.asset_id, rebuilt.width) == (descriptor.asset_id, 1024)
    assert service.asset_path(descriptor.asset_id) is not None

    for candidate in (
        "radar:2000932:de_inferno/../../etc/passwd",
        "../../etc/passwd",
        "radar:2000932:..",
        "radar:2000932:de_nuke",
        "radar:9999:de_inferno",
        "overview:2000932:de_inferno",
        "radar:2000932:de_inferno:lower",
    ):
        assert service.asset_path(candidate) is None, candidate


def test_declared_altitude_section_selects_its_own_asset(fake: Fake) -> None:
    fake.overview("de_nuke", NUKE)
    fake.radar("de_nuke_radar_psd")
    fake.radar("de_nuke_lower_radar_psd")

    descriptor = fake.service().resolve("de_nuke", "2000932")

    assert descriptor.asset_id == "radar:2000932:de_nuke"
    assert descriptor.levels == [
        {
            "name": "lower",
            "asset_id": "radar:2000932:de_nuke:lower",
            "altitude_min": -10000.0,
            "altitude_max": -495.0,
            "width": 1024,
            "height": 1024,
        }
    ]
    lower = fake.service().asset_path("radar:2000932:de_nuke:lower")
    assert lower is not None and lower.name == "lower.png"
    assert lower.read_bytes() == (fake.payloads / "radars" / "de_nuke_lower_radar_psd.png").read_bytes()


def test_declared_section_without_a_texture_is_omitted(fake: Fake) -> None:
    fake.overview("de_nuke", NUKE)
    fake.radar("de_nuke_radar_psd")

    descriptor = fake.service().resolve("de_nuke", "2000932")

    assert descriptor.asset_id == "radar:2000932:de_nuke"
    assert descriptor.levels == []
    assert "lower" in (descriptor.warning or "")
    assert fake.service().asset_path("radar:2000932:de_nuke:lower") is None


def test_tool_failure_warns_and_leaves_no_cache(fake: Fake, monkeypatch) -> None:
    inferno(fake)
    monkeypatch.setenv("FAKE_TOOL_FAIL", "1")

    descriptor = fake.service().resolve("de_inferno", "2000932")

    assert descriptor.asset_id is None
    assert "exited 3" in (descriptor.warning or "")
    assert not fake.cache().exists()


def test_unsupported_map_name_is_absence_without_io(fake: Fake) -> None:
    inferno(fake)
    service = fake.service()

    for bad in ("../de_inferno", "de/inferno", "de inferno", ""):
        descriptor = service.resolve(bad)
        assert descriptor.asset_id is None, bad
        assert "unsupported map name" in (descriptor.warning or ""), bad

    assert fake.calls() == []
    assert not (fake.data_root / "assets").exists()
