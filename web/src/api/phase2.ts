// Phase 2 client: subject configuration, participation, encounters, context and
// static geometry.
//
// Every request/response shape comes from the generated OpenAPI contract in
// `api/types.ts` (aliases over `components['schemas']` and `operations`), so a
// backend rename breaks compilation instead of the runtime. This module only
// builds bounded requests and normalises errors.
import { ApiError, isAbortError } from './client';
import {
  route,
  type ContextQuery,
  type ContextSnapshot,
  type EncounterContext,
  type EncounterContextQuery,
  type EncounterDetail,
  type EncounterList,
  type EncounterQuery,
  type EncountersQuery,
  GeometryCapabilities,
  type GeometryCapabilitiesQuery,
  type GeometryLocationQuery,
  type GeometrySegmentQuery,
  type Participation,
  type ParticipationPageQuery,
  type ParticipationQuery,
  type PointLocation,
  type SegmentResult,
  type SubjectConfig,
  type SubjectRequest,
} from './types';

/** Server-side ceilings, mirrored from the API's Query bounds. */
export const PHASE2_LIMITS = {
  participationPage: 500,
  encounterPage: 500,
  groupingSeconds: 60,
  coordinate: 32768,
} as const;

function queryString(params: Record<string, unknown> = {}): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') continue;
    search.set(key, String(value));
  }
  const text = search.toString();
  return text === '' ? '' : `?${text}`;
}

/** Same error surface as `api/client.ts`: abort passes through untouched. */
async function requestJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.method !== undefined && init.method !== 'GET' && init.method !== 'HEAD') {
    headers.set('content-type', 'application/json');
  }
  let response: Response;
  try {
    response = await fetch(path, { ...init, headers, credentials: 'same-origin' });
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
  if (!response.ok) {
    let code = `HTTP_${response.status}`;
    let message = text.trim() === '' ? `Request failed with status ${response.status}` : text.trim().slice(0, 400);
    let stage = 'http';
    let retryable = response.status >= 500;
    try {
      const parsed = JSON.parse(text) as { code?: unknown; message?: unknown; stage?: unknown; retryable?: unknown };
      if (typeof parsed.code === 'string') code = parsed.code;
      if (typeof parsed.message === 'string') message = parsed.message;
      if (typeof parsed.stage === 'string') stage = parsed.stage;
      if (parsed.retryable === true) retryable = true;
    } catch {
      // keep the generic error carrying the raw body
    }
    throw new ApiError(response.status, { code, message, stage, retryable });
  }
  if (text.trim() === '') return undefined as T;
  return JSON.parse(text) as T;
}

function demoPath(template: 'demoParticipation' | 'demoEncounters' | 'demoEncounter' | 'demoContext' | 'demoEncounterContext', demoId: string, extra: Record<string, string> = {}): string {
  return `${route(template, { demo_id: demoId, ...extra })}`;
}

export const phase2 = {
  /** The persisted primary subject; never changed by a per-demo selection. */
  subject(signal?: AbortSignal): Promise<SubjectConfig> {
    return requestJson<SubjectConfig>(route('analysisSubject'), { signal });
  },
  /** Persists the primary subject. This never re-ingests or reprocesses a demo. */
  setSubject(body: SubjectRequest): Promise<SubjectConfig> {
    return requestJson<SubjectConfig>(route('analysisSubject'), { method: 'PUT', body: JSON.stringify(body) });
  },
  participationList(query: ParticipationPageQuery = {}, signal?: AbortSignal): Promise<Participation[]> {
    return requestJson<Participation[]>(`${route('subjectParticipation')}${queryString(query)}`, { signal });
  },
  /** Participation of the primary subject, or of an explicit `player_id` override. */
  participation(demoId: string, query: ParticipationQuery = {}, signal?: AbortSignal): Promise<Participation> {
    return requestJson<Participation>(`${demoPath('demoParticipation', demoId)}${queryString(query)}`, { signal });
  },
  encounters(demoId: string, query: EncountersQuery = {}, signal?: AbortSignal): Promise<EncounterList> {
    return requestJson<EncounterList>(`${demoPath('demoEncounters', demoId)}${queryString(query)}`, { signal });
  },
  encounter(demoId: string, encounterId: string, query: EncounterQuery = {}, signal?: AbortSignal): Promise<EncounterDetail> {
    return requestJson<EncounterDetail>(
      `${demoPath('demoEncounter', demoId, { encounter_id: encounterId })}${queryString(query)}`,
      { signal },
    );
  },
  context(demoId: string, query: ContextQuery, signal?: AbortSignal): Promise<ContextSnapshot> {
    return requestJson<ContextSnapshot>(`${demoPath('demoContext', demoId)}${queryString(query)}`, { signal });
  },
  encounterContext(demoId: string, encounterId: string, query: EncounterContextQuery = {}, signal?: AbortSignal): Promise<EncounterContext> {
    return requestJson<EncounterContext>(
      `${demoPath('demoEncounterContext', demoId, { encounter_id: encounterId })}${queryString(query)}`,
      { signal },
    );
  },
  geometryCapabilities(query: GeometryCapabilitiesQuery, signal?: AbortSignal): Promise<GeometryCapabilities> {
    return requestJson<GeometryCapabilities>(`${route('geometryCapabilities')}${queryString(query)}`, { signal });
  },
  segment(query: GeometrySegmentQuery, signal?: AbortSignal): Promise<SegmentResult> {
    return requestJson<SegmentResult>(`${route('geometrySegment')}${queryString(query)}`, { signal });
  },
  /** Static facts about one world point; the point is used verbatim, never corrected. */
  locate(query: GeometryLocationQuery, signal?: AbortSignal): Promise<PointLocation> {
    return requestJson<PointLocation>(`${route('geometryLocation')}${queryString(query)}`, { signal });
  },
  /** Explicit preprocessing of one map; never triggered by scrubbing a replay. */
  prepareGeometry(mapName: string): Promise<GeometryCapabilities> {
    return requestJson<GeometryCapabilities>(route('geometryPrepare', { map_name: mapName }), { method: 'POST', body: '{}' });
  },
};
