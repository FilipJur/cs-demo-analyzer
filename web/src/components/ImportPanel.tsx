import { useState, type FormEvent, type ReactNode } from 'react';
import { client, isAbortError, toApiError, type ApiError } from '../api/client';
import { ErrorNotice } from './Notices';

export function ImportPanel({ onChanged }: { onChanged: () => void }): ReactNode {
  const [path, setPath] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const [requestError, setRequestError] = useState<ApiError | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const candidate = path.trim();
    if (!candidate.startsWith('/')) {
      setFormError('Import source must be an absolute local file path (starting with "/").');
      return;
    }
    setFormError(null);
    setRequestError(null);
    setStatus(null);
    setBusy(true);
    try {
      const accepted = await client.importFile(candidate);
      setStatus(`import accepted — ${accepted.status}${accepted.demo_id !== undefined && accepted.demo_id !== null ? ` (${accepted.demo_id})` : ''}`);
      setPath('');
      onChanged();
    } catch (exc) {
      if (!isAbortError(exc)) setRequestError(toApiError(exc));
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="panel" aria-label="Import recording">
      <header className="panel-header">
        <h2>Import recording</h2>
      </header>
      <p className="hint">
        One absolute local <span className="mono">.dem</span> path. The file is settled, hashed and snapshotted exactly like a discovered demo; no upload or URL
        import exists.
      </p>
      <form className="form" onSubmit={(event) => void submit(event)}>
        <label htmlFor="import-path">Absolute local demo path</label>
        <input
          id="import-path"
          value={path}
          onChange={(event) => setPath(event.target.value)}
          placeholder="/abs/path/to/match.dem"
          autoComplete="off"
          spellCheck={false}
        />
        <div className="form-actions">
          <button type="submit" disabled={busy}>
            Import file
          </button>
        </div>
        {formError !== null ? (
          <p className="notice notice-error" role="alert">
            {formError}
          </p>
        ) : null}
        {status !== null ? (
          <p className="notice" role="status">
            {status}
          </p>
        ) : null}
        <ErrorNotice error={requestError} context="POST /imports" />
      </form>
    </section>
  );
}
