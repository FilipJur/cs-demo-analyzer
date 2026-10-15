// Read-only analytics queries used by the player inspector.
//
// The browser never computes analytics: these wrappers forward the current
// inspector selection to the typed analytics routes and return the response
// verbatim. Response types come from the generated OpenAPI schema, so a
// backend rename breaks compilation instead of the runtime.
import { ApiError, isAbortError } from '../api/client';
import type { EventsResponse, StateResponse, TrajectoryResponse } from '../api/types';

/** Datasets merged by the events endpoint; the server default is the same set. */
export const ANALYTICS_DATASETS = ['kills', 'damages', 'shots', 'bomb'] as const;

const ANALYTICS_ROUTES = {
  state: '/api/v1/demos/{demo_id}/analytics/state',
  trajectory: '/api/v1/demos/{demo_id}/analytics/trajectory',
  events: '/api/v1/demos/{demo_id}/analytics/events',
} as const;

export type StateQuery = {
  generationId?: string | null;
  tick: number;
  playerId?: string | null;
  /** Nearest tick tolerance; 0 (the server default) requires the exact tick. */
  maxGap?: number | null;
};

export type TrajectoryQuery = {
  generationId?: string | null;
  playerId: string;
  start: number;
  end: number;
  stride?: number | null;
};

export type EventsQuery = {
  generationId?: string | null;
  datasets?: readonly string[] | null;
  start: number;
  end: number;
  limit?: number | null;
};

function analyticsPath(template: keyof typeof ANALYTICS_ROUTES, demoId: string): string {
  return ANALYTICS_ROUTES[template].replace('{demo_id}', encodeURIComponent(demoId));
}

function queryString(params: Record<string, string | number | null | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') continue;
    search.set(key, String(value));
  }
  const text = search.toString();
  return text === '' ? '' : `?${text}`;
}

function parseBody(text: string, status: number): ApiError {
  if (text !== '') {
    try {
      const parsed = JSON.parse(text) as { code?: unknown; message?: unknown; stage?: unknown; retryable?: unknown; job_id?: unknown };
      if (parsed !== null && typeof parsed.code === 'string' && typeof parsed.message === 'string') {
        return new ApiError(status, {
          code: parsed.code,
          message: parsed.message,
          stage: typeof parsed.stage === 'string' ? parsed.stage : 'http',
          retryable: parsed.retryable === true,
          job_id: typeof parsed.job_id === 'string' ? parsed.job_id : null,
        });
      }
    } catch {
      // fall through to a generic error carrying the raw body
    }
  }
  const message = text.trim() === '' ? `Request failed with status ${status}` : text.trim().slice(0, 400);
  return new ApiError(status, { code: `HTTP_${status}`, message, stage: 'http', retryable: status >= 500 });
}

/** Same error surface as `api/client.ts` `request()`: abort passes through untouched. */
async function getJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  let response: Response;
  try {
    response = await fetch(path, { signal, credentials: 'same-origin' });
  } catch (exc) {
    if (isAbortError(exc)) throw exc;
    throw new ApiError(0, {
      code: 'NETWORK',
      message: exc instanceof Error ? exc.message : 'Network request failed',
      stage: 'client',
      retryable: true,
    });
  }
  const text = await response.text();
  if (!response.ok) throw parseBody(text, response.status);
  if (text.trim() === '') {
    throw new ApiError(response.status, { code: 'HTTP_EMPTY_BODY', message: 'The analytics endpoint returned an empty body', stage: 'http', retryable: false });
  }
  return JSON.parse(text) as T;
}

export function getState(demoId: string, query: StateQuery, signal?: AbortSignal): Promise<StateResponse> {
  const search = queryString({
    generation_id: query.generationId,
    tick: query.tick,
    player_id: query.playerId,
    max_gap: query.maxGap,
  });
  return getJson<StateResponse>(`${analyticsPath('state', demoId)}${search}`, signal);
}

export function getTrajectory(demoId: string, query: TrajectoryQuery, signal?: AbortSignal): Promise<TrajectoryResponse> {
  const search = queryString({
    generation_id: query.generationId,
    player_id: query.playerId,
    start: query.start,
    end: query.end,
    stride: query.stride,
  });
  return getJson<TrajectoryResponse>(`${analyticsPath('trajectory', demoId)}${search}`, signal);
}

export function getEvents(demoId: string, query: EventsQuery, signal?: AbortSignal): Promise<EventsResponse> {
  const search = queryString({
    generation_id: query.generationId,
    datasets: query.datasets !== undefined && query.datasets !== null && query.datasets.length > 0 ? query.datasets.join(',') : undefined,
    start: query.start,
    end: query.end,
    limit: query.limit,
  });
  return getJson<EventsResponse>(`${analyticsPath('events', demoId)}${search}`, signal);
}
