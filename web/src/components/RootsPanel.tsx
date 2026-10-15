import { useState, type FormEvent, type ReactNode } from 'react';
import { client, isAbortError, toApiError, type ApiError } from '../api/client';
import type { RootRecord } from '../api/types';
import { ErrorNotice } from './Notices';

type Props = {
  roots: RootRecord[] | null;
  error: ApiError | null;
  onChanged: () => void;
};

export function RootsPanel({ roots, error, onChanged }: Props): ReactNode {
  const [path, setPath] = useState('');
  const [recursive, setRecursive] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [requestError, setRequestError] = useState<ApiError | null>(null);
  const [busy, setBusy] = useState(false);
  const [scanState, setScanState] = useState<string | null>(null);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const candidate = path.trim();
    if (!candidate.startsWith('/')) {
      setFormError('Watch root must be an absolute local path (starting with "/").');
      return;
    }
    setFormError(null);
    setRequestError(null);
    setBusy(true);
    try {
      await client.addRoot({ path: candidate, recursive });
      setPath('');
      setRecursive(false);
      onChanged();
    } catch (exc) {
      if (!isAbortError(exc)) setRequestError(toApiError(exc));
    } finally {
      setBusy(false);
    }
  };

  const scan = async () => {
    setRequestError(null);
    setBusy(true);
    try {
      const accepted = await client.scan();
      setScanState(`scan ${accepted.status}`);
      onChanged();
    } catch (exc) {
      if (!isAbortError(exc)) setRequestError(toApiError(exc));
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="panel" aria-label="Watch roots">
      <header className="panel-header">
        <h2>Watch roots</h2>
        <button type="button" onClick={() => void scan()} disabled={busy}>
          Scan now
        </button>
      </header>
      {scanState !== null ? (
        <p className="notice" role="status">
          {scanState}
        </p>
      ) : null}
      <ul className="list">
        {(roots ?? []).map((root) => (
          <li key={root.id} className="list-row">
            <span className="mono grow" title={root.path}>
              {root.path}
            </span>
            <span className="badge">{root.recursive ? 'recursive' : 'top-level'}</span>
            <span className={root.available ? 'badge badge-succeeded' : 'badge badge-failed'}>{root.available ? 'available' : 'unavailable'}</span>
            {root.error !== null && root.error !== undefined ? <span className="notice-meta">{root.error}</span> : null}
          </li>
        ))}
        {roots !== null && roots.length === 0 ? <li className="list-empty">No watch roots configured.</li> : null}
      </ul>
      <form className="form" onSubmit={(event) => void submit(event)}>
        <label htmlFor="root-path">Add watch root (absolute local path)</label>
        <input
          id="root-path"
          value={path}
          onChange={(event) => setPath(event.target.value)}
          placeholder="/mnt/nvme/SteamLibrary/steamapps/common/Counter-Strike Global Offensive/game/csgo/replays"
          autoComplete="off"
          spellCheck={false}
        />
        <label className="checkbox">
          <input type="checkbox" checked={recursive} onChange={(event) => setRecursive(event.target.checked)} />
          Recursive
        </label>
        <div className="form-actions">
          <button type="submit" disabled={busy}>
            Add root
          </button>
        </div>
        {formError !== null ? (
          <p className="notice notice-error" role="alert">
            {formError}
          </p>
        ) : null}
        <ErrorNotice error={requestError} context="POST /roots" />
      </form>
      <ErrorNotice error={error} context="GET /roots" />
    </section>
  );
}
