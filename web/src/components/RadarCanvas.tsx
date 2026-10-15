import { useEffect, useRef, useState, type ReactNode } from 'react';
import type { RadarDescriptor, ReplayPlayer } from '../api/types';
import { actorLabel, type ActorFrame, type Projection, type RadarLevel } from '../lib/radar';
import { sideColor } from '../lib/format';

export type KillMarker = {
  tick: number;
  x: number;
  y: number;
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

export function RadarCanvas({ radar, projection, levels, level, onLevelChange, actors, playerById, markers, tick, imageUrl }: Props): ReactNode {
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
  }, [size, image, actors, markers, projection, playerById, tick]);

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
          aria-label={`Radar of ${radar.map_name} at tick ${tick}: ${actors.length} visible players, ${markers.length} kill markers`}
        />
        <span className="radar-tick" aria-hidden="true">
          tick {tick}
        </span>
      </div>
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
