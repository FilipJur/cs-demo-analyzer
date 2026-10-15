"""Demo candidate scanning and filesystem watching.

:func:`scan_root` reports bounded file metadata (path, stat fingerprint, root
id) for demo candidates below a root. :func:`watch_roots` blocks on filesystem
notifications and only tells the caller *that* something changed; the
notification set is never interpreted. Neither function reads, hashes, copies,
parses, decompresses or stores demo data, and neither writes anywhere.
"""

from __future__ import annotations

import logging
import os
import stat
import threading
from collections.abc import Callable, Iterator
from pathlib import Path

import watchfiles

from ..domain.contracts import AppError, Fingerprint, Observation, RootRecord

logger = logging.getLogger(__name__)

DEMO_SUFFIXES = (".dem", ".dem.gz", ".dem.bz2", ".dem.zst", ".dem.zip")
"""Recognized candidate names; compressed names are reported, not decompressed."""

DEBOUNCE_MS = 1_000
"""Coalescing window handed to watchfiles."""

STEP_MS = 50
"""Granularity of the watchfiles debounce loop."""

RUST_TIMEOUT_MS = 1_000
"""Longest interval (ms) the watcher blocks before re-checking the stop event.

Kept short so a re-arm (which stops and restarts the watcher thread) is
observed quickly; the caller joins the watcher thread with a short timeout.
"""

REARM_SECONDS = 15.0
"""Grace period between passes that re-check which roots exist and are watchable."""

STOP_JOIN_SECONDS = RUST_TIMEOUT_MS / 1_000 + 2.0
"""Upper bound on waiting for watcher threads to finish after a stop request."""


def scan_root(root: RootRecord, excluded: Path) -> list[Observation]:
    """Return observations for the demo candidates below ``root``.

    ``root.recursive`` selects a full walk or direct children only. Symbolic
    links are never followed (neither files nor directories). ``excluded`` and
    everything below it are pruned. An unavailable root, an unreadable
    directory or an unresolvable root raises :class:`AppError` so the caller can
    record the root as unavailable; candidates that vanish mid-scan are
    skipped.
    """
    base = _normalised(root.path)
    if not base.is_dir():
        raise AppError("SOURCE_MISSING", f"Root is unavailable: {base}", "discovery", True)
    exclusion = _normalised(excluded)
    observations: list[Observation] = []
    for entry in _candidates(base, recursive=root.recursive, excluded=exclusion):
        observation = _observe(entry, root)
        if observation is not None:
            observations.append(observation)
    observations.sort(key=lambda observation: observation.path)
    return observations


def watch_roots(roots: list[RootRecord], stop_event: threading.Event, on_change: Callable[[], None]) -> None:
    """Block until ``stop_event`` is set, calling ``on_change`` when roots change.

    Only roots that exist as directories are watched; a root that appears later
    is picked up on a following pass, so a missing root neither spins nor
    causes a notification storm. Roots are watched per recursive policy in one
    worker thread per policy, and notifications are coalesced by watchfiles and
    treated as hints: the callback receives no paths and every error is
    reported through it, leaving reconciliation to the caller.
    """
    covered: set[Path] = set()
    workers: list[threading.Thread] = []
    try:
        while not stop_event.is_set():
            for recursive, paths in _watch_groups(roots).items():
                fresh = tuple(path for path in paths if path not in covered)
                if not fresh:
                    continue
                _notify(on_change)
                workers.append(_start_watcher(fresh, recursive, stop_event, on_change))
                covered.update(fresh)
            stop_event.wait(REARM_SECONDS)
    finally:
        for worker in workers:
            worker.join(timeout=STOP_JOIN_SECONDS)


def _candidates(base: Path, *, recursive: bool, excluded: Path) -> Iterator[os.DirEntry]:
    """Yield candidate entries below ``base``, skipping symlinks and exclusions."""
    if _excluded(base, excluded):
        return
    stack = [base]
    while stack:
        directory = stack.pop()
        for entry in _read_dir(directory):
            if entry.is_symlink():
                continue
            try:
                is_dir = entry.is_dir(follow_symlinks=False)
            except OSError:
                continue
            if is_dir:
                child = Path(entry.path)
                if recursive and not _excluded(child, excluded):
                    stack.append(child)
                continue
            if _is_candidate(entry.name):
                yield entry


def _read_dir(directory: Path) -> list[os.DirEntry]:
    """List a directory, mapping failures onto root-level error codes."""
    try:
        with os.scandir(directory) as entries:
            return sorted(entries, key=lambda entry: entry.name)
    except PermissionError as exc:
        raise AppError("PERMISSION_DENIED", f"Root directory is not readable: {directory}", "discovery", True) from exc
    except FileNotFoundError:
        return []  # a subdirectory disappeared while walking; the next scan recovers it
    except OSError as exc:
        raise AppError("IO_ERROR", f"Cannot read root directory {directory}: {exc}", "discovery", True) from exc


def _observe(entry: os.DirEntry, root: RootRecord) -> Observation | None:
    """Build an observation from a candidate entry, or ``None`` if it is gone."""
    try:
        info = entry.stat(follow_symlinks=False)
    except OSError:
        return None
    if not stat.S_ISREG(info.st_mode):
        return None
    return Observation(
        path=str(_normalised(entry.path)),
        fingerprint=Fingerprint(
            device=info.st_dev,
            inode=info.st_ino,
            size=info.st_size,
            mtime_ns=info.st_mtime_ns,
            ctime_ns=info.st_ctime_ns,
        ),
        root_id=root.id,
    )


def _is_candidate(name: str) -> bool:
    lowered = name.lower()
    return any(lowered.endswith(suffix) for suffix in DEMO_SUFFIXES)


def _excluded(path: Path, excluded: Path) -> bool:
    return path == excluded or path.is_relative_to(excluded)


def _watch_groups(roots: list[RootRecord]) -> dict[bool, tuple[Path, ...]]:
    """Group the existing root directories by recursive policy.

    A path required recursively by any root is watched recursively only, and
    roots that do not exist as directories are omitted.
    """
    groups: dict[bool, list[Path]] = {True: [], False: []}
    claimed: set[Path] = set()
    for recursive in (True, False):
        for root in roots:
            if bool(root.recursive) is not recursive:
                continue
            path = _normalised(root.path)
            if path in claimed or not path.is_dir():
                continue
            claimed.add(path)
            groups[recursive].append(path)
    return {recursive: tuple(paths) for recursive, paths in groups.items()}


def _start_watcher(
    paths: tuple[Path, ...], recursive: bool, stop_event: threading.Event, on_change: Callable[[], None]
) -> threading.Thread:
    thread = threading.Thread(
        target=_watch_group,
        args=(paths, recursive, stop_event, on_change),
        name=f"csda-watch-{'recursive' if recursive else 'direct'}",
        daemon=True,
    )
    thread.start()
    return thread


def _watch_group(
    paths: tuple[Path, ...], recursive: bool, stop_event: threading.Event, on_change: Callable[[], None]
) -> None:
    """Watch one group of roots until stopped, re-arming after a failure.

    Failures (a root removed or made unreadable, a watcher error) are reported
    through ``on_change`` and retried after a grace period instead of spinning.
    """
    while not stop_event.is_set():
        try:
            for _changes in watchfiles.watch(
                *paths,
                recursive=recursive,
                stop_event=stop_event,
                debounce=DEBOUNCE_MS,
                step=STEP_MS,
                rust_timeout=RUST_TIMEOUT_MS,
            ):
                _notify(on_change)
            return
        except Exception as exc:
            logger.warning("watchfiles stopped for %s: %s", ", ".join(str(path) for path in paths), exc)
            _notify(on_change)
            stop_event.wait(REARM_SECONDS)


def _notify(on_change: Callable[[], None]) -> None:
    """Call the caller's reconciliation hook; a failing hook must not stop watching."""
    try:
        on_change()
    except Exception:
        logger.exception("on_change callback failed")


def _normalised(path: str | Path) -> Path:
    """Normalize a path lexically; symlinks are never resolved (or followed)."""
    return Path(os.path.normpath(os.path.abspath(path)))
