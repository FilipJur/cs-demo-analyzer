# CS2 Demo Analyzer

Local-first CS2 demo discovery, immutable ingestion, queryable Parquet extraction and a minimal 2D replay. Python 3.13/FastAPI, Awpy 3.0, Polars, SQLite and React/TypeScript. No Steam login, replay downloading, cloud backend, coaching algorithms or model calls.

## Setup and run

From the repository root, with Python 3.13, uv and Node/npm installed:

```sh
uv sync --project backend --locked --python 3.13
npm --prefix web ci
npm --prefix web run build
uv run --project backend csda --data-root /mnt/nvme/developer/cs-demo-analyzer-data serve
```

Open `http://127.0.0.1:8765`. The server binds loopback only. Dependencies are provisioned during setup; normal import/parsing/replay does not require network access. The data root is printed by `/api/v1/health` and displayed in the UI.

**Choose the data root before importing large demos.** Precedence: `--data-root` > `CSDA_DATA_ROOT` > `data_root` in config > `$XDG_DATA_HOME/cs-demo-analyzer` (or `~/.local/share/cs-demo-analyzer`). Use an absolute local path with adequate space; do not put application data under the CS2 installation. Data-root relocation while running and network-filesystem storage are not supported.

An optional config lives at `$XDG_CONFIG_HOME/cs-demo-analyzer/config.toml` (normally `~/.config/cs-demo-analyzer/config.toml`), or supply `--config /absolute/config.toml` before the command:

```toml
data_root = "/mnt/nvme/developer/cs-demo-analyzer-data"
install_path = "/mnt/nvme/SteamLibrary/steamapps/common/Counter-Strike Global Offensive"
source2viewer = "/absolute/path/to/Source2Viewer-CLI"
settle_seconds = 10.0
scan_seconds = 60.0
poll_seconds = 2.0
reserve_bytes = 268435456
worker_timeout = 300.0
```

Import checks require two input sizes plus the reserve; parsing an already-owned copy requires one input size plus reserve. These conservative checks are not a filesystem reservation; actual IO failures are still reported. Raw demos, catalog, datasets, assets and staging live under the selected root, not Git.

### Radar tooling

Provision the official [Source2Viewer-CLI 20.1 Linux x64 release](https://github.com/ValveResourceFormat/ValveResourceFormat/releases/tag/20.1), then supply `--source2viewer /absolute/Source2Viewer-CLI` or the config setting. The application never downloads the tool or game files. It reads the user's local VPKs and caches extracted radar PNGs/overviews in its own data root. No system .NET installation is needed for the self-contained binary.

The verified installation on this machine is:

```text
/mnt/nvme/developer/cs-demo-analyzer-data/tools/source2viewer-20.1/Source2Viewer-CLI
```

Without the tool/asset, ingestion still works and replay reports radar unavailability rather than showing a fake map. Current-install assets are explicitly labelled when the recording's inferred game version differs. No historical collision/visibility claim is made.

## Ingestion and commands

Steam library/app manifests locate the CS2 installation. Existing `game/csgo/replays` is watched recursively, direct `.dem` files in `game/csgo` and the XDG Downloads directory are scanned, and custom roots can be added in the UI. The actual observed replay directory is not assumed to exist on every machine. Missing roots remain visible and are reconsidered; game directories are never created.

```sh
uv run --project backend csda --data-root /mnt/nvme/developer/cs-demo-analyzer-data import /absolute/match.dem
uv run --project backend csda --data-root /mnt/nvme/developer/cs-demo-analyzer-data scan
uv run --project backend csda --data-root /mnt/nvme/developer/cs-demo-analyzer-data reprocess <demo-sha256>
```

Flags precede the subcommand. `import` and `reprocess` wait for a durable result and emit JSON; errors exit nonzero. Only one application instance may own a data root, so stop `serve` before running another CLI command on that root, or use the UI/API actions while the server runs.

Ordinary CS2 `PBDEMS2` `.dem` files only. `.dem.gz/.bz2/.zst/.zip` are reported as unsupported; decompress them yourself without overwriting the originals. A downloaded local file is detected automatically; **automatic detection does not download server-hosted replays**.

The quiet window is a heuristic, not proof that a writer has finished. Source fingerprints are reconsidered after changes/restarts. Each stable recording is copied and SHA-256 verified into `raw/<hash>/source.dem`; identical content converges even at another path. Sources are never renamed, deleted or edited. Optional `.dem.info` sidecars neither establish completion nor change recording identity. Do not delete retained originals if future reprocessing matters.

## Data and correctness limits

`foundation-v1` has **seven explicit tables**: players, rounds, full-rate player_state, kills, damages, shots and bomb events. Only the fields in `backend/src/cs_demo_analyzer/domain/tables.py` are normalized. Utility/economy inventories and advanced engine fields are intentionally not required; later named profiles can extract them from preserved recordings. No second parser or standardized lossy replay format is the internal authority.

- SteamIDs remain exact strings; null/zero IDs never join by names or positions. Awpy returns some dead-player observations without IDs. Those rows retain unique observation ordinals and nullable references; partial quality/warnings are visible. Full bot/controlled-pawn continuity is not established.
- Angles come from typed `Demo.snapshots(every=1)`, not raw angle aliases that returned all-null strings in the actual probe. Invalid source tick rates are rejected, never replaced with an assumed 64 Hz clock.
- Immutable generations record parser/schema/profile versions, hashes, dtypes, row counts and tick/build provenance. A failed reprocess leaves the last successful generation available. API reads are generation-pinned and bounded, not a full-match JSON dump or parse-on-scrub path.
- The replay is a foundation proof: one round, pause/play, seek and exact-tick kill navigation. No LOS, fog of war, tactical judgments or coaching. GOTV state is not proof of what a player saw. POV/bots/overtime/multilevel fidelity is not broadly certified by the one local Inferno recording.

## Development and verification

```sh
uv run --project backend python scripts/export_contracts.py
npm --prefix web run types
uv run --project backend pytest backend/tests -q
npm --prefix web run build
```

The ordinary suite uses isolated authored fixtures, not downloaded/private gameplay. Real-demo compatibility is verified with explicit local CLI imports; no integration test silently downloads demos. Keep real `.dem`, Parquet, SQLite, secrets and Valve assets out of Git.

For frontend development, run the backend with `CSDA_DEV_ORIGIN=http://127.0.0.1:5173`, then `npm --prefix web run dev`; Vite proxies `/api` to port 8765. Production UI is same-origin, with no wildcard CORS. Foreign-origin mutations, non-JSON mutation bodies and non-loopback hosts are rejected.

Implementation decisions, contracts, checkpoint criteria and preparation measurements are under [docs/planning](docs/planning/phase-0-execution.md). The research documents are references, not executable specifications for future analytics.

## Attribution

Demo parsing uses [Awpy](https://github.com/pnxenopoulos/awpy) (MIT). Columnar processing uses [Polars](https://github.com/pola-rs/polars) (MIT); local notifications use [watchfiles](https://github.com/samuelcolvin/watchfiles) (MIT); KeyValues parsing uses [srctools](https://github.com/TeamSpen210/srctools) (MIT). Radar extraction is powered by [Source 2 Viewer](https://s2v.app) / [ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat) (MIT tool). Extracted Valve game assets have separate rights and are not redistributed in this repository. Retain the upstream tool's notices when provisioning/distributing its binary.
