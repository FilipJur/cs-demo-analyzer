import type { ReactNode } from 'react';
import { ApiError } from '../api/client';

export function ErrorNotice({ error, context }: { error: ApiError | null; context?: string }): ReactNode {
  if (error === null) return null;
  return (
    <p className="notice notice-error" role="alert">
      <span className="notice-code">{error.code}</span>
      <span>{error.message}</span>
      {error.retryable ? <span className="notice-meta">retryable</span> : null}
      {context ? <span className="notice-meta">{context}</span> : null}
      {error.status > 0 ? <span className="notice-meta">HTTP {error.status}</span> : null}
    </p>
  );
}

export function WarningList({ warnings }: { warnings: string[] }): ReactNode {
  if (warnings.length === 0) return null;
  return (
    <ul className="warning-list" role="status">
      {warnings.map((warning) => (
        <li key={warning}>{warning}</li>
      ))}
    </ul>
  );
}

export function StateBadge({ state }: { state: string }): ReactNode {
  const known = ['queued', 'running', 'succeeded', 'failed', 'interrupted'];
  const modifier = known.includes(state) ? state : 'other';
  return <span className={`badge badge-${modifier}`}>{state}</span>;
}
