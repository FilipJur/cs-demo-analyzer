// Phase 2 presentation helpers: status vocabulary and replay-anchor math.
//
// The sightline qualifier is the one place that decides how a static collision
// result is worded. Only an `exact` installed-asset scan that reports
// `static_clear` may be shown as unobstructed; `mismatch`, `unknown` and
// `unsupported` are always presented as unproven, never as clear.
import type { MatchStatus, ParticipationStatus, SegmentStatus } from '../api/types';

export type QualifierKey = 'clear' | 'estimated' | 'blocked' | 'unproven';
export type Qualifier = { key: QualifierKey; label: string; className: string };

/** Where the two endpoints of a static sightline came from. */
export type EndpointBasis = 'recorded' | 'estimated' | 'entered';

/** Badge/modifier pair for one participation status; the four states stay distinct. */
export function participationBadge(status: ParticipationStatus): string {
  if (status === 'present') return 'badge-succeeded';
  if (status === 'absent') return 'badge-failed';
  if (status === 'unresolved') return 'badge-warn';
  return 'badge-queued';
}

/**
 * How one static sightline may be described.
 *
 * `effective` is the provider's already-downgraded status (mismatched or
 * unprovable results arrive as `unknown`); the raw segment status is used as a
 * fallback and to name the reason.
 */
export function sightlineQualifier(
  status: SegmentStatus | null,
  matchStatus: MatchStatus | null,
  effective?: SegmentStatus | null,
  endpointBasis: EndpointBasis = 'recorded',
): Qualifier {
  const resolved = effective ?? status;
  if (resolved === 'static_blocked') {
    return {
      key: 'blocked',
      label: matchStatus === 'exact' ? 'static obstruction in the matching installed assets' : 'static obstruction in the installed assets (client version not matched)',
      className: 'qualifier-blocked',
    };
  }
  if (resolved === 'static_clear' && matchStatus === 'exact') {
    if (endpointBasis === 'estimated') {
      return {
        key: 'estimated',
        label: 'static clear between estimated (unqualified) eye positions',
        className: 'qualifier-estimated',
      };
    }
    return {
      key: 'clear',
      label: endpointBasis === 'entered' ? 'no static obstruction along the given coordinates' : 'no static obstruction in installed assets',
      className: 'qualifier-clear',
    };
  }
  if (matchStatus === 'mismatch') {
    return { key: 'unproven', label: 'client version mismatch — sightline not proven', className: 'qualifier-unproven' };
  }
  if (resolved === 'unsupported') {
    return { key: 'unproven', label: 'no static geometry available', className: 'qualifier-unproven' };
  }
  if (resolved === 'static_clear') {
    return { key: 'unproven', label: 'static clear, provenance unverified', className: 'qualifier-unproven' };
  }
  return { key: 'unproven', label: 'sightline unknown', className: 'qualifier-unproven' };
}

/** Bounded follow step: at most `samplesPerSecond` context reads while playing. */
export function followStep(tickRateHz: number, samplesPerSecond: number): number {
  return tickRateHz > 0 ? Math.max(1, Math.round(tickRateHz / samplesPerSecond)) : 1;
}

/** One evidence reference rendered as `dataset#ordinal@tick`. */
export function evidenceLabel(ref: {
  dataset: string;
  row_ordinal: number;
  tick: number;
  round_id: number | null;
  player_ids: string[];
}): string {
  return `${ref.dataset}#${ref.row_ordinal}@${ref.tick}${ref.round_id === null ? '' : ` r${ref.round_id}`}${
    ref.player_ids.length === 0 ? '' : ` [${ref.player_ids.join(', ')}]`
  }`;
}
