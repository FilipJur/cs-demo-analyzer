import { useEffect, useRef, useState, type ReactNode } from 'react';
import type { RadarDescriptor, ReplayPlayer } from '../api/types';
import { actorLabel, type ActorFrame, type Projection, type RadarLevel } from '../lib/radar';
import { sideColor } from '../lib/format';

export type KillMarker = {
  tick: number;
  x: number;
  y: number;
};

/** One qualified relation line drawn in world/radar space. */
export type RadarRelationLine = {
  id: string;
  qualifier: 'clear' | 'estimated' | 'blocked' | 'unproven';
  from: { x: number; y: number };
  to: { x: number; y: number };
};

/** One recorded trajectory sample; nulls and death are recorded gaps, not edges. */
export type RadarTrajectorySample = {
  tick: number;
  x: number | null;
  y: number | null;
  health: number | null;
};

/**
 * A recorded trajectory on the encounter's sampling grid.
 *
 * The polyline is drawn only between samples that are exactly `strideTicks`
 * apart and observable at both ends; missing grid ticks, unusable coordinates
 * and death breaks are never connected.
 */
export type RadarTrajectory = {
  id: string;
  label: string;
  strideTicks: number;
  samples: RadarTrajectorySample[];
};

type Props = {
  radar: RadarDescriptor;
  projection: Projection;
  levels: RadarLevel[];
  level: RadarLevel | null;
  onLevelChange: (level: RadarLevel | null) => void;
  actors: ActorFrame[];
  playerById: Map<string, ReplayPlayer>;
  markers: KillMarker[];
  tick: number;
  imageUrl: string | null;
  /** Qualified sightline overlay; omitted or empty draws nothing extra. */
  relations?: RadarRelationLine[];
  /** Recorded subject trajectory of the selected encounter. */
  trajectory?: RadarTrajectory | null;
};

function drawGrid(context: CanvasRenderingContext2D, width: number, height: number): void {
  const spacing = 64;
  context.strokeStyle = '#262d38';
  context.lineWidth = 1;
  for (let x = 0; x <= width; x += spacing) {
    context.beginPath();
    context.moveTo(x, 0);
    context.lineTo(x, height);
    context.stroke();
  }
  for (let y = 0; y <= height; y += spacing) {
    context.beginPath();
    context.moveTo(0, y);
    context.lineTo(width, y);
    context.stroke();
  }
}

function drawMarker(context: CanvasRenderingContext2D, px: number, py: number, active: boolean): void {
  const arm = active ? 9 : 6;
  context.strokeStyle = active ? '#ff5b5b' : '#c2454b';
  context.lineWidth = active ? 3 : 2;
  context.beginPath();
  context.moveTo(px - arm, py - arm);
  context.lineTo(px + arm, py + arm);
  context.moveTo(px + arm, py - arm);
  context.lineTo(px - arm, py + arm);
  context.stroke();
}

function drawActor(context: CanvasRenderingContext2D, px: number, py: number, actor: ActorFrame, player: ReplayPlayer | undefined): void {
  const color = sideColor(actor.side);
  if (actor.yaw !== null) {
    const radians = (actor.yaw * Math.PI) / 180;
    context.strokeStyle = color;
    context.lineWidth = 2;
    context.beginPath();
    context.moveTo(px, py);
    context.lineTo(px + Math.cos(radians) * 15, py - Math.sin(radians) * 15);
    context.stroke();
  }
  context.beginPath();
  context.arc(px, py, 5.5, 0, Math.PI * 2);
  context.fillStyle = color;
  context.fill();
  context.lineWidth = 1.5;
  context.strokeStyle = actor.interpolated ? 'rgba(255,255,255,0.55)' : '#ffffff';
  context.stroke();
  const label = `${actorLabel(player, actor.player_id)}  ${actor.health}hp${actor.weapon !== null ? `  ${actor.weapon}` : ''}`;
  context.font = '600 12px system-ui, -apple-system, sans-serif';
  const textWidth = context.measureText(label).width;
  context.fillStyle = 'rgba(10,13,18,0.72)';
  context.fillRect(px - textWidth / 2 - 4, py - 26, textWidth + 8, 16);
  context.fillStyle = '#e8ebf0';
  context.textAlign = 'center';
  context.textBaseline = 'middle';
  context.fillText(label, px, py - 18);
}

/** Overlay colors: only a proven static line with recorded endpoints is green. */
const QUALIFIER_COLORS = { clear: '#5ad18a', estimated: '#6fd3c7', blocked: '#ff5b5b', unproven: '#8b93a1' } as const;

/**
 * Draw one relation line. Only an exact static-clear answer with recorded
 * endpoints is drawn as a solid unobstructed line; a clear answer between
 * estimated endpoints is drawn dashed teal, blocked lines are solid red, and
 * every unknown, unsupported or version-mismatched answer is dashed grey —
 * never clear.
 */
function drawRelation(context: CanvasRenderingContext2D, line: RadarRelationLine, scaleX: number, scaleY: number, projection: Projection): void {
  const from = projection.toPixels(line.from.x, line.from.y);
  const to = projection.toPixels(line.to.x, line.to.y);
  context.strokeStyle = QUALIFIER_COLORS[line.qualifier];
  context.lineWidth = line.qualifier === 'clear' || line.qualifier === 'blocked' ? 2.5 : 1.5;
  context.setLineDash(line.qualifier === 'clear' || line.qualifier === 'blocked' ? [] : [5, 5]);
  context.beginPath();
  context.moveTo(from.px * scaleX, from.py * scaleY);
  context.lineTo(to.px * scaleX, to.py * scaleY);
  context.stroke();
  context.setLineDash([]);
}

/**
 * Draw a recorded trajectory as dashes on its sampling grid.
 *
 * A run ends — and a new one starts — whenever a sample is unusable (missing
 * grid tick, non-finite coordinate, dead or unknown health), so no edge ever
 * crosses a gap or a death. Each recorded sample also gets a dot, so isolated
 * observations stay visible instead of being silently dropped.
 */
function drawTrajectory(context: CanvasRenderingContext2D, trajectory: RadarTrajectory, scaleX: number, scaleY: number, projection: Projection): void {
  const stride = Math.max(1, trajectory.strideTicks);
  context.strokeStyle = 'rgba(232,235,240,0.6)';
  context.fillStyle = 'rgba(232,235,240,0.6)';
  context.lineWidth = 1.5;
  context.setLineDash([2, 4]);
  let expectedTick: number | null = null;
  let drawing = false;
  for (const sample of trajectory.samples) {
    const x = sample.x;
    const y = sample.y;
    const usable = x !== null && y !== null && Number.isFinite(x) && Number.isFinite(y) && sample.health !== null && sample.health > 0;
    if (!usable) {
      if (drawing) {
        context.stroke();
        drawing = false;
      }
      expectedTick = null;
      continue;
    }
    const pixels = projection.toPixels(x, y);
    const px = pixels.px * scaleX;
    const py = pixels.py * scaleY;
    if (!drawing || sample.tick !== expectedTick) {
      if (drawing) context.stroke();
      context.beginPath();
      context.moveTo(px, py);
      drawing = true;
    } else {
      context.lineTo(px, py);
    }
    expectedTick = sample.tick + stride;
    context.beginPath();
    context.arc(px, py, 1.5, 0, Math.PI * 2);
    context.fill();
    context.beginPath();
    context.moveTo(px, py);
  }
  if (drawing) context.stroke();
  context.setLineDash([]);
}

export function RadarCanvas({ radar, projection, levels, level, onLevelChange, actors, playerById, markers, tick, imageUrl, relations = [], trajectory = null }: Props): ReactNode {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  const [imageError, setImageError] = useState<string | null>(null);
  const aspect = projection.height / projection.width;

  useEffect(() => {
    const element = containerRef.current;
    if (element === null) return;
    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry === undefined) return;
      const width = Math.max(200, Math.floor(entry.contentRect.width));
      setSize({ width, height: Math.max(160, Math.round(width * aspect)) });
    });
    observer.observe(element);
    return () => observer.disconnect();
  }, [aspect]);

  useEffect(() => {
    setImage(null);
    setImageError(null);
    if (imageUrl === null) return;
    const next = new Image();
    next.decoding = 'async';
    next.onload = () => setImage(next);
    next.onerror = () => setImageError('Radar image unavailable from the local asset endpoint.');
    next.src = imageUrl;
    return () => {
      next.onload = null;
      next.onerror = null;
    };
  }, [imageUrl]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas === null || size.width === 0) return;
    const context = canvas.getContext('2d');
    if (context === null) return;
    const ratio = window.devicePixelRatio || 1;
    canvas.width = Math.round(size.width * ratio);
    canvas.height = Math.round(size.height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.fillStyle = '#0e1218';
    context.fillRect(0, 0, size.width, size.height);
    if (image !== null) {
      context.globalAlpha = 0.9;
      context.drawImage(image, 0, 0, size.width, size.height);
      context.globalAlpha = 1;
    } else {
      drawGrid(context, size.width, size.height);
    }
    const scaleX = size.width / projection.width;
    const scaleY = size.height / projection.height;
    if (trajectory !== null) drawTrajectory(context, trajectory, scaleX, scaleY, projection);
    for (const line of relations) drawRelation(context, line, scaleX, scaleY, projection);
    for (const marker of markers) {
      const point = projection.toPixels(marker.x, marker.y);
      drawMarker(context, point.px * scaleX, point.py * scaleY, marker.tick === tick);
    }
    for (const actor of actors) {
      const point = projection.toPixels(actor.x, actor.y);
      drawActor(context, point.px * scaleX, point.py * scaleY, actor, playerById.get(actor.player_id));
    }
    if (actors.length === 0) {
      context.font = '600 14px system-ui, -apple-system, sans-serif';
      context.fillStyle = '#8b93a1';
      context.textAlign = 'center';
      context.textBaseline = 'middle';
      context.fillText('No live player observations at this tick', size.width / 2, size.height / 2);
    }
  }, [size, image, actors, markers, projection, playerById, tick, relations, trajectory]);

  return (
    <div className="radar">
      <div className="radar-header">
        <span className="mono">{radar.map_name}</span>
        {levels.length > 1 ? (
          <label className="radar-level">
            Radar level
            <select
              value={level?.name ?? ''}
              onChange={(event) => {
                const next = levels.find((candidate) => candidate.name === event.target.value) ?? null;
                onLevelChange(next);
              }}
            >
              <option value="">auto (by player altitude)</option>
              {levels.map((candidate) => (
                <option key={candidate.name} value={candidate.name}>
                  {candidate.name}
                </option>
              ))}
            </select>
          </label>
        ) : null}
        <span className="badge">
          {radar.match_status === 'exact' ? 'client match' : radar.match_status === 'mismatch' ? 'version mismatch' : 'version unknown'}
        </span>
        <span className="small">
          {radar.installed_client_version ?? 'no installed version'} vs demo {radar.demo_client_version ?? 'unknown'}
        </span>
      </div>
      <div className="radar-canvas" ref={containerRef} style={{ aspectRatio: `${projection.width} / ${projection.height}` }}>
        <canvas
          ref={canvasRef}
          style={{ width: '100%', height: '100%' }}
          role="img"
          aria-label={`Radar of ${radar.map_name} at tick ${tick}: ${actors.length} visible players, ${markers.length} kill markers, ${relations.length} qualified relation lines`}
        />
        <span className="radar-tick" aria-hidden="true">
          tick {tick}
        </span>
      </div>
      {relations.length > 0 || trajectory !== null ? (
        <p className="small radar-overlay-legend" role="status">
          <span className="qualifier-clear">solid green</span> = no static obstruction in the matching installed assets ·{' '}
          <span className="qualifier-estimated">dashed teal</span> = static clear but at least one endpoint is an estimated eye position ·{' '}
          <span className="qualifier-blocked">solid red</span> = static obstruction recorded ·{' '}
          <span className="qualifier-unproven">dashed grey</span> = unknown, unsupported or version-mismatched sightline (not proven clear)
          {trajectory === null ? '' : ` · dotted white = ${trajectory.label} — sampled recorded positions, not continuous movement`}
        </p>
      ) : null}
      {imageError !== null ? (
        <p className="notice notice-warning" role="status">
          {imageError} Positions are still drawn in world-scaled radar space.
        </p>
      ) : null}
      {radar.warning !== null && radar.warning !== undefined ? (
        <p className="notice notice-warning" role="status">
          {radar.warning}
        </p>
      ) : null}
      {imageUrl === null ? (
        <p className="notice notice-warning" role="status">
          No radar image is registered for this map and client version; the replay shows geometry-only positions.
        </p>
      ) : null}
      {projection.source === 'relative' ? (
        <p className="notice notice-warning" role="status">
          The API supplied no overview origin/scale for this map, so positions are relative and not map-scaled.
        </p>
      ) : null}
    </div>
  );
}
