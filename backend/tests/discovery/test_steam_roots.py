"""Behaviour of Steam/installation root discovery."""

from __future__ import annotations

from pathlib import Path

import pytest

from cs_demo_analyzer.discovery.steam import discover_install, discover_roots, downloads_dir
from cs_demo_analyzer.domain.contracts import AppError

INSTALL_DIR_NAME = "Counter-Strike Global Offensive"


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _libraryfolders(libraries: list[Path]) -> str:
    blocks = []
    for index, library in enumerate(libraries):
        blocks.append(
            f'\t"{index}"\n'
            "\t{\n"
            f'\t\t"path"\t\t"{library}"\n'
            f'\t\t"apps"\n'
            "\t\t{\n"
            f'\t\t\t"730"\t\t"{index + 1000}"\n'
            "\t\t}\n"
            "\t}"
        )
    return '"libraryfolders"\n{\n' + "\n".join(blocks) + "\n}\n"


def _app_manifest(installdir: str) -> str:
    return (
        '"AppState"\n{\n'
        '\t"appid"\t\t"730"\n'
        '\t"name"\t\t"Counter-Strike 2"\n'
        f'\t"installdir"\t\t"{installdir}"\n'
        "}\n"
    )


def _install(library: Path, name: str = INSTALL_DIR_NAME, *, replays: bool = True) -> Path:
    _write(library / "steamapps" / "appmanifest_730.acf", _app_manifest(name))
    install = library / "steamapps" / "common" / name
    (install / "game" / "csgo").mkdir(parents=True, exist_ok=True)
    if replays:
        (install / "game" / "csgo" / "replays").mkdir(exist_ok=True)
    return install


def _roots() -> dict[str, bool]:
    return {request.path: request.recursive for request in discover_roots()}


def _tree(base: Path) -> list[str]:
    return sorted(str(path) for path in base.rglob("*"))


@pytest.fixture
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A hermetic user home: real Steam libraries on this machine are invisible."""
    home = tmp_path / "home"
    (home / ".config").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
    monkeypatch.delenv("XDG_DOWNLOAD_DIR", raising=False)
    return home


def test_resolves_install_and_roots_from_steam_metadata(home: Path) -> None:
    library = home / "SteamLibrary"
    install = _install(library)
    _write(home / ".local" / "share" / "Steam" / "config" / "libraryfolders.vdf", _libraryfolders([library, home / "OtherLibrary"]))
    (home / "Downloads").mkdir()

    assert discover_install() == install.resolve()
    assert _roots() == {
        str((install / "game" / "csgo" / "replays").resolve()): True,
        str((install / "game" / "csgo").resolve()): False,
        str((home / "Downloads").resolve()): False,
    }


def test_missing_roots_are_kept_without_creating_anything(home: Path) -> None:
    library = home / "SteamLibrary"
    install = _install(library, replays=False)
    (install / "game" / "csgo").rmdir()
    _write(home / ".local" / "share" / "Steam" / "config" / "libraryfolders.vdf", _libraryfolders([library]))

    before = _tree(home)
    roots = _roots()
    assert _tree(home) == before
    assert roots[str((install / "game" / "csgo" / "replays").resolve())] is True
    assert roots[str((home / "Downloads").resolve())] is False
    assert not (install / "game" / "csgo").exists()
    assert not (home / "Downloads").exists()
    assert discover_install() == install.resolve()


def test_roots_without_steam_only_include_downloads(home: Path) -> None:
    _write(home / ".config" / "user-dirs.dirs", 'XDG_DOWNLOAD_DIR="$HOME/Downloads"\n')

    assert discover_install() is None
    assert _roots() == {str((home / "Downloads").resolve()): False}


def test_explicit_install_override_ignores_steam_libraries(home: Path) -> None:
    library = home / "SteamLibrary"
    _install(library)
    _write(home / ".local" / "share" / "Steam" / "config" / "libraryfolders.vdf", _libraryfolders([library]))
    standalone = home / "standalone"
    (standalone / "game" / "csgo" / "replays").mkdir(parents=True)

    assert discover_install(standalone) == standalone.resolve()
    roots = [request.path for request in discover_roots(standalone)]
    assert str((standalone / "game" / "csgo" / "replays").resolve()) in roots
    assert not any("SteamLibrary" in path for path in roots)


def test_missing_install_override_is_rejected(home: Path) -> None:
    with pytest.raises(AppError) as failure:
        discover_install(home / "gone")

    assert failure.value.code == "INVALID_CONFIG"


def test_install_override_must_be_a_directory(home: Path) -> None:
    plain = _write(home / "install.txt", "not a directory")

    with pytest.raises(AppError) as failure:
        discover_install(plain)

    assert failure.value.code == "INVALID_CONFIG"


def test_legacy_libraryfolders_numeric_entries(home: Path) -> None:
    library = home / "legacy" / "SteamLibrary"
    install = _install(library)
    _write(
        home / ".steam" / "steam" / "steamapps" / "libraryfolders.vdf",
        '"LibraryFolders"\n{\n\t"TimeNextStatsReport"\t"1712000000"\n\t"1"\t\t"%s"\n}\n' % library,
    )

    assert discover_install() == install.resolve()


def test_equivalent_steam_roots_are_deduplicated(home: Path) -> None:
    library = home / "SteamLibrary"
    install = _install(library)
    real = home / ".local" / "share" / "Steam"
    _write(real / "config" / "libraryfolders.vdf", _libraryfolders([library]))
    (home / ".steam").mkdir()
    (home / ".steam" / "steam").symlink_to(real, target_is_directory=True)
    (home / ".steam" / "root").symlink_to(real, target_is_directory=True)

    paths = [request.path for request in discover_roots()]

    assert len(paths) == len(set(paths)) == 3
    assert str((install / "game" / "csgo" / "replays").resolve()) in paths


def test_downloads_dir_expands_home_without_executing_shell(
    home: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sentinel = tmp_path / "pwned"
    _write(
        home / ".config" / "user-dirs.dirs",
        "# xdg-user-dirs\n"
        f'XDG_DOWNLOAD_DIR="$(touch {sentinel})"\n'
        'XDG_DOCUMENTS_DIR="$HOME/Documents"\n',
    )

    assert downloads_dir() == home / "Downloads"
    assert not sentinel.exists()
    assert not list(tmp_path.rglob("pwned"))

    _write(home / ".config" / "user-dirs.dirs", 'XDG_DOWNLOAD_DIR="$HOME/My Dloads"\n')
    assert downloads_dir() == home / "My Dloads"

    monkeypatch.setenv("XDG_DOWNLOAD_DIR", "~/Elsewhere")
    assert downloads_dir() == home / "Elsewhere"

    monkeypatch.setenv("XDG_DOWNLOAD_DIR", "$NOPE/elsewhere")
    assert downloads_dir() == home / "My Dloads"
