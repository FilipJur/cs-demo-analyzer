"""Steam library and demo-root resolution.

Steam metadata (``libraryfolders.vdf`` and the Counter-Strike 2 app manifest)
is parsed with srctools. Nothing in this module writes to the game
installation, creates directories, or walks anything other than the named
candidate roots; discovery is limited to Steam metadata plus the XDG download
directory.
"""

from __future__ import annotations

import os
from collections.abc import Iterable, Iterator
from pathlib import Path

import srctools.keyvalues as keyvalues

from ..domain.contracts import AppError, RootRequest

APPID = 730
"""Steam app id of Counter-Strike 2 (appmanifest_730.acf)."""

INSTALL_DIR_FALLBACK = "Counter-Strike Global Offensive"
"""``installdir`` used when the app manifest omits it."""

REPLAYS_SUBDIR = Path("game") / "csgo" / "replays"
"""Current CS2 layout, watched recursively: it is where the client writes demos."""

CSGO_SUBDIR = Path("game") / "csgo"
"""Current CS2 ``csgo`` directory, scanned for direct children only."""

XDG_DOWNLOAD_DIR = "XDG_DOWNLOAD_DIR"
"""Key of the XDG user directory used for demo downloads."""

_LIBRARYFOLDERS = "libraryfolders"
_APPSTATE = "AppState"


def discover_install(override: Path | None = None) -> Path | None:
    """Return the local Counter-Strike 2 installation directory, if any.

    ``override`` is an explicitly configured installation path and wins over
    Steam metadata. It raises :class:`AppError` when it is not a directory.
    Otherwise the app manifest of app 730 in every Steam library is consulted
    and the first installation that exists on disk is returned; ``None`` means
    no installation was found (nothing is guessed or created).
    """
    if override is not None:
        return _explicit_install(override)
    for install in _installs():
        if install.is_dir():
            return install
    return None


def discover_roots(install_path: Path | None = None) -> list[RootRequest]:
    """Return the demo roots to scan, in preference order, deduplicated by path.

    ``install_path`` restricts installation resolution to that path (an
    explicitly configured installation is never combined with Steam
    libraries). Roots that do not exist yet are still returned so the caller
    can persist them as configured-but-unavailable; they are never created.
    """
    roots: list[RootRequest] = []
    for install in _installs(install_path):
        roots.append(RootRequest(path=str(_resolve(install / REPLAYS_SUBDIR)), recursive=True))
        roots.append(RootRequest(path=str(_resolve(install / CSGO_SUBDIR)), recursive=False))
    downloads = downloads_dir()
    if downloads is not None:
        roots.append(RootRequest(path=str(_resolve(downloads)), recursive=False))
    return _deduplicate(roots)


def downloads_dir() -> Path | None:
    """Return the directory demos downloaded by the browser land in.

    Resolution order: the ``XDG_DOWNLOAD_DIR`` environment variable, the
    ``XDG_DOWNLOAD_DIR`` entry of ``$XDG_CONFIG_HOME/user-dirs.dirs``, then
    ``$HOME/Downloads``. Only a leading ``~``/``$HOME`` is expanded; the value
    is never passed to a shell, so a value with other shell syntax is ignored.
    The returned path may not exist.
    """
    base = Path.home()
    override = os.environ.get(XDG_DOWNLOAD_DIR)
    if override:
        expanded = _expand_home(override, base)
        if expanded is not None:
            return expanded
    for value in _xdg_user_dirs(base, XDG_DOWNLOAD_DIR):
        expanded = _expand_home(value, base)
        if expanded is not None:
            return expanded
    return base / "Downloads"


def steam_roots() -> list[Path]:
    """Return existing Steam installation directories for this user, deduplicated."""
    base = Path.home()
    found: list[Path] = []
    for candidate in (
        base / ".steam" / "steam",
        base / ".steam" / "root",
        base / ".local" / "share" / "Steam",
        base / ".var" / "app" / "com.valvesoftware.Steam" / "data" / "Steam",
    ):
        root = _resolve(candidate)
        if root.is_dir() and root not in found:
            found.append(root)
    return found


def _installs(install_path: Path | None = None) -> Iterator[Path]:
    """Yield installation candidates, deduplicated by resolved path."""
    if install_path is not None:
        yield _explicit_install(install_path)
        return
    seen: set[Path] = set()
    for steam_root in steam_roots():
        for library in _libraries(steam_root):
            install = _app_install(library)
            if install is None or install in seen:
                continue
            seen.add(install)
            yield install


def _explicit_install(install_path: Path) -> Path:
    install = _resolve(install_path)
    if not install.is_dir():
        raise AppError("INVALID_CONFIG", f"Install path is not a directory: {install}", "discovery")
    return install


def _libraries(steam_root: Path) -> list[Path]:
    """Return the libraries to check for app 730, deduplicated.

    Both the modern ``config/libraryfolders.vdf`` and the older
    ``steamapps/libraryfolders.vdf`` locations are read; the modern block maps
    library ids to ``path`` values, the older one maps ids to the path itself.
    A missing or unreadable metadata file is skipped silently, and the Steam
    root itself is always a library.
    """
    home = Path.home()
    found: list[Path] = [_resolve(steam_root)]
    for metadata in (
        steam_root / "config" / "libraryfolders.vdf",
        steam_root / "steamapps" / "libraryfolders.vdf",
    ):
        document = _load_vdf(metadata)
        if document is None:
            continue
        for entry in _block(document, _LIBRARYFOLDERS):
            if entry.has_children():
                value = _text(entry, "path")
            else:
                value = entry.value
            library = _expand_home(value, home)
            if library is None:
                continue
            resolved = _resolve(library)
            if resolved not in found:
                found.append(resolved)
    return found


def _app_install(library: Path) -> Path | None:
    """Return the app 730 installation inside ``library``, or ``None``.

    ``None`` means Steam does not record app 730 in that library, so no path is
    invented for it. The returned path may not exist (uninstalled or moved).
    """
    manifest = library / "steamapps" / f"appmanifest_{APPID}.acf"
    document = _load_vdf(manifest)
    if document is None:
        return None
    state = _block(document, _APPSTATE)
    installdir = _text(state, "installdir") or INSTALL_DIR_FALLBACK
    return _resolve(library / "steamapps" / "common" / installdir)


def _load_vdf(path: Path) -> keyvalues.Keyvalues | None:
    """Parse a Valve keyvalues document, or return ``None`` when unavailable."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    try:
        return keyvalues.Keyvalues.parse(text, str(path))
    except keyvalues.KeyValError:
        return None


def _block(document: keyvalues.Keyvalues, name: str) -> keyvalues.Keyvalues:
    """Return the named top-level block, or the document itself as a fallback."""
    for child in document:
        if (child.name or "").casefold() == name:
            return child
    return document


def _text(block: keyvalues.Keyvalues, key: str) -> str:
    """Return the value of a leaf entry, case-insensitively, or ``''``."""
    for child in block:
        if (child.name or "").casefold() == key.casefold() and not child.has_children():
            return child.value
    return ""


def _expand_home(value: str, home: Path) -> Path | None:
    """Resolve a configured path without ever evaluating shell syntax.

    Only a leading ``~``, ``$HOME`` or ``${HOME}`` is expanded and only an
    absolute path is accepted; anything else (relative paths, other variables,
    Windows paths) returns ``None``.
    """
    text = value.strip().strip('"').strip("'")
    for prefix in ("$HOME", "${HOME}", "~"):
        if not text.startswith(prefix):
            continue
        rest = text[len(prefix) :]
        if not rest:
            return home
        if rest.startswith("/"):
            return home / rest[1:]
    if text.startswith("$"):
        return None
    if text.startswith("/"):
        return Path(text)
    return None


def _xdg_user_dirs(home: Path, key: str) -> Iterator[str]:
    """Yield values assigned to ``key`` in ``user-dirs.dirs``, in file order.

    The file is shell syntax, so it is read as plain text and never executed or
    sourced; only ``name = value`` assignment lines are understood.
    """
    config_home = os.environ.get("XDG_CONFIG_HOME") or str(home / ".config")
    try:
        text = (Path(config_home) / "user-dirs.dirs").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, separator, value = line.partition("=")
        if separator and name.strip() == key:
            yield value.strip()


def _deduplicate(requests: Iterable[RootRequest]) -> list[RootRequest]:
    """Drop repeated paths; a path needed recursively stays recursive."""
    merged: dict[str, RootRequest] = {}
    for request in requests:
        found = merged.get(request.path)
        if found is None:
            merged[request.path] = request
        elif request.recursive and not found.recursive:
            merged[request.path] = RootRequest(path=found.path, recursive=True)
    return list(merged.values())


def _resolve(path: Path) -> Path:
    """Resolve a root path once; discovered symlinks are never followed later."""
    return path.resolve()
