import { useEffect, useState, type ReactNode } from 'react';
import type { AnalyticState, EventsResponse, StateResponse, TrajectoryResponse } from '../api/types';
import type { ReplayPlayer } from '../api/types';
import { ANALYTICS_DATASETS, getEvents, getState, getTrajectory } from '../lib/analytics';
import { formatTickTime, sideLabel } from '../lib/format';
import { useAnalyticsQuery } from '../lib/useAnalyticsQuery';
import { EventList } from './EventList';
import { ErrorNotice } from './Notices';

type Props = {
  demoId: string;
  generationId: string;
  /** Live replay tick; the inspector follows it unless the tick is held. */
  tick: number;
  players: ReplayPlayer[];
  tickRateHz: number;
  startTick: number | null;
  onSeek: (tick: number) => void;
};

const EVENTS_LIMIT = 500;
/** Inspector refresh granularity while following: ~8 reads per second. */
const FOLLOW_SAMPLES_PER_SECOND = 8;

function MissingValue({ label }: { label: string }): ReactNode {
  return (
    <span className="badge badge-warn" title={`No ${label} recorded for this observation`}>
      missing
    </span>
  );
}

function numberValue(value: number | null, digits: number, label: string): ReactNode {
  if (value === null || !Number.isFinite(value)) return <MissingValue label={label} />;
  return <span className="mono">{value.toFixed(digits)}</span>;
}

/** `missing_ranges` entries are `[lo, hi]` tick pairs from the trajectory response. */
function containsTick(range: number[], tick: number): boolean {
  const [lo, hi] = range;
  return lo !== undefined && hi !== undefined && tick >= lo && tick <= hi;
}

function velocityValue(row: AnalyticState): ReactNode {
  if (row.velocity_x === null && row.velocity_y === null && row.velocity_z === null) return <MissingValue label="velocity" />;
  return (
    <span className="mono small">
      {numberValue(row.velocity_x, 1, 'velocity x')} {numberValue(row.velocity_y, 1, 'velocity y')} {numberValue(row.velocity_z, 1, 'velocity z')}
    </span>
  );
}

/** Presentation of one verbatim state row; no value is derived from the others. */
function stateRows(row: AnalyticState): { label: string; value: ReactNode }[] {
  return [
    { label: 'tick', value: <span className="mono">{row.tick}</span> },
    {
      label: 'player',
      value: row.player_id === null ? <MissingValue label="player identity" /> : <span className="mono small">{row.player_id}</span>,
    },
    { label: 'x', value: numberValue(row.x, 2, 'x') },
    { label: 'y', value: numberValue(row.y, 2, 'y') },
    { label: 'z', value: numberValue(row.z, 2, 'z') },
    { label: 'yaw', value: numberValue(row.yaw, 2, 'yaw') },
    { label: 'pitch', value: numberValue(row.pitch, 2, 'pitch') },
    { label: 'velocity (x, y, z)', value: velocityValue(row) },
    { label: 'health', value: row.health === null ? <MissingValue label="health" /> : <span className="mono">{row.health}</span> },
  ];
}

/**
 * Player inspector for the replay. Every number shown comes from an analytics
 * endpoint response (or from the replay chunk already loaded); nothing is
 * interpolated or computed in the browser.
 */
export function Inspector({ demoId, generationId, tick, players, tickRateHz, startTick, onSeek }: Props): ReactNode {
  const [playerId, setPlayerId] = useState<string | null>(null);
  const [heldTick, setHeldTick] = useState<number | null>(null);

  useEffect(() => {
    // A new round brings a new roster: drop the stale selection and hold.
    setPlayerId((current) => (current !== null && players.some((player) => player.player_id === current) ? current : players[0]?.player_id ?? null));
    setHeldTick(null);
  }, [players]);

  const sampleStep = tickRateHz > 0 ? Math.max(1, Math.round(tickRateHz / FOLLOW_SAMPLES_PER_SECOND)) : 1;
  const secondStep = tickRateHz > 0 ? Math.max(1, Math.round(tickRateHz)) : sampleStep;
  const liveTick = Math.floor(tick / sampleStep) * sampleStep;
  const following = heldTick === null;
  const targetTick = heldTick ?? liveTick;
  const windowCenter = Math.floor(targetTick / secondStep) * secondStep;
  const windowSpan = Math.max(64, secondStep);
  const enabled = playerId !== null;

  // Each query tags its response with the selection it was issued for, so a
  // slow answer for a previous player or tick is never shown as the current one.
  // `playerId ?? ''` is only ever a placeholder: the queries stay disabled
  // until a player is selected. The state read tolerates one follow step, so a
  // tick without a recorded row falls back to the nearest recorded row, which
  // the readout labels with its own tick.
  const stateQuery = useAnalyticsQuery(
    (signal) =>
      getState(demoId, { generationId, tick: targetTick, playerId, maxGap: sampleStep }, signal).then((response) => ({ playerId, anchor: targetTick, response })),
    `${demoId}|${generationId}|player:${playerId ?? ''}|state:${targetTick}`,
    enabled,
  );
  const trajectoryQuery = useAnalyticsQuery(
    (signal) =>
      getTrajectory(
        demoId,
        { generationId, playerId: playerId ?? '', start: Math.max(0, windowCenter - windowSpan), end: windowCenter + windowSpan, stride: 1 },
        signal,
      ).then((response) => ({ playerId, anchor: windowCenter, response })),
    `${demoId}|${generationId}|player:${playerId ?? ''}|window:${windowCenter}`,
    enabled,
  );
  const trajectory =
    trajectoryQuery.data !== null && trajectoryQuery.data.playerId === playerId && trajectoryQuery.data.anchor === windowCenter
      ? trajectoryQuery.data.response
      : null;

  const eventsQuery = useAnalyticsQuery(
    (signal) =>
      getEvents(
        demoId,
        {
          generationId,
          datasets: ANALYTICS_DATASETS,
          start: Math.max(0, windowCenter - windowSpan),
          end: windowCenter + windowSpan,
          limit: EVENTS_LIMIT,
        },
        signal,
      ).then((response) => ({ anchor: windowCenter, response })),
    `${demoId}|${generationId}|events:${windowCenter}`,
    true,
  );
  const events = eventsQuery.data !== null && eventsQuery.data.anchor === windowCenter ? eventsQuery.data.response : null;

  const selectedPlayer = players.find((player) => player.player_id === playerId) ?? null;
  const stateAnswer = stateQuery.data;
  const state = stateAnswer !== null && stateAnswer.playerId === playerId && stateAnswer.anchor === targetTick ? stateAnswer.response : null;
  // The last answer for this player stays on screen while the next tick loads;
  // every row carries its own tick, so nothing is presented as the current one.
  const stateShown = state !== null ? state : stateAnswer !== null && stateAnswer.playerId === playerId ? stateAnswer.response : null;
  const observations = stateShown === null ? [] : stateShown.states;
  const missingRanges = trajectory === null ? [] : trajectory.missing_ranges;
  const missingAtTick = missingRanges.some((range) => containsTick(range, targetTick));
  const windowLabel = `±${windowSpan} ticks`;

  return (
    <div className="participants">
      <h3>Inspector</h3>
      <div className="replay-select">
        <label htmlFor="inspector-player">Player</label>
        <select
          id="inspector-player"
          value={playerId ?? ''}
          onChange={(event) => setPlayerId(event.target.value === '' ? null : event.target.value)}
          disabled={players.length === 0}
        >
          <option value="">{players.length === 0 ? 'no players in this round' : 'select a player'}</option>
          {players.map((player) => (
            <option key={player.player_id} value={player.player_id}>
              {player.name ?? '(no name in recording)'} · {sideLabel(player.side)}
            </option>
          ))}
        </select>
        <button type="button" onClick={() => setHeldTick(following ? liveTick : null)} aria-pressed={!following} disabled={!enabled}>
          {following ? 'Hold tick' : 'Follow replay'}
        </button>
        <span className="small mono">
          {following ? `following replay at ~${FOLLOW_SAMPLES_PER_SECOND}/s` : `held at ${targetTick}`}
        </span>
      </div>

      <div className="tick-readout">
        <span className="tick-label">Inspector tick</span>
        <span className="tick-value mono" data-testid="inspector-tick">
          {targetTick}
        </span>
        <span className="small">
          {startTick === null ? 'round time n/a' : `${formatTickTime(targetTick, startTick, tickRateHz)} after freeze end`} ·{' '}
          {tickRateHz > 0 ? `${tickRateHz} Hz` : 'tick rate unknown'} · {selectedPlayer?.player_id ?? 'no player selected'}
        </span>
        {state === null ? (
          stateShown !== null ? <span className="badge">awaiting tick {targetTick}</span> : null
        ) : state.exact ? (
          <span className="badge badge-succeeded">exact tick</span>
        ) : state.actual_tick !== null ? (
          <span className="badge">nearest tick {state.actual_tick} (±{state.gap_ticks ?? 0})</span>
        ) : (
          <span className="badge badge-warn">no state row within ±{sampleStep} ticks</span>
        )}
        {missingAtTick ? <span className="badge badge-warn">player has no row here ({windowLabel})</span> : null}
        {trajectory !== null ? <span className="badge">{missingRanges.length} gap range(s) in {windowLabel}</span> : null}
      </div>

      <ErrorNotice error={stateQuery.error} context="GET /demos/{demo_id}/analytics/state" />
      <ErrorNotice error={trajectoryQuery.error} context="GET /demos/{demo_id}/analytics/trajectory" />

      {playerId === null ? (
        <p className="hint">Select a player to inspect the recorded state row at the current tick.</p>
      ) : observations.length === 0 ? (
        state === null ? (
          <p className="hint">Loading the state row for tick {targetTick}…</p>
        ) : (
          <p className="list-empty">No state row recorded for this player within ±{sampleStep} ticks of {targetTick}.</p>
        )
      ) : (
        <>
          {observations.length > 1 ? <p className="hint">{observations.length} state rows at this tick.</p> : null}
          <ul className="list">
            {observations.map((row: AnalyticState) => (
              <li className="list-row" key={`${row.tick}:${row.row_ordinal}`}>
                <div className="demo-meta">
                  {stateRows(row).map((field) => (
                    <span className="small" key={field.label}>
                      {field.label} {field.value}
                    </span>
                  ))}
                </div>
              </li>
            ))}
          </ul>
        </>
      )}

      {trajectory !== null ? (
        <p className="hint">
          {trajectory.sample_count} recorded sample(s) for this player in {windowLabel} ({trajectory.start_tick}–{trajectory.end_tick}, stride {trajectory.stride}).
        </p>
      ) : null}

      <ErrorNotice error={eventsQuery.error} context="GET /demos/{demo_id}/analytics/events" />
      <EventList
        events={events === null ? [] : events.events}
        tick={targetTick}
        startTick={startTick}
        tickRateHz={tickRateHz}
        onJump={onSeek}
        loading={eventsQuery.loading}
      />
      {events !== null ? (
        <p className="hint">
          {events.event_count} event(s) between ticks {events.start_tick} and {events.end_tick}
          {events.event_count >= EVENTS_LIMIT ? ` (server limit of ${EVENTS_LIMIT} reached)` : ''}.
        </p>
      ) : null}
    </div>
  );
}
