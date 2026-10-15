"""Local demo discovery: Steam/installation roots, scanning and watching."""

from .steam import discover_install, discover_roots
from .watcher import scan_root, watch_roots

__all__ = ["discover_install", "discover_roots", "scan_root", "watch_roots"]
