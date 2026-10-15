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

// -- Phase 2 reconstruction -------------------------------------------------
export type SubjectConfig = Schemas['SubjectConfig'];
export type SubjectRequest = Schemas['SubjectRequest'];
export type Participation = Schemas['Participation'];
export type ParticipationMeasurements = Schemas['ParticipationMeasurements'];
export type EncounterList = Schemas['EncounterList'];
export type EncounterSummary = Schemas['EncounterSummary'];
export type EncounterDetail = Schemas['EncounterDetail'];
export type EncounterAnchor = Schemas['EncounterAnchor'];
export type EncounterEvent = Schemas['EncounterEvent'];
export type EncounterParticipant = Schemas['EncounterParticipant'];
export type EncounterGrouping = Schemas['EncounterGrouping'];
export type EncounterSourceWindow = Schemas['EncounterSourceWindow'];
export type ContextSnapshot = Schemas['ContextSnapshot'];
export type ContextRelation = Schemas['ContextRelation'];
export type ContextStateRef = Schemas['ContextStateRef'];
export type ContextCapabilities = Schemas['ContextCapabilities'];
export type ContextCounts = Schemas['ContextCounts'];
export type ContextAnchorSnapshot = Schemas['ContextAnchorSnapshot'];
export type ContextUtilityFact = Schemas['ContextUtilityFact'];
export type ContextPositionChange = Schemas['ContextPositionChange'];
export type CrossSightline = Schemas['CrossSightline'];
export type AngularSpread = Schemas['AngularSpread'];
export type OpponentDirection = Schemas['OpponentDirection'];
export type LifecycleFact = Schemas['LifecycleFact'];
export type ParticipantTrack = Schemas['ParticipantTrack'];
export type FacingDelta = Schemas['FacingDelta'];
export type TrajectorySample = Schemas['TrajectorySample'];
export type EncounterContext = Schemas['EncounterContext'];
export type EncounterExposure = Schemas['EncounterExposure'];
export type ExposureSampling = Schemas['ExposureSampling'];
export type OpponentExposure = Schemas['OpponentExposure'];
export type ViewOrigin = Schemas['ViewOrigin'];
export type EvidenceCapability = Schemas['EvidenceCapability'];
export type ReconstructionProvenance = Schemas['ReconstructionProvenance'];
export type GeometryCapabilities = Schemas['GeometryCapabilities'];
export type GeometryAsset = Schemas['GeometryAsset'];
export type GeometryComponent = Schemas['GeometryComponent'];
export type GeometrySource = Schemas['GeometrySource'];
export type SegmentResult = Schemas['SegmentResult'];
export type NavigationResult = Schemas['NavigationResult'];
export type PointLocation = Schemas['PointLocation'];

// Vocabularies are read off the generated models, never restated here.
export type ParticipationStatus = Participation['status'];
export type MatchStatus = GeometryCapabilities['match_status'];
export type ComponentStatus = GeometryComponent['status'];
export type SegmentStatus = SegmentResult['status'];
export type NavigationStatus = NavigationResult['status'];
export type CapabilityStatus = EvidenceCapability['status'];
export type RelationKind = ContextRelation['relation'];
export type ViewOriginMode = ViewOrigin['mode'];
export type ExposureStatus = EncounterExposure['status'];
export type EvidenceKind = ContextAnchorSnapshot['kind'];
export type EncounterAnchorKind = EncounterAnchor['kind'];
export type AnchorStatus = EncounterAnchor['status'];
export type ResolutionKind = NonNullable<EncounterAnchor['resolution']>;
export type EventDataset = EncounterEvent['dataset'];
export type SubjectRole = NonNullable<EncounterEvent['subject_role']>;
export type Vec3 = SegmentResult['start'];
/** Provenance reference carried by encounters, context and event rows. */
export type EvidenceRef = Schemas['EvidenceRef'];

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
  analysisSubject: '/api/v1/analysis-subject',
  subjectParticipation: '/api/v1/subject-participation',
  demoParticipation: '/api/v1/demos/{demo_id}/participation',
  demoEncounters: '/api/v1/demos/{demo_id}/encounters',
  demoEncounter: '/api/v1/demos/{demo_id}/encounters/{encounter_id}',
  demoContext: '/api/v1/demos/{demo_id}/context',
  demoEncounterContext: '/api/v1/demos/{demo_id}/encounters/{encounter_id}/context',
  geometryCapabilities: '/api/v1/geometry/capabilities',
  geometrySegment: '/api/v1/geometry/segment',
  geometryNavigation: '/api/v1/geometry/navigation',
  geometryLocation: '/api/v1/geometry/location',
  geometryPrepare: '/api/v1/geometry/{map_name}/prepare',
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
export type ParticipationPageQuery = NonNullable<operations['subject_participation_api_v1_subject_participation_get']['parameters']['query']>;
export type ParticipationQuery = NonNullable<operations['demo_participation_api_v1_demos__demo_id__participation_get']['parameters']['query']>;
export type EncountersQuery = NonNullable<operations['demo_encounters_api_v1_demos__demo_id__encounters_get']['parameters']['query']>;
export type EncounterQuery = NonNullable<operations['demo_encounter_api_v1_demos__demo_id__encounters__encounter_id__get']['parameters']['query']>;
export type ContextQuery = operations['demo_context_api_v1_demos__demo_id__context_get']['parameters']['query'];
export type EncounterContextQuery = NonNullable<operations['demo_encounter_context_api_v1_demos__demo_id__encounters__encounter_id__context_get']['parameters']['query']>;
export type GeometryCapabilitiesQuery = NonNullable<operations['geometry_capabilities_api_v1_geometry_capabilities_get']['parameters']['query']>;
export type GeometrySegmentQuery = NonNullable<operations['geometry_segment_api_v1_geometry_segment_get']['parameters']['query']>;
export type GeometryNavigationQuery = NonNullable<operations['geometry_navigation_api_v1_geometry_navigation_get']['parameters']['query']>;
export type GeometryLocationQuery = NonNullable<operations['geometry_location_api_v1_geometry_location_get']['parameters']['query']>;
