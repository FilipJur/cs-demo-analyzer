import type { ReactNode } from 'react';
import type { TimelineEvent } from '../api/types';
import { formatTickTime } from '../lib/format';

type Props = {
  events: TimelineEvent[];
  /** Tick the inspector is pinned to; the first later event is highlighted. */
  tick: number;
  startTick: number | null;
  tickRateHz: number;
  onJump: (tick: number) => void;
  loading: boolean;
};

function eventActors(event: TimelineEvent): string | null {
  const actor1 = event.actor1 ?? null;
  const actor2 = event.actor2 ?? null;
  if (actor1 !== null && actor2 !== null) return `${actor1} → ${actor2}`;
  if (actor1 !== null) return actor1;
  if (actor2 !== null) return `→ ${actor2}`;
  return null;
}

/**
 * Nearby timeline events returned by the events endpoint. The list is purely
 * presentational: rows are verbatim API rows and a click asks the replay to
 * seek to that tick.
 */
export function EventList({ events, tick, startTick, tickRateHz, onJump, loading }: Props): ReactNode {
  const nextTick = events.find((event) => event.tick > tick)?.tick ?? null;

  return (
    <div className="events">
      <h3>Nearby events ({events.length})</h3>
      {loading && events.length === 0 ? <p className="hint">Loading events…</p> : null}
      {!loading && events.length === 0 ? <p className="list-empty">No kills, damages, shots or bomb events in this window.</p> : null}
      {events.length > 0 ? (
        <ul className="list">
          {events.map((event) => {
            const actors = eventActors(event);
            const detail = event.detail ?? null;
            const selected = event.tick === nextTick;
            return (
              <li key={`${event.dataset}:${event.row_ordinal}`} className={selected ? 'list-row list-row-selected' : 'list-row'}>
                <button
                  type="button"
                  className="grow demo-head"
                  onClick={() => onJump(event.tick)}
                  title={`Jump replay to tick ${event.tick}`}
                >
                  <span className="badge">{event.dataset}</span>
                  <span className="mono">tick {event.tick}</span>
                  <span className="small">{startTick === null ? 'round time n/a' : formatTickTime(event.tick, startTick, tickRateHz)}</span>
                  {actors === null ? <span className="badge badge-warn">actor not recorded</span> : <span className="grow truncate">{actors}</span>}
                  {detail === null ? <span className="badge badge-warn">no detail</span> : <span className="small truncate">{detail}</span>}
                </button>
              </li>
            );
          })}
        </ul>
      ) : null}
      <p className="hint">Click an event to move the replay to that tick. Events are read-only rows from the analytics endpoint.</p>
    </div>
  );
}
