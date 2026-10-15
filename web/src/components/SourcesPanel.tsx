import type { ReactNode } from 'react';
import type { ApiError } from '../api/client';
import type { SourceRecord } from '../api/types';
import { formatTimestamp, shortHash } from '../lib/format';
import { ErrorNotice } from './Notices';

const VISIBLE_LIMIT = 12;

export function SourcesPanel({ sources, error }: { sources: SourceRecord[] | null; error: ApiError | null }): ReactNode {
  const all = sources ?? [];
  const failing = all.filter((source) => source.error !== null && source.error !== undefined);
  const others = all.filter((source) => source.error === null || source.error === undefined);
  const visible = [...failing, ...others].slice(0, VISIBLE_LIMIT);

  return (
    <section className="panel" aria-label="Source observations">
      <header className="panel-header">
        <h2>Sources</h2>
        <span className="count">{all.length === 0 ? 'none' : `${failing.length} error / ${all.length} observed`}</span>
      </header>
      <ul className="list">
        {visible.map((source) => {
          const hasError = source.error !== null && source.error !== undefined;
          return (
            <li key={`${source.path}-${source.updated_at}`} className={hasError ? 'list-row list-row-error' : 'list-row'}>
              <span className="mono grow" title={source.path}>
                {source.path}
              </span>
              <span className={hasError ? 'badge badge-failed' : 'badge'}>{source.status}</span>
              {source.demo_id !== null && source.demo_id !== undefined ? <span className="mono small">{shortHash(source.demo_id)}</span> : null}
              <span className="small">{formatTimestamp(source.updated_at)}</span>
              {hasError && source.error ? (
                <p className="notice notice-error inline-error" role="alert">
                  <span className="notice-code">{source.error.code}</span>
                  <span>{source.error.message}</span>
                  <span className="notice-meta">{source.error.stage}</span>
                </p>
              ) : null}
            </li>
          );
        })}
        {all.length === 0 ? <li className="list-empty">No source observations yet.</li> : null}
        {all.length > VISIBLE_LIMIT ? <li className="list-empty">{all.length - VISIBLE_LIMIT} more not shown.</li> : null}
      </ul>
      <ErrorNotice error={error} context="GET /sources" />
    </section>
  );
}
