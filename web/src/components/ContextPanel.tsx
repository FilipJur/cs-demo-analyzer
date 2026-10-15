import { useEffect, useState, type ReactNode } from 'react';
import { phase2 } from '../api/phase2';
import type {
  ContextCapabilities,
  ContextRelation,
  ContextSnapshot,
  ContextStateRef,
  EvidenceRef,
  LifecycleFact,
  ReplayPlayer,
} from '../api/types';
import { shortHash, sideLabel } from '../lib/format';
import { evidenceLabel, followStep, sightlineQualifier } from '../lib/phase2';
import { useAnalyticsQuery } from '../lib/useAnalyticsQuery';
import { ErrorNotice, WarningList } from './Notices';

type Props = {
  demoId: string;
  generationId: string;
  /** Resolved recording identity of the subject; null when the primary is unavailable. */
  subjectId: string | null;
  /** Participation status behind `subjectId`, used for the unavailable message. */
  subjectStatus: string | null;
  /** Live replay tick: the exact tick shown in the replay readout. */
  tick: number;
  playing: boolean;
  tickRateHz: number;
  playerById: Map<string, ReplayPlayer>;
  /** Seek the replay to an exact tick. */
  onSeek: (tick: number) => void;
  /** Latest snapshot, lifted so the radar can draw its qualified relation lines. */
  onSnapshot: (snapshot: ContextSnapshot | null) => void;
};

/** Context reads per second while the replay plays. */
const FOLLOW_SAMPLES_PER_SECOND = 4;

function EvidenceRefList({ refs }: { refs: (EvidenceRef | null)[] }): ReactNode {
  const present = refs.filter((ref): ref is EvidenceRef => ref !== null);
  if (present.length === 0) return <p className="hint">No evidence reference is attached to this view.</p>;
  return (
    <ul className="list dense">
      {present.map((ref) => (
        <li key={`${ref.dataset}#${ref.row_ordinal}`} className="mono small">
          {evidenceLabel(ref)}
        </li>
      ))}
    </ul>
  );
}

function StateLine({ label, state }: { label: string; state: ContextStateRef | null }): ReactNode {
  if (state === null) return <li className="list-row"><span className="grow">{label}</span><span className="badge badge-warn">no recorded state</span></li>;
  const health = state.health === null ? 'health not recorded' : `${state.health}hp`;
  return (
    <li className="list-row">
      <span className="grow truncate">{label}</span>
      <span className={`badge ${state.alive ? 'badge-succeeded' : 'badge-failed'}`}>{state.alive ? 'alive' : 'not alive'}</span>
      <span className="small">{state.side === null ? 'side unknown' : sideLabel(state.side)}</span>
      <span className="mono small">{health}</span>
      <span className="small">{state.active_weapon ?? 'weapon unknown'}</span>
      <span className="small">
        {state.is_crouched === null ? 'stance unknown' : state.is_crouched ? 'crouched' : 'standing'}
        {state.is_scoped === null ? '' : state.is_scoped ? ' · scoped' : ' · unscoped'}
      </span>
      <span className="mono small" title={state.evidence === null ? '' : evidenceLabel(state.evidence)}>
        {state.dataset}#{state.row_ordinal}
      </span>
    </li>
  );
}

function relationRow(relation: ContextRelation, playerById: Map<string, ReplayPlayer>): ReactNode {
  const qualifier = sightlineQualifier(
    relation.static_sightline?.status ?? null,
    relation.static_sightline?.match_status ?? null,
    relation.static_effective_status,
    relation.view_origin.qualified && relation.other_view_origin.qualified ? 'recorded' : 'estimated',
  );
  const other = playerById.get(relation.player_id);
  const name = other?.name ?? null;
  return (
    <span className="relation-row" title={relation.limitations.join('\n')}>
      <span className="badge">{relation.relation}</span>
      <span className="grow truncate mono small" title={relation.player_id}>
        {name ?? relation.player_id}
      </span>
      <span className="small">{relation.other_side === null ? 'side unknown' : sideLabel(relation.other_side)}</span>
      <span className="mono small">
        {relation.distance_2d === null ? 'd2 n/a' : `${relation.distance_2d.toFixed(0)}u`}
        {relation.distance_3d === null ? '' : ` / ${relation.distance_3d.toFixed(0)}u3`}
      </span>
      <span className="mono small">{relation.relative_yaw === null ? 'relative yaw n/a' : `${relation.relative_yaw.toFixed(1)}°`}</span>
      <span className={`badge ${qualifier.className}`} title={relation.static_sightline?.limitations.join('\n') ?? ''}>
        {qualifier.label}
      </span>
      <span className="small">
        subject eye {relation.view_origin.mode}
        {relation.view_origin.qualified ? ' (recorded)' : ' (unqualified estimate)'} · other eye {relation.other_view_origin.mode}
        {relation.other_view_origin.qualified ? ' (recorded)' : ' (unqualified estimate)'}
      </span>
      {relation.other_state !== null ? (
        <span className="small">
          {relation.other_state.health === null ? 'health not recorded' : `${relation.other_state.health}hp`}
        </span>
      ) : null}
      {relation.navigation !== null ? (
        <span className="small" title={relation.navigation.limitations.join('\n')}>
          nav {relation.navigation.status}
          {relation.navigation.path_distance === null ? '' : ` · ~${relation.navigation.path_distance.toFixed(0)}u area-centre estimate`}
        </span>
      ) : null}
      {relation.limitations.length > 0 ? <span className="badge badge-warn">{relation.limitations.length}</span> : null}
    </span>
  );
}

function capabilityRows(capabilities: ContextCapabilities): { label: string; status: string; source: string; limitations: string[] }[] {
  return [
    { label: 'state', ...capabilities.state },
    { label: 'geometry', ...capabilities.geometry },
    { label: 'sightlines', ...capabilities.sightlines },
    { label: 'navigation', ...capabilities.navigation },
    { label: 'utility', ...capabilities.utility },
    { label: 'exposure', ...capabilities.exposure },
    { label: 'view origin', ...capabilities.view_origin },
    { label: 'lifecycle', ...capabilities.lifecycle },
  ];
}

function lifecycleLine(label: string, fact: LifecycleFact | null | undefined, tick: number): ReactNode {
  if (fact === null || fact === undefined) {
    return (
      <li className="list-row">
        <span className="badge">{label}</span>
        <span className="grow small">no recorded lifecycle row</span>
      </li>
    );
  }
  return (
    <li className="list-row" title={fact.limitations.join('\n')}>
      <span className="badge">{label}</span>
      <span className="badge">{fact.kind}</span>
      <span className="mono small">
        tick {fact.tick} ({fact.tick === tick ? 'at' : fact.tick < tick ? `${tick - fact.tick} before` : `${fact.tick - tick} after`})
      </span>
      <span className="grow truncate mono small">{fact.player_id ?? 'unattributed row'}</span>
      <span className="small">{fact.team ?? 'team unknown'}</span>
      {fact.previous_team === null || fact.previous_team === undefined ? null : <span className="small">was {fact.previous_team}</span>}
      {fact.reason_code === null || fact.reason_code === undefined ? null : <span className="small">reason {fact.reason_code}</span>}
      {fact.is_bot === null || fact.is_bot === undefined ? null : <span className="small">{fact.is_bot ? 'bot' : 'human'}</span>}
      {fact.ever_fully_connected === false ? <span className="badge badge-warn">never fully connected</span> : null}
    </li>
  );
}

function SnapshotView({
  snapshot,
  playerById,
  tickRateHz,
  crossPairs,
}: {
  snapshot: ContextSnapshot;
  playerById: Map<string, ReplayPlayer>;
  tickRateHz: number;
  crossPairs: boolean;
}): ReactNode {
  const counts = snapshot.counts;
  return (
    <>
      <div className="tick-readout">
        <span className="tick-label">Context tick</span>
        <span className="tick-value mono">{snapshot.tick}</span>
        <span className="small">
          requested {snapshot.tick} · recorded row tick {snapshot.actual_tick ?? 'none'} · {snapshot.exact ? 'exact' : 'NOT exact'}
          {snapshot.gap_ticks === null ? '' : ` · gap ${snapshot.gap_ticks} ticks`} · round {snapshot.round_id ?? 'unknown'} ·{' '}
          {tickRateHz > 0 ? `${tickRateHz} Hz` : 'tick rate unknown'}
        </span>
      </div>

      <h4>Subject</h4>
      <ul className="list dense">
        <StateLine label={`subject ${snapshot.subject_id}`} state={snapshot.subject} />
      </ul>
      {!snapshot.subject_alive ? (
        <p className="notice notice-warning" role="status">
          The subject has no living observation at this tick: relations are reported as recorded state, and exposure is not counted.
        </p>
      ) : null}

      <h4>Recorded lifecycle</h4>
      <ul className="list dense">
        {lifecycleLine('before', snapshot.lifecycle_before, snapshot.tick)}
        {lifecycleLine('after', snapshot.lifecycle_after, snapshot.tick)}
      </ul>
      <p className="small">
        lifecycle capability {snapshot.capabilities.lifecycle.status} · unattributed lifecycle rows at this read{' '}
        {snapshot.lifecycle_unattributed_rows}
        {snapshot.lifecycle_unattributed_rows > 0 ? ' (rows whose account id is unresolved: counted, never assigned to a player)' : ''}
      </p>
      {snapshot.capabilities.lifecycle.status !== 'available' ? (
        <p className="hint">
          {snapshot.capabilities.lifecycle.limitations.join(' · ') ||
            'No recorded lifecycle rows exist for this generation, so a missing participant state has no recorded explanation here and is never reported as inactivity.'}
        </p>
      ) : null}

      <h4>Observations at this tick</h4>
      <p className="small">
        state rows {counts.state_rows} · identified {counts.identity_identified} · null identity {counts.identity_null} (alive {counts.identity_null_alive}) · living{' '}
        {counts.living} · dead {counts.dead} · health unknown {counts.unknown_health}
      </p>
      <p className="small">
        active relations {counts.active_relations} · inactive {counts.inactive_relations} · same side {counts.same_side} · opposite {counts.opposite_side} · side
        unknown {counts.unknown_side}
      </p>
      <p className="small">
        opponent statics: clear {counts.opponent_static_clear} · blocked {counts.opponent_static_blocked} · unknown {counts.opponent_static_unknown} · sightlines
        evaluated {counts.sightlines_evaluated} · unavailable {counts.sightlines_unavailable} · cross pairs {counts.cross_pairs_evaluated}
      </p>
      <p className="small">
        static readings are scoped to {snapshot.static_scope}: a static-geometry fact of the installed map build, never confirmed visibility or exposure.
      </p>

      <h4>Participants at this tick ({snapshot.participants.length})</h4>
      <ul className="list dense">
        {snapshot.participants.map((participant) => (
          <li key={participant.player_id} className="list-row">
            <span className="badge">{participant.side === null ? 'side unknown' : sideLabel(participant.side)}</span>
            <span className="grow truncate mono small">{participant.player_id}</span>
            <span className="small">{participant.health === null ? 'health not recorded' : `${participant.health}hp`}</span>
            <span className="mono small">
              {participant.dataset}#{participant.row_ordinal}
            </span>
          </li>
        ))}
        {snapshot.participants.length === 0 ? <li className="list-empty">No identified participant row at this exact tick.</li> : null}
      </ul>

      <h4>Angular geometry</h4>
      <p className="small">
        opponents {snapshot.angular_spread.opponent_count} · span {snapshot.angular_spread.span_degrees === null ? 'n/a' : `${snapshot.angular_spread.span_degrees.toFixed(1)}°`} · max pair
        separation{' '}
        {snapshot.angular_spread.max_pair_separation_degrees === null ? 'n/a' : `${snapshot.angular_spread.max_pair_separation_degrees.toFixed(1)}°`} · subject yaw{' '}
        {snapshot.angular_spread.subject_yaw === null ? 'not recorded' : snapshot.angular_spread.subject_yaw.toFixed(1)}
        {snapshot.angular_spread.subject_yaw === null ? '' : snapshot.angular_spread.subject_yaw_recorded ? ' (recorded)' : ' (estimated)'}
      </p>
      <ul className="list dense">
        {snapshot.opponent_directions.map((direction) => (
          <li key={direction.player_id} className="list-row">
            <span className="badge">opponent</span>
            <span className="grow truncate mono small">{direction.player_id}</span>
            <span className="small">bearing {direction.bearing_degrees === null ? 'n/a' : `${direction.bearing_degrees.toFixed(1)}°`}</span>
            <span className="small">relative yaw {direction.relative_yaw === null ? 'n/a' : `${direction.relative_yaw.toFixed(1)}°`}</span>
          </li>
        ))}
      </ul>

      <h4>Teammate → opponent pair sightlines ({crossPairs ? snapshot.pair_relations.length : 'not requested'})</h4>
      {crossPairs ? (
        <ul className="list dense">
          {snapshot.pair_relations.map((pair) => {
            const qualifier = sightlineQualifier(
              pair.static_sightline?.status ?? null,
              pair.static_sightline?.match_status ?? null,
              pair.static_effective_status,
              pair.teammate_origin.qualified && pair.opponent_origin.qualified ? 'recorded' : 'estimated',
            );
            return (
              <li key={`${pair.teammate_id}->${pair.opponent_id}`} className="list-row" title={pair.limitations.join('\n')}>
                <span className="grow truncate mono small">
                  {pair.teammate_id} → {pair.opponent_id}
                </span>
                <span className="mono small">{pair.distance_2d === null ? 'd2 n/a' : `${pair.distance_2d.toFixed(0)}u`}</span>
                <span className={`badge ${qualifier.className}`}>{qualifier.label}</span>
                {pair.navigation !== null ? (
                  <span className="small" title={pair.navigation.limitations.join('\n')}>
                    nav {pair.navigation.status}
                    {pair.navigation.path_distance === null ? '' : ` · ~${pair.navigation.path_distance.toFixed(0)}u area-centre estimate`}
                  </span>
                ) : null}
                <span className="small">scope {pair.scope}</span>
              </li>
            );
          })}
          {snapshot.pair_relations.length === 0 ? <li className="list-empty">No living teammate/opponent pair is recorded at this exact tick.</li> : null}
        </ul>
      ) : (
        <p className="hint">
          Pair sightlines are opt-in: this read only resolved the subject's own relations, so no teammate → opponent pair was evaluated ({snapshot.counts.cross_pairs_evaluated}{' '}
          evaluated).
        </p>
      )}

      <h4>Active relations ({snapshot.relations.length})</h4>
      <ul className="list dense">
        {snapshot.relations.map((relation) => (
          <li key={`active-${relation.player_id}`}>{relationRow(relation, playerById)}</li>
        ))}
        {snapshot.relations.length === 0 ? <li className="list-empty">No living relation is recorded at this exact tick.</li> : null}
      </ul>

      {snapshot.inactive_relations.length > 0 ? (
        <details>
          <summary>Inactive relations ({snapshot.inactive_relations.length}) — recorded state, not counted as available</summary>
          <ul className="list dense">
            {snapshot.inactive_relations.map((relation) => (
              <li key={`inactive-${relation.player_id}`}>{relationRow(relation, playerById)}</li>
            ))}
          </ul>
        </details>
      ) : null}
      <h4>Observed movement ({snapshot.position_change === null ? 'not requested' : snapshot.position_change.contiguous_living ? 'contiguous' : 'withheld'})</h4>
      {snapshot.position_change === null ? (
        <p className="hint">This read returned no bounded movement window for the subject.</p>
      ) : (
        <>
          <p className="small">
            ticks {snapshot.position_change.from_tick}–{snapshot.position_change.to_tick} every {snapshot.position_change.stride_ticks} ·{' '}
            {snapshot.position_change.living_samples} living sample(s) · {snapshot.position_change.dead_samples} dead/unrecorded-health sample(s) ·{' '}
            {snapshot.position_change.missing_samples} missing
          </p>
          {snapshot.position_change.contiguous_living ? (
            <p className="small mono">
              displacement {snapshot.position_change.displacement_2d === null ? 'n/a' : `${snapshot.position_change.displacement_2d.toFixed(0)}u`} 2D /{' '}
              {snapshot.position_change.displacement_3d === null ? 'n/a' : `${snapshot.position_change.displacement_3d.toFixed(0)}u`} 3D · path{' '}
              {snapshot.position_change.path_length_2d === null ? 'n/a' : `${snapshot.position_change.path_length_2d.toFixed(0)}u`} · d
              ({snapshot.position_change.dx?.toFixed(0) ?? 'n/a'}, {snapshot.position_change.dy?.toFixed(0) ?? 'n/a'}, {snapshot.position_change.dz?.toFixed(0) ?? 'n/a'})
            </p>
          ) : (
            <p className="notice notice-warning" role="status">
              Movement is withheld: the living samples are not one contiguous run on this grid inside a single round, so no displacement or path is reported.
            </p>
          )}
          <WarningList warnings={snapshot.position_change.limitations} />
        </>
      )}

      <h4>Recorded utility</h4>
      <ul className="list dense">
        {snapshot.utility.map((fact, index) => (
          <li
            key={`${fact.kind}-${fact.start_tick}-${index}`}
            className="list-row"
            title={fact.limitations.join('\n')}
          >
            <span className="badge">{fact.kind}</span>
            <span className={`badge ${fact.semantics_reliable ? '' : 'badge-warn'}`}>{fact.semantics_reliable ? 'semantics recorded' : 'semantics unresolved'}</span>
            <span className="badge">{fact.evidence_kind}</span>
            <span className="grow truncate mono small">{fact.owner_id ?? 'owner unresolved (absent upstream field)'}</span>
            <span className="small">
              ticks {fact.start_tick}
              {fact.end_tick === null ? ' → unresolved' : ` → ${fact.end_tick}`}
            </span>
            <span className="small">{fact.site === null ? 'site unknown' : fact.site}</span>
            <span className="mono small" title={fact.evidence === null ? 'no source row' : evidenceLabel(fact.evidence)}>
              {fact.evidence === null ? 'no source row' : `${fact.evidence.dataset}#${fact.evidence.row_ordinal}`}
            </span>
          </li>
        ))}
        {snapshot.utility.length === 0 ? <li className="list-empty">No recorded utility interval is active at this exact tick.</li> : null}
      </ul>

      <h4>Capabilities</h4>
      <ul className="list dense">
        {capabilityRows(snapshot.capabilities).map((entry) => (
          <li key={entry.label} className="list-row" title={entry.limitations.join('\n')}>
            <span className="badge">{entry.label}</span>
            <span className="grow mono small">{entry.status}</span>
            <span className="small truncate">{entry.source}</span>
            {entry.limitations.length > 0 ? <span className="badge badge-warn">{entry.limitations.length}</span> : null}
          </li>
        ))}
      </ul>

      <h4>Evidence references</h4>
      <EvidenceRefList refs={[snapshot.subject?.evidence ?? null, ...snapshot.relations.map((relation) => relation.evidence)]} />

      <h4>Provenance</h4>
      <p className="small mono">
        {snapshot.provenance.method} {snapshot.provenance.method_version} · {snapshot.provenance.map_name} · map assets{' '}
        {snapshot.provenance.map_match_status} · scope {snapshot.provenance.information_scope} · gen {shortHash(snapshot.generation_id)}
      </p>
      <p className="small mono">profile {snapshot.provenance.profile_key}</p>
    </>
  );
}

/**
 * Exact-tick context of the subject, tied to the tick shown in the replay.
 *
 * While the replay plays the read is stepped (at most four reads per second) and
 * its own tick is displayed; as soon as the replay is paused the exact displayed
 * tick is requested. An unavailable subject leaves the panel in an explicit
 * unavailable state — no other participant is analysed in its place.
 */
export function ContextPanel({
  demoId,
  generationId,
  subjectId,
  subjectStatus,
  tick,
  playing,
  tickRateHz,
  playerById,
  onSeek,
  onSnapshot,
}: Props): ReactNode {
  const step = followStep(tickRateHz, FOLLOW_SAMPLES_PER_SECOND);
  const requestedTick = playing ? Math.floor(tick / step) * step : tick;
  const [crossPairs, setCrossPairs] = useState(false);
  const [navigation, setNavigation] = useState(false);

  const query = useAnalyticsQuery(
    (signal) =>
      phase2.context(
        demoId,
        { generation_id: generationId, subject_id: subjectId, tick: requestedTick, cross_pairs: crossPairs, navigation },
        signal,
      ),
    `${demoId}|${generationId}|subject:${subjectId ?? ''}|context:${requestedTick}|pairs:${crossPairs}|nav:${navigation}`,
    subjectId !== null,
  );

  const snapshot = query.data !== null && query.data.tick === requestedTick && query.data.subject_id === subjectId ? query.data : null;

  useEffect(() => {
    onSnapshot(snapshot);
  }, [snapshot, onSnapshot]);

  if (subjectId === null) {
    return (
      <section className="panel" aria-label="Context">
        <header className="panel-header">
          <h2>Context</h2>
          <span className="count mono">gen {shortHash(generationId)}</span>
        </header>
        <p className="notice notice-warning" role="status">
          The configured subject is {subjectStatus ?? 'unavailable'} in this demo, so no context is reconstructed. Select a participant in the replay to inspect one
          explicitly — nothing is substituted automatically.
        </p>
      </section>
    );
  }

  return (
    <section className="panel" aria-label="Context">
      <header className="panel-header">
        <h2>Context</h2>
        <button type="button" onClick={() => onSeek(requestedTick)} disabled={requestedTick === tick}>
          Seek replay to context tick
        </button>
        <span className="count mono" title={subjectId}>
          subject {subjectId} · gen {shortHash(generationId)}
        </span>
      </header>

      <p className="hint">
        {playing
          ? `Replay tick ${tick}; context is stepped to ${requestedTick} while playing (${step}-tick step) and is exact once paused.`
          : `Replay tick ${tick}; the exact displayed tick is requested.`}
      </p>
      <p className="hint">
        A sightline is only described as obstructed or unobstructed when the installed geometry assets and the recorded state agree; unknown, unsupported and
        client-version-mismatched sightlines stay unproven in the panel and on the radar. Static geometry status for this map is in the geometry panel below.
      </p>
      <label className="checkbox">
        <input type="checkbox" checked={crossPairs} onChange={(event) => setCrossPairs(event.target.checked)} />
        also resolve living teammate → opponent pair sightlines at this tick (~20 extra static segments per read)
      </label>
      <label className="checkbox">
        <input type="checkbox" checked={navigation} onChange={(event) => setNavigation(event.target.checked)} />
        include installed-nav graph estimates for the subject's relations (area-centre graph, not a route, path or travel time)
      </label>

      <ErrorNotice error={query.error} context="GET /demos/{demo_id}/context" />
      {query.loading && snapshot === null ? <p className="hint">Loading context…</p> : null}
      {snapshot !== null ? <SnapshotView snapshot={snapshot} playerById={playerById} tickRateHz={snapshot.tick_rate_hz} crossPairs={crossPairs} /> : null}
      {snapshot === null && !query.loading && query.error === null ? (
        <p className="hint">Waiting for the first context answer for tick {requestedTick}.</p>
      ) : null}

      {snapshot !== null && snapshot.limitations.length > 0 ? (
        <details open>
          <summary>{snapshot.limitations.length} context limitation(s)</summary>
          <ul className="list dense">
            {snapshot.limitations.map((item) => (
              <li key={item} className="small">
                {item}
              </li>
            ))}
          </ul>
        </details>
      ) : null}
    </section>
  );
}
