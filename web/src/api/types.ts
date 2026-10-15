// Types resolved from the generated OpenAPI client. `schema.d.ts` is generated
// from `contracts/openapi.json`; nothing here is hand-maintained except the
// route literals, which are checked against the generated `paths` table.
import type { components, operations, paths } from './schema';

type Schemas = components['schemas'];

export type ErrorResponse = Schemas['ErrorResponse'];
export type HealthResponse = Schemas['HealthResponse'];
export type RootRecord = Schemas['RootRecord'];
export type RootRequest = Schemas['RootRequest'];
export type Accepted = Schemas['Accepted'];
export type SourceRecord = Schemas['SourceRecord'];
export type DemoRecord = Schemas['DemoRecord'];
export type DemoDetail = Schemas['DemoDetail'];
export type JobRecord = Schemas['JobRecord'];
export type RoundRecord = Schemas['RoundRecord'];
export type RoundResponse = Schemas['RoundResponse'];
export type ReplayChunk = Schemas['ReplayChunk'];
export type ReplayPlayer = Schemas['ReplayPlayer'];
export type ReplaySample = Schemas['ReplaySample'];
export type ReplayEvent = Schemas['ReplayEvent'];
export type RadarDescriptor = Schemas['RadarDescriptor'];
export type AnalyticState = Schemas['AnalyticState'];
export type StateResponse = Schemas['StateResponse'];
export type TrajectoryResponse = Schemas['TrajectoryResponse'];
export type TimelineEvent = Schemas['TimelineEvent'];
export type EventsResponse = Schemas['EventsResponse'];
export type EventWindowResponse = Schemas['EventWindowResponse'];
export type CoverageResponse = Schemas['CoverageResponse'];
export type DistanceResponse = Schemas['DistanceResponse'];
/** Provenance reference for future detectors; mirrors the backend EvidenceRef model. */
export type EvidenceRef = {
  demo_id: string;
  generation_id: string;
  profile_key: string;
  dataset: string;
  row_ordinal: number;
  tick: number;
  round_id: number | null;
  player_ids: string[];
};

// Every literal below must exist in the generated `paths` table, so a route
// rename in the backend breaks this file at compile time instead of at runtime.
export const ROUTES = {
  health: '/api/v1/health',
  roots: '/api/v1/roots',
  scans: '/api/v1/scans',
  imports: '/api/v1/imports',
  sources: '/api/v1/sources',
  demos: '/api/v1/demos',
  demo: '/api/v1/demos/{demo_id}',
  jobs: '/api/v1/jobs',
  job: '/api/v1/jobs/{job_id}',
  reprocess: '/api/v1/demos/{demo_id}/reprocess',
  rounds: '/api/v1/demos/{demo_id}/rounds',
  replay: '/api/v1/demos/{demo_id}/replay',
  asset: '/api/v1/assets/{asset_id}',
} as const satisfies Record<string, keyof paths>;

export function route(template: keyof typeof ROUTES, values: Record<string, string> = {}): string {
  let path: string = ROUTES[template];
  for (const [name, value] of Object.entries(values)) {
    path = path.split(`{${name}}`).join(encodeURIComponent(value));
  }
  return path;
}

// Query/parameter contracts taken from the generated operations.
export type ReplayPath = NonNullable<operations['replay_api_v1_demos__demo_id__replay_get']['parameters']['path']>;
export type ReplayQuery = NonNullable<operations['replay_api_v1_demos__demo_id__replay_get']['parameters']['query']>;
export type ReplayRequest = ReplayPath & ReplayQuery;
export type DemosQuery = NonNullable<operations['demos_api_v1_demos_get']['parameters']['query']>;
export type RoundsQuery = NonNullable<operations['rounds_api_v1_demos__demo_id__rounds_get']['parameters']['query']>;
