import { useEffect, useState, type ReactNode } from 'react';
import { isAbortError, toApiError, type ApiError } from '../api/client';
import { phase2 } from '../api/phase2';
import type { Participation, SubjectConfig } from '../api/types';
import { shortHash } from '../lib/format';
import { participationBadge } from '../lib/phase2';
import { usePolled } from '../lib/usePolling';
import { ErrorNotice } from './Notices';

type Props = {
  /** SteamID currently used by the replay/context panels; null until loaded. */
  subjectSteamId: string | null;
  onSubjectChanged: (config: SubjectConfig) => void;
};

const PARTICIPATION_PAGE = 100;

function ParticipationRow({ entry }: { entry: Participation }): ReactNode {
  const measurements = entry.measurements;
  return (
    <li className="list-row" title={entry.limitations.join('\n')}>
      <span className={`badge ${participationBadge(entry.status)}`}>{entry.status}</span>
      <span className="grow truncate mono small" title={entry.demo_id}>
        {shortHash(entry.demo_id)}
      </span>
      <span className="small truncate">{entry.map_name ?? 'map unknown'}</span>
      <span className="mono small" title={entry.player_id ?? ''}>
        {entry.player_id ?? 'no resolved id'} ({entry.player_id_source})
      </span>
      {measurements !== null ? (
        <span className="small">
          {measurements.alive_rows} alive / {measurements.state_rows} rows · {measurements.rounds_with_subject}/{measurements.rounds_total} rounds
        </span>
      ) : (
        <span className="small">no measurements</span>
      )}
      {entry.limitations.length > 0 ? <span className="badge badge-warn">{entry.limitations.length} limitation(s)</span> : null}
    </li>
  );
}

/**
 * The persisted analysis subject, shown for every demo in the catalog.
 *
 * Changing the value only writes the setting: no demo is re-ingested and no
 * existing generation is touched. An absent or unresolved subject is reported
 * as such — a different participant is never substituted.
 */
export function SubjectPanel({ subjectSteamId, onSubjectChanged }: Props): ReactNode {
  const config = usePolled((signal) => phase2.subject(signal), 60000);
  const participation = usePolled((signal) => phase2.participationList({ limit: PARTICIPATION_PAGE, offset: 0 }, signal), 30000);
  const [draft, setDraft] = useState('');
  const [dirty, setDirty] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<ApiError | null>(null);
  const [saveNotice, setSaveNotice] = useState<string | null>(null);

  const current = config.data;
  useEffect(() => {
    if (current !== null && !dirty) setDraft(current.steam_id);
  }, [current, dirty]);

  useEffect(() => {
    if (current !== null && subjectSteamId === null) onSubjectChanged(current);
  }, [current, subjectSteamId, onSubjectChanged]);

  const save = (): void => {
    const value = draft.trim();
    if (value === '') {
      setSaveError(toApiError({ code: 'INVALID_ARGUMENT', message: 'Enter a 17-digit SteamID64', stage: 'client' }));
      return;
    }
    setSaving(true);
    setSaveError(null);
    setSaveNotice(null);
    void (async () => {
      try {
        const updated = await phase2.setSubject({ steam_id: value });
        setDirty(false);
        setSaveNotice(`Saved ${updated.steam_id}; no demo was re-ingested.`);
        onSubjectChanged(updated);
        config.refresh();
        participation.refresh();
      } catch (exc) {
        if (!isAbortError(exc)) setSaveError(toApiError(exc));
      } finally {
        setSaving(false);
      }
    })();
  };

  const rows = participation.data ?? [];

  return (
    <section className="panel" aria-label="Analysis subject">
      <header className="panel-header">
        <h2>Analysis subject</h2>
        <span className="count mono" title={current?.player_id ?? ''}>
          {config.loading ? 'loading…' : current === null ? 'unavailable' : `canonical ${current.player_id ?? 'unresolved'}`}
        </span>
      </header>

      <p className="hint">
        The primary subject is a persisted SteamID64 and stays in force across demos. Every reconstruction read is generation-pinned and uses this identity, or an
        explicitly selected participant — never a substitute.
      </p>

      <div className="form">
        <label htmlFor="subject-steam-id">Primary SteamID64 (exact 17 digits, stored as text)</label>
        <input
          id="subject-steam-id"
          type="text"
          inputMode="numeric"
          className="mono"
          value={draft}
          onChange={(event) => {
            setDirty(true);
            setDraft(event.target.value);
          }}
          aria-invalid={saveError !== null}
        />
        <div className="form-actions">
          <button type="button" onClick={save} disabled={saving || draft.trim() === ''}>
            {saving ? 'Saving…' : 'Save subject'}
          </button>
          <button
            type="button"
            onClick={() => {
              if (current !== null) {
                setDirty(false);
                setDraft(current.steam_id);
                setSaveError(null);
              }
            }}
            disabled={!dirty}
          >
            Revert
          </button>
          <span className="small">
            {current === null ? 'no configured subject' : `updated ${current.updated_at}`}
          </span>
        </div>
      </div>

      <ErrorNotice error={config.error} context="GET /api/v1/analysis-subject" />
      <ErrorNotice error={saveError} context="PUT /api/v1/analysis-subject" />
      {saveNotice !== null ? (
        <p className="notice" role="status">
          {saveNotice}
        </p>
      ) : null}

      <h3>Participation across demos ({rows.length}{participation.data !== null && rows.length === PARTICIPATION_PAGE ? '+' : ''})</h3>
      <ul className="list">
        {rows.map((entry) => (
          <ParticipationRow key={`${entry.demo_id}:${entry.generation_id ?? 'none'}:${entry.player_id ?? 'unresolved'}`} entry={entry} />
        ))}
        {rows.length === 0 ? <li className="list-empty">{participation.loading ? 'Loading participation…' : 'No catalog demos yet.'}</li> : null}
      </ul>
      <ErrorNotice error={participation.error} context="GET /api/v1/subject-participation" />
      <p className="hint">
        <span className="badge badge-succeeded">present</span> <span className="badge badge-failed">absent</span>{' '}
        <span className="badge badge-warn">unresolved</span> <span className="badge badge-queued">not ready</span> — an absent or unresolved subject leaves
        encounter/context reads unavailable instead of silently analysing someone else.
      </p>
    </section>
  );
}
