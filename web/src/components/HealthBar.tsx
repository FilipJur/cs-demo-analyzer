import type { ReactNode } from 'react';
import type { ApiError } from '../api/client';
import type { HealthResponse } from '../api/types';
import { formatBytes, formatTimestamp } from '../lib/format';
import { ErrorNotice } from './Notices';

export function HealthBar({ health, error, updatedAt }: { health: HealthResponse | null; error: ApiError | null; updatedAt: number | null }): ReactNode {
  return (
    <section className="health" aria-label="Backend health">
      <div className="health-item">
        <span className="health-label">Status</span>
        <span className="health-value">{health?.status ?? 'unavailable'}</span>
      </div>
      <div className="health-item">
        <span className="health-label">Worker</span>
        <span className="health-value">
          {health === null ? 'unavailable' : health.worker_running ? 'running' : 'idle'}
        </span>
      </div>
      <div className="health-item health-wide">
        <span className="health-label">Data root</span>
        <span className="health-value mono" title={health?.data_root ?? ''}>
          {health?.data_root ?? 'unknown'}
        </span>
      </div>
      <div className="health-item">
        <span className="health-label">Free disk</span>
        <span className="health-value">{health === null ? 'unknown' : formatBytes(health.free_bytes)}</span>
      </div>
      <div className="health-item">
        <span className="health-label">Schema</span>
        <span className="health-value">{health === null ? 'unknown' : `v${health.schema_version}`}</span>
      </div>
      <div className="health-item">
        <span className="health-label">Refreshed</span>
        <span className="health-value">{updatedAt === null ? 'never' : formatTimestamp(new Date(updatedAt).toISOString())}</span>
      </div>
      <ErrorNotice error={error} context="health" />
    </section>
  );
}
