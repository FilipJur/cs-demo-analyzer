import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { assetUrl, client, type ApiError } from '../api/client';
import type { DemoDetail, RoundRecord } from '../api/types';
import { formatTickTime, shortHash, sideLabel } from '../lib/format';
import { actorAt, actorLabel, buildTracks, medianZ, parseLevels, pickLevelForZ, positionAt, radarProjection, relativeProjection, type ActorFrame, type RadarLevel } from '../lib/radar';
import { useRafClock } from '../lib/useRafClock';
import { usePolled } from '../lib/usePolling';
import { useReplay } from '../lib/useReplay';
import { ErrorNotice, WarningList } from './Notices';
import { RadarCanvas, type KillMarker } from './RadarCanvas';

type Props = {
  demoId: string | null;
  detail: DemoDetail | null;
  detailError: ApiError | null;
  detailLoading: boolean;
};

function roundLabel(round: RoundRecord): string {
  const suffix = round.source_round_num === null ? '' : ` (source #${round.source_round_num})`;
  const outcome = round.winner_side === null ? '' : ` — ${sideLabel(round.winner_side)} won`;
  return `Round ${round.round_id}${suffix}${outcome}`;
}

function hasTiming(round: RoundRecord): boolean {
  const begin = round.freeze_end_tick ?? round.start_tick;
  return begin !== null && round.end_tick !== null && round.end_tick >= begin;
}

export function ReplayPanel({ demoId, detail, detailError, detailLoading }: Props): ReactNode {
  const generationId = detail?.demo.generation_id ?? null;
  const tickRateHz = detail?.manifest?.tick_rate_hz ?? null;
  const [roundId, setRoundId] = useState<number | null>(null);
  const [manualLevel, setManualLevel] = useState<RadarLevel | null>(null);

  const rounds = usePolled((signal) => client.rounds(demoId ?? '', { generation_id: generationId }, signal), 20000, {
    enabled: demoId !== null && generationId !== null,
    key: `${demoId ?? ''}|${generationId ?? ''}`,
  });

  const roundList = rounds.data?.rounds ?? [];
  const selectedRound = roundList.find((round) => round.round_id === roundId) ?? null;

  useEffect(() => {
    setRoundId(null);
    setManualLevel(null);
  }, [demoId, generationId]);

  useEffect(() => {
    if (roundId !== null && roundList.some((round) => round.round_id === roundId)) return;
    const first = roundList.find((round) => hasTiming(round));
    setRoundId(first?.round_id ?? null);
  }, [roundList, roundId]);

  const target = useMemo(
    () => (demoId !== null && generationId !== null && selectedRound !== null ? { demoId, generationId, round: selectedRound, tickRateHz } : null),
    [demoId, generationId, selectedRound, tickRateHz],
  );

  const replay = useReplay(target);
  const bounds = useMemo(
    () => (replay.startTick !== null && replay.endTick !== null && replay.endTick >= replay.startTick ? { min: replay.startTick, max: replay.endTick } : null),
    [replay.startTick, replay.endTick],
  );
  const clock = useRafClock(bounds, replay.tickRateHz);
  const tracks = useMemo(() => buildTracks(replay.samples), [replay.samples]);
  const playerById = useMemo(() => new Map(replay.players.map((player) => [player.player_id, player])), [replay.players]);

  const actors = useMemo(() => {
    const frames: ActorFrame[] = [];
    for (const track of tracks.values()) {
      const frame = actorAt(track, clock.tick, replay.strideTicks);
      if (frame !== null) frames.push(frame);
    }
    frames.sort((a, b) => (a.side === b.side ? a.player_id.localeCompare(b.player_id) : a.side.localeCompare(b.side)));
    return frames;
  }, [tracks, clock.tick, replay.strideTicks]);

  const levels = useMemo(() => (replay.radar === null ? [] : parseLevels(replay.radar)), [replay.radar]);
  const autoLevel = useMemo(() => pickLevelForZ(levels, medianZ(actors)), [levels, actors]);
  const activeLevel = levels.length > 1 ? manualLevel ?? autoLevel : null;

  const projection = useMemo(() => {
    if (replay.radar === null) return null;
    return radarProjection(replay.radar, activeLevel) ?? relativeProjection(actors);
  }, [replay.radar, activeLevel, actors]);

  const radar = replay.radar;
  const canvasProjection = projection;
  const imageAssetId = activeLevel?.assetId ?? radar?.asset_id ?? null;
  const imageUrl = imageAssetId === null ? null : assetUrl(imageAssetId);

  const markers = useMemo(() => {
    const list: KillMarker[] = [];
    for (const event of replay.events) {
      if (event.victim_id === null) continue;
      const track = tracks.get(event.victim_id);
      if (track === undefined) continue;
      const point = positionAt(track, event.tick);
      if (point === null) continue;
      list.push({ tick: event.tick, x: point.x, y: point.y });
    }
    return list;
  }, [replay.events, tracks]);

  const killTicks = useMemo(() => replay.events.map((event) => event.tick), [replay.events]);
  const previousKill = [...killTicks].reverse().find((tick) => tick < clock.tick) ?? null;
  const nextKill = killTicks.find((tick) => tick > clock.tick) ?? null;
  const sampleStep = Math.max(1, replay.strideTicks);
  const secondStep = replay.tickRateHz > 0 ? Math.max(1, Math.round(replay.tickRateHz)) : sampleStep;

  if (demoId === null) {
    return (
      <section className="panel" aria-label="Replay">
        <header className="panel-header">
          <h2>Replay</h2>
        </header>
        <p className="hint">Select a demo with a successful extraction to load one round of generation-pinned replay.</p>
      </section>
    );
  }

  return (
    <section className="panel" aria-label="Replay">
      <header className="panel-header">
        <h2>Replay</h2>
        <span className="count mono" title={demoId}>
          demo {shortHash(demoId)}
          {generationId !== null ? ` · gen ${shortHash(generationId)}` : ''}
        </span>
      </header>

      {detailLoading ? <p className="hint">Loading demo detail…</p> : null}
      <ErrorNotice error={detailError} context="GET /demos/{demo_id}" />

      {generationId === null && detail !== null ? (
        <p className="notice notice-warning" role="status">
          This demo has no successful generation yet, so replay data is unavailable. Watch its job state in the Jobs panel.
        </p>
      ) : null}

      {generationId !== null ? (
        <>
          <div className="replay-select">
            <label htmlFor="round-select">Round</label>
            <select
              id="round-select"
              value={roundId ?? ''}
              onChange={(event) => setRoundId(event.target.value === '' ? null : Number(event.target.value))}
              disabled={roundList.length === 0}
            >
              {roundList.map((round) => (
                <option key={round.round_id} value={round.round_id} disabled={!hasTiming(round)}>
                  {roundLabel(round)}
                  {hasTiming(round) ? '' : ' — timing incomplete'}
                </option>
              ))}
            </select>
            {roundList.length === 0 ? <span className="hint">{rounds.loading ? 'Loading rounds…' : 'No rounds published for this generation.'}</span> : null}
          </div>
          <ErrorNotice error={rounds.error} context="GET /demos/{demo_id}/rounds" />

          {replay.error !== null ? (
            <div className="notice notice-error" role="alert">
              <span className="notice-code">{replay.error.code}</span>
              <span>{replay.error.message}</span>
              {replay.error.code === 'GENERATION_MISMATCH' || replay.error.code === 'GENERATION_UNAVAILABLE' || replay.error.code === 'ARTIFACT_INVALID' ? (
                <span className="notice-meta">This generation is no longer the pinned one; reload the demo before replaying.</span>
              ) : null}
              <button type="button" onClick={replay.reload}>
                Retry replay
              </button>
            </div>
          ) : null}

          {replay.loading ? <p className="hint">Loading bounded replay window…</p> : null}

          {radar !== null && canvasProjection !== null ? (
            <>
              <div className="replay-controls">
                <button type="button" onClick={clock.toggle} aria-label={clock.playing ? 'Pause replay' : 'Play replay'} disabled={bounds === null}>
                  {clock.playing ? 'Pause' : 'Play'}
                </button>
                <button type="button" onClick={() => clock.step(-secondStep)} aria-label={`Back ${secondStep} ticks (one second)`} disabled={bounds === null}>
                  −1s
                </button>
                <button type="button" onClick={() => clock.step(-sampleStep)} aria-label={`Back ${sampleStep} ticks (one sample)`} disabled={bounds === null}>
                  −1 sample
                </button>
                <button type="button" onClick={() => clock.step(sampleStep)} aria-label={`Forward ${sampleStep} ticks (one sample)`} disabled={bounds === null}>
                  +1 sample
                </button>
                <button type="button" onClick={() => clock.step(secondStep)} aria-label={`Forward ${secondStep} ticks (one second)`} disabled={bounds === null}>
                  +1s
                </button>
                <button type="button" onClick={() => (previousKill === null ? undefined : clock.seek(previousKill))} disabled={previousKill === null}>
                  Previous kill
                </button>
                <button type="button" onClick={() => (nextKill === null ? undefined : clock.seek(nextKill))} disabled={nextKill === null}>
                  Next kill
                </button>
              </div>

              <div className="seek">
                <label htmlFor="tick-slider">Tick position (round {selectedRound?.round_id ?? '—'})</label>
                <input
                  id="tick-slider"
                  type="range"
                  min={bounds?.min ?? 0}
                  max={bounds?.max ?? 0}
                  step={1}
                  value={clock.tick}
                  onChange={(event) => clock.seek(Number(event.target.value))}
                  disabled={bounds === null}
                />
                <div className="tick-readout">
                  <span className="tick-label">Current tick</span>
                  <span className="tick-value mono" data-testid="current-tick">
                    {clock.tick}
                  </span>
                  <span className="small">
                    {replay.startTick === null ? 'round time n/a' : formatTickTime(clock.tick, replay.startTick, replay.tickRateHz)} after freeze end ·{' '}
                    {replay.tickRateHz > 0 ? `${replay.tickRateHz} Hz` : 'tick rate unknown'} · stride {replay.strideTicks} ticks
                  </span>
                </div>
              </div>

              <RadarCanvas
                radar={radar}
                projection={canvasProjection}
                levels={levels}
                level={activeLevel}
                onLevelChange={setManualLevel}
                actors={actors}
                playerById={playerById}
                markers={markers}
                tick={clock.tick}
                imageUrl={imageUrl}
              />

              <WarningList warnings={replay.warnings} />

              <div className="participants">
                <h3>Participants ({replay.players.length})</h3>
                <ul className="list">
                  {replay.players.map((player) => {
                    const unresolved = player.steam_id === null || player.name === null;
                    return (
                      <li key={player.player_id} className="list-row">
                        <span className={`badge ${player.side === 'ct' ? 'badge-ct' : player.side === 't' ? 'badge-t' : ''}`}>{sideLabel(player.side)}</span>
                        <span className="grow truncate">{player.name ?? '(no name in recording)'}</span>
                        <span className="mono small" title={player.steam_id ?? ''}>
                          steam_id {player.steam_id ?? 'null'}
                        </span>
                        {unresolved ? <span className="badge badge-warn">identity unresolved</span> : null}
                      </li>
                    );
                  })}
                </ul>
                <p className="hint">
                  A null SteamID is a recording-local roster entry and is never joined by name or converted to a number; unresolved observations stay separate.
                </p>
              </div>

              <div className="events">
                <h3>Kill events ({replay.events.length})</h3>
                <ul className="list">
                  {replay.events.map((event) => (
                    <li key={event.row_ordinal} className="list-row">
                      <button type="button" onClick={() => clock.seek(event.tick)} aria-label={`Jump to tick ${event.tick}`} className="mono">
                        tick {event.tick}
                      </button>
                      <span className="grow truncate">
                        {actorLabel(event.attacker_id === null ? undefined : playerById.get(event.attacker_id), event.attacker_id ?? 'world')} →{' '}
                        {actorLabel(event.victim_id === null ? undefined : playerById.get(event.victim_id), event.victim_id ?? 'unknown victim')}
                      </span>
                      <span className="small">{event.weapon ?? 'unknown weapon'}</span>
                      {event.headshot ? <span className="badge badge-warn">headshot</span> : null}
                    </li>
                  ))}
                  {replay.events.length === 0 ? <li className="list-empty">No kill events in this window.</li> : null}
                </ul>
              </div>
            </>
          ) : null}

          {!replay.loading && replay.error === null && replay.samples.length === 0 ? (
            <p className="hint">The selected round returned no player samples in its window.</p>
          ) : null}
        </>
      ) : null}
    </section>
  );
}
