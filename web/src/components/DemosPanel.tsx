import { useState, type ReactNode } from 'react';
import { client, isAbortError, toApiError, type ApiError } from '../api/client';
import type { DemoRecord, JobRecord } from '../api/types';
import { formatBytes, formatTimestamp, shortHash } from '../lib/format';
import { ErrorNotice, StateBadge } from './Notices';

type Props = {
  demos: DemoRecord[] | null;
  error: ApiError | null;
  latestJobByDemo: Map<string, JobRecord>;
  selectedDemoId: string | null;
  onSelect: (demoId: string) => void;
  onChanged: () => void;
};

export function DemosPanel({ demos, error, latestJobByDemo, selectedDemoId, onSelect, onChanged }: Props): ReactNode {
  const [requestError, setRequestError] = useState<ApiError | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const all = demos ?? [];

  const reprocess = async (demoId: string) => {
    setRequestError(null);
    setBusy(demoId);
    try {
      await client.reprocess(demoId);
      onChanged();
    } catch (exc) {
      if (!isAbortError(exc)) setRequestError(toApiError(exc));
    } finally {
      setBusy(null);
    }
  };

  return (
    <section className="panel" aria-label="Demo library">
      <header className="panel-header">
        <h2>Library</h2>
        <span className="count">{all.length === 0 ? 'no demos' : `${all.length} demo${all.length === 1 ? '' : 's'}`}</span>
      </header>
      <ul className="list list-demos">
        {all.map((demo) => {
          const job = latestJobByDemo.get(demo.demo_id);
          const hasGeneration = demo.generation_id !== null && demo.generation_id !== undefined;
          const name = demo.raw_path.split('/').pop() ?? demo.demo_id;
          const warnings = demo.warnings ?? [];
          return (
            <li key={demo.demo_id} className={demo.demo_id === selectedDemoId ? 'list-row list-row-selected' : 'list-row'}>
              <div className="demo-head">
                <span className="grow truncate" title={demo.raw_path}>
                  {name}
                </span>
                {job ? <StateBadge state={job.state} /> : null}
                {hasGeneration ? <span className="badge badge-succeeded">{demo.quality ?? 'generation'}</span> : <span className="badge badge-failed">no generation</span>}
              </div>
              <div className="demo-meta small">
                <span>{demo.map_name ?? 'unknown map'}</span>
                <span>{formatBytes(demo.size)}</span>
                <span>{formatTimestamp(demo.created_at)}</span>
                <span className="mono" title={demo.demo_id}>
                  demo {shortHash(demo.demo_id)}
                </span>
                {hasGeneration ? (
                  <span className="mono" title={demo.generation_id ?? ''}>
                    gen {shortHash(demo.generation_id ?? '')}
                  </span>
                ) : null}
              </div>
              {warnings.length > 0 ? (
                <details className="demo-warnings">
                  <summary>
                    {warnings.length} warning{warnings.length === 1 ? '' : 's'}
                  </summary>
                  <ul>
                    {warnings.map((warning) => (
                      <li key={warning}>{warning}</li>
                    ))}
                  </ul>
                </details>
              ) : null}
              <div className="form-actions">
                <button type="button" onClick={() => onSelect(demo.demo_id)} disabled={!hasGeneration || demo.demo_id === selectedDemoId}>
                  Open replay
                </button>
                <button type="button" onClick={() => void reprocess(demo.demo_id)} disabled={busy === demo.demo_id}>
                  {busy === demo.demo_id ? 'Requesting…' : 'Reprocess'}
                </button>
              </div>
            </li>
          );
        })}
        {all.length === 0 ? <li className="list-empty">No demos recorded yet. Add a watch root and scan, or import an absolute path.</li> : null}
      </ul>
      <ErrorNotice error={requestError} context="POST /demos/{demo_id}/reprocess" />
      <ErrorNotice error={error} context="GET /demos" />
    </section>
  );
}
