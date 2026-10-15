import type { ReactNode } from 'react';
import type { ApiError } from '../api/client';
import type { JobRecord } from '../api/types';
import { formatTimestamp, shortHash } from '../lib/format';
import { ErrorNotice, StateBadge } from './Notices';

const ACTIVE: JobRecord['state'][] = ['queued', 'running'];

export function JobsPanel({ jobs, error, onSelectDemo }: { jobs: JobRecord[] | null; error: ApiError | null; onSelectDemo: (demoId: string) => void }): ReactNode {
  const all = jobs ?? [];
  const ordered = [...all].sort((a, b) => (b.updated_at > a.updated_at ? 1 : b.updated_at < a.updated_at ? -1 : 0));
  const active = ordered.filter((job) => ACTIVE.includes(job.state)).length;

  return (
    <section className="panel" aria-label="Extraction jobs">
      <header className="panel-header">
        <h2>Jobs</h2>
        <span className="count">{all.length === 0 ? 'none' : `${active} active / ${all.length} total`}</span>
      </header>
      <ul className="list">
        {ordered.slice(0, 10).map((job) => (
          <li key={job.id} className="list-row">
            <StateBadge state={job.state} />
            <button type="button" className="link mono small" onClick={() => onSelectDemo(job.demo_id)} title={job.demo_id}>
              {shortHash(job.demo_id)}
            </button>
            <span className="small">attempt {job.attempt}</span>
            <span className="small">{formatTimestamp(job.updated_at)}</span>
            {job.error ? (
              <p className="notice notice-error inline-error" role="alert">
                <span className="notice-code">{job.error.code}</span>
                <span>{job.error.message}</span>
                <span className="notice-meta">{job.error.stage}</span>
                {job.error.retryable ? <span className="notice-meta">retryable</span> : null}
              </p>
            ) : null}
          </li>
        ))}
        {all.length === 0 ? <li className="list-empty">No extraction jobs yet.</li> : null}
        {all.length > 10 ? <li className="list-empty">{all.length - 10} more not shown.</li> : null}
      </ul>
      <ErrorNotice error={error} context="GET /jobs" />
    </section>
  );
}
