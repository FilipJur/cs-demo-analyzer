import { useEffect, useState, type ReactNode } from 'react';
import { isAbortError, toApiError, type ApiError } from '../api/client';
import { PHASE2_LIMITS, phase2 } from '../api/phase2';
import type { GeometryCapabilities, GeometrySegmentQuery, PointLocation, SegmentResult, Vec3 } from '../api/types';
import { shortHash } from '../lib/format';
import { sightlineQualifier } from '../lib/phase2';
import { usePolled } from '../lib/usePolling';
import { ErrorNotice, WarningList } from './Notices';

type Props = {
  /** Map of the loaded generation; the panel stays inert without it. */
  mapName: string | null;
  /** Client version recorded in this demo, for the exact/mismatch comparison. */
  demoClientVersion: string | null;
  /** Recorded view origins of the subject at the current tick (eye height: sightlines only). */
  subjectPoint: Vec3 | null;
  /** Recorded view origin of the nearest relation (eye height: sightlines only). */
  otherPoint: Vec3 | null;
  /** Recorded player origin (feet) of the subject at the current tick: the ground point for floor/nav queries. */
  subjectOrigin: Vec3 | null;
};

type Vectors = { start: [string, string, string]; end: [string, string, string] };

const AXES = ['x', 'y', 'z'] as const;

function textOf(point: Vec3 | null): [string, string, string] {
  return point === null ? ['', '', ''] : [String(point[0]), String(point[1]), String(point[2])];
}

/**
 * Parse the six probe fields: every coordinate must be finite and inside the
 * API's world bound, so a malformed value is reported instead of silently sent.
 */
function parseVectors(vectors: Vectors): { start: Vec3; end: Vec3 } | string {
  const parse = (values: [string, string, string]): Vec3 | string => {
    const numbers = values.map((value) => Number(value.trim()));
    if (values.some((value) => value.trim() === '')) return 'each coordinate must be filled in';
    if (numbers.some((value) => !Number.isFinite(value))) return 'coordinates must be finite numbers';
    if (numbers.some((value) => Math.abs(value) > PHASE2_LIMITS.coordinate)) {
      return `coordinates must stay inside ±${PHASE2_LIMITS.coordinate} world units`;
    }
    return [numbers[0] ?? 0, numbers[1] ?? 0, numbers[2] ?? 0];
  };
  const start = parse(vectors.start);
  if (typeof start === 'string') return `start: ${start}`;
  const end = parse(vectors.end);
  if (typeof end === 'string') return `end: ${end}`;
  return { start, end };
}

function PointFields({
  idPrefix,
  label,
  values,
  onChange,
}: {
  idPrefix: string;
  label: string;
  values: [string, string, string];
  onChange: (next: [string, string, string]) => void;
}): ReactNode {
  return (
    <div className="geometry-point">
      <span className="small">{label}</span>
      {AXES.map((axis, index) => (
        <label key={axis} className="small">
          {axis}
          <input
            id={`${idPrefix}-${axis}`}
            type="text"
            inputMode="decimal"
            className="mono"
            value={values[index] ?? ''}
            onChange={(event) => {
              const next: [string, string, string] = [values[0], values[1], values[2]];
              next[index] = event.target.value;
              onChange(next);
            }}
          />
        </label>
      ))}
    </div>
  );
}

/** The six bounded coordinates of one probe, in the API's own wire shape. */
function probeQuery(mapName: string, demoClientVersion: string | null, start: Vec3, end: Vec3): GeometrySegmentQuery {
  return {
    map_name: mapName,
    demo_client_version: demoClientVersion,
    start_x: start[0],
    start_y: start[1],
    start_z: start[2],
    end_x: end[0],
    end_y: end[1],
    end_z: end[2],
  };
}

function segmentSummary(result: SegmentResult): ReactNode {
  const qualifier = sightlineQualifier(result.status, result.match_status, result.status, 'entered');
  return (
    <ul className="list dense">
      <li className="list-row">
        <span className="badge">{result.status}</span>
        <span className={`badge ${qualifier.className}`}>{qualifier.label}</span>
        <span className="small">assets {result.match_status}</span>
        <span className="small">length {result.length.toFixed(1)}u</span>
        <span className="small">{result.hit_distance === null ? 'no hit recorded' : `hit at ${result.hit_distance.toFixed(1)}u`}</span>
        <span className="mono small" title={result.asset_id ?? ''}>
          {result.asset_id === null ? 'no asset id' : shortHash(result.asset_id)}
        </span>
      </li>
    </ul>
  );
}

/**
 * Static geometry of the loaded map: what is installed, what can be prepared,
 * and a bounded manual static-ray probe between two world points.
 *
 * Nothing is extracted implicitly: preparation is an explicit button and the
 * probe runs only on request. An unprepared map or a version mismatch is shown
 * as unproven, never as a clear line. Navigation is not queried from the eye
 * points entered here — a nav-graph question needs ground origins, so it is
 * answered by the context panels' explicit opt-in instead.
 */
export function GeometryPanel({ mapName, demoClientVersion, subjectPoint, otherPoint, subjectOrigin }: Props): ReactNode {
  const capabilities = usePolled(
    (signal) => phase2.geometryCapabilities({ map_name: mapName ?? '', demo_client_version: demoClientVersion }, signal),
    120000,
    { enabled: mapName !== null, key: `${mapName ?? ''}|${demoClientVersion ?? ''}` },
  );
  const [vectors, setVectors] = useState<Vectors>({ start: ['', '', ''], end: ['', '', ''] });
  const [segment, setSegment] = useState<SegmentResult | null>(null);
  const [location, setLocation] = useState<PointLocation | null>(null);
  const [locationError, setLocationError] = useState<ApiError | null>(null);
  const [locating, setLocating] = useState(false);
  const [probeError, setProbeError] = useState<ApiError | null>(null);
  const [probing, setProbing] = useState(false);
  const [preparing, setPreparing] = useState(false);
  const [prepared, setPrepared] = useState<GeometryCapabilities | null>(null);

  useEffect(() => {
    setSegment(null);
    setProbeError(null);
  }, [mapName]);

  const capabilitiesAnswer = prepared ?? capabilities.data;
  const warning = ((): string | null => {
    if (capabilitiesAnswer === null) return null;
    if (!capabilitiesAnswer.prepared) return `No prepared static geometry for ${capabilitiesAnswer.map_name}; sightlines stay unproven until it is prepared.`;
    if (capabilitiesAnswer.match_status !== 'exact') {
      return `Installed geometry is for client ${capabilitiesAnswer.install_client_version ?? 'unknown'} but this demo recorded ${
        capabilitiesAnswer.demo_client_version ?? 'unknown'
      }; static answers cannot prove this recording's sightlines.`;
    }
    return null;
  })();

  const probe = (): void => {
    const parsed = parseVectors(vectors);
    if (typeof parsed === 'string') {
      setProbeError(toApiError({ code: 'INVALID_ARGUMENT', message: parsed, stage: 'client' }));
      return;
    }
    if (mapName === null) return;
    setProbing(true);
    setProbeError(null);
    void (async () => {
      try {
        setSegment(await phase2.segment(probeQuery(mapName, demoClientVersion, parsed.start, parsed.end)));
      } catch (exc) {
        if (!isAbortError(exc)) setProbeError(toApiError(exc));
      } finally {
        setProbing(false);
      }
    })();
  };

  /**
   * Ask the installed build about one world point: is it inside the map, does
   * it sit in solid, what is the floor under it and which nav area is there.
   * The point is the subject's recorded *origin* (feet), never an eye position.
   */
  const locateOrigin = (): void => {
    if (mapName === null || subjectOrigin === null) return;
    setLocating(true);
    setLocationError(null);
    void (async () => {
      try {
        setLocation(
          await phase2.locate({
            map_name: mapName,
            demo_client_version: demoClientVersion,
            x: subjectOrigin[0],
            y: subjectOrigin[1],
            z: subjectOrigin[2],
          }),
        );
      } catch (exc) {
        if (!isAbortError(exc)) setLocationError(toApiError(exc));
      } finally {
        setLocating(false);
      }
    })();
  };

  const prepare = (): void => {
    if (mapName === null) return;
    setPreparing(true);
    setProbeError(null);
    void (async () => {
      try {
        setPrepared(await phase2.prepareGeometry(mapName));
        capabilities.refresh();
      } catch (exc) {
        if (!isAbortError(exc)) setProbeError(toApiError(exc));
      } finally {
        setPreparing(false);
      }
    })();
  };

  if (mapName === null) {
    return (
      <section className="panel" aria-label="Static geometry">
        <header className="panel-header">
          <h2>Static geometry</h2>
        </header>
        <p className="hint">Load a round to inspect the installed static geometry of its map.</p>
      </section>
    );
  }

  return (
    <section className="panel" aria-label="Static geometry">
      <header className="panel-header">
        <h2>Static geometry</h2>
        <span className="count mono">
          {mapName} · demo {demoClientVersion ?? 'unknown'}
        </span>
      </header>

      <ErrorNotice error={capabilities.error} context="GET /geometry/capabilities" />
      {capabilitiesAnswer !== null ? (
        <ul className="list dense">
          <li className="list-row">
            <span className="badge">{capabilitiesAnswer.prepared ? 'prepared' : 'not prepared'}</span>
            <span className="grow small">
              physics {capabilitiesAnswer.physics.status} · navigation {capabilitiesAnswer.navigation.status} · triangles{' '}
              {capabilitiesAnswer.triangle_count} · nav areas {capabilitiesAnswer.nav_area_count}
            </span>
            <span className="badge">{`assets ${capabilitiesAnswer.match_status}`}</span>
          </li>
          <li className="list-row">
            <span className="badge">bounds</span>
            <span className="grow mono small">
              {capabilitiesAnswer.bounds_min === null ? 'unknown' : capabilitiesAnswer.bounds_min.map((value) => value.toFixed(0)).join(', ')} →{' '}
              {capabilitiesAnswer.bounds_max === null ? 'unknown' : capabilitiesAnswer.bounds_max.map((value) => value.toFixed(0)).join(', ')}
            </span>
            <span className="small">installed {capabilitiesAnswer.install_client_version ?? 'unknown'}</span>
          </li>
        </ul>
      ) : capabilities.loading ? (
        <p className="hint">Loading geometry capabilities…</p>
      ) : null}

      <div className="form-actions">
        <button type="button" onClick={prepare} disabled={preparing}>
          {preparing ? 'Preparing…' : 'Prepare geometry for this map'}
        </button>
        <span className="small">Extraction only happens here, never while scrubbing the replay.</span>
      </div>

      {warning !== null ? (
        <p className="notice notice-warning" role="status">
          {warning}
        </p>
      ) : null}
      {capabilitiesAnswer !== null && capabilitiesAnswer.limitations.length > 0 ? (
        <details>
          <summary>{capabilitiesAnswer.limitations.length} geometry limitation(s)</summary>
          <ul className="list dense">
            {capabilitiesAnswer.limitations.map((item) => (
              <li key={item} className="small">
                {item}
              </li>
            ))}
          </ul>
        </details>
      ) : null}

      <h4>Locate the subject's recorded origin (ground point)</h4>
      <p className="hint">
        Uses the recorded <span className="mono">player_state</span> origin of the subject at the current replay tick — feet on the ground, not the eye position —
        because floor height, nav area and solidity are ground questions. Coordinates outside the map are reported as such, never corrected.
      </p>
      <div className="form-actions">
        <button type="button" onClick={locateOrigin} disabled={locating || subjectOrigin === null}>
          {locating ? 'Locating…' : 'Locate origin'}
        </button>
        <span className="mono small">
          {subjectOrigin === null ? 'no recorded origin for the subject at this tick' : `origin ${subjectOrigin.map((value) => value.toFixed(0)).join(', ')}`}
        </span>
      </div>
      <ErrorNotice error={locationError} context="GET /geometry/location" />
      {location !== null ? (
        <>
          <ul className="list dense">
            <li className="list-row">
              <span className="badge">point</span>
              <span className="grow mono small">{location.point.map((value) => value.toFixed(0)).join(', ')}</span>
              <span className={`badge ${location.in_bounds === false ? 'badge-warn' : ''}`}>
                {location.in_bounds === null ? 'bounds unknown' : location.in_bounds ? 'in bounds' : 'outside the map'}
              </span>
              <span className={`badge ${location.inside_solid === true ? 'badge-warn' : ''}`}>
                {location.inside_solid === null ? 'solidity unknown' : location.inside_solid ? 'inside solid' : 'not in solid'}
              </span>
              <span className="badge">{`assets ${location.match_status}`}</span>
            </li>
            <li className="list-row">
              <span className="badge">floor</span>
              <span className="mono small">{location.floor_z === null ? 'z not recorded' : `z ${location.floor_z.toFixed(0)}`}</span>
              <span className="mono small">
                {location.floor_distance === null ? 'distance not recorded' : `${location.floor_distance.toFixed(0)}u below`}
              </span>
              <span className="mono small" title="free vertical space above the point">
                clearance {location.clearance_up === null ? 'not recorded' : `${location.clearance_up.toFixed(0)}u`}
              </span>
            </li>
            <li className="list-row">
              <span className="badge">nav</span>
              <span className="mono small">
                {location.nav_area_id === null ? 'no nav area recorded' : `area ${location.nav_area_id}`}
              </span>
              <span className="mono small" title={location.asset_id ?? ''}>
                {location.asset_id === null ? 'no asset id' : shortHash(location.asset_id)}
              </span>
              <span className="small">
                {location.inside_solid === null && location.in_bounds === null
                  ? 'no collision data covers this point'
                  : 'collision reading from the installed build'}
              </span>
            </li>
          </ul>
          {location.limitations.length > 0 ? <WarningList warnings={location.limitations} /> : null}
        </>
      ) : null}

      <h4>Manual static-segment probe</h4>
      <p className="hint">
        Use “Use subject → relation” to fill the ray endpoints from the current context's eye positions, which are stance-based estimates unless explicitly
        marked as recorded. These points are separate from the recorded ground origin above.
      </p>
      <PointFields idPrefix="geometry-start" label="start" values={vectors.start} onChange={(next) => setVectors((current) => ({ ...current, start: next }))} />
      <PointFields idPrefix="geometry-end" label="end" values={vectors.end} onChange={(next) => setVectors((current) => ({ ...current, end: next }))} />
      <div className="form-actions">
        <button type="button" onClick={probe} disabled={probing}>
          {probing ? 'Probing…' : 'Probe static line'}
        </button>
        <button
          type="button"
          onClick={() => setVectors({ start: textOf(subjectPoint), end: textOf(otherPoint) })}
          disabled={subjectPoint === null && otherPoint === null}
        >
          Use subject → relation
        </button>
        <span className="small">
          coordinates must stay inside ±{PHASE2_LIMITS.coordinate}u; one probe is a single static segment read
        </span>
      </div>
      <ErrorNotice error={probeError} context="geometry probe" />
      {segment !== null ? segmentSummary(segment) : null}
    </section>
  );
}
