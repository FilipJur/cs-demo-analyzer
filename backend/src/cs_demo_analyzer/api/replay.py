from __future__ import annotations

import json
from pathlib import Path

import polars as pl

from ..domain.contracts import AppError, Manifest, ReplayChunk, ReplayEvent, ReplayPlayer, ReplaySample, RoundRecord, RoundResponse


class ReplayReader:
    def __init__(self, application):
        self.app = application
        self._validated: set[str] = set()

    def manifest(self, demo_id: str, generation_id: str | None = None) -> tuple[Manifest, Path]:
        demo = self.app.catalog.get_demo(demo_id)
        if demo is None:
            raise AppError("NOT_FOUND", "Demo does not exist", "read")
        generation = generation_id or demo.generation_id
        if generation is None:
            raise AppError("NOT_READY", "Demo has no successful extraction yet", "read", True)
        path = self.app.catalog.generation_path(demo_id, generation)
        if path is None:
            raise AppError("GENERATION_UNAVAILABLE", "Requested generation is not registered", "read")
        path = Path(path)
        try:
            if generation not in self._validated:
                manifest = self.app.artifacts.validate(path)
                self._validated.add(generation)
            else:
                manifest = Manifest.model_validate_json(path.read_text())
        except Exception as exc:
            raise AppError("ARTIFACT_INVALID", f"Generation cannot be read: {exc}", "read", True) from exc
        if manifest.demo_id != demo_id or manifest.generation_id != generation:
            raise AppError("ARTIFACT_INVALID", "Generation identity differs from catalog", "read")
        return manifest, path.parent

    def rounds(self, demo_id: str, generation_id: str | None = None) -> RoundResponse:
        manifest, directory = self.manifest(demo_id, generation_id)
        rows = pl.read_parquet(directory / manifest.tables['rounds'].path).to_dicts()
        return RoundResponse(generation_id=manifest.generation_id, rounds=[RoundRecord(**r) for r in rows])

    def replay(self, demo_id: str, generation_id: str, round_id: int, stride_ticks: int | None = None, start_tick: int | None = None, end_tick: int | None = None) -> ReplayChunk:
        manifest, directory = self.manifest(demo_id, generation_id)
        rounds = pl.read_parquet(directory / manifest.tables['rounds'].path)
        selected = rounds.filter(pl.col('round_id') == round_id)
        if selected.height != 1:
            raise AppError("NOT_FOUND", "Round does not exist", "replay")
        r = selected.row(0, named=True)
        begin = r['freeze_end_tick'] if r['freeze_end_tick'] is not None else r['start_tick']
        finish = r['end_tick']
        if begin is None or finish is None or finish < begin:
            raise AppError("PARTIAL_ROUND", "Round timing is incomplete", "replay")
        start = begin if start_tick is None else start_tick
        end = finish if end_tick is None else end_tick
        stride = max(1, round(manifest.tick_rate_hz / 8)) if stride_ticks is None else stride_ticks
        if not (begin <= start <= end <= finish) or not 1 <= stride <= 4096:
            raise AppError("INVALID_WINDOW", "Window must fit one round and have stride 1–4096", "replay")
        kills = pl.read_parquet(directory / manifest.tables['kills'].path).filter(pl.col('tick').is_between(start, end))
        events = [ReplayEvent(**row) for row in kills.select(list(ReplayEvent.model_fields)).to_dicts()]
        states = pl.scan_parquet(directory / manifest.tables['player_state'].path)
        ticks = [event.tick for event in events]
        predicate = pl.col('tick').is_between(start, end) & (((pl.col('tick') - start) % stride == 0) | pl.col('tick').is_in(ticks)) & pl.col('player_id').is_not_null()
        samples = states.filter(predicate).select(list(ReplaySample.model_fields)).sort('tick', 'player_id').limit(120001).collect()
        if samples.height > 120000:
            raise AppError("WINDOW_TOO_LARGE", "Replay exceeds 120,000 player samples; request a smaller window", "replay")
        players = pl.read_parquet(directory / manifest.tables['players'].path)
        radar = self.app.radar.resolve(manifest.map_name, manifest.demo_client_version)
        warnings = list(manifest.warnings)
        if radar.warning:
            warnings.append(radar.warning)
        return ReplayChunk(generation_id=manifest.generation_id, tick_rate_hz=manifest.tick_rate_hz, start_tick=start, end_tick=end, stride_ticks=stride, players=[ReplayPlayer(**row) for row in players.to_dicts()], samples=[ReplaySample(**row) for row in samples.to_dicts()], events=events, radar=radar, warnings=warnings)
