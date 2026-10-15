import { useEffect, useState, type ReactNode } from 'react';
import type { ApiError } from '../api/client';
import { PHASE2_LIMITS, phase2 } from '../api/phase2';
import type {
  EncounterContext,
  EncounterDetail,
  EncounterEvent,
  EncounterList,
  EncounterSummary,
  RoundRecord,
} from '../api/types';
import { formatTickTime, shortHash, sideLabel } from '../lib/format';
import { evidenceLabel } from '../lib/phase2';
import { useAnalyticsQuery } from '../lib/useAnalyticsQuery';
import { usePolled } from '../lib/usePolling';
import { ErrorNotice, WarningList } from './Notices';

type Props = {
  demoId: string;
  generationId: string;
  /** Resolved recording identity of the subject; null when the primary is unavailable. */
  subjectId: string | null;
  subjectStatus: string | null;
  rounds: RoundRecord[];
  tickRateHz: number;
  /** Current replay tick, used as a label only. */
  tick: number;
  /** Seek the replay to an anchor of the encounter's round. */
  onSeekAnchor: (roundId: number, tick: number) => void;
  /** The selected detail, for the radar overlay; null clears the overlay. */
  onDetailChanged: (detail: EncounterDetail | null) => void;
};

const PAGE_SIZE = 50;

type Grouping = { gap: number; pre: number; post: number };

function groupingLabel(grouping: Grouping): string {
  return `gap ${grouping.gap}s · pre ${grouping.pre}s · post ${grouping.post}s`;
}

function SummaryRow({
  encounter,
  selected,
  onSelect,
  tickRateHz,
  roundStart,
}: {
  encounter: EncounterSummary;
  selected: boolean;
  onSelect: () => void;
  tickRateHz: number;
  roundStart: number | null;
}): ReactNode {
  return (
    <li className={`list-row${selected ? ' list-row-selected' : ''}`}>
      <button type="button" className="mono" onClick={onSelect} aria-pressed={selected}>
        {encounter.encounter_id}
      </button>
      <span className="small">round {encounter.round_id}</span>
      <span className="mono small">
        {encounter.start_tick}–{encounter.end_tick}
        {roundStart === null ? '' : ` (${formatTickTime(encounter.first_interaction_tick, roundStart, tickRateHz)} at first contact)`}
      </span>
      <span className="small">
        {encounter.event_count} events · {encounter.kill_count} kill / {encounter.death_count} death / {encounter.assist_count} assist
      </span>
      <span className="small">{encounter.participant_ids.length} participants</span>
      {encounter.subject_died ? <span className="badge badge-failed">subject died</span> : null}
      {encounter.limitations.length > 0 ? <span className="badge badge-warn">{encounter.limitations.length} limitation(s)</span> : null}
    </li>
  );
}

function eventRow(event: EncounterEvent): ReactNode {
  return (
    <li key={`${event.dataset}#${event.row_ordinal}`} className="list-row" title={evidenceLabel(event.evidence)}>
      <span className="badge">{event.dataset}</span>
      <span className="mono small">tick {event.tick}</span>
      <span className="grow truncate small">
        {event.actor_id ?? 'world'} → {event.target_id ?? 'unknown target'}
        {event.assister_id === null ? '' : ` (assist ${event.assister_id})`}
      </span>
      <span className="small">{event.weapon ?? 'weapon unknown'}</span>
      {event.damage_health === null ? null : <span className="mono small">dmg {event.damage_health}</span>}
      {event.headshot === true ? <span className="badge badge-warn">headshot</span> : null}
      {event.subject_involved ? <span className="badge">episode seed · subject {event.subject_role ?? 'involved'}</span> : null}
      {event.contextual && !event.subject_involved ? (
        <span className="badge badge-warn">
          {event.subject_role === null ? 'contextual row of another participant' : `adjacent episode row · subject ${event.subject_role}`}
        </span>
      ) : null}
      <span className="mono small">#{event.row_ordinal}</span>
    </li>
  );
}

function DetailView({
  detail,
  context,
  contextError,
  tickRateHz,
  onSeekAnchor,
}: {
  detail: EncounterDetail;
  context: EncounterContext | null;
  contextError: ApiError | null;
  tickRateHz: number;
  onSeekAnchor: (roundId: number, tick: number) => void;
}): ReactNode {
  const summary = detail.summary;
  const window = detail.source_window;
  const roundStart = window.round_start_tick;
  return (
    <>
      <h4>Encounter {summary.encounter_id}</h4>
      <p className="small">
        round {summary.round_id} · ticks {summary.start_tick}–{summary.end_tick} · first contact {summary.first_interaction_tick} (
        {formatTickTime(summary.first_interaction_tick, roundStart, tickRateHz)}) · last contact {summary.last_interaction_tick}
      </p>
      <p className="small mono">
        window {window.window_start_tick}–{window.window_end_tick} {window.truncated_start ? '(start clipped to round)' : ''}{' '}
        {window.truncated_end ? '(end clipped to round)' : ''} · {groupingLabel({ gap: detail.grouping.gap_seconds, pre: detail.grouping.pre_seconds, post: detail.grouping.post_seconds })}
      </p>
      <p className="small">
        {detail.subject_event_count} seed row(s) of this episode · {detail.contextual_event_count} other recorded row(s) in the window · trajectory{' '}
        {detail.subject_trajectory.length} sample(s) every {detail.trajectory_stride} ticks
        {detail.trajectory_missing_ranges.length === 0 ? '' : ` · ${detail.trajectory_missing_ranges.length} gap(s) in the trajectory`}
      </p>

      <h4>Anchors</h4>
      <ul className="list dense">
        {summary.anchors.map((anchor) => (
          <li key={anchor.anchor_id} className="list-row">
            <span className="badge">{anchor.kind}</span>
            <span className={`badge ${anchor.status === 'unavailable' ? 'badge-warn' : ''}`}>{anchor.status}</span>
            <span className="badge">{anchor.evidence_kind}</span>
            <span className="grow truncate small">
              {anchor.anchor_id}
              {anchor.detail === null ? '' : ` — ${anchor.detail}`}
              {anchor.resolution === null ? '' : ` (closed by ${anchor.resolution})`}
            </span>
            <span className="mono small">{anchor.dataset === null ? 'window marker' : `${anchor.dataset}#${anchor.row_ordinal ?? '?'}`}</span>
            {anchor.tick === null ? (
              <span className="badge badge-warn">tick unavailable</span>
            ) : (
              <>
                <span className="mono small">tick {anchor.tick}</span>
                <button type="button" onClick={() => onSeekAnchor(summary.round_id, anchor.tick ?? summary.start_tick)}>
                  Seek round {summary.round_id} tick {anchor.tick}
                </button>
              </>
            )}
            {anchor.status === 'observed' && anchor.evidence.length === 0 ? <span className="badge badge-warn">no evidence row</span> : null}
          </li>
        ))}
      </ul>

      <h4>Participants ({detail.participants.length})</h4>
      <ul className="list dense">
        {detail.participants.map((participant) => (
          <li key={participant.player_id} className="list-row">
            <span className="badge">{participant.relation}</span>
            <span className="grow truncate mono small">{participant.player_id}</span>
            <span className="small">{participant.side === null ? 'side unknown' : sideLabel(participant.side)}</span>
            <span className="small">
              ticks {participant.first_seen_tick}–{participant.last_seen_tick} · {participant.event_count} events
            </span>
            <span className="small">{participant.roles.join(', ') || 'no role recorded'}</span>
            {participant.direct ? <span className="badge">direct contact</span> : <span className="badge badge-warn">contextual only</span>}
          </li>
        ))}
      </ul>

      <h4>Events ({detail.events.length})</h4>
      <ul className="list dense">{detail.events.map((event) => eventRow(event))}</ul>

      <h4>Exposure</h4>
      <ErrorNotice error={contextError} context="GET /demos/{demo_id}/encounters/{encounter_id}/context" />
      {context !== null ? (
        <>
          <ul className="list dense">
            <li className="list-row">
              <span className={`badge ${context.exposure.status === 'qualified' ? '' : 'badge-warn'}`}>{context.exposure.status}</span>
              <span className="grow small">
                {context.exposure.earliest_exposure_tick === null
                  ? 'no qualified sampled static-clear segment'
                  : `earliest sampled static-clear segment at tick ${context.exposure.earliest_exposure_tick} (${context.exposure.earliest_exposure_player_id ?? 'opponent unknown'})`}
              </span>
              {context.exposure.earliest_exposure_tick === null ? null : (
                <button
                  type="button"
                  onClick={() => onSeekAnchor(context.round_id, context.exposure.earliest_exposure_tick ?? context.start_tick)}
                  title="the earliest sampled tick whose static segment is clear between living, stance-known endpoints — not confirmed visibility"
                >
                  Seek sample
                </button>
              )}
            </li>
            <li className="list-row">
              <span className="badge">scan</span>
              <span className="grow mono small">
                ticks {context.exposure.sampling.start_tick}–{context.exposure.sampling.end_tick} every {context.exposure.sampling.stride_ticks} ·{' '}
                {context.exposure.sampling.samples} sample(s) · subject alive in {context.exposure.sampling.subject_alive_samples}
              </span>
              <details>
                <summary>sampled grid ({context.exposure.sampling.ticks.length})</summary>
                <p className="small mono">{context.exposure.sampling.ticks.join(', ')}</p>
              </details>
            </li>
          </ul>
          <p className="hint">
            A clear segment is a static reading of the installed map build along one sampled ray between living endpoints; it is not confirmed visibility, and it
            says nothing about a player's knowledge, reactions or trades.
          </p>
          <WarningList warnings={context.exposure.limitations} />
          <ul className="list dense">
            {context.exposure.opponents.map((opponent) => (
              <li key={opponent.player_id} className="list-row">
                <span className="badge">{opponent.relation}</span>
                <span className="grow truncate mono small">{opponent.player_id}</span>
                <span className="small">
                  clear {opponent.clear_ticks} · blocked {opponent.blocked_ticks} · unknown {opponent.unknown_ticks} · mismatched{' '}
                  {opponent.mismatched_ticks} · missing {opponent.missing_ticks}
                </span>
                <span className="small">{opponent.earliest_clear_tick === null ? 'no clear tick' : `first clear ${opponent.earliest_clear_tick}`}</span>
              </li>
            ))}
          </ul>
          {context.exposure.unknown_dynamics.length > 0 ? (
            <details>
              <summary>{context.exposure.unknown_dynamics.length} unknown dynamic(s) limiting exposure</summary>
              <ul className="list dense">
                {context.exposure.unknown_dynamics.map((item) => (
                  <li key={item} className="small">
                    {item}
                  </li>
                ))}
              </ul>
            </details>
          ) : null}
          {context.exposure.mismatches.length > 0 ? (
            <p className="notice notice-warning" role="status">
              {context.exposure.mismatches.length} static sightline answer(s) were discarded because the installed map assets do not match this recording.
            </p>
          ) : null}

          <h4>Anchor snapshots ({context.snapshots.length})</h4>
          <ul className="list dense">
            {context.snapshots.map((anchor) => (
              <li key={`${anchor.name}-${anchor.requested_tick ?? 'none'}-${anchor.kind}`} className="list-row">
                <span className="badge">{anchor.kind}</span>
                <span className="grow truncate small">
                  {anchor.name}
                  {anchor.anchor_kind === null ? '' : ` (${anchor.anchor_kind})`} — {anchor.reason}
                </span>
                <span className="mono small">{anchor.requested_tick === null ? 'no tick' : `tick ${anchor.requested_tick}`}</span>
                <span className="small">
                  exact {String(anchor.snapshot.exact)} · subject {anchor.snapshot.subject_alive ? 'alive' : 'not alive'} ·{' '}
                  {anchor.snapshot.relations.length} active relation(s)
                </span>
                {anchor.requested_tick === null ? null : (
                  <button type="button" onClick={() => onSeekAnchor(context.round_id, anchor.requested_tick ?? context.start_tick)}>
                    Seek
                  </button>
                )}
              </li>
            ))}
          </ul>

          <h4>Recorded tracks over the window</h4>
          <ul className="list dense">
            <li className="list-row">
              <span className="badge">subject</span>
              <span className="grow mono small">
                {context.subject_track === null
                  ? 'no verbatim subject track'
                  : `${context.subject_track.samples.length} sample(s) every ${context.subject_track.stride_ticks} ticks · ${context.subject_track.missing_samples} missing`}
              </span>
              <span className="small">
                ticks {context.subject_track?.from_tick ?? 'n/a'}–{context.subject_track?.to_tick ?? 'n/a'}
              </span>
            </li>
            <li className="list-row">
              <span className="badge">facing</span>
              <span className="grow small">
                {context.subject_facing_delta === null
                  ? 'no trustworthy recorded yaw change'
                  : `yaw ${context.subject_facing_delta.yaw_from.toFixed(1)}° → ${context.subject_facing_delta.yaw_to.toFixed(1)}° (Δ ${context.subject_facing_delta.delta_degrees.toFixed(1)}°) over ticks ${context.subject_facing_delta.from_tick}–${context.subject_facing_delta.to_tick}`}
              </span>
            </li>
            {context.participant_tracks.map((track) => (
              <li key={track.player_id} className="list-row">
                <span className="badge">{track.relation}</span>
                <span className="grow truncate mono small">{track.player_id}</span>
                <span className="small">
                  {track.samples.length} sample(s) every {track.stride_ticks} ticks · {track.missing_samples} missing
                </span>
                <span className="small">ticks {track.from_tick ?? 'n/a'}–{track.to_tick ?? 'n/a'}</span>
              </li>
            ))}
            {context.participant_tracks.length === 0 ? <li className="list-empty">No participant track is recorded for this window.</li> : null}
          </ul>

          <h4>Recorded lifecycle in the window ({context.lifecycle.length})</h4>
          <ul className="list dense">
            {context.lifecycle.map((fact) => (
              <li key={`${fact.kind}-${fact.tick}-${fact.player_id ?? 'unattributed'}`} className="list-row" title={fact.limitations.join('\n')}>
                <span className="badge">{fact.kind}</span>
                <span className="mono small">tick {fact.tick}</span>
                <span className="grow truncate mono small">{fact.player_id ?? 'unattributed row'}</span>
                <span className="small">{fact.team ?? 'team unknown'}</span>
                {fact.reason_code === null || fact.reason_code === undefined ? null : <span className="small">reason {fact.reason_code}</span>}
                {fact.is_bot === null || fact.is_bot === undefined ? null : <span className="small">{fact.is_bot ? 'bot' : 'human'}</span>}
                {fact.ever_fully_connected === false ? <span className="badge badge-warn">never fully connected</span> : null}
                <button type="button" onClick={() => onSeekAnchor(context.round_id, fact.tick)}>
                  Seek
                </button>
              </li>
            ))}
            {context.lifecycle.length === 0 ? (
              <li className="list-empty">
                No recorded lifecycle row for the subject in this window ({context.lifecycle_unattributed_rows} unattributed row(s) counted, never assigned).
              </li>
            ) : null}
          </ul>

          <h4>Utility timeline</h4>
          <ul className="list dense">
            {context.utility.map((fact, index) => (
              <li key={`${fact.kind}-${fact.start_tick}-${index}`} className="list-row" title={fact.limitations.join('\n')}>
                <span className="badge">{fact.kind}</span>
                <span className="badge">{fact.evidence_kind}</span>
                <span className="mono small">{fact.owner_id ?? 'owner unresolved'}</span>
                <span className="small">
                  ticks {fact.start_tick}
                  {fact.end_tick === null ? ' → unresolved' : ` → ${fact.end_tick}`}
                </span>
                {fact.site === null ? null : <span className="small">site {fact.site}</span>}
                <span className="mono small" title={fact.evidence === null ? 'no source row' : evidenceLabel(fact.evidence)}>
                  {fact.evidence === null ? 'no source row' : `${fact.evidence.dataset}#${fact.evidence.row_ordinal}`}
                </span>
                <button type="button" onClick={() => onSeekAnchor(context.round_id, fact.start_tick)}>
                  Seek
                </button>
              </li>
            ))}
            {context.utility.length === 0 ? <li className="list-empty">No recorded utility fact in this encounter window.</li> : null}
          </ul>
        </>
      ) : (
        <p className="hint">Loading encounter context…</p>
      )}

      <p className="small mono">
        provenance {detail.provenance.method} {detail.provenance.method_version} · {detail.provenance.map_name} · assets {detail.provenance.map_match_status} · gen{' '}
        {shortHash(detail.provenance.generation_id)}
      </p>
      {detail.limitations.length > 0 ? (
        <details>
          <summary>{detail.limitations.length} encounter limitation(s)</summary>
          <ul className="list dense">
            {detail.limitations.map((item) => (
              <li key={item} className="small">
                {item}
              </li>
            ))}
          </ul>
        </details>
      ) : null}
    </>
  );
}

/**
 * Encounters of the pinned generation involving the subject.
 *
 * The list, the detail and the encounter context are all read with the same
 * grouping options, so the `encounter_id` a summary reports always resolves in
 * the detail read. Anchors are selectable and seek the replay by round + tick.
 */
export function EncountersPanel({
  demoId,
  generationId,
  subjectId,
  subjectStatus,
  rounds,
  tickRateHz,
  tick,
  onSeekAnchor,
  onDetailChanged,
}: Props): ReactNode {
  const [roundFilter, setRoundFilter] = useState<number | null>(null);
  const [grouping, setGrouping] = useState<Grouping>({ gap: 3, pre: 3, post: 1 });
  const [pending, setPending] = useState<Grouping>({ gap: 3, pre: 3, post: 1 });
  const [page, setPage] = useState(0);
  const [navigation, setNavigation] = useState(false);
  const [encounterId, setEncounterId] = useState<string | null>(null);

  const list = usePolled<EncounterList | null>(
    (signal) =>
      subjectId === null
        ? Promise.resolve(null)
        : phase2.encounters(
            demoId,
            {
              generation_id: generationId,
              subject_id: subjectId,
              round_id: roundFilter,
              limit: PAGE_SIZE,
              offset: page * PAGE_SIZE,
              gap_seconds: grouping.gap,
              pre_seconds: grouping.pre,
              post_seconds: grouping.post,
            },
            signal,
          ),
    30000,
    { key: `${demoId}|${generationId}|${subjectId ?? ''}|${roundFilter ?? 'all'}|${grouping.gap}|${grouping.pre}|${grouping.post}|${page}` },
  );

  const detail = useAnalyticsQuery(
    (signal) =>
      encounterId === null || subjectId === null
        ? Promise.resolve(null)
        : phase2.encounter(
            demoId,
            encounterId,
            { generation_id: generationId, subject_id: subjectId, gap_seconds: grouping.gap, pre_seconds: grouping.pre, post_seconds: grouping.post },
            signal,
          ),
    `${demoId}|${generationId}|${subjectId ?? ''}|${encounterId ?? ''}|${grouping.gap}|${grouping.pre}|${grouping.post}`,
    encounterId !== null && subjectId !== null,
  );

  const encounterContext = useAnalyticsQuery(
    (signal) =>
      encounterId === null || subjectId === null
        ? Promise.resolve(null)
        : phase2.encounterContext(
            demoId,
            encounterId,
            {
              generation_id: generationId,
              subject_id: subjectId,
              gap_seconds: grouping.gap,
              pre_seconds: grouping.pre,
              post_seconds: grouping.post,
              navigation,
            },
            signal,
          ),
    `${demoId}|${generationId}|${subjectId ?? ''}|${encounterId ?? ''}|context|${grouping.gap}|${grouping.pre}|${grouping.post}|nav:${navigation}`,
    encounterId !== null && subjectId !== null,
  );

  const selected = detail.data ?? null;
  useEffect(() => {
    onDetailChanged(selected);
  }, [selected, onDetailChanged]);

  useEffect(() => {
    setEncounterId(null);
    setPage(0);
  }, [demoId, generationId, subjectId, roundFilter]);

  if (subjectId === null) {
    return (
      <section className="panel" aria-label="Encounters">
        <header className="panel-header">
          <h2>Encounters</h2>
          <span className="count mono">gen {shortHash(generationId)}</span>
        </header>
        <p className="notice notice-warning" role="status">
          The configured subject is {subjectStatus ?? 'unavailable'} in this demo, so no encounter is grouped. Select a participant in the replay to inspect one
          explicitly — the configured subject is never replaced automatically.
        </p>
      </section>
    );
  }

  const entries = list.data?.encounters ?? [];
  const total = list.data?.total ?? 0;
  const groupingDirty = grouping.gap !== pending.gap || grouping.pre !== pending.pre || grouping.post !== pending.post;

  return (
    <section className="panel" aria-label="Encounters">
      <header className="panel-header">
        <h2>Encounters</h2>
        <span className="count mono" title={subjectId}>
          subject {subjectId} · gen {shortHash(generationId)} · replay tick {tick}
        </span>
      </header>

      <p className="hint">
        An encounter groups the subject's interactions that are closer than the gap window, with the pre/post window around them. Grouping is heuristic and is
        reported as such; changing it changes the encounter ids.
      </p>

      <div className="replay-select">
        <label htmlFor="encounter-round">Round</label>
        <select
          id="encounter-round"
          value={roundFilter ?? ''}
          onChange={(event) => setRoundFilter(event.target.value === '' ? null : Number(event.target.value))}
        >
          <option value="">all rounds</option>
          {rounds.map((round) => (
            <option key={round.round_id} value={round.round_id}>
              round {round.round_id}
            </option>
          ))}
        </select>

        <label htmlFor="encounter-gap">gap s</label>
        <input
          id="encounter-gap"
          type="text"
          inputMode="decimal"
          className="mono"
          value={pending.gap}
          onChange={(event) => setPending((current) => ({ ...current, gap: Number(event.target.value) || 0 }))}
        />
        <label htmlFor="encounter-pre">pre s</label>
        <input
          id="encounter-pre"
          type="text"
          inputMode="decimal"
          className="mono"
          value={pending.pre}
          onChange={(event) => setPending((current) => ({ ...current, pre: Number(event.target.value) || 0 }))}
        />
        <label htmlFor="encounter-post">post s</label>
        <input
          id="encounter-post"
          type="text"
          inputMode="decimal"
          className="mono"
          value={pending.post}
          onChange={(event) => setPending((current) => ({ ...current, post: Number(event.target.value) || 0 }))}
        />
        <button
          type="button"
          onClick={() => setGrouping(pending)}
          disabled={!groupingDirty}
          title={`each window is bounded to ${PHASE2_LIMITS.groupingSeconds}s by the API`}
        >
          Apply grouping
        </button>
      </div>

      <p className="small">
        {groupingLabel(grouping)} · {total} encounter(s) {roundFilter === null ? 'in all rounds' : `in round ${roundFilter}`} · page {page + 1}
      </p>

      <ErrorNotice error={list.error} context="GET /demos/{demo_id}/encounters" />
      <ul className="list">
        {entries.map((encounter) => (
          <SummaryRow
            key={encounter.encounter_id}
            encounter={encounter}
            selected={encounter.encounter_id === encounterId}
            onSelect={() => setEncounterId(encounter.encounter_id === encounterId ? null : encounter.encounter_id)}
            tickRateHz={tickRateHz}
            roundStart={rounds.find((round) => round.round_id === encounter.round_id)?.freeze_end_tick ?? null}
          />
        ))}
        {entries.length === 0 ? (
          <li className="list-empty">
            {list.loading ? 'Loading encounters…' : 'No encounter is grouped for this subject, round filter and grouping window.'}
          </li>
        ) : null}
      </ul>

      <div className="form-actions">
        <button type="button" onClick={() => setPage((value) => Math.max(0, value - 1))} disabled={page === 0}>
          Previous page
        </button>
        <button type="button" onClick={() => setPage((value) => value + 1)} disabled={(page + 1) * PAGE_SIZE >= total}>
          Next page
        </button>
      </div>

      <ErrorNotice error={detail.error} context="GET /demos/{demo_id}/encounters/{encounter_id}" />
      {detail.loading && selected === null ? <p className="hint">Loading encounter detail…</p> : null}
      {selected !== null ? (
        <>
          <label className="checkbox">
            <input type="checkbox" checked={navigation} onChange={(event) => setNavigation(event.target.checked)} />
            include installed-nav graph estimates for this encounter's context (area-centre graph, not a route, path or travel time)
          </label>
          <DetailView
            detail={selected}
            context={encounterContext.data}
            contextError={encounterContext.error}
            tickRateHz={tickRateHz}
            onSeekAnchor={onSeekAnchor}
          />
        </>
      ) : null}
    </section>
  );
}
