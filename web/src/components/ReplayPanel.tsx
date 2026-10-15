import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import { assetUrl, client, type ApiError } from '../api/client';
import { phase2 } from '../api/phase2';
import type { ContextSnapshot, DemoDetail, EncounterDetail, Participation, RoundRecord, Vec3 } from '../api/types';
import { formatTickTime, shortHash, sideLabel } from '../lib/format';
import { participationBadge, sightlineQualifier } from '../lib/phase2';
import { actorAt, actorLabel, buildTracks, medianZ, parseLevels, pickLevelForZ, positionAt, radarProjection, relativeProjection, type ActorFrame, type RadarLevel } from '../lib/radar';
import { useRafClock } from '../lib/useRafClock';
import { usePolled } from '../lib/usePolling';
import { useReplay } from '../lib/useReplay';
import { ContextPanel } from './ContextPanel';
import { EncountersPanel } from './EncountersPanel';
import { GeometryPanel } from './GeometryPanel';
import { Inspector } from './Inspector';
import { ErrorNotice, WarningList } from './Notices';
import { RadarCanvas, type KillMarker, type RadarRelationLine, type RadarTrajectory } from './RadarCanvas';

type Props = {
  demoId: string | null;
  detail: DemoDetail | null;
  detailError: ApiError | null;
  detailLoading: boolean;
  /** Persisted primary SteamID; changing it re-reads participation and clears a manual override. */
  subjectSteamId: string | null;
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

export function ReplayPanel({ demoId, detail, detailError, detailLoading, subjectSteamId }: Props): ReactNode {
  const generationId = detail?.demo.generation_id ?? null;
  const tickRateHz = detail?.manifest?.tick_rate_hz ?? null;
  const [roundId, setRoundId] = useState<number | null>(null);
  const [manualLevel, setManualLevel] = useState<RadarLevel | null>(null);
  const [inspectorOpen, setInspectorOpen] = useState(false);
  const [manualSubjectId, setManualSubjectId] = useState<string | null>(null);
  const [pendingSeek, setPendingSeek] = useState<{ roundId: number; tick: number } | null>(null);
  const [seekNotice, setSeekNotice] = useState<string | null>(null);
  const [snapshot, setSnapshot] = useState<ContextSnapshot | null>(null);
  const [encounterDetail, setEncounterDetail] = useState<EncounterDetail | null>(null);

  // Participation of the configured primary in the pinned generation. It is
  // displayed and never used to substitute another player.
  const participation = usePolled<Participation | null>(
    (signal) => (demoId === null ? Promise.resolve(null) : phase2.participation(demoId, { generation_id: generationId }, signal)),
    30000,
    { enabled: demoId !== null, key: `${demoId ?? ''}|${generationId ?? ''}|${subjectSteamId ?? ''}` },
  );
  const subject = participation.data;
  const subjectId = manualSubjectId ?? (subject !== null && subject.status === 'present' ? subject.player_id : null);
  const subjectStatus = subject === null ? null : subject.status;

  useEffect(() => {
    // A new configured primary supersedes a manual selection: the override is
    // per-demo convenience, not a replacement of the persisted identity.
    setManualSubjectId(null);
  }, [subjectSteamId]);

  const rounds = usePolled((signal) => client.rounds(demoId ?? '', { generation_id: generationId }, signal), 20000, {
    enabled: demoId !== null && generationId !== null,
    key: `${demoId ?? ''}|${generationId ?? ''}`,
  });

  const roundList = rounds.data?.rounds ?? [];
  const selectedRound = roundList.find((round) => round.round_id === roundId) ?? null;

  useEffect(() => {
    setRoundId(null);
    setManualLevel(null);
    setManualSubjectId(null);
    setPendingSeek(null);
    setSnapshot(null);
    setEncounterDetail(null);
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

  /**
   * Seek by anchor.
   *
   * A tick is only applied against the payload of the round it belongs to: the
   * previous round's window is never used to clamp it. When that round's window
   * is not the loaded one yet, the round switch and the tick are queued together
   * and applied once the new payload arrives. A tick outside the loaded window
   * is clamped to its edge and reported, never silently moved.
   */
  const seekTo = useCallback(
    (targetRoundId: number, tick: number) => {
      if (bounds === null || replay.roundId !== targetRoundId) {
        setRoundId(targetRoundId);
        setPendingSeek({ roundId: targetRoundId, tick });
        return;
      }
      const clamped = Math.min(bounds.max, Math.max(bounds.min, tick));
      setSeekNotice(
        clamped === tick
          ? null
          : `anchor tick ${tick} lies outside round ${targetRoundId}'s loaded window ${bounds.min}–${bounds.max}; seeked to ${clamped}`,
      );
      clock.seek(clamped);
    },
    [bounds, clock, replay.roundId],
  );

  useEffect(() => {
    if (pendingSeek === null) return;
    if (replay.error !== null) {
      setSeekNotice(`round ${pendingSeek.roundId} could not be loaded (${replay.error.code}); the anchor tick was not applied`);
      setPendingSeek(null);
      return;
    }
    // `replay.roundId` is the round the payload actually describes, so a stale
    // window can never satisfy this gate; the clock's bounds reset runs before
    // this effect in the same commit, so the seek lands after the reset.
    if (replay.loading || replay.roundId !== pendingSeek.roundId || bounds === null) return;
    const clamped = Math.min(bounds.max, Math.max(bounds.min, pendingSeek.tick));
    setSeekNotice(
      clamped === pendingSeek.tick
        ? null
        : `anchor tick ${pendingSeek.tick} lies outside round ${pendingSeek.roundId}'s loaded window ${bounds.min}–${bounds.max}; seeked to ${clamped}`,
    );
    clock.seek(clamped);
    setPendingSeek(null);
  }, [pendingSeek, replay.loading, replay.error, replay.roundId, bounds, clock]);

  // Relation overlay: one line per active relation, using only recorded view
  // origins. A relation without a recorded origin is left out instead of being
  // drawn at an invented position.
  const relationLines = useMemo<RadarRelationLine[]>(() => {
    if (snapshot === null) return [];
    const lines: RadarRelationLine[] = [];
    for (const relation of snapshot.relations) {
      const from = relation.view_origin;
      const to = relation.other_view_origin;
      if (from.x === null || from.y === null || to.x === null || to.y === null) continue;
      const qualifier = sightlineQualifier(
        relation.static_sightline?.status ?? null,
        relation.static_sightline?.match_status ?? null,
        relation.static_effective_status,
        from.qualified && to.qualified ? 'recorded' : 'estimated',
      );
      lines.push({
        id: relation.player_id,
        qualifier: qualifier.key,
        from: { x: from.x, y: from.y },
        to: { x: to.x, y: to.y },
      });
    }
    return lines;
  }, [snapshot]);

  const trajectoryOverlay = useMemo<RadarTrajectory | null>(() => {
    if (encounterDetail === null || encounterDetail.subject_trajectory.length === 0) return null;
    return {
      id: encounterDetail.summary.encounter_id,
      label: `recorded subject samples every ${encounterDetail.trajectory_stride} ticks (gaps, missing coordinates and death are not connected)`,
      strideTicks: encounterDetail.trajectory_stride,
      samples: encounterDetail.subject_trajectory.map((state) => ({
        tick: state.tick,
        x: state.x,
        y: state.y,
        health: state.health,
      })),
    };
  }, [encounterDetail]);

  // Geometry probe prefill: the first active relation's recorded view origins.
  const probePoints = useMemo<{ subjectPoint: Vec3 | null; otherPoint: Vec3 | null }>(() => {
    const relation = snapshot?.relations[0] ?? null;
    if (relation === null) return { subjectPoint: null, otherPoint: null };
    const from = relation.view_origin;
    const to = relation.other_view_origin;
    return {
      subjectPoint: from.x === null || from.y === null || from.z === null ? null : [from.x, from.y, from.z],
      otherPoint: to.x === null || to.y === null || to.z === null ? null : [to.x, to.y, to.z],
    };
  }, [snapshot]);

  // Recorded player origin (feet) of the subject at the current tick, for
  // ground questions (floor, nav area). A missing altitude is not invented.
  const subjectOrigin = useMemo<Vec3 | null>(() => {
    if (subjectId === null) return null;
    const actor = actors.find((frame) => frame.player_id === subjectId) ?? null;
    return actor === null || actor.z === null ? null : [actor.x, actor.y, actor.z];
  }, [actors, subjectId]);

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
        {generationId !== null ? (
          <button type="button" onClick={() => setInspectorOpen((open) => !open)} aria-pressed={inspectorOpen}>
            {inspectorOpen ? 'Hide inspector' : 'Show inspector'}
          </button>
        ) : null}
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

          <div className="replay-select">
            <label htmlFor="subject-select">Analysis subject</label>
            <select
              id="subject-select"
              value={manualSubjectId ?? ''}
              onChange={(event) => setManualSubjectId(event.target.value === '' ? null : event.target.value)}
            >
              <option value="">
                configured primary — {subject === null ? 'loading…' : `${subject.status}${subject.player_id === null ? '' : ` · ${subject.player_id}`}`}
              </option>
              {replay.players.map((player) => (
                <option key={player.player_id} value={player.player_id}>
                  {player.name ?? '(no name in recording)'} · {player.player_id}
                  {player.steam_id === null ? ' · identity unresolved (reconstruction unavailable)' : ''}
                </option>
              ))}
            </select>
            {subject !== null ? <span className={`badge ${participationBadge(subject.status)}`}>{subject.status}</span> : null}
            {subject !== null && subject.player_id_source === 'override' ? <span className="badge badge-warn">override</span> : null}
            {manualSubjectId !== null ? (
              <button type="button" onClick={() => setManualSubjectId(null)}>
                Use configured subject
              </button>
            ) : null}
            <span className="small">{subject === null ? 'participation not loaded' : `${subject.map_name ?? 'map unknown'} · gen ${shortHash(subject.generation_id ?? '')}`}</span>
          </div>
          <ErrorNotice error={participation.error} context="GET /demos/{demo_id}/participation" />
          {subject !== null && subject.limitations.length > 0 ? (
            <p className="notice notice-warning" role="status">
              {subject.limitations.join(' · ')}
            </p>
          ) : null}
          {subject !== null && subject.status !== 'present' && manualSubjectId === null ? (
            <p className="notice notice-warning" role="status">
              The configured subject is {subject.status} in this generation. Encounter and context panels stay unavailable until a participant is selected
              explicitly; the configured identity is never replaced.
            </p>
          ) : null}

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
                relations={relationLines}
                trajectory={trajectoryOverlay}
              />

              <WarningList warnings={replay.warnings} />
              {seekNotice !== null ? (
                <p className="notice notice-warning" role="status">
                  {seekNotice}
                </p>
              ) : null}

              {inspectorOpen ? (
                <Inspector
                  demoId={demoId}
                  generationId={generationId}
                  tick={clock.tick}
                  players={replay.players}
                  tickRateHz={replay.tickRateHz}
                  startTick={replay.startTick}
                  onSeek={clock.seek}
                />
              ) : null}

              <div className="participants">
                <h3>Participants ({replay.players.length})</h3>
                <ul className="list">
                  {replay.players.map((player) => {
                    const unresolved = player.steam_id === null || player.name === null;
                    return (
                      <li key={player.player_id} className="list-row">
                        <span
                          className={`badge ${player.side === 'ct' ? 'badge-ct' : player.side === 't' ? 'badge-t' : ''}`}
                          title="recording roster side; not the side observed at the current tick"
                        >
                          roster {sideLabel(player.side)}
                        </span>
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
                  A null SteamID is a recording-local roster entry and is never joined by name or converted to a number; unresolved observations stay separate. The
                  side shown here comes from the recording roster, not the current tick — tick-side observations and per-tick relations are in the
                  context panel below.
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

          {/* Kept outside the radar-ready block: a round load clears the radar
              payload for a moment, and unmounting here would drop the selected
              encounter, the probe fields and the tick-following context read. */}
          <EncountersPanel
            demoId={demoId}
            generationId={generationId}
            subjectId={subjectId}
            subjectStatus={subjectStatus}
            rounds={roundList}
            tickRateHz={replay.tickRateHz}
            tick={clock.tick}
            onSeekAnchor={seekTo}
            onDetailChanged={setEncounterDetail}
          />

          <ContextPanel
            demoId={demoId}
            generationId={generationId}
            subjectId={subjectId}
            subjectStatus={subjectStatus}
            tick={clock.tick}
            playing={clock.playing}
            tickRateHz={replay.tickRateHz}
            playerById={playerById}
            onSeek={clock.seek}
            onSnapshot={setSnapshot}
          />

          <GeometryPanel
            mapName={radar?.map_name ?? null}
            demoClientVersion={radar?.demo_client_version ?? null}
            subjectPoint={probePoints.subjectPoint}
            otherPoint={probePoints.otherPoint}
            subjectOrigin={subjectOrigin}
          />

          {!replay.loading && replay.error === null && replay.samples.length === 0 ? (
            <p className="hint">The selected round returned no player samples in its window.</p>
          ) : null}
        </>
      ) : null}
    </section>
  );
}

