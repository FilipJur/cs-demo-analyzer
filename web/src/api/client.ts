// Fetch client for the local /api/v1 surface. Same-origin only: no external
// hosts, no uploads, no full-match requests.
import {
  route,
  type Accepted,
  type DemoDetail,
  type DemoRecord,
  type DemosQuery,
  type ErrorResponse,
  type HealthResponse,
  type JobRecord,
  type ReplayChunk,
  type ReplayRequest,
  type RootRecord,
  type RootRequest,
  type RoundResponse,
  type RoundsQuery,
  type SourceRecord,
} from './types';

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly stage: string;
  readonly retryable: boolean;
  readonly jobId: string | null;

  constructor(status: number, body: Omit<ErrorResponse, 'retryable' | 'job_id'> & { retryable?: boolean; job_id?: string | null }) {
    super(body.message);
    this.name = 'ApiError';
    this.status = status;
    this.code = body.code;
    this.stage = body.stage;
    this.retryable = body.retryable ?? false;
    this.jobId = body.job_id ?? null;
  }
}

export function isAbortError(exc: unknown): boolean {
  return exc instanceof DOMException && exc.name === 'AbortError';
}

/** Normalise anything thrown by the client or a data loader into an ApiError. */
export function toApiError(exc: unknown): ApiError {
  if (exc instanceof ApiError) return exc;
  if (isAbortError(exc)) {
    return new ApiError(0, { code: 'ABORTED', message: 'Request cancelled', stage: 'client', retryable: true });
  }
  const candidate = exc as { code?: unknown; message?: unknown; stage?: unknown; retryable?: unknown } | null;
  if (candidate && typeof candidate.code === 'string') {
    return new ApiError(0, {
      code: candidate.code,
      message: typeof candidate.message === 'string' ? candidate.message : candidate.code,
      stage: typeof candidate.stage === 'string' ? candidate.stage : 'client',
      retryable: candidate.retryable === true,
    });
  }
  return new ApiError(0, {
    code: 'CLIENT',
    message: exc instanceof Error ? exc.message : 'Unexpected client error',
    stage: 'client',
    retryable: false,
  });
}

function queryString(params: Record<string, unknown> = {}): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') continue;
    search.set(key, String(value));
  }
  const text = search.toString();
  return text === '' ? '' : `?${text}`;
}

function parseErrorBody(text: string, status: number): ApiError {
  if (text !== '') {
    try {
      const parsed = JSON.parse(text) as Partial<ErrorResponse>;
      if (parsed && typeof parsed.code === 'string' && typeof parsed.message === 'string') {
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

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const body = init.body ?? null;
  if (init.method !== undefined && init.method !== 'GET' && init.method !== 'HEAD') {
    // The backend rejects mutations without an exact application/json type.
    headers.set('content-type', 'application/json');
  }
  let response: Response;
  try {
    response = await fetch(path, { ...init, body, headers, credentials: 'same-origin' });
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
  if (!response.ok) throw parseErrorBody(text, response.status);
  if (text.trim() === '') return undefined as T;
  return JSON.parse(text) as T;
}

export function assetUrl(assetId: string): string {
  return route('asset', { asset_id: assetId });
}

export const client = {
  health(signal?: AbortSignal): Promise<HealthResponse> {
    return request<HealthResponse>(route('health'), { signal });
  },
  roots(signal?: AbortSignal): Promise<RootRecord[]> {
    return request<RootRecord[]>(route('roots'), { signal });
  },
  async addRoot(body: RootRequest): Promise<RootRecord> {
    return request<RootRecord>(route('roots'), { method: 'POST', body: JSON.stringify(body) });
  },
  scan(): Promise<Accepted> {
    return request<Accepted>(route('scans'), { method: 'POST', body: '{}' });
  },
  importFile(path: string): Promise<Accepted> {
    return request<Accepted>(route('imports'), { method: 'POST', body: JSON.stringify({ path }) });
  },
  sources(signal?: AbortSignal): Promise<SourceRecord[]> {
    return request<SourceRecord[]>(route('sources'), { signal });
  },
  demos(query: DemosQuery = {}, signal?: AbortSignal): Promise<DemoRecord[]> {
    return request<DemoRecord[]>(`${route('demos')}${queryString({ limit: query.limit, offset: query.offset })}`, { signal });
  },
  demoDetail(demoId: string, signal?: AbortSignal): Promise<DemoDetail> {
    return request<DemoDetail>(route('demo', { demo_id: demoId }), { signal });
  },
  jobs(signal?: AbortSignal): Promise<JobRecord[]> {
    return request<JobRecord[]>(route('jobs'), { signal });
  },
  async reprocess(demoId: string): Promise<Accepted> {
    return request<Accepted>(route('reprocess', { demo_id: demoId }), { method: 'POST', body: '{}' });
  },
  async rounds(demoId: string, query: RoundsQuery = {}, signal?: AbortSignal): Promise<RoundResponse> {
    return request<RoundResponse>(`${route('rounds', { demo_id: demoId })}${queryString({ generation_id: query.generation_id })}`, { signal });
  },
  replay(params: ReplayRequest, signal?: AbortSignal): Promise<ReplayChunk> {
    const query = queryString({
      generation_id: params.generation_id,
      round_id: params.round_id,
      stride_ticks: params.stride_ticks,
      start_tick: params.start_tick,
      end_tick: params.end_tick,
    });
    return request<ReplayChunk>(`${route('replay', { demo_id: params.demo_id })}${query}`, { signal });
  },
};
