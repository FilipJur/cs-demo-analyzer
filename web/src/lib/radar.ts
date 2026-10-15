// Radar projection and actor interpolation. Pure functions only: no clock, no
// React, no hardcoded map geometry or player counts.
import type { RadarDescriptor, ReplayPlayer, ReplaySample } from '../api/types';

export type RadarLevel = {
  name: string;
  assetId: string;
  altitudeMin: number | null;
  altitudeMax: number | null;
  width: number | null;
  height: number | null;
};

export type Projection = {
  width: number;
  height: number;
  source: 'radar' | 'relative';
  toPixels: (x: number, y: number) => { px: number; py: number };
};

export type ActorFrame = {
  player_id: string;
  x: number;
  y: number;
  z: number | null;
  yaw: number | null;
  health: number;
  side: string;
  weapon: string | null;
  interpolated: boolean;
};

type LiveSample = ReplaySample & { x: number; y: number; health: number };

function isLive(sample: ReplaySample): sample is LiveSample {
  return sample.health !== null && sample.health > 0 && sample.x !== null && sample.y !== null;
}

function finite(value: unknown): number | null {
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}

function frameOf(sample: LiveSample, interpolated: boolean): ActorFrame {
  return {
    player_id: sample.player_id,
    x: sample.x,
    y: sample.y,
    z: sample.z,
    yaw: sample.yaw,
    health: sample.health,
    side: sample.side,
    weapon: sample.active_weapon,
    interpolated,
  };
}

/** Radar altitude bands come from the API metadata as untyped dicts. */
export function parseLevels(radar: RadarDescriptor): RadarLevel[] {
  const levels: RadarLevel[] = [];
  for (const entry of radar.levels ?? []) {
    if (typeof entry !== 'object' || entry === null) continue;
    const record: Record<string, unknown> = entry;
    const name = record['name'];
    const assetId = record['asset_id'];
    if (typeof name !== 'string' || typeof assetId !== 'string') continue;
    levels.push({
      name,
      assetId,
      altitudeMin: finite(record['altitude_min']),
      altitudeMax: finite(record['altitude_max']),
      width: finite(record['width']),
      height: finite(record['height']),
    });
  }
  return levels;
}

export function pickLevelForZ(levels: RadarLevel[], z: number | null): RadarLevel | null {
  if (z === null) return null;
  for (const level of levels) {
    const low = level.altitudeMin ?? Number.NEGATIVE_INFINITY;
    const high = level.altitudeMax ?? Number.POSITIVE_INFINITY;
    if (z >= low && z <= high) return level;
  }
  return null;
}

export function medianZ(actors: ActorFrame[]): number | null {
  const values = actors
    .map((actor) => actor.z)
    .filter((value): value is number => value !== null)
    .sort((a, b) => a - b);
  if (values.length === 0) return null;
  const middle = values.length >> 1;
  if (values.length % 2 === 1) return values[middle] ?? null;
  const low = values[middle - 1];
  const high = values[middle];
  if (low === undefined || high === undefined) return null;
  return (low + high) / 2;
}

/** World XYZ (Z-up, Hammer units) to radar image pixels for the base overview. */
export function radarProjection(radar: RadarDescriptor, level: RadarLevel | null): Projection | null {
  const posX = finite(radar.pos_x);
  const posY = finite(radar.pos_y);
  const scale = finite(radar.scale);
  if (posX === null || posY === null || scale === null || scale === 0) return null;
  const levelWidth = level?.width;
  const levelHeight = level?.height;
  return {
    width: levelWidth !== undefined && levelWidth !== null && levelWidth > 0 ? levelWidth : radar.width,
    height: levelHeight !== undefined && levelHeight !== null && levelHeight > 0 ? levelHeight : radar.height,
    source: 'radar',
    toPixels: (x, y) => ({ px: (x - posX) / scale, py: (posY - y) / scale }),
  };
}

/** Fallback used only when the API supplies no overview geometry. */
export function relativeProjection(actors: ActorFrame[], width = 1024, height = 1024): Projection {
  if (actors.length === 0) {
    return {
      width,
      height,
      source: 'relative',
      toPixels: (x, y) => ({ px: width / 2 + x * 0.1, py: height / 2 - y * 0.1 }),
    };
  }
  const xs = actors.map((actor) => actor.x);
  const ys = actors.map((actor) => actor.y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const spanX = Math.max(maxX - minX, 1);
  const spanY = Math.max(maxY - minY, 1);
  const pad = 0.1;
  return {
    width,
    height,
    source: 'relative',
    toPixels: (x, y) => ({
      px: ((x - minX) / spanX) * width * (1 - 2 * pad) + width * pad,
      py: ((maxY - y) / spanY) * height * (1 - 2 * pad) + height * pad,
    }),
  };
}

/** Yaw is in degrees; angles must never interpolate the long way round. */
export function shortestArcYaw(from: number, to: number): number {
  return ((to - from + 540) % 360) - 180;
}

export function interpolateAngle(from: number, to: number, ratio: number): number {
  return from + shortestArcYaw(from, to) * ratio;
}

export function buildTracks(samples: ReplaySample[]): Map<string, ReplaySample[]> {
  const sorted = [...samples].sort((a, b) => a.tick - b.tick || (a.player_id < b.player_id ? -1 : a.player_id > b.player_id ? 1 : 0));
  const tracks = new Map<string, ReplaySample[]>();
  for (const sample of sorted) {
    const track = tracks.get(sample.player_id);
    if (track) track.push(sample);
    else tracks.set(sample.player_id, [sample]);
  }
  return tracks;
}

function locate(track: ReplaySample[], tick: number): { exact: ReplaySample | null; index: number } {
  let low = 0;
  let high = track.length - 1;
  while (low <= high) {
    const middle = (low + high) >> 1;
    const sample = track[middle];
    if (sample === undefined) break;
    if (sample.tick === tick) return { exact: sample, index: middle };
    if (sample.tick < tick) low = middle + 1;
    else high = middle - 1;
  }
  return { exact: null, index: low };
}

/**
 * Position of one actor at an exact tick. Interpolation happens only between two
 * live observations closer than one sample stride; dead actors, missing
 * observations and window edges never produce an invented position.
 */
export function actorAt(track: ReplaySample[], tick: number, stride: number): ActorFrame | null {
  if (track.length === 0) return null;
  const { exact, index } = locate(track, tick);
  if (exact !== null) return isLive(exact) ? frameOf(exact, false) : null;
  const previous = index > 0 ? track[index - 1] : undefined;
  const next = index < track.length ? track[index] : undefined;
  if (previous !== undefined && next !== undefined && isLive(previous) && isLive(next) && next.tick - previous.tick <= stride) {
    const span = next.tick - previous.tick;
    const ratio = span === 0 ? 0 : (tick - previous.tick) / span;
    const base = frameOf(previous, true);
    return {
      ...base,
      x: previous.x + (next.x - previous.x) * ratio,
      y: previous.y + (next.y - previous.y) * ratio,
      yaw: previous.yaw !== null && next.yaw !== null ? interpolateAngle(previous.yaw, next.yaw, ratio) : previous.yaw,
    };
  }
  if (previous !== undefined && isLive(previous) && tick - previous.tick <= stride) return frameOf(previous, false);
  return null;
}

/** Exact-tick position, ignoring liveness: used to place kill markers. */
export function positionAt(track: ReplaySample[], tick: number): { x: number; y: number } | null {
  const { exact } = locate(track, tick);
  if (exact === null || exact.x === null || exact.y === null) return null;
  return { x: exact.x, y: exact.y };
}

export function actorLabel(player: ReplayPlayer | undefined, fallbackId: string): string {
  if (!player || player.name === null || player.name.trim() === '') return fallbackId;
  return player.name;
}
