import { useCallback, useEffect, useRef, useState } from 'react';
import { ApiError, client, isAbortError, toApiError } from '../api/client';
import type { RadarDescriptor, ReplayChunk, ReplayEvent, ReplayPlayer, ReplaySample, RoundRecord } from '../api/types';

export type ReplayTarget = {
  demoId: string;
  generationId: string;
  round: RoundRecord;
  tickRateHz: number | null;
};

export type ReplayState = {
  samples: ReplaySample[];
  players: ReplayPlayer[];
  events: ReplayEvent[];
  radar: RadarDescriptor | null;
  warnings: string[];
  tickRateHz: number;
  strideTicks: number;
  startTick: number | null;
  endTick: number | null;
  loading: boolean;
  error: ApiError | null;
};

type LoadedReplay = Omit<ReplayState, 'loading' | 'error'>;

const EMPTY: ReplayState = {
  samples: [],
  players: [],
  events: [],
  radar: null,
  warnings: [],
  tickRateHz: 0,
  strideTicks: 1,
  startTick: null,
  endTick: null,
  loading: false,
  error: null,
};

// Each window request stays far below the server's 120,000 player-sample cap.
const MAX_SEGMENT_SAMPLES_PER_PLAYER = 6000;

class ReplayWindowError extends Error {
  readonly code = 'ROUND_WINDOW';
  readonly stage = 'replay';
  readonly retryable = false;

  constructor(message: string) {
    super(message);
    this.name = 'ReplayWindowError';
  }
}

class GenerationChangedError extends Error {
  readonly code = 'GENERATION_MISMATCH';
  readonly stage = 'replay';
  readonly retryable = true;

  constructor(expected: string, received: string) {
    super(`The server returned generation ${received} but generation ${expected} was pinned; reload the round`);
    this.name = 'GenerationChangedError';
  }
}

function roundWindow(round: RoundRecord): { begin: number; end: number } {
  const begin = round.freeze_end_tick ?? round.start_tick;
  const end = round.end_tick;
  if (begin === null || end === null || end < begin) {
    throw new ReplayWindowError(`Round ${round.round_id} has incomplete timing; its replay window is unavailable`);
  }
  return { begin, end };
}

async function loadRound(target: ReplayTarget, signal: AbortSignal): Promise<LoadedReplay> {
  const { begin, end } = roundWindow(target.round);
  const requestedStride = target.tickRateHz !== null && target.tickRateHz > 0 ? Math.max(1, Math.round(target.tickRateHz / 8)) : null;
  const baseSegment = Math.max(requestedStride ?? 8, (requestedStride ?? 8) * MAX_SEGMENT_SAMPLES_PER_PLAYER);
  let segmentTicks = baseSegment;
  const samples: ReplaySample[] = [];
  const events = new Map<number, ReplayEvent>();
  const warnings = new Set<string>();
  let players: ReplayPlayer[] = [];
  let radar: RadarDescriptor | null = null;
  let startTick: number | null = null;
  let endTick: number | null = null;
  let tickRateHz = target.tickRateHz ?? 0;
  let strideTicks = requestedStride ?? 1;
  let cursor = begin;

  while (cursor <= end) {
    const segmentEnd = Math.min(end, cursor + segmentTicks - 1);
    let chunk: ReplayChunk;
    try {
      chunk = await client.replay(
        {
          demo_id: target.demoId,
          generation_id: target.generationId,
          round_id: target.round.round_id,
          stride_ticks: requestedStride,
          start_tick: cursor,
          end_tick: segmentEnd,
        },
        signal,
      );
    } catch (exc) {
      if (exc instanceof ApiError && exc.code === 'WINDOW_TOO_LARGE' && segmentTicks > 1) {
        segmentTicks = Math.max(1, Math.floor(segmentTicks / 2));
        continue;
      }
      throw exc;
    }
    if (chunk.generation_id !== target.generationId) throw new GenerationChangedError(target.generationId, chunk.generation_id);
    for (const sample of chunk.samples) samples.push(sample);
    for (const event of chunk.events) events.set(event.row_ordinal, event);
    for (const warning of chunk.warnings) warnings.add(warning);
    if (radar === null) radar = chunk.radar;
    if (players.length === 0) players = chunk.players;
    tickRateHz = chunk.tick_rate_hz;
    strideTicks = chunk.stride_ticks;
    startTick = startTick === null ? chunk.start_tick : Math.min(startTick, chunk.start_tick);
    endTick = endTick === null ? chunk.end_tick : Math.max(endTick, chunk.end_tick);
    cursor = segmentEnd + 1;
  }

  samples.sort((a, b) => a.tick - b.tick || (a.player_id < b.player_id ? -1 : a.player_id > b.player_id ? 1 : 0));
  const orderedEvents = [...events.values()].sort((a, b) => a.tick - b.tick || a.row_ordinal - b.row_ordinal);
  return {
    samples,
    players,
    events: orderedEvents,
    radar,
    warnings: [...warnings],
    tickRateHz,
    strideTicks,
    startTick,
    endTick,
  };
}

/**
 * Loads one round as a generation-pinned, bounded window. A selection change
 * aborts the in-flight request and drops its response.
 */
export function useReplay(target: ReplayTarget | null): ReplayState & { reload: () => void } {
  const [state, setState] = useState<ReplayState>(EMPTY);
  const [nonce, setNonce] = useState(0);
  const targetRef = useRef(target);
  targetRef.current = target;
  const key = target === null ? null : `${target.demoId}|${target.generationId}|${target.round.round_id}`;

  useEffect(() => {
    const current = targetRef.current;
    if (current === null || key === null) {
      setState(EMPTY);
      return;
    }
    const controller = new AbortController();
    let active = true;
    setState({ ...EMPTY, loading: true });
    void (async () => {
      try {
        const loaded = await loadRound(current, controller.signal);
        if (!active || controller.signal.aborted) return;
        setState({ ...loaded, loading: false, error: null });
      } catch (exc) {
        if (!active || controller.signal.aborted || isAbortError(exc)) return;
        setState({ ...EMPTY, loading: false, error: toApiError(exc) });
      }
    })();
    return () => {
      active = false;
      controller.abort();
    };
  }, [key, nonce]);

  const reload = useCallback(() => setNonce((value) => value + 1), []);
  return { ...state, reload };
}
